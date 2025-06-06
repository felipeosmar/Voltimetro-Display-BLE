"""
Nó Voltímetro - ESP32 com leitura de 3 canais ADC
Envia dados via BLE para o nó Display
"""

import time
import sys
import gc
from machine import Pin

# Adiciona o diretório comum ao path
sys.path.append('/common')

# Importações locais
from adc_reader import ADCReader
from ble_voltmeter_server import BLEVoltmeterServer
from ble_utils import print_debug

class VoltmeterNode:
    def __init__(self):
        """Inicializa o nó voltímetro"""
        print_debug("Inicializando nó Voltímetro...")
        
        # Estado do nó
        self.running = False
        self.last_measurement = time.time()
        self.last_heartbeat = time.time()
        self.ble_server = None
        
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
            self.status_led.value(0)
            return
        
        # Inicializa o servidor BLE (para ser descoberto pelo PC e Display)
        try:
            self.ble_server = BLEVoltmeterServer(self.adc_reader)
            print_debug("Servidor BLE inicializado")
        except Exception as e:
            print_debug(f"Erro ao inicializar servidor BLE: {e}")
            self.ble_server = None
        
        print_debug("Nó Voltímetro inicializado com sucesso!")
        self.running = True
        
        # Teste inicial dos ADCs
        self.initial_test()
        
        print_debug("Nó Voltímetro pronto - dados disponíveis via BLE")
    
    def initial_test(self):
        """Executa teste inicial dos canais ADC"""
        if not self.adc_reader:
            print_debug("ADC reader não disponível para teste")
            return
            
        print_debug("Executando teste inicial do ADC...")
        
        try:
            # Testa cada canal individualmente
            self.adc_reader.test_channels()
            
            # Faz algumas leituras de teste
            for i in range(5):
                voltages = self.adc_reader.read_all_voltages()
                print_debug(f"Teste {i+1}: {voltages}")
                time.sleep(0.5)
            
            print_debug("Teste inicial concluído")
            
        except Exception as e:
            print_debug(f"Erro no teste inicial: {e}")
    
    def heartbeat(self):
        """Pisca LED de status para indicar que o sistema está funcionando"""
        current_time = time.time()
        if current_time - self.last_heartbeat >= 2:  # Pisca a cada 2 segundos
            self.status_led.value(not self.status_led.value())
            self.last_heartbeat = current_time
    
    def status_info(self):
        """Exibe informações de status periodicamente"""
        try:
            voltages = self.adc_reader.read_all_voltages() if self.adc_reader else [0, 0, 0]
            server_connections = len(self.ble_server.connections) if self.ble_server else 0
            
            print_debug(f"Status - Tensões: {voltages}")
            print_debug(f"Status - Conexões BLE: {server_connections}")
                
        except Exception as e:
            print_debug(f"Erro ao obter status: {e}")
    
    def run(self):
        """Loop principal do nó"""
        print_debug("Iniciando loop principal...")
        
        last_status_time = time.time()
        measurement_interval = 1.0  # Intervalo de medição em segundos
        
        try:
            while self.running:
                current_time = time.time()
                
                # Heartbeat
                self.heartbeat()
                
                # Medições e envio de dados
                if current_time - self.last_measurement >= measurement_interval:
                    self.measure_and_send()
                    self.last_measurement = current_time
                
                # Status info a cada 15 segundos
                if current_time - last_status_time >= 15:
                    self.status_info()
                    last_status_time = current_time
                
                # Limpa memória periodicamente
                if current_time % 30 < 0.1:  # A cada 30 segundos
                    gc.collect()
                
                # Small delay para não sobrecarregar o CPU
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print_debug("Interrupção pelo usuário")
            self.shutdown()
        except Exception as e:
            print_debug(f"Erro no loop principal: {e}")
            self.shutdown()
    
    def measure_and_send(self):
        """Faz medições e atualiza dados do servidor BLE"""
        try:
            if not self.adc_reader:
                return
                
            # Lê as tensões
            voltages = self.adc_reader.read_all_voltages()
            
            # Atualiza os dados no servidor BLE para clientes conectados
            if self.ble_server:
                self.ble_server.update_voltage_data(voltages)
                    
        except Exception as e:
            print_debug(f"Erro ao medir e atualizar: {e}")
    
    def shutdown(self):
        """Desliga o nó graciosamente"""
        print_debug("Desligando nó Voltímetro...")
        
        self.running = False
        
        # Para servidor BLE
        try:
            if self.ble_server:
                # O servidor será desconectado automaticamente quando o BLE for desativado
                pass
        except Exception as e:
            print_debug(f"Erro ao parar servidor BLE: {e}")
        
        # Apaga LED de status
        try:
            self.status_led.value(0)
        except Exception as e:
            print_debug(f"Erro ao apagar LED: {e}")
        
        print_debug("Nó Voltímetro desligado")

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
                time.sleep(0.1)
                error_led.value(0)
                time.sleep(0.1)
        except:
            pass

if __name__ == "__main__":
    main()
