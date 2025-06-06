#!/usr/bin/env python3
"""
Teste específico para verificar se as correções do erro BLE -18 funcionam
Este script deve ser executado diretamente no ESP32 para validar as correções
"""

import time
import gc
import sys
import os

def test_ble_error18_fix():
    """Testa as correções implementadas para o erro BLE -18"""
    
    print("=== TESTE DE CORREÇÃO DO ERRO BLE -18 ===")
    print("Este teste verifica se as estratégias implementadas resolvem o problema")
    print("")
    
    # Teste 1: Importação dos módulos corrigidos
    print("1. Testando importação dos módulos corrigidos...")
    try:
        sys.path.append('/common')
        from constants import *
        print("   ✓ constants.py importado")
        
        # Testa se os módulos corrigidos existem
        try:
            import bluetooth
            print("   ✓ bluetooth disponível")
        except ImportError as e:
            print(f"   ❌ bluetooth não disponível: {e}")
            return False
            
        # Importa módulo de correção se existir
        try:
            if os.path.exists('ble_fixed.py'):
                import ble_fixed
                print("   ✓ ble_fixed.py encontrado")
            else:
                print("   ⚠️  ble_fixed.py não encontrado (será gerado)")
        except Exception as e:
            print(f"   ⚠️  Erro ao importar ble_fixed: {e}")
            
    except Exception as e:
        print(f"   ❌ Erro na importação: {e}")
        return False
    
    # Teste 2: Executa script de correção
    print("\n2. Executando script de correção automática...")
    try:
        # Importa e executa o script de correção
        exec(open('fix_ble_error18.py').read())
        print("   ✓ Script de correção executado")
    except Exception as e:
        print(f"   ❌ Erro no script de correção: {e}")
        # Continua mesmo se falhar, pois podemos testar manualmente
    
    # Teste 3: Testa estratégias de inicialização BLE manualmente
    print("\n3. Testando estratégias de inicialização BLE...")
    
    strategies_results = {}
    
    # Estratégia 1: Reset + Delay
    print("   Testando Estratégia 1: Reset + Delay")
    try:
        result = test_ble_strategy_reset_delay()
        strategies_results["reset_delay"] = result
        print(f"   {'✓' if result else '❌'} Estratégia Reset + Delay: {'SUCESSO' if result else 'FALHA'}")
    except Exception as e:
        print(f"   ❌ Erro na Estratégia 1: {e}")
        strategies_results["reset_delay"] = False
    
    # Estratégia 2: Conservadora
    print("   Testando Estratégia 2: Conservadora")
    try:
        result = test_ble_strategy_conservative()
        strategies_results["conservative"] = result
        print(f"   {'✓' if result else '❌'} Estratégia Conservadora: {'SUCESSO' if result else 'FALHA'}")
    except Exception as e:
        print(f"   ❌ Erro na Estratégia 2: {e}")
        strategies_results["conservative"] = False
    
    # Estratégia 3: GC Intensivo
    print("   Testando Estratégia 3: GC Intensivo")
    try:
        result = test_ble_strategy_gc_heavy()
        strategies_results["gc_heavy"] = result
        print(f"   {'✓' if result else '❌'} Estratégia GC Intensivo: {'SUCESSO' if result else 'FALHA'}")
    except Exception as e:
        print(f"   ❌ Erro na Estratégia 3: {e}")
        strategies_results["gc_heavy"] = False
    
    # Estratégia 4: Retry Exponencial
    print("   Testando Estratégia 4: Retry Exponencial")
    try:
        result = test_ble_strategy_exponential()
        strategies_results["exponential"] = result
        print(f"   {'✓' if result else '❌'} Estratégia Retry Exponencial: {'SUCESSO' if result else 'FALHA'}")
    except Exception as e:
        print(f"   ❌ Erro na Estratégia 4: {e}")
        strategies_results["exponential"] = False
    
    # Teste 4: Testa módulos corrigidos
    print("\n4. Testando módulos BLE corrigidos...")
    
    # Testa display node corrigido
    print("   Testando Display Node corrigido...")
    try:
        from display_node.ble_server_fixed import FixedBLEDisplayServer
        print("   ✓ FixedBLEDisplayServer importado")
        
        # Simula display controller
        class MockDisplayController:
            def update_voltages(self, v1, v2, v3):
                pass
            def show_text(self, text):
                pass
            def clear_all(self):
                pass
        
        mock_display = MockDisplayController()
        
        # Tenta inicializar
        try:
            ble_display = FixedBLEDisplayServer(mock_display)
            print("   ✓ FixedBLEDisplayServer inicializado")
            ble_display.stop()
            strategies_results["display_fixed"] = True
        except Exception as e:
            print(f"   ❌ Erro ao inicializar FixedBLEDisplayServer: {e}")
            strategies_results["display_fixed"] = False
            
    except ImportError as e:
        print(f"   ❌ Erro ao importar FixedBLEDisplayServer: {e}")
        strategies_results["display_fixed"] = False
    
    # Testa voltmeter node corrigido
    print("   Testando Voltmeter Node corrigido...")
    try:
        from voltmeter_node.ble_voltmeter_server_fixed import FixedBLEVoltmeterServer
        print("   ✓ FixedBLEVoltmeterServer importado")
        
        # Simula ADC reader
        class MockADCReader:
            def read_all_voltages(self):
                return 3.3, 2.5, 1.8
        
        mock_adc = MockADCReader()
        
        # Tenta inicializar
        try:
            ble_voltmeter = FixedBLEVoltmeterServer(mock_adc)
            print("   ✓ FixedBLEVoltmeterServer inicializado")
            ble_voltmeter.stop()
            strategies_results["voltmeter_fixed"] = True
        except Exception as e:
            print(f"   ❌ Erro ao inicializar FixedBLEVoltmeterServer: {e}")
            strategies_results["voltmeter_fixed"] = False
            
    except ImportError as e:
        print(f"   ❌ Erro ao importar FixedBLEVoltmeterServer: {e}")
        strategies_results["voltmeter_fixed"] = False
    
    # Teste 5: Resumo dos resultados
    print("\n5. RESUMO DOS RESULTADOS:")
    print("=" * 50)
    
    successful_strategies = []
    failed_strategies = []
    
    for strategy, result in strategies_results.items():
        status = "✓ SUCESSO" if result else "❌ FALHA"
        print(f"   {strategy:20} : {status}")
        
        if result:
            successful_strategies.append(strategy)
        else:
            failed_strategies.append(strategy)
    
    print("=" * 50)
    
    if successful_strategies:
        print(f"\n🎉 ESTRATÉGIAS QUE FUNCIONARAM ({len(successful_strategies)}):")
        for strategy in successful_strategies:
            print(f"   • {strategy}")
        
        print(f"\n📋 RECOMENDAÇÃO:")
        print(f"   Use a estratégia '{successful_strategies[0]}' como padrão")
        
        # Cria arquivo de configuração
        create_working_config(successful_strategies[0])
        
        return True
        
    else:
        print(f"\n❌ NENHUMA ESTRATÉGIA FUNCIONOU!")
        print(f"   Possíveis problemas:")
        print(f"   • Firmware MicroPython incompatível")
        print(f"   • Hardware ESP32 com BLE defeituoso")
        print(f"   • Configuração de sistema incorreta")
        
        print(f"\n🔧 PRÓXIMOS PASSOS:")
        print(f"   1. Verifique a versão do MicroPython")
        print(f"   2. Teste com firmware diferente")
        print(f"   3. Verifique se o BLE está habilitado no ESP32")
        
        return False

