"""
Nó Voltímetro - ESP32 com 3 canais ADC
Lê tensões e transmite via BLE para o nó Display
Também funciona como servidor BLE para conexões de computador
"""

import time
import sys
import gc
from machine import Pin, Timer

# Adiciona o diretório comum ao path
sys.path.append('/common')

# Importações locais
from adc_reader import ADCReader
from ble_client import BLEVoltmeterClient, BLEVoltmeterServer
from ble_utils import print_debug

class VoltmeterNode:
    def __init__(self):
        """Inicializa o nó voltímetro"""
        print_debug("Inicializando nó Voltímetro...")
        
        # LED indicador de status
        self.status_led = Pin(2, Pin.OUT)
        self.status_led.value(0)
        
        # Inicializa o leitor ADC
        try:
            self.adc_reader = ADCReader()
            print_debug("Leitor ADC inicializado")
            self.status_led.value(1)  # LED aceso = ADC OK
        except Exception as e:
            print_debug(f"Erro ao inicializar ADC: {e}")
            return
        
        # Inicializa o cliente BLE (para conectar ao display)
        try:
            self.ble_client = BLEVoltmeterClient(self.adc_reader)
            print_debug("Cliente BLE inicializado")
        except Exception as e:
            print_debug(f"Erro ao inicializar cliente BLE: {e}")
            return
        
        # Inicializa o servidor BLE (para conexões de computador)
        try:
            self.ble_server = BLEVoltmeterServer(self.adc_reader)
            print_debug("Servidor BLE inicializado")
        except Exception as e:
            print_debug(f"Erro ao inicializar servidor BLE: {e}")
            return
        
        # Estado do nó
        self.running = True
        self.last_heartbeat = time.time()
        self.last_scan_attempt = 0
        self.scan_interval = 30  # Tenta reconectar a cada 30 segundos
        self.last_server_update = 0
        self.server_update_interval = 2  # Atualiza servidor a cada 2 segundos
        
        # Timer para leituras periódicas
        self.reading_timer = Timer(0)
        self.reading_timer.init(period=500, mode=Timer.PERIODIC, callback=self._timer_callback)
        
        print_debug("Nó Voltímetro inicializado com sucesso!")
        
        # Teste inicial
        self.initial_test()
        
        # Inicia busca pelo display
        self.start_display_search()
    
    def initial_test(self):
        """Executa teste inicial do ADC"""
        print_debug("Executando teste inicial do ADC...")
        
        # Testa os canais ADC
        self.adc_reader.test_channels()
        
        # Lê tensões algumas vezes
        for i in range(5):
            voltages = self.adc_reader.read_all_voltages()
            print_debug(f"Teste {i+1}: {voltages}")
            time.sleep(0.5)
        
        print_debug("Teste inicial concluído")
    
    def start_display_search(self):
        """Inicia busca pelo nó display"""
        print_debug("Iniciando busca pelo nó Display...")
        self.ble_client.start_scan(10000)  # Scan por 10 segundos
        self.last_scan_attempt = time.time()
    
    def _timer_callback(self, timer):
        """Callback do timer para leituras periódicas"""
        try:
            # Auto-envio de tensões para o display
            if self.ble_client.is_connected():
                self.ble_client.auto_send_voltages()
        except Exception as e:
            print_debug(f"Erro no timer callback: {e}")
    
    def heartbeat(self):
        """Pisca LED de status para indicar funcionamento"""
        current_time = time.time()
        if current_time - self.last_heartbeat >= 1:  # Pisca a cada 1 segundo
            # LED pisca mais rápido se conectado ao display
            if self.ble_client.is_connected():
                self.status_led.value(not self.status_led.value())
            else:
                # Pisca mais devagar se não conectado
                if int(current_time) % 2 == 0:
                    self.status_led.value(1)
                else:
                    self.status_led.value(0)
            
            self.last_heartbeat = current_time
    
    def manage_display_connection(self):
        """Gerencia conexão com o display"""
        current_time = time.time()
        
        # Se não está conectado e passou o intervalo, tenta reconectar
        if not self.ble_client.is_connected():
            if current_time - self.last_scan_attempt >= self.scan_interval:
                if not self.ble_client.scanning:
                    print_debug("Tentando reconectar ao display...")
                    
                    # Tenta conectar com resultados do scan anterior
                    if not self.ble_client.connect_to_display():
                        # Se não conseguiu, inicia novo scan
                        self.ble_client.start_scan(5000)
                    
                    self.last_scan_attempt = current_time
    
    def update_server_data(self):
        """Atualiza dados do servidor BLE"""
        current_time = time.time()
        
        if current_time - self.last_server_update >= self.server_update_interval:
            try:
                self.ble_server.update_voltage_data()
                self.last_server_update = current_time
            except Exception as e:
                print_debug(f"Erro ao atualizar servidor: {e}")
    
    def status_info(self):
        """Exibe informações de status periodicamente"""
        voltages = self.adc_reader.get_last_readings()
        client_connected = self.ble_client.is_connected()
        server_connections = self.ble_server.get_connection_count()
        
        print_debug(f"Status - Tensões: {voltages}")
        print_debug(f"Status - Display conectado: {client_connected}, Clientes PC: {server_connections}")
    
    def run(self):
        """Loop principal do nó"""
        print_debug("Iniciando loop principal...")
        
        last_status_time = time.time()
        
        try:
            while self.running:
                current_time = time.time()
                
                # Heartbeat
                self.heartbeat()
                
                # Gerencia conexão com display
                self.manage_display_connection()
                
                # Atualiza dados do servidor
                self.update_server_data()
                
                # Status info a cada 15 segundos
                if current_time - last_status_time >= 15:
                    self.status_info()
                    last_status_time = current_time
                
                # Limpa memória periodicamente
                if current_time % 60 < 0.1:  # A cada 60 segundos
                    gc.collect()
                
                # Small delay
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print_debug("Interrupção pelo usuário")
            self.shutdown()
        except Exception as e:
            print_debug(f"Erro no loop principal: {e}")
            self.shutdown()
    
    def shutdown(self):
        """Desliga o nó graciosamente"""
        print_debug("Desligando nó Voltímetro...")
        
        self.running = False
        
        # Para o timer
        try:
            self.reading_timer.deinit()
        except:
            pass
        
        # Desconecta do display
        try:
            self.ble_client.disconnect()
        except:
            pass
        
        # Para scan se ativo
        try:
            self.ble_client.stop_scan()
        except:
            pass
        
        # Apaga LED de status
        try:
            self.status_led.value(0)
        except:
            pass
        
        print_debug("Nó Voltímetro desligado")
    
    def calibrate_channel(self, channel, known_voltage):
        """Calibra um canal específico"""
        print_debug(f"Calibrando canal {channel+1} com tensão conhecida {known_voltage}V")
        self.adc_reader.auto_calibrate(channel, known_voltage)
    
    def set_send_interval(self, interval):
        """Define intervalo de envio para o display"""
        self.ble_client.set_send_interval(interval)
    
    def get_diagnostics(self):
        """Retorna informações de diagnóstico"""
        return {
            'adc_info': self.adc_reader.get_channel_info(),
            'client_info': self.ble_client.get_connection_info(),
            'server_connections': self.ble_server.get_connection_count(),
            'running': self.running,
            'uptime': time.time()
        }

def main():
    """Função principal"""
    try:
        # Cria e executa o nó voltímetro
        node = VoltmeterNode()
        node.run()
    except Exception as e:
        print_debug(f"Erro fatal: {e}")
        # Pisca LED rapidamente para indicar erro
        try:
            error_led = Pin(2, Pin.OUT)
            for _ in range(20):
                error_led.value(1)
                time.sleep(0.05)
                error_led.value(0)
                time.sleep(0.05)
        except:
            pass

if __name__ == "__main__":
    main()
