"""
Ponto de entrada principal do nó display com correções para erro BLE -18
Utiliza o servidor BLE corrigido que implementa múltiplas estratégias
"""

import time
import sys
import gc
sys.path.append('/common')

from constants import *
from display_controller import DisplayController
from ble_server_fixed import FixedBLEDisplayServer

def main():
    """Função principal do nó display com tratamento robusto de erros"""
    print("=== INICIALIZANDO NÓ DISPLAY (VERSÃO CORRIGIDA) ===")
    
    display_controller = None
    ble_server = None
    
    try:
        # Força limpeza inicial de memória
        gc.collect()
        
        # Inicializa controlador do display
        print("Inicializando controlador do display...")
        display_controller = DisplayController()
        print("✓ Controlador do display inicializado")
        
        # Teste inicial do display
        print("Testando display...")
        display_controller.display_texts(["INIT", "INIT", "INIT"])
        time.sleep(1)
        display_controller.clear_all()
        print("✓ Display testado")
        
        # Inicializa servidor BLE corrigido
        print("Inicializando servidor BLE corrigido...")
        ble_server = FixedBLEDisplayServer(display_controller)
        print("✓ Servidor BLE inicializado com sucesso")
        
        # Exibe mensagem de pronto
        display_controller.display_texts(["RDY", "RDY", "RDY"])
        print("✓ Nó Display pronto para receber conexões")
        
        # Loop principal
        loop_count = 0
        last_status_time = 0
        status_interval = 30  # Status a cada 30 segundos
        
        while True:
            try:
                current_time = time.time()
                
                # Atualiza display (não há método update_display, a multiplexação é automática)
                # A multiplexação roda automaticamente via timer
                
                # Status periódico
                if current_time - last_status_time > status_interval:
                    num_connections = len(ble_server.connections) if ble_server else 0
                    print(f"Status: {num_connections} conexões ativas")
                    last_status_time = current_time
                
                # Garbage collection periódico
                loop_count += 1
                if loop_count % 1000 == 0:
                    gc.collect()
                    loop_count = 0
                
                # Delay pequeno para não sobrecarregar
                time.sleep(0.001)
                
            except KeyboardInterrupt:
                print("\n⚠️  Interrupção pelo usuário")
                break
                
            except Exception as e:
                print(f"⚠️  Erro no loop principal: {e}")
                time.sleep(1)  # Pausa antes de continuar
                
    except Exception as e:
        print(f"❌ Erro crítico na inicialização: {e}")
        
        # Tenta mostrar erro no display se possível
        if display_controller:
            try:
                display_controller.display_texts(["ERR", "ERR", "ERR"])
            except:
                pass
        
        return False
        
    finally:
        # Limpeza final
        print("\n=== FINALIZANDO NÓ DISPLAY ===")
        
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
        
        # Limpeza final de memória
        gc.collect()
        print("✓ Recursos liberados")
    
    return True

def test_mode():
    """Modo de teste do display sem BLE"""
    print("=== MODO DE TESTE DO DISPLAY ===")
    
    try:
        # Inicializa apenas o display
        display_controller = DisplayController()
        
        # Sequência de teste
        test_sequence = [
            ("8888", "Todos os segmentos"),
            ("123", "Números sequenciais"),
            ("AbC", "Letras"),
            ("HELo", "Texto"),
            ("12.34", "Com ponto decimal"),
            ("", "Display limpo")
        ]
        
        for text, description in test_sequence:
            print(f"Testando: {description}")
            if text:
                display_controller.display_texts([text, text, text])
            else:
                display_controller.clear_all()
            time.sleep(2)
        
        print("✓ Teste concluído")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    # Verifica se deve executar em modo de teste
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        success = test_mode()
    else:
        success = main()
    
    if success:
        print("✅ Execução concluída com sucesso")
    else:
        print("❌ Execução falhou")
