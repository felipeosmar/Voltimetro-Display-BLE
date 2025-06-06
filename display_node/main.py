"""
Nó Display - ESP32 com 3 displays de 7 segmentos multiplexados (4 dígitos cada)
Recebe dados via BLE e exibe nos displays
"""

import time
import sys
import gc
from machine import Pin

# Adiciona o diretório comum ao path
sys.path.append('/common')

# Importações locais
from display_controller import DisplayController
from ble_server import BLEDisplayServer
from ble_utils import print_debug

class DisplayNode:
    def __init__(self):
        """Inicializa o nó display"""
        print_debug("Inicializando nó Display com displays multiplexados...")
        
        # Estado do nó (inicializar antes de tudo)
        self.running = False
        self.last_heartbeat = time.time()
        self.ble_server = None
        self.display_controller = None
        
        # LED indicador de status
        self.status_led = Pin(2, Pin.OUT)
        self.status_led.value(0)
        
        # Inicializa o controlador dos displays
        try:
            self.display_controller = DisplayController()
            print_debug("Controlador de displays multiplexados inicializado")
            self.status_led.value(1)  # LED aceso = displays OK
        except Exception as e:
            print_debug(f"Erro ao inicializar displays: {e}")
            self.status_led.value(0)
            return
        
        # Inicializa o servidor BLE
        try:
            print_debug("Tentando inicializar servidor BLE...")
            self.ble_server = BLEDisplayServer(self.display_controller)
            print_debug("Servidor BLE inicializado com sucesso")
            self.running = True  # Só marca como funcionando se BLE OK
        except Exception as e:
            print_debug(f"Erro ao inicializar BLE: {e}")
            print_debug("Continuando sem BLE - apenas displays funcionando")
            # Continua sem BLE, apenas com displays
            self.ble_server = None
            self.running = True
            return
        
        print_debug("Nó Display inicializado com sucesso!")
        
        # Teste inicial dos displays
        self.initial_test()
    
    def initial_test(self):
        """Executa teste inicial dos displays"""
        if not self.display_controller:
            print_debug("Display controller não disponível para teste")
            return
            
        print_debug("Executando teste inicial dos displays multiplexados...")
        
        try:
            # Mostra "8888" em todos os displays por 3 segundos
            self.display_controller.display_texts(['8888', '8888', '8888'])
            time.sleep(3)
            
            # Mostra contagem 0-9 em todos os displays
            for i in range(10):
                num_str = f"{i:4d}"  # Número com 4 dígitos, alinhado à direita
                self.display_controller.display_texts([num_str, num_str, num_str])
                time.sleep(0.5)
            
            # Limpa os displays
            self.display_controller.clear_all()
            time.sleep(0.5)
            
            # Mostra valores padrão de voltagem
            self.display_controller.display_voltages([0.00, 0.00, 0.00])
            
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
            connections = self.ble_server.get_connection_count() if self.ble_server else 0
            current_values = self.display_controller.get_current_values() if self.display_controller else ['', '', '']
            
            print_debug(f"Status - Conexões: {connections}, Displays: {current_values}")
        except Exception as e:
            print_debug(f"Erro ao obter status: {e}")
    
    def run(self):
        """Loop principal do nó"""
        print_debug("Iniciando loop principal...")
        
        last_status_time = time.time()
        
        try:
            while self.running:
                # Heartbeat
                self.heartbeat()
                
                # Status info a cada 15 segundos
                current_time = time.time()
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
    
    def shutdown(self):
        """Desliga o nó graciosamente"""
        print_debug("Desligando nó Display...")
        
        self.running = False
        
        # Para multiplexação e limpa displays
        try:
            if self.display_controller:
                self.display_controller.stop_multiplexing()
                self.display_controller.clear_all()
        except Exception as e:
            print_debug(f"Erro ao parar displays: {e}")
        
        # Apaga LED de status
        try:
            self.status_led.value(0)
        except Exception as e:
            print_debug(f"Erro ao apagar LED: {e}")
        
        print_debug("Nó Display desligado")

def main():
    """Função principal"""
    try:
        # Cria e executa o nó display
        node = DisplayNode()
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
