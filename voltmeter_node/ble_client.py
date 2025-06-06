import bluetooth
import time
import sys
sys.path.append('/common')
from constants import *
from ble_utils import BLEUtils, print_debug, _IRQ_PERIPHERAL_CONNECT, _IRQ_PERIPHERAL_DISCONNECT, _IRQ_GATTC_SERVICE_RESULT, _IRQ_GATTC_SERVICE_DONE, _IRQ_GATTC_CHARACTERISTIC_RESULT, _IRQ_GATTC_CHARACTERISTIC_DONE, _IRQ_GATTC_WRITE_DONE, _IRQ_SCAN_RESULT, _IRQ_SCAN_DONE, _IRQ_CENTRAL_CONNECT, _IRQ_CENTRAL_DISCONNECT

class BLEVoltmeterClient:
    def __init__(self, adc_reader):
        """Inicializa o cliente BLE para o nó voltímetro"""
        self.adc_reader = adc_reader
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.ble.irq(self._irq_handler)
        
        # Estado da conexão
        self.connected = False
        self.conn_handle = None
        self.display_service_handle = None
        self.voltage_char_handle = None
        
        # Estado do scan
        self.scanning = False
        self.scan_results = []
        
        # Buffer para envio de dados
        self.pending_data = None
        self.last_send_time = 0
        self.send_interval = 1.0  # Envia dados a cada 1 segundo
        
        print_debug("Cliente BLE do Voltímetro inicializado")
    
    def start_scan(self, duration_ms=10000):
        """Inicia scan para encontrar o nó display"""
        print_debug("Iniciando scan BLE...")
        self.scanning = True
        self.scan_results = []
        
        # Inicia o scan
        self.ble.gap_scan(duration_ms, 30000, 30000)
    
    def stop_scan(self):
        """Para o scan BLE"""
        if self.scanning:
            self.ble.gap_scan(None)
            self.scanning = False
            print_debug("Scan BLE parado")
    
    def connect_to_display(self, addr_type=None, addr=None):
        """Conecta ao nó display"""
        if addr_type is not None and addr is not None:
            print_debug(f"Tentando conectar ao display: {addr}")
            try:
                self.ble.gap_connect(addr_type, addr)
                return True
            except Exception as e:
                print_debug(f"Erro ao conectar: {e}")
                return False
        else:
            # Procura por displays nos resultados do scan
            for addr_type, addr, adv_type, rssi, adv_data in self.scan_results:
                if self._is_display_device(adv_data):
                    print_debug(f"Encontrado display, conectando... RSSI: {rssi}")
                    return self.connect_to_display(addr_type, addr)
            
            print_debug("Nenhum display encontrado nos resultados do scan")
            return False
    
    def _is_display_device(self, adv_data):
        """Verifica se o dispositivo é um nó display"""
        try:
            # Procura pelo nome do dispositivo nos dados de advertising
            name = self._extract_name_from_adv_data(adv_data)
            return name == BLE_NAME_DISPLAY
        except:
            return False
    
    def _extract_name_from_adv_data(self, adv_data):
        """Extrai o nome do dispositivo dos dados de advertising"""
        try:
            i = 0
            while i < len(adv_data):
                length = adv_data[i]
                if length == 0:
                    break
                
                ad_type = adv_data[i + 1]
                ad_data = adv_data[i + 2:i + 1 + length]
                
                # Tipo 0x09 = Complete Local Name
                if ad_type == 0x09:
                    return ad_data.decode('utf-8')
                
                i += 1 + length
        except:
            pass
        return None
    
    def disconnect(self):
        """Desconecta do display"""
        if self.connected and self.conn_handle is not None:
            try:
                self.ble.gap_disconnect(self.conn_handle)
            except:
                pass
    
    def _irq_handler(self, event, data):
        """Manipula eventos BLE"""
        if event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            self.scan_results.append((addr_type, addr, adv_type, rssi, adv_data))
            
            # Verifica se é um display
            if self._is_display_device(adv_data):
                print_debug(f"Display encontrado! RSSI: {rssi}")
        
        elif event == _IRQ_SCAN_DONE:
            self.scanning = False
            print_debug(f"Scan concluído. Dispositivos encontrados: {len(self.scan_results)}")
        
        elif event == _IRQ_PERIPHERAL_CONNECT:
            conn_handle, addr_type, addr = data
            self.conn_handle = conn_handle
            print_debug(f"Conectado ao display: {conn_handle}")
            
            # Descobrir serviços
            self.ble.gattc_discover_services(conn_handle)
        
        elif event == _IRQ_PERIPHERAL_DISCONNECT:
            conn_handle, addr_type, addr = data
            self.connected = False
            self.conn_handle = None
            self.display_service_handle = None
            self.voltage_char_handle = None
            print_debug("Desconectado do display")
        
        elif event == _IRQ_GATTC_SERVICE_RESULT:
            conn_handle, start_handle, end_handle, uuid = data
            if uuid == DISPLAY_SERVICE_UUID:
                self.display_service_handle = start_handle
                print_debug(f"Serviço do display encontrado: {start_handle}")
        
        elif event == _IRQ_GATTC_SERVICE_DONE:
            if self.display_service_handle:
                # Descobrir características
                self.ble.gattc_discover_characteristics(self.conn_handle, self.display_service_handle)
        
        elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT:
            conn_handle, def_handle, value_handle, properties, uuid = data
            if uuid == VOLTAGE_CHAR_UUID:
                self.voltage_char_handle = value_handle
                print_debug(f"Característica de tensão encontrada: {value_handle}")
        
        elif event == _IRQ_GATTC_CHARACTERISTIC_DONE:
            if self.voltage_char_handle:
                self.connected = True
                print_debug("Conexão estabelecida com sucesso!")
        
        elif event == _IRQ_GATTC_WRITE_DONE:
            conn_handle, value_handle, status = data
            if status == 0:
                print_debug("Dados enviados com sucesso")
            else:
                print_debug(f"Erro ao enviar dados: {status}")
    
    def send_voltage_data(self, voltages):
        """Envia dados de tensão para o display"""
        if not self.connected or not self.voltage_char_handle:
            return False
        
        try:
            data = BLEUtils.encode_voltage_data(voltages)
            self.ble.gattc_write(self.conn_handle, self.voltage_char_handle, data)
            return True
        except Exception as e:
            print_debug(f"Erro ao enviar dados de tensão: {e}")
            return False
    
    def auto_send_voltages(self):
        """Envia automaticamente as tensões lidas"""
        current_time = time.time()
        
        if current_time - self.last_send_time >= self.send_interval:
            if self.connected:
                voltages = self.adc_reader.read_all_voltages()
                success = self.send_voltage_data(voltages)
                
                if success:
                    print_debug(f"Tensões enviadas: {voltages}")
                else:
                    print_debug("Falha ao enviar tensões")
                
                self.last_send_time = current_time
    
    def set_send_interval(self, interval_seconds):
        """Define o intervalo de envio de dados"""
        self.send_interval = max(0.1, interval_seconds)  # Mínimo 100ms
        print_debug(f"Intervalo de envio definido para {self.send_interval}s")
    
    def is_connected(self):
        """Verifica se está conectado ao display"""
        return self.connected
    
    def get_connection_info(self):
        """Retorna informações da conexão"""
        return {
            'connected': self.connected,
            'conn_handle': self.conn_handle,
            'scanning': self.scanning,
            'scan_results': len(self.scan_results),
            'send_interval': self.send_interval,
            'last_send_time': self.last_send_time
        }

