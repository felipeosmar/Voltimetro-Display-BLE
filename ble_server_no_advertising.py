"""
Servidor BLE alternativo que contorna o erro -18 do advertising
Este servidor funciona apenas como receptor de conexões diretas
"""

import bluetooth
import time
import gc
import sys
sys.path.append('/common')
from constants import *
from ble_utils import BLEUtils, print_debug, _IRQ_CENTRAL_CONNECT, _IRQ_CENTRAL_DISCONNECT, _IRQ_GATTS_WRITE

class NoAdvertisingBLEServer:
    """Servidor BLE que funciona sem advertising para contornar erro -18"""
    
    def __init__(self, controller, node_type="display"):
        """Inicializa servidor BLE sem advertising"""
        self.controller = controller
        self.node_type = node_type
        self.connections = set()
        self.ble = None
        self.handles = {}
        
        # Tenta inicializar BLE
        if self._init_ble_safe():
            print_debug(f"Servidor BLE {node_type} inicializado (sem advertising)")
        else:
            raise Exception("Falha na inicialização do BLE")
    
    def _init_ble_safe(self):
        """Inicialização segura do BLE sem advertising"""
        try:
            # Limpeza prévia
            for _ in range(3):
                gc.collect()
                time.sleep(0.1)
            
            # Inicializa BLE
            self.ble = bluetooth.BLE()
            self.ble.active(True)
            time.sleep(2)
            
            # Configura handler de eventos
            self.ble.irq(self._irq_handler)
            
            # Registra serviços
            if self._setup_services():
                print_debug("BLE inicializado com sucesso (modo servidor)")
                return True
            else:
                print_debug("Erro ao configurar serviços BLE")
                return False
                
        except Exception as e:
            print_debug(f"Erro na inicialização BLE: {e}")
            return False
    
    def _setup_services(self):
        """Configura serviços BLE sem fazer advertising"""
        try:
            if self.node_type == "display":
                # Serviços do display
                services = [
                    (BLE_DISPLAY_SERVICE_UUID, [
                        (BLE_VOLTAGE_CHAR_UUID, bluetooth.FLAG_WRITE),
                        (BLE_COMMAND_CHAR_UUID, bluetooth.FLAG_WRITE),
                        (BLE_DISPLAY_CHAR_UUID, bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY),
                    ]),
                ]
            else:  # voltmeter
                # Serviços do voltímetro
                services = [
                    (BLE_VOLTMETER_SERVICE_UUID, [
                        (BLE_VOLTAGE1_CHAR_UUID, bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY),
                        (BLE_VOLTAGE2_CHAR_UUID, bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY),
                        (BLE_VOLTAGE3_CHAR_UUID, bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY),
                        (BLE_STATUS_CHAR_UUID, bluetooth.FLAG_READ),
                    ]),
                ]
            
            # Registra serviços
            handles = self.ble.gatts_register_services(services)
            
            # Mapeia handles
            if self.node_type == "display":
                ((self.handles['voltage'], self.handles['command'], self.handles['display']),) = handles
            else:
                ((self.handles['voltage1'], self.handles['voltage2'], self.handles['voltage3'], self.handles['status']),) = handles
            
            print_debug(f"Serviços {self.node_type} registrados com sucesso")
            return True
            
        except Exception as e:
            print_debug(f"Erro ao registrar serviços: {e}")
            return False
    
    def _irq_handler(self, event, data):
        """Handler de eventos BLE"""
        try:
            if event == _IRQ_CENTRAL_CONNECT:
                conn_handle, addr_type, addr = data
                self.connections.add(conn_handle)
                print_debug(f"Cliente conectado: {conn_handle}")
                
            elif event == _IRQ_CENTRAL_DISCONNECT:
                conn_handle, addr_type, addr = data
                self.connections.discard(conn_handle)
                print_debug(f"Cliente desconectado: {conn_handle}")
                
            elif event == _IRQ_GATTS_WRITE:
                conn_handle, value_handle = data
                self._handle_write(conn_handle, value_handle)
                
        except Exception as e:
            print_debug(f"Erro no handler BLE: {e}")
    
    def _handle_write(self, conn_handle, value_handle):
        """Processa dados escritos pelo cliente"""
        try:
            data = self.ble.gatts_read(value_handle)
            
            if self.node_type == "display":
                # Display node - processa comandos e voltagens
                if value_handle == self.handles.get('voltage'):
                    # Dados de voltagem recebidos
                    voltages = BLEUtils.decode_voltage_data(data)
                    if voltages and len(voltages) >= 3:
                        self.controller.display_voltages(voltages)
                        print_debug(f"Voltagens exibidas: {voltages}")
                        
                elif value_handle == self.handles.get('command'):
                    # Comando recebido
                    command = data.decode('utf-8').strip()
                    self._process_command(command)
                    
        except Exception as e:
            print_debug(f"Erro ao processar escrita: {e}")
    
    def _process_command(self, command):
        """Processa comandos recebidos"""
        try:
            print_debug(f"Comando recebido: {command}")
            
            if command.startswith("TEXT:"):
                # Comando de texto
                text_data = command[5:]
                texts = text_data.split(',')
                self.controller.display_texts(texts[:3])
                
            elif command == "CLEAR":
                # Limpar displays
                self.controller.clear_all()
                
        except Exception as e:
            print_debug(f"Erro ao processar comando: {e}")
    
    def start_server(self):
        """Inicia o servidor (sem advertising)"""
        try:
            print_debug("Servidor BLE ativo - aguardando conexões diretas")
            print_debug("Nota: Advertising desabilitado para contornar erro -18")
            print_debug("Clientes devem conectar diretamente ao endereço MAC")
            
            # Tenta obter endereço MAC para conexão direta
            try:
                mac = self.ble.config('mac')
                mac_str = ':'.join(['%02x' % b for b in mac[1]])
                print_debug(f"Endereço MAC para conexão direta: {mac_str}")
            except:
                print_debug("Não foi possível obter endereço MAC")
            
            return True
            
        except Exception as e:
            print_debug(f"Erro ao iniciar servidor: {e}")
            return False
    
    def stop(self):
        """Para o servidor BLE"""
        try:
            if self.ble:
                # Desconecta todos os clientes
                for conn_handle in list(self.connections):
                    try:
                        self.ble.gap_disconnect(conn_handle)
                    except:
                        pass
                
                # Desativa BLE
                self.ble.active(False)
                self.ble = None
                
                print_debug("Servidor BLE parado")
                
        except Exception as e:
            print_debug(f"Erro ao parar servidor: {e}")
    
    def get_connection_count(self):
        """Retorna número de conexões ativas"""
        return len(self.connections)
    
    def is_connected(self):
        """Verifica se há conexões ativas"""
        return len(self.connections) > 0

