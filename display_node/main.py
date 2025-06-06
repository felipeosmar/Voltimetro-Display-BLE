"""
Nó Display - ESP32 com 3 displays de 7 segmentos
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
        print_debug("Inicializando nó Display...")
        
        # LED indicador de status
        self.status_led = Pin(2, Pin.OUT)
        self.status_led.value(0)
        
        # Inicializa o controlador dos displays
        try:
            self.display_controller = DisplayController()
            print_debug("Controlador de displays inicializado")
            self.status_led.value(1)  # LED aceso = displays OK
        except Exception as e:
            print_debug(f"Erro ao inicializar displays: {e}")
            return
        
        # Inicializa o servidor BLE
        try:
            self.ble_server = BLEDisplayServer(self.display_controller)
            print_debug("Servidor BLE inicializado")
        except Exception as e:
            print_debug(f"Erro ao inicializar BLE: {e}")
            return
        
        # Estado do nó
        self.running = True
        self.last_heartbeat = time.time()
        
        print_debug("Nó Display inicializado com sucesso!")
        
        # Teste inicial dos displays
        self.initial_test()
    
    def initial_test(self):
        """Executa teste inicial dos displays"""
        print_debug("Executando teste inicial...")
        
        # Mostra "888" em todos os displays por 2 segundos
        self.display_controller.display_texts(['8', '8', '8'])
        time.sleep(2)
        
        # Mostra contagem 0-9 em todos os displays
        for i in range(10):
            self.display_controller.display_texts([str(i), str(i), str(i)])
            time.sleep(0.3)
        
        # Limpa os displays
        self.display_controller.clear_all()
        time.sleep(0.5)
        
        # Mostra valores padrão
        self.display_controller.display_texts(['0.0', '0.0', '0.0'])
        
        print_debug("Teste inicial concluído")
    
    def heartbeat(self):
        """Pisca LED de status para indicar que o sistema está funcionando"""
        current_time = time.time()
        if current_time - self.last_heartbeat >= 2:  # Pisca a cada 2 segundos
            self.status_led.value(not self.status_led.value())
            self.last_heartbeat = current_time
    
    def status_info(self):
        """Exibe informações de status periodicamente"""
        connections = self.ble_server.get_connection_count()
        current_values = self.display_controller.get_current_values()
        
        print_debug(f"Status - Conexões: {connections}, Displays: {current_values}")
    
    def run(self):
        """Loop principal do nó"""
        print_debug("Iniciando loop principal...")
        
        last_status_time = time.time()
        
        try:
            while self.running:
                # Heartbeat
                self.heartbeat()
                
                # Status info a cada 10 segundos
                current_time = time.time()
                if current_time - last_status_time >= 10:
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
        
        # Limpa displays
        try:
            self.display_controller.clear_all()
        except:
            pass
        
        # Apaga LED de status
        try:
            self.status_led.value(0)
        except:
            pass
        
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
            for _ in range(10):
                error_led.value(1)
                time.sleep(0.1)
                error_led.value(0)
                time.sleep(0.1)
        except:
            pass

if __name__ == "__main__":
    main()
