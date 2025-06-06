"""
Display Node main com servidor BLE sem advertising
Contorna o erro -18 usando conexões diretas
"""

import time
import sys
import gc
sys.path.append('/common')

from constants import *
from display_controller import DisplayController
from ble_server_no_advertising import NoAdvertisingDisplayServer

def main():
    """Função principal do display node sem advertising"""
    print("=== DISPLAY NODE (SEM ADVERTISING - CONTORNO ERRO -18) ===")
    
    display_controller = None
    ble_server = None
    
    try:
        # Força limpeza inicial
        gc.collect()
        
        # Inicializa controlador do display
        print("Inicializando controlador do display...")
        display_controller = DisplayController()
        print("✓ Controlador do display inicializado")
        
        # Teste inicial
        print("Testando display...")
        display_controller.display_texts(["INIT", "INIT", "INIT"])
        time.sleep(1)
        display_controller.clear_all()
        print("✓ Display testado")
        
        # Inicializa servidor BLE sem advertising
        print("Inicializando servidor BLE (sem advertising)...")
        ble_server = NoAdvertisingDisplayServer(display_controller)
        
        if ble_server.start_server():
            print("✓ Servidor BLE iniciado com sucesso")
            display_controller.display_texts(["RDY", "RDY", "RDY"])
        else:
            raise Exception("Falha ao iniciar servidor BLE")
        
        print("\n🎉 Display Node pronto!")
        print("💡 Modo: Servidor sem advertising (contorna erro -18)")
        print("📡 Aguardando conexões diretas de clientes BLE")
        
        # Loop principal
        loop_count = 0
        last_status_time = 0
        status_interval = 30
        
        while True:
            try:
                current_time = time.time()
                
                # Status periódico
                if current_time - last_status_time > status_interval:
                    connections = ble_server.get_connection_count()
                    print(f"Status: {connections} conexões ativas")
                    
                    # Mostra status no display
                    if connections > 0:
                        display_controller.display_texts(["CON", str(connections), "ACT"])
                    else:
                        display_controller.display_texts(["RDY", "RDY", "RDY"])
                    
                    last_status_time = current_time
                
                # Garbage collection periódico
                loop_count += 1
                if loop_count % 1000 == 0:
                    gc.collect()
                    loop_count = 0
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                print("\\n⚠️  Interrupção pelo usuário")
                break
                
            except Exception as e:
                print(f"⚠️  Erro no loop principal: {e}")
                time.sleep(1)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        
        # Mostra erro no display
        if display_controller:
            try:
                display_controller.display_texts(["ERR", "ERR", "ERR"])
            except:
                pass
        
        return False
        
    finally:
        # Limpeza final
        print("\\n=== FINALIZANDO DISPLAY NODE ===")
        
        if ble_server:
            try:
                ble_server.stop()
                print("✓ Servidor BLE parado")
            except Exception as e:
                print(f"⚠️  Erro ao parar BLE: {e}")
        
        if display_controller:
            try:
                display_controller.clear_all()
                print("✓ Display limpo")
            except Exception as e:
                print(f"⚠️  Erro ao limpar display: {e}")
        
        gc.collect()
        print("✓ Recursos liberados")

def test_mode():
    """Modo de teste apenas do display"""
    print("=== MODO DE TESTE DO DISPLAY ===")
    
    try:
        display_controller = DisplayController()
        
        # Sequência de teste
        tests = [
            (["8888", "8888", "8888"], "Todos os segmentos"),
            (["123", "456", "789"], "Números"),
            (["HELo", "CAr", "dEAd"], "Texto"),
            (["12.3", "45.6", "78.9"], "Decimais"),
        ]
        
        for texts, description in tests:
            print(f"Testando: {description}")
            display_controller.display_texts(texts)
            time.sleep(2)
        
        # Limpa
        display_controller.clear_all()
        print("✓ Teste concluído")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    # Verifica argumentos
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        success = test_mode()
    else:
        success = main()
    
    if success:
        print("✅ Execução concluída com sucesso")
    else:
        print("❌ Execução falhou")
