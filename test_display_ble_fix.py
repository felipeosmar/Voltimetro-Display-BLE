# filepath: test_display_ble_fix.py
"""
Teste de correção para erro BLE -18 no ESP32 Display
Este script tenta diferentes estratégias para inicializar o BLE
"""

import bluetooth
import time
from machine import Pin

def test_ble_initialization():
    """Testa diferentes estratégias de inicialização BLE"""
    led = Pin(2, Pin.OUT)
    led.value(0)
    
    print("=== TESTE DE CORREÇÃO BLE -18 ===")
    
    # Estratégia 1: Inicialização básica
    print("Estratégia 1: Inicialização básica...")
    try:
        ble = bluetooth.BLE()
        ble.active(True)
        time.sleep(1)
        print("✓ Estratégia 1: Sucesso")
        led.value(1)
        return ble
    except Exception as e:
        print(f"✗ Estratégia 1: Falhou - {e}")
    
    # Estratégia 2: Reinicialização
    print("Estratégia 2: Reinicialização...")
    try:
        ble = bluetooth.BLE()
        ble.active(False)
        time.sleep(0.5)
        ble.active(True)
        time.sleep(2)
        print("✓ Estratégia 2: Sucesso")
        led.value(1)
        return ble
    except Exception as e:
        print(f"✗ Estratégia 2: Falhou - {e}")
    
    # Estratégia 3: Múltiplas tentativas
    print("Estratégia 3: Múltiplas tentativas...")
    for attempt in range(5):
        try:
            print(f"  Tentativa {attempt + 1}/5...")
            ble = bluetooth.BLE()
            ble.active(False)
            time.sleep(0.2)
            ble.active(True)
            time.sleep(1 + attempt * 0.5)  # Tempo crescente
            print(f"✓ Estratégia 3: Sucesso na tentativa {attempt + 1}")
            led.value(1)
            return ble
        except Exception as e:
            print(f"  Tentativa {attempt + 1}: {e}")
            time.sleep(0.5)
    
    # Estratégia 4: Reset completo
    print("Estratégia 4: Reset completo...")
    try:
        import machine
        print("  Aguardando 3 segundos...")
        time.sleep(3)
        ble = bluetooth.BLE()
        ble.active(True)
        time.sleep(2)
        print("✓ Estratégia 4: Sucesso")
        led.value(1)
        return ble
    except Exception as e:
        print(f"✗ Estratégia 4: Falhou - {e}")
    
    print("❌ TODAS AS ESTRATÉGIAS FALHARAM")
    print("Possíveis causas:")
    print("1. Firmware MicroPython não suporta BLE")
    print("2. Hardware BLE defeituoso")
    print("3. Conflito com WiFi (se ativo)")
    print("4. Memória insuficiente")
    
    # Pisca LED em padrão de erro
    for _ in range(20):
        led.value(1)
        time.sleep(0.1)
        led.value(0)
        time.sleep(0.1)
    
    return None

def test_simple_advertising(ble):
    """Testa advertising simples se BLE funcionar"""
    if not ble:
        return False
    
    print("\n=== TESTE DE ADVERTISING ===")
    try:
        # Payload mínimo
        payload = bytes([
            2, 0x01, 0x06,  # Flags: General Discoverable + BR/EDR Not Supported
            13, 0x09,       # Complete Local Name (12 chars + type)
        ]) + b"ESP32_Test"
        
        print(f"Payload: {len(payload)} bytes")
        print(f"Conteúdo: {payload}")
        
        # Tenta advertising
        ble.gap_advertise(100, payload)
        print("✓ Advertising iniciado com sucesso!")
        
        # Loop de teste
        for i in range(10):
            print(f"Advertising ativo: {i+1}/10")
            time.sleep(1)
        
        ble.gap_advertise(None)  # Para advertising
        print("✓ Teste de advertising concluído")
        return True
        
    except Exception as e:
        print(f"✗ Erro no advertising: {e}")
        return False

def main():
    """Função principal"""
    print("Iniciando teste de correção BLE...")
    
    # Testa inicialização
    ble = test_ble_initialization()
    
    if ble:
        print("\n🎉 BLE INICIALIZADO COM SUCESSO!")
        # Testa advertising
        if test_simple_advertising(ble):
            print("\n🎉 TESTE COMPLETO REALIZADO COM SUCESSO!")
            print("O BLE está funcionando corretamente")
        else:
            print("\n⚠️ BLE inicializado mas advertising falhou")
    else:
        print("\n❌ FALHA TOTAL NA INICIALIZAÇÃO BLE")
        print("Verifique:")
        print("1. Firmware MicroPython com suporte BLE")
        print("2. Modelo do ESP32 (alguns não têm BLE)")
        print("3. Memória disponível")

if __name__ == "__main__":
    main()
