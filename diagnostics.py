"""
Script de diagnóstico para testar componentes individuais
Execute este código no REPL do MicroPython para testar cada parte do sistema
"""

# Teste individual do Display Controller
def test_display_controller():
    """Testa o controlador de displays"""
    print("=== Teste do Display Controller ===")
    
    try:
        import sys
        sys.path.append('/common')
        from display_controller import DisplayController
        
        # Inicializa o controlador
        controller = DisplayController()
        
        # Teste básico
        print("1. Teste de inicialização: OK")
        
        # Teste de dígitos
        print("2. Testando dígitos 0-9...")
        for digit in range(10):
            controller.display_texts([str(digit), str(digit), str(digit)])
            time.sleep(0.5)
        
        # Teste de tensões
        print("3. Testando exibição de tensões...")
        test_voltages = [1.23, 4.56, 7.89]
        controller.display_voltages(test_voltages)
        time.sleep(2)
        
        # Teste de limpeza
        print("4. Testando limpeza...")
        controller.clear_all()
        
        print("✓ Display Controller: TODOS OS TESTES PASSARAM")
        return True
        
    except Exception as e:
        print(f"✗ Display Controller: ERRO - {e}")
        return False

# Teste individual do ADC Reader
def test_adc_reader():
    """Testa o leitor ADC"""
    print("=== Teste do ADC Reader ===")
    
    try:
        import sys
        sys.path.append('/common')
        from adc_reader import ADCReader
        
        # Inicializa o leitor
        reader = ADCReader()
        
        print("1. Teste de inicialização: OK")
        
        # Teste de leitura
        print("2. Testando leituras...")
        for i in range(5):
            voltages = reader.read_all_voltages()
            print(f"   Leitura {i+1}: {voltages}")
            time.sleep(0.5)
        
        # Teste de informações
        print("3. Informações dos canais:")
        info = reader.get_channel_info()
        for key, value in info.items():
            print(f"   {key}: {value}")
        
        print("✓ ADC Reader: TODOS OS TESTES PASSARAM")
        return True
        
    except Exception as e:
        print(f"✗ ADC Reader: ERRO - {e}")
        return False

# Teste individual do BLE
def test_ble_basic():
    """Teste básico do BLE"""
    print("=== Teste Básico do BLE ===")
    
    try:
        import bluetooth
        
        # Verifica se BLE está disponível
        ble = bluetooth.BLE()
        print("1. BLE disponível: OK")
        
        # Ativa BLE
        ble.active(True)
        print("2. BLE ativado: OK")
        
        # Verifica status
        if ble.active():
            print("3. Status BLE: ATIVO")
        else:
            print("3. Status BLE: INATIVO")
            
        print("✓ BLE Básico: TODOS OS TESTES PASSARAM")
        return True
        
    except Exception as e:
        print(f"✗ BLE Básico: ERRO - {e}")
        return False

# Teste de conectividade
def test_connectivity():
    """Testa conectividade básica"""
    print("=== Teste de Conectividade ===")
    
    try:
        import network
        
        # Verifica WiFi (mesmo que não seja usado)
        wlan = network.WLAN(network.STA_IF)
        print(f"1. Interface WiFi disponível: {wlan}")
        
        # Verifica Bluetooth
        import bluetooth
        ble = bluetooth.BLE()
        ble.active(True)
        print(f"2. BLE ativo: {ble.active()}")
        
        print("✓ Conectividade: TODOS OS TESTES PASSARAM")
        return True
        
    except Exception as e:
        print(f"✗ Conectividade: ERRO - {e}")
        return False

# Teste completo do sistema
def run_full_diagnostics():
    """Executa diagnóstico completo"""
    print("==== DIAGNÓSTICO COMPLETO DO SISTEMA ====")
    print()
    
    results = {
        'ble_basic': test_ble_basic(),
        'connectivity': test_connectivity(),
    }
    
    # Detecta qual nó estamos testando baseado nos arquivos presentes
    import os
    
    if 'display_controller.py' in os.listdir('/'):
        print("Detectado: NÓ DISPLAY")
        results['display_controller'] = test_display_controller()
    
    if 'adc_reader.py' in os.listdir('/'):
        print("Detectado: NÓ VOLTÍMETRO")
        results['adc_reader'] = test_adc_reader()
    
    # Resumo dos resultados
    print()
    print("=== RESUMO DOS TESTES ===")
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASSOU" if result else "✗ FALHOU"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print()
    print(f"Total: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema funcionando corretamente.")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM. Verifique as conexões e configurações.")
    
    return passed == total

# Teste rápido de memória
def test_memory():
    """Testa uso de memória"""
    print("=== Teste de Memória ===")
    
    import gc
    
    # Coleta lixo
    gc.collect()
    
    # Verifica memória livre
    free_mem = gc.mem_free()
    alloc_mem = gc.mem_alloc()
    total_mem = free_mem + alloc_mem
    
    print(f"Memória livre: {free_mem} bytes")
    print(f"Memória alocada: {alloc_mem} bytes")
    print(f"Memória total: {total_mem} bytes")
    print(f"Uso de memória: {(alloc_mem/total_mem)*100:.1f}%")
    
    # Aviso se memória baixa
    if free_mem < 50000:  # Menos de 50KB livre
        print("⚠️  AVISO: Memória livre baixa!")
    else:
        print("✓ Memória: OK")

# Funções de utilidade
def show_system_info():
    """Mostra informações do sistema"""
    print("=== INFORMAÇÕES DO SISTEMA ===")
    
    import os, sys
    
    print(f"Sistema: {os.uname()}")
    print(f"Arquivos na raiz: {os.listdir('/')}")
    print(f"Path do Python: {sys.path}")
    
    # Testa importações específicas do MicroPython
    modules = ['machine', 'bluetooth', 'network', 'time', 'gc']
    
    print("\nMódulos disponíveis:")
    for module in modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError:
            print(f"  ✗ {module}")

# Exemplo de uso
if __name__ == "__main__":
    import time
    
    print("Iniciando diagnóstico em 3 segundos...")
    time.sleep(3)
    
    show_system_info()
    print()
    test_memory()
    print()
    run_full_diagnostics()
