# filepath: test_ble_basic.py
"""
Teste básico de BLE para ESP32 - apenas advertising
Deve ser executado no ESP32 para testar a funcionalidade BLE básica
"""

import bluetooth
import time
from machine import Pin

def create_simple_advertising_payload(name):
    """Cria um payload de advertising simples"""
    # Flags (0x01) + tipo (0x02 = General Discoverable)
    payload = bytes([2, 0x01, 0x02])
    
    # Nome completo (0x09)
    name_bytes = name.encode('utf-8')
    payload += bytes([len(name_bytes) + 1, 0x09]) + name_bytes
    
    return payload

def test_ble_advertising():
    """Testa advertising BLE básico"""
    led = Pin(2, Pin.OUT)
    led.value(0)
    
    try:
        print("Inicializando BLE...")
        ble = bluetooth.BLE()
        ble.active(True)
        time.sleep(1)
        
        print("BLE ativo, iniciando advertising...")
        
        # Cria payload simples
        payload = create_simple_advertising_payload("ESP32_Test")
        
        print(f"Payload: {payload}")
        print(f"Tamanho: {len(payload)} bytes")
        
        # Inicia advertising (100ms intervalo)
        ble.gap_advertise(100, payload)
        
        print("Advertising iniciado!")
        print("Dispositivo deve aparecer como 'ESP32_Test'")
        
        led.value(1)  # LED aceso = advertising ativo
        
        # Loop infinito com heartbeat
        count = 0
        while True:
            time.sleep(1)
            count += 1
            print(f"Advertising ativo - {count}s")
            
            # Pisca LED a cada 5 segundos
            if count % 5 == 0:
                led.value(0)
                time.sleep(0.1)
                led.value(1)
                
    except Exception as e:
        print(f"Erro: {e}")
        # Pisca LED rapidamente em caso de erro
        for _ in range(20):
            led.value(1)
            time.sleep(0.1)
            led.value(0)
            time.sleep(0.1)

if __name__ == "__main__":
    test_ble_advertising()