def test_ble_strategy_reset_delay():
    """Testa estratégia de reset + delay"""
    try:
        import bluetooth
        
        # Reset prévio
        try:
            temp_ble = bluetooth.BLE()
            temp_ble.active(False)
            time.sleep(1)
        except:
            pass
        
        gc.collect()
        time.sleep(0.5)
        
        # Inicialização principal
        ble = bluetooth.BLE()
        time.sleep(0.3)
        ble.active(True)
        time.sleep(1.2)
        
        # Verifica se funcionou
        if ble.active():
            ble.active(False)
            return True
        else:
            return False
            
    except Exception as e:
        if hasattr(e, 'errno') and e.errno == -18:
            return False
        raise e

def test_ble_strategy_conservative():
    """Testa estratégia conservadora"""
    try:
        import bluetooth
        
        ble = bluetooth.BLE()
        
        # Verifica estado anterior
        try:
            if ble.active():
                ble.active(False)
                time.sleep(0.8)
        except:
            pass
        
        # Ativa com verificação
        ble.active(True)
        time.sleep(1.0)
        
        # Verifica se ativação foi bem-sucedida
        if ble.active():
            ble.active(False)
            return True
        else:
            return False
            
    except Exception as e:
        if hasattr(e, 'errno') and e.errno == -18:
            return False
        raise e