class BLEVoltmeterServer:
    def __init__(self, adc_reader, ble_instance=None):
        """Servidor BLE do voltímetro para conexões de computador"""
        self.adc_reader = adc_reader
        
        # Usa instância BLE compartilhada ou cria nova
        if ble_instance:
            self.ble = ble_instance
            self.shared_ble = True
        else:
            self.ble = bluetooth.BLE()
            self.ble.active(True)
            self.shared_ble = False
        
        # Adiciona handler para eventos de servidor
        if hasattr(self.ble, '_original_irq_handler'):
            self.original_handler = self.ble._original_irq_handler
        else:
            self.original_handler = None
            
        self.ble._original_irq_handler = self.ble._irq_handler if hasattr(self.ble, '_irq_handler') else None
        self.ble.irq(self._combined_irq_handler)
        
        # Conexões ativas
        self.connections = set()
        self.server_enabled = False
        
        try:
            # Configura serviços
            self._setup_services()
            
            # Marca como habilitado
            self.server_enabled = True
            
            print_debug("Servidor BLE do Voltímetro inicializado")
        except Exception as e:
            print_debug(f"Erro ao configurar servidor BLE: {e}")
            self.server_enabled = False
    
    def _combined_irq_handler(self, event, data):
        """Handler combinado para eventos BLE do cliente e servidor"""
        # Primeiro, chama o handler original se existir
        if self.original_handler:
            try:
                self.original_handler(event, data)
            except:
                pass
        
        # Depois processa eventos do servidor
        self._server_irq_handler(event, data)
    
    def _server_irq_handler(self, event, data):
        """Manipula eventos BLE do servidor"""
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, addr_type, addr = data
            self.connections.add(conn_handle)
            print_debug(f"Cliente conectado ao servidor voltímetro: {conn_handle}")
        
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, addr_type, addr = data
            self.connections.discard(conn_handle)
            print_debug(f"Cliente desconectado do servidor voltímetro: {conn_handle}")
    
    def _setup_services(self):
        """Configura os serviços BLE"""
        # Serviço do Voltímetro
        VOLTMETER_SERVICE = (
            VOLTMETER_SERVICE_UUID,
            (
                # Característica para ler tensões
                (VOLTAGE_CHAR_UUID, bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY),
                # Característica para comandos
                (COMMAND_CHAR_UUID, bluetooth.FLAG_WRITE | bluetooth.FLAG_READ),
            ),
        )
        
        # Registra os serviços
        ((self.voltage_handle, self.command_handle),) = self.ble.gatts_register_services((VOLTMETER_SERVICE,))
        
        print_debug("Serviços BLE do voltímetro registrados")
    
    def start_advertising(self):
        """Inicia advertising BLE"""
        if not self.server_enabled:
            return False
            
        try:
            payload = BLEUtils.advertising_payload(
                name=BLE_NAME_VOLTMETER,
                services=[VOLTMETER_SERVICE_UUID]
            )
            
            self.ble.gap_advertise(100, payload)
            print_debug(f"Advertising iniciado como '{BLE_NAME_VOLTMETER}'")
            return True
        except Exception as e:
            print_debug(f"Erro ao iniciar advertising: {e}")
            return False
    
    def stop_advertising(self):
        """Para advertising BLE"""
        try:
            self.ble.gap_advertise(None)
            print_debug("Advertising parado")
        except Exception as e:
            print_debug(f"Erro ao parar advertising: {e}")
    
    def _start_advertising(self):
        """Inicia advertising BLE (método legado)"""
        self.start_advertising()
    
    def update_voltage_data(self):
        """Atualiza dados de tensão e notifica clientes"""
        if not self.server_enabled or not self.adc_reader:
            return
            
        try:
            voltages = self.adc_reader.read_all_voltages()
            data = BLEUtils.encode_voltage_data(voltages)
            
            # Atualiza a característica
            self.ble.gatts_write(self.voltage_handle, data)
            
            # Notifica clientes
            for conn_handle in list(self.connections):
                try:
                    self.ble.gatts_notify(conn_handle, self.voltage_handle)
                except:
                    self.connections.discard(conn_handle)
        
        except Exception as e:
            print_debug(f"Erro ao atualizar dados do servidor: {e}")
    
    def get_connection_count(self):
        """Retorna número de conexões ativas"""
        return len(self.connections) if self.server_enabled else 0
