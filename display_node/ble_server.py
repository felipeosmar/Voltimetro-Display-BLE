import bluetooth
import time
import sys
sys.path.append('/common')
from constants import *
from ble_utils import BLEUtils, print_debug, _IRQ_CENTRAL_CONNECT, _IRQ_CENTRAL_DISCONNECT, _IRQ_GATTS_WRITE

class BLEDisplayServer:
    def __init__(self, display_controller):
        """Inicializa o servidor BLE para o nó display"""
        self.display_controller = display_controller
        self.connections = set()
        self.voltage_handle = None
        self.command_handle = None
        self.display_handle = None
        
        try:
            # Inicializa BLE com tentativas múltiplas
            self.ble = bluetooth.BLE()
            
            # Primeira tentativa de ativação
            print_debug("Tentativa 1: Ativando BLE...")
            try:
                self.ble.active(True)
                time.sleep(1)  # Aguarda mais tempo
                print_debug("BLE ativado com sucesso")
            except Exception as e:
                print_debug(f"Tentativa 1 falhou: {e}, tentando reinicializar...")
                # Segunda tentativa: desativa e reativa
                try:
                    self.ble.active(False)
                    time.sleep(0.5)
                    self.ble.active(True)
                    time.sleep(1.5)
                    print_debug("BLE ativado na segunda tentativa")
                except Exception as e2:
                    print_debug(f"Tentativa 2 falhou: {e2}")
                    raise Exception(f"Falha ao ativar BLE: {e2}")
            
            # Configura handler de eventos
            self.ble.irq(self._irq_handler)
            
            # Configura os serviços e características
            self._setup_services()
            
            # Inicia o advertising
            self._start_advertising()
            
            print_debug("Servidor BLE do Display inicializado")
            
        except Exception as e:
            print_debug(f"Erro ao inicializar BLE: {e}")
            raise e
    
    def _setup_services(self):
        """Configura os serviços e características BLE"""
        # Serviço do Display
        DISPLAY_SERVICE = (
            DISPLAY_SERVICE_UUID,
            (
                # Característica para receber dados de tensão
                (VOLTAGE_CHAR_UUID, bluetooth.FLAG_WRITE | bluetooth.FLAG_NOTIFY),
                # Característica para receber comandos de texto
                (COMMAND_CHAR_UUID, bluetooth.FLAG_WRITE | bluetooth.FLAG_READ),
                # Característica para ler valores atuais do display
                (DISPLAY_CHAR_UUID, bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY),
            ),
        )
        
        # Registra os serviços
        ((self.voltage_handle, self.command_handle, self.display_handle),) = self.ble.gatts_register_services((DISPLAY_SERVICE,))
        
        print_debug("Serviços BLE registrados")
    
    def _start_advertising(self):
        """Inicia o advertising BLE"""
        payload = BLEUtils.advertising_payload(
            name=BLE_NAME_DISPLAY,
            services=[DISPLAY_SERVICE_UUID]
        )
        
        self.ble.gap_advertise(100, payload)
        print_debug(f"Advertising iniciado como '{BLE_NAME_DISPLAY}'")
    
    def _irq_handler(self, event, data):
        """Manipula eventos BLE"""
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, addr_type, addr = data
            self.connections.add(conn_handle)
            print_debug(f"Cliente conectado: {conn_handle}, Total conexões: {len(self.connections)}")
            
            # Se ainda há espaço para mais conexões, continua advertising
            if len(self.connections) < MAX_CONNECTIONS:
                self._start_advertising()
        
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, addr_type, addr = data
            self.connections.discard(conn_handle)
            print_debug(f"Cliente desconectado: {conn_handle}, Total conexões: {len(self.connections)}")
            
            # Reinicia advertising se há espaço
            if len(self.connections) < MAX_CONNECTIONS:
                self._start_advertising()
        
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            
            if value_handle == self.voltage_handle:
                self._handle_voltage_data(conn_handle)
            elif value_handle == self.command_handle:
                self._handle_command_data(conn_handle)
    
    def _handle_voltage_data(self, conn_handle):
        """Processa dados de tensão recebidos"""
        try:
            data = self.ble.gatts_read(self.voltage_handle)
            voltages = BLEUtils.decode_voltage_data(data)
            
            print_debug(f"Tensões recebidas: {voltages}")
            
            # Exibe as tensões nos displays (agora com 4 dígitos cada)
            success = self.display_controller.display_voltages(voltages)
            
            if success:
                print_debug("Tensões exibidas com sucesso nos displays multiplexados")
                # Notifica clientes sobre a atualização
                self._notify_display_update()
            else:
                print_debug("Erro ao exibir tensões")
                
        except Exception as e:
            print_debug(f"Erro ao processar dados de tensão: {e}")
    
    def _handle_command_data(self, conn_handle):
        """Processa comandos recebidos"""
        try:
            data = self.ble.gatts_read(self.command_handle)
            command = data.decode('utf-8').strip()
            
            print_debug(f"Comando recebido: '{command}'")
            
            if command.startswith("TEXT:"):
                # Comando para exibir texto: "TEXT:1234,5678,9012"
                text_data = command[5:]  # Remove "TEXT:"
                texts = text_data.split(',')
                
                # Ajusta textos para 4 dígitos se necessário
                adjusted_texts = []
                for text in texts:
                    adjusted_texts.append(text[:4])  # Limita a 4 caracteres
                
                success = self.display_controller.display_texts(adjusted_texts)
                if success:
                    print_debug(f"Textos exibidos nos displays 4-dígitos: {adjusted_texts}")
                    self._notify_display_update()
            
            elif command == "CLEAR":
                # Comando para limpar displays
                self.display_controller.clear_all()
                print_debug("Displays multiplexados limpos")
                self._notify_display_update()
            
            elif command == "TEST":
                # Comando para testar displays
                print_debug("Iniciando teste dos displays multiplexados")
                self.display_controller.test_all_displays()
            
            elif command.startswith("TEST_DISP:"):
                # Comando para testar display específico: "TEST_DISP:1"
                try:
                    disp_num = int(command[10:]) - 1  # Remove "TEST_DISP:" e converte para índice
                    if 0 <= disp_num <= 2:
                        self.display_controller.test_individual_display(disp_num)
                        print_debug(f"Teste do display {disp_num + 1} executado")
                except ValueError:
                    print_debug("Número de display inválido")
            
            elif command.startswith("VOLT:"):
                # Comando para exibir tensões específicas: "VOLT:12.34,56.78,90.12"
                volt_data = command[5:]  # Remove "VOLT:"
                try:
                    voltages = [float(v.strip()) for v in volt_data.split(',')]
                    success = self.display_controller.display_voltages(voltages)
                    if success:
                        print_debug(f"Tensões manuais exibidas: {voltages}")
                        self._notify_display_update()
                except ValueError:
                    print_debug("Formato de tensão inválido")
            
            elif command.startswith("NUM:"):
                # Comando para exibir números com formatação específica: "NUM:1234,5678,9012"
                num_data = command[4:]  # Remove "NUM:"
                try:
                    numbers = num_data.split(',')
                    formatted_nums = []
                    for num in numbers:
                        # Formata número para 4 dígitos com zeros à esquerda se necessário
                        if num.strip().isdigit():
                            formatted_nums.append(f"{int(num.strip()):04d}")
                        else:
                            formatted_nums.append(num.strip()[:4])
                    
                    success = self.display_controller.display_texts(formatted_nums)
                    if success:
                        print_debug(f"Números formatados exibidos: {formatted_nums}")
                        self._notify_display_update()
                except ValueError:
                    print_debug("Formato de número inválido")
            
            else:
                print_debug(f"Comando desconhecido: {command}")
                
        except Exception as e:
            print_debug(f"Erro ao processar comando: {e}")
    
    def _notify_display_update(self):
        """Notifica clientes sobre atualização do display"""
        try:
            current_values = self.display_controller.get_current_values()
            data = BLEUtils.encode_display_data(current_values)
            
            # Atualiza a característica
            self.ble.gatts_write(self.display_handle, data)
            
            # Notifica todos os clientes conectados
            for conn_handle in list(self.connections):
                try:
                    self.ble.gatts_notify(conn_handle, self.display_handle)
                except:
                    # Remove conexões inválidas
                    self.connections.discard(conn_handle)
                    
        except Exception as e:
            print_debug(f"Erro ao notificar atualização: {e}")
    
    def send_display_data(self, texts):
        """Envia dados para exibição (chamada externa)"""
        try:
            success = self.display_controller.display_texts(texts)
            if success:
                self._notify_display_update()
            return success
        except Exception as e:
            print_debug(f"Erro ao enviar dados para display: {e}")
            return False
    
    def get_connection_count(self):
        """Retorna o número de conexões ativas"""
        return len(self.connections)
    
    def is_connected(self):
        """Verifica se há pelo menos uma conexão ativa"""
        return len(self.connections) > 0
