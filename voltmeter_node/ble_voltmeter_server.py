import bluetooth
import time
import sys
sys.path.append('/common')
from constants import *
from ble_utils import BLEUtils, print_debug, _IRQ_CENTRAL_CONNECT, _IRQ_CENTRAL_DISCONNECT, _IRQ_GATTS_WRITE

class BLEVoltmeterServer:
    """Servidor BLE para o voltímetro - permite conexões de PCs para monitoramento"""
    
    def __init__(self, adc_reader):
        """Inicializa o servidor BLE para o nó voltímetro"""
        self.adc_reader = adc_reader
        self.connections = set()
        self.voltage_handle = None
        self.command_handle = None
        
        try:
            # Inicializa BLE
            self.ble = bluetooth.BLE()
            self.ble.active(True)
            time.sleep(0.5)  # Aguarda inicialização
            
            # Configura handler de eventos
            self.ble.irq(self._irq_handler)
            
            # Configura os serviços e características
            self._setup_services()
            
            # Inicia o advertising
            self._start_advertising()
            
            print_debug("Servidor BLE do Voltímetro inicializado")
            
        except Exception as e:
            print_debug(f"Erro ao inicializar servidor BLE: {e}")
            raise e
    
    def _setup_services(self):
        """Configura os serviços e características BLE"""
        # Serviço do Voltímetro
        VOLTMETER_SERVICE = (
            VOLTMETER_SERVICE_UUID,
            (
                # Característica para ler dados de tensão
                (VOLTAGE_CHAR_UUID, bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY),
                # Característica para receber comandos
                (COMMAND_CHAR_UUID, bluetooth.FLAG_WRITE | bluetooth.FLAG_READ),
            ),
        )
        
        # Registra os serviços
        ((self.voltage_handle, self.command_handle),) = self.ble.gatts_register_services((VOLTMETER_SERVICE,))
        
        print_debug("Serviços BLE do voltímetro registrados")
    
    def _start_advertising(self):
        """Inicia o advertising BLE"""
        payload = BLEUtils.advertising_payload(
            name=BLE_NAME_VOLTMETER,
            services=[VOLTMETER_SERVICE_UUID]
        )
        
        self.ble.gap_advertise(100, payload)
        print_debug(f"Advertising iniciado como '{BLE_NAME_VOLTMETER}'")
    
    def _irq_handler(self, event, data):
        """Manipula eventos BLE"""
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, addr_type, addr = data
            self.connections.add(conn_handle)
            print_debug(f"PC conectado: {conn_handle}, Total conexões: {len(self.connections)}")
            
            # Se ainda há espaço para mais conexões, continua advertising
            if len(self.connections) < MAX_CONNECTIONS:
                self._start_advertising()
        
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, addr_type, addr = data
            self.connections.discard(conn_handle)
            print_debug(f"PC desconectado: {conn_handle}, Total conexões: {len(self.connections)}")
            
            # Reinicia advertising se há espaço
            if len(self.connections) < MAX_CONNECTIONS:
                self._start_advertising()
        
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            
            if value_handle == self.command_handle:
                self._handle_command_data(conn_handle)
    
    def _handle_command_data(self, conn_handle):
        """Processa comandos recebidos de PCs"""
        try:
            data = self.ble.gatts_read(self.command_handle)
            command = data.decode('utf-8').strip()
            
            print_debug(f"Comando recebido de PC: '{command}'")
            
            if command == "GET_VOLTAGES":
                # Comando para ler tensões atuais
                voltages = self.adc_reader.read_all_voltages() if self.adc_reader else [0, 0, 0]
                self.update_voltage_data(voltages)
                print_debug(f"Tensões enviadas para PC: {voltages}")
            
            elif command == "TEST_ADC":
                # Comando para testar ADCs
                if self.adc_reader:
                    self.adc_reader.test_channels()
                    print_debug("Teste ADC executado")
            
            else:
                print_debug(f"Comando desconhecido de PC: {command}")
                
        except Exception as e:
            print_debug(f"Erro ao processar comando de PC: {e}")
    
    def update_voltage_data(self, voltages):
        """Atualiza dados de tensão e notifica clientes"""
        try:
            data = BLEUtils.encode_voltage_data(voltages)
            
            # Atualiza a característica
            self.ble.gatts_write(self.voltage_handle, data)
            
            # Notifica todos os clientes conectados
            for conn_handle in list(self.connections):
                try:
                    self.ble.gatts_notify(conn_handle, self.voltage_handle)
                except:
                    # Remove conexões inválidas
                    self.connections.discard(conn_handle)
                    
        except Exception as e:
            print_debug(f"Erro ao atualizar dados de tensão: {e}")
    
    def get_connection_count(self):
        """Retorna o número de conexões ativas"""
        return len(self.connections)
    
    def is_connected(self):
        """Verifica se há pelo menos uma conexão ativa"""
        return len(self.connections) > 0