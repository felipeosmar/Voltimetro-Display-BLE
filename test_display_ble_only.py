# filepath: test_display_ble_only.py
"""
Teste mínimo de BLE para ESP32 Display
Execute este arquivo no ESP32 Display para testar apenas o advertising BLE
"""

import bluetooth
import time
from machine import Pin

def create_advertising_payload(name, service_uuid):
    """Cria payload de advertising com nome e serviço"""
    # Flags (0x01) + tipo (0x02 = General Discoverable)
    payload = bytes([2, 0x01, 0x02])
    
    # Nome completo (0x09)
    name_bytes = name.encode('utf-8')
    payload += bytes([len(name_bytes) + 1, 0x09]) + name_bytes
    
    # UUID do serviço (0x03 = Complete List of 16-bit Service UUIDs)
    # Para UUIDs de 128 bits usamos 0x07
    uuid_bytes = service_uuid.to_bytes()
    payload += bytes([len(uuid_bytes) + 1, 0x07]) + uuid_bytes
    
    return payload

def test_display_ble():
    """Testa advertising BLE do Display"""
    led = Pin(2, Pin.OUT)
    led.value(0)
    
    try:
        print("=== TESTE BLE DISPLAY ===")
        print("Inicializando BLE...")
        
        ble = bluetooth.BLE()
        ble.active(True)
        time.sleep(1)
        
        print("BLE ativo!")
        
        # UUID do serviço display
        display_service_uuid = bluetooth.UUID('12345678-1234-1234-1234-123456789abc')
        
        # Cria payload
        payload = create_advertising_payload("ESP32_Display", display_service_uuid)
        
        print(f"Payload criado: {len(payload)} bytes")
        print(f"Conteúdo: {payload}")
        
        # Inicia advertising
        print("Iniciando advertising...")
        ble.gap_advertise(100, payload)  # 100ms intervalo
        
        print("✅ ADVERTISING ATIVO!")
        print("Nome: ESP32_Display")
        print("Serviço: Display Service")
        print("Procure este dispositivo no scan BLE")
        
        led.value(1)  # LED aceso = sucesso
        
        # Loop com heartbeat
        count = 0
        while True:
            time.sleep(1)
            count += 1
            print(f"Advertising: {count}s")
            
            # Pisca LED a cada 5 segundos
            if count % 5 == 0:
                led.value(0)
                time.sleep(0.2)
                led.value(1)
                print("💓 Heartbeat")
                
    except Exception as e:
        print(f"❌ ERRO: {e}")
        # Pisca LED rapidamente em caso de erro
        for _ in range(30):
            led.value(1)
            time.sleep(0.1)
            led.value(0)
            time.sleep(0.1)

if __name__ == "__main__":
    test_display_ble()
