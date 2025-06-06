#!/usr/bin/env python3
"""
Script para corrigir erro -18 (ESP_ERR_NOT_SUPPORTED) no BLE
Implementa estratégias específicas para resolver problemas de inicialização BLE
"""

import bluetooth
import time
import gc
import sys
sys.path.append('/common')

def force_ble_reset():
    """Força um reset completo do BLE"""
    try:
        print("=== FORÇA RESET DO BLE ===")
        
        # Força garbage collection
        gc.collect()
        
        # Tenta desativar qualquer instância BLE existente
        try:
            ble = bluetooth.BLE()
            ble.active(False)
            print("BLE desativado")
        except:
            print("Nenhuma instância BLE ativa para desativar")
        
        # Aguarda tempo suficiente para reset completo
        time.sleep(2)
        
        # Força mais garbage collection
        gc.collect()
        
        print("Reset do BLE concluído")
        return True
        
    except Exception as e:
        print(f"Erro no reset do BLE: {e}")
        return False

def test_ble_initialization_strategies():
    """Testa diferentes estratégias de inicialização BLE"""
    
    strategies = [
        ("Inicialização Padrão", init_ble_standard),
        ("Inicialização com Delay Longo", init_ble_long_delay),
        ("Inicialização com Reset", init_ble_with_reset),
        ("Inicialização Conservadora", init_ble_conservative),
        ("Inicialização com Retry Exponencial", init_ble_exponential_retry),
    ]
    
    successful_strategy = None
    
    for strategy_name, strategy_func in strategies:
        print(f"\n=== TESTANDO: {strategy_name} ===")
        
        # Reset antes de cada teste
        force_ble_reset()
        time.sleep(1)
        
        try:
            ble = strategy_func()
            if ble:
                print(f"✓ SUCESSO: {strategy_name}")
                successful_strategy = strategy_name
                ble.active(False)  # Limpa para próximo teste
                break
            else:
                print(f"✗ FALHA: {strategy_name}")
                
        except Exception as e:
            print(f"✗ ERRO em {strategy_name}: {e}")
            if hasattr(e, 'errno') and e.errno == -18:
                print("   -> Erro -18 detectado (ESP_ERR_NOT_SUPPORTED)")
            
        time.sleep(1)
    
    return successful_strategy

def init_ble_standard():
    """Inicialização padrão"""
    ble = bluetooth.BLE()
    ble.active(True)
    time.sleep(0.5)
    return ble

def init_ble_long_delay():
    """Inicialização com delays longos"""
    ble = bluetooth.BLE()
    time.sleep(1)  # Delay antes de ativar
    ble.active(True)
    time.sleep(2)  # Delay após ativar
    return ble

def init_ble_with_reset():
    """Inicialização com reset prévio"""
    # Primeira instância só para garantir reset
    try:
        temp_ble = bluetooth.BLE()
        temp_ble.active(False)
        time.sleep(1)
    except:
        pass
    
    # Segunda instância para uso real
    ble = bluetooth.BLE()
    ble.active(True)
    time.sleep(1.5)
    return ble

def init_ble_conservative():
    """Inicialização conservadora com verificações"""
    ble = bluetooth.BLE()
    
    # Verifica se já está ativo
    try:
        if ble.active():
            print("BLE já estava ativo, desativando primeiro...")
            ble.active(False)
            time.sleep(1)
    except:
        pass
    
    # Ativa com delay
    ble.active(True)
    time.sleep(1)
    
    # Verifica se ativação foi bem-sucedida
    if not ble.active():
        raise Exception("Falha na ativação do BLE")
    
    return ble

def init_ble_exponential_retry():
    """Inicialização com retry exponencial"""
    max_retries = 5
    base_delay = 0.5
    
    for attempt in range(max_retries):
        try:
            print(f"Tentativa {attempt + 1}/{max_retries}")
            
            ble = bluetooth.BLE()
            
            # Delay exponencial
            delay = base_delay * (2 ** attempt)
            print(f"Aguardando {delay}s...")
            time.sleep(delay)
            
            ble.active(True)
            
            # Delay após ativação também exponencial
            post_delay = delay / 2
            time.sleep(post_delay)
            
            # Testa se realmente está funcionando
            if ble.active():
                print(f"BLE ativado na tentativa {attempt + 1}")
                return ble
            else:
                print(f"BLE não ativou corretamente na tentativa {attempt + 1}")
                
        except Exception as e:
            print(f"Tentativa {attempt + 1} falhou: {e}")
            if attempt == max_retries - 1:
                raise e
            time.sleep(0.5)
    
    raise Exception("Todas as tentativas falharam")