def test_ble_strategy_gc_heavy():
    """Testa estratégia com garbage collection intensivo"""
    try:
        import bluetooth
        
        # Limpeza intensiva de memória
        for i in range(4):
            gc.collect()
            time.sleep(0.1)
        
        ble = bluetooth.BLE()
        gc.collect()
        time.sleep(0.4)
        
        ble.active(True)
        gc.collect()
        time.sleep(0.8)
        
        # Verifica se funcionou
        if ble.active():
            ble.active(False)
            return True
        else:
            return False
            
    except Exception as e:
        if hasattr(e, 'errno') and e.errno == -18:
            return False
        raise e

def test_ble_strategy_exponential():
    """Testa estratégia com retry exponencial"""
    try:
        import bluetooth
        
        max_retries = 3
        base_delay = 0.2
        
        for attempt in range(max_retries):
            try:
                ble = bluetooth.BLE()
                
                # Delay exponencial
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
                
                ble.active(True)
                time.sleep(delay * 1.5)
                
                # Verifica se ativou corretamente
                if ble.active():
                    ble.active(False)
                    return True
                    
            except Exception as e:
                if hasattr(e, 'errno') and e.errno == -18:
                    if attempt == max_retries - 1:
                        return False
                    continue
                else:
                    raise e
                    
            time.sleep(0.15)
        
        return False
        
    except Exception as e:
        if hasattr(e, 'errno') and e.errno == -18:
            return False
        raise e

def create_working_config(best_strategy):
    """Cria arquivo de configuração com a estratégia que funcionou"""
    
    config_content = f"""# Configuração BLE que funcionou
# Gerado automaticamente em {time.time()}
# Melhor estratégia: {best_strategy}

WORKING_BLE_STRATEGY = "{best_strategy}"

# Use esta configuração nos seus projetos:
# from ble_working_config import WORKING_BLE_STRATEGY

print(f"Usando estratégia BLE: {{WORKING_BLE_STRATEGY}}")
"""
    
    try:
        with open('ble_working_config.py', 'w') as f:
            f.write(config_content)
        print(f"\n✓ Configuração salva em 'ble_working_config.py'")
    except Exception as e:
        print(f"\n⚠️  Erro ao salvar configuração: {e}")

def main():
    """Função principal do teste"""
    try:
        success = test_ble_error18_fix()
        
        if success:
            print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
            print("As correções para o erro BLE -18 estão funcionando.")
            print("\nPróximos passos:")
            print("1. Use os módulos *_fixed.py em seus projetos")
            print("2. Execute main_fixed.py ao invés de main.py")
            print("3. Monitore os logs para verificar estabilidade")
        else:
            print("\n❌ TESTE FALHOU!")
            print("As correções não resolveram o erro BLE -18.")
            print("\nVerifique:")
            print("1. Versão do MicroPython")
            print("2. Compatibilidade do hardware ESP32")
            print("3. Configurações do sistema")
        
        return success
        
    except Exception as e:
        print(f"\n💥 ERRO CRÍTICO NO TESTE: {e}")
        return False

if __name__ == "__main__":
    main()