# Para compatibilidade com código existente
class NoAdvertisingDisplayServer(NoAdvertisingBLEServer):
    def __init__(self, display_controller):
        super().__init__(display_controller, "display")

class NoAdvertisingVoltmeterServer(NoAdvertisingBLEServer):
    def __init__(self, adc_reader):
        super().__init__(adc_reader, "voltmeter")
        self.adc_reader = adc_reader
        
    def update_voltages(self):
        """Atualiza leituras de voltagem (para uso do voltmeter)"""
        try:
            if self.adc_reader and self.is_connected():
                voltages = self.adc_reader.read_all_voltages()
                # Atualiza características BLE com as voltagens
                self._update_voltage_characteristics(voltages)
                
        except Exception as e:
            print_debug(f"Erro ao atualizar voltagens: {e}")
    
    def _update_voltage_characteristics(self, voltages):
        """Atualiza características de voltagem no BLE"""
        try:
            for i, voltage in enumerate(voltages):
                handle_key = f'voltage{i+1}'
                if handle_key in self.handles:
                    data = BLEUtils.encode_voltage_value(voltage)
                    self.ble.gatts_write(self.handles[handle_key], data)
                    
                    # Notifica clientes conectados
                    for conn_handle in self.connections:
                        try:
                            self.ble.gatts_notify(conn_handle, self.handles[handle_key])
                        except:
                            pass
                            
        except Exception as e:
            print_debug(f"Erro ao atualizar características: {e}")