def create_fixed_ble_module():
    """Cria um módulo BLE com a estratégia que funcionou"""
    print("\n=== CRIANDO MÓDULO BLE CORRIGIDO ===")
    
    # Testa estratégias
    successful_strategy = test_ble_initialization_strategies()
    
    if not successful_strategy:
        print("❌ Nenhuma estratégia funcionou!")
        return False
    
    print(f"\n✓ Estratégia bem-sucedida: {successful_strategy}")
    
    # Cria arquivo com a estratégia que funcionou
    fixed_code = generate_fixed_ble_code(successful_strategy)
    
    with open('/home/felipe/work/display7segBluetooth/projeto/ble_fixed.py', 'w') as f:
        f.write(fixed_code)
    
    print("✓ Módulo BLE corrigido salvo em 'ble_fixed.py'")
    return True

def generate_fixed_ble_code(strategy_name):
    """Gera código BLE corrigido baseado na estratégia que funcionou"""
    
    code_templates = {
        "Inicialização Padrão": """
def init_ble_safe():
    ble = bluetooth.BLE()
    ble.active(True)
    time.sleep(0.5)
    return ble
""",
        
        "Inicialização com Delay Longo": """
def init_ble_safe():
    ble = bluetooth.BLE()
    time.sleep(1)
    ble.active(True)
    time.sleep(2)
    return ble
""",
        
        "Inicialização com Reset": """
def init_ble_safe():
    # Reset prévio
    try:
        temp_ble = bluetooth.BLE()
        temp_ble.active(False)
        time.sleep(1)
    except:
        pass
    
    # Inicialização principal
    ble = bluetooth.BLE()
    ble.active(True)
    time.sleep(1.5)
    return ble
""",
        
        "Inicialização Conservadora": """
def init_ble_safe():
    ble = bluetooth.BLE()
    
    # Verifica estado anterior
    try:
        if ble.active():
            ble.active(False)
            time.sleep(1)
    except:
        pass
    
    # Ativa com verificação
    ble.active(True)
    time.sleep(1)
    
    if not ble.active():
        raise Exception("Falha na ativação do BLE")
    
    return ble
""",
        
        "Inicialização com Retry Exponencial": """
def init_ble_safe():
    max_retries = 5
    base_delay = 0.5
    
    for attempt in range(max_retries):
        try:
            ble = bluetooth.BLE()
            delay = base_delay * (2 ** attempt)
            time.sleep(delay)
            ble.active(True)
            time.sleep(delay / 2)
            
            if ble.active():
                return ble
                
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(0.5)
    
    raise Exception("Todas as tentativas falharam")
"""
    }
    
    template = code_templates.get(strategy_name, code_templates["Inicialização Padrão"])
    
    full_code = f'''"""
Módulo BLE corrigido para erro -18
Estratégia utilizada: {strategy_name}
Gerado automaticamente pelo script fix_ble_error18.py
"""

import bluetooth
import time
import gc

{template}

class SafeBLEWrapper:
    """Wrapper seguro para BLE que evita erro -18"""
    
    def __init__(self):
        self.ble = None
        self.is_active = False
    
    def initialize(self):
        """Inicializa BLE de forma segura"""
        try:
            # Força garbage collection
            gc.collect()
            
            # Usa estratégia que funcionou
            self.ble = init_ble_safe()
            self.is_active = True
            
            print(f"BLE inicializado com sucesso usando: {strategy_name}")
            return True
            
        except Exception as e:
            print(f"Erro ao inicializar BLE: {{e}}")
            self.is_active = False
            return False
    
    def get_ble(self):
        """Retorna instância BLE se inicializada"""
        if not self.is_active or not self.ble:
            raise Exception("BLE não foi inicializado corretamente")
        return self.ble
    
    def cleanup(self):
        """Limpa recursos BLE"""
        if self.ble:
            try:
                self.ble.active(False)
            except:
                pass
        self.ble = None
        self.is_active = False
        gc.collect()

# Instância global para uso fácil
safe_ble = SafeBLEWrapper()
'''
    
    return full_code

def main():
    """Função principal do script de correção"""
    print("=== SCRIPT DE CORREÇÃO DO ERRO BLE -18 ===")
    print("Este script vai testar diferentes estratégias de inicialização BLE")
    print("para resolver o erro ESP_ERR_NOT_SUPPORTED (-18)\n")
    
    try:
        # Executa testes e cria módulo corrigido
        if create_fixed_ble_module():
            print("\n🎉 CORREÇÃO CONCLUÍDA COM SUCESSO!")
            print("\nPróximos passos:")
            print("1. Use o módulo 'ble_fixed.py' em seus projetos")
            print("2. Substitua a inicialização BLE padrão pela versão corrigida")
            print("3. Teste no hardware real")
        else:
            print("\n❌ NÃO FOI POSSÍVEL CORRIGIR O PROBLEMA")
            print("Possíveis causas:")
            print("- Firmware MicroPython incompatível")
            print("- Hardware ESP32 com BLE defeituoso")
            print("- Configuração de sistema incorreta")
            
    except Exception as e:
        print(f"\n❌ ERRO DURANTE A CORREÇÃO: {e}")

if __name__ == "__main__":
    main()
