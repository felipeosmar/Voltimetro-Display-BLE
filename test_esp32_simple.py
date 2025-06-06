#!/usr/bin/env python3
"""
Teste simples para ESP32 - carrega um código básico de teste
"""

import serial
import time
import sys

def test_basic_functionality(device, name):
    """Testa funcionalidade básica do ESP32"""
    try:
        print(f"=== Testando {name} ({device}) ===")
        ser = serial.Serial(device, 115200, timeout=3)
        time.sleep(1)
        
        # Para execução atual
        ser.write(b'\x03')
        time.sleep(0.5)
        
        # Comando simples
        ser.write(b'print("ESP32 funcionando")\r\n')
        time.sleep(1)
        
        response = ser.read_all().decode('utf-8', errors='ignore')
        print(f"Resposta: {response}")
        
        # Teste de Bluetooth
        ser.write(b'import bluetooth\r\n')
        time.sleep(1)
        
        response = ser.read_all().decode('utf-8', errors='ignore')
        if "Traceback" in response:
            print("❌ Bluetooth não disponível")
        else:
            print("✅ Bluetooth disponível")
        
        # Testa inicialização BLE básica
        test_ble_code = '''
try:
    import bluetooth
    ble = bluetooth.BLE()
    ble.active(True)
    print("BLE ativado com sucesso")
except Exception as e:
    print(f"Erro BLE: {e}")
'''
        
        for line in test_ble_code.strip().split('\n'):
            ser.write(f'{line}\r\n'.encode())
            time.sleep(0.2)
        
        time.sleep(2)
        response = ser.read_all().decode('utf-8', errors='ignore')
        print(f"Teste BLE: {response}")
        
        ser.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro testando {name}: {e}")
        return False

def load_simple_test_code(device, name):
    """Carrega código de teste simples no ESP32"""
    simple_code = '''
# Código de teste simples
import time
import bluetooth

print("=== Teste ESP32 ===")
print(f"Nó: {name}")

# Testa BLE
try:
    ble = bluetooth.BLE()
    ble.active(True)
    print("✅ BLE ativado")
    
    # Teste de advertising simples
    import ubinascii
    mac = ubinascii.hexlify(ble.config('mac')[1], ':').decode().upper()
    print(f"MAC: {mac}")
    
    # Nome do dispositivo
    device_name = "ESP32_Test_" + name
    
    # Advertising básico
    adv_data = bytearray([
        0x02, 0x01, 0x06,  # Flags
        len(device_name) + 1, 0x09  # Nome completo
    ]) + device_name.encode()
    
    ble.gap_advertise(100, adv_data)
    print(f"✅ Advertising como: {device_name}")
    
except Exception as e:
    print(f"❌ Erro BLE: {e}")

print("✅ Teste concluído - ESP32 funcionando")

# Loop simples
counter = 0
while True:
    counter += 1
    print(f"Heartbeat {counter}")
    time.sleep(5)
    
    if counter > 10:
        print("Reiniciando contador...")
        counter = 0
'''.replace('{name}', name)
    
    try:
        print(f"Carregando código de teste em {name}...")
        ser = serial.Serial(device, 115200, timeout=3)
        time.sleep(1)
        
        # Para execução atual
        ser.write(b'\x03')
        time.sleep(0.5)
        
        # Remove main.py existente
        ser.write(b'try:\r\n')
        ser.write(b'    import os\r\n')
        ser.write(b'    os.remove("main.py")\r\n')
        ser.write(b'    print("main.py removido")\r\n')
        ser.write(b'except:\r\n')
        ser.write(b'    print("main.py nao existia")\r\n')
        ser.write(b'\r\n')
        time.sleep(2)
        
        # Cria novo main.py
        ser.write(b'with open("main.py", "w") as f:\r\n')
        for line in simple_code.split('\n'):
            escaped_line = line.replace('"', '\\"').replace("'", "\\'")
            ser.write(f'    f.write("{escaped_line}\\n")\r\n'.encode())
            time.sleep(0.1)
        ser.write(b'\r\n')
        time.sleep(2)
        
        # Soft reset para executar
        ser.write(b'\x04')
        time.sleep(3)
        
        # Lê resposta
        response = ser.read_all().decode('utf-8', errors='ignore')
        print(f"Resposta: {response[-500:]}")  # Últimas 500 chars
        
        ser.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro carregando código em {name}: {e}")
        return False

if __name__ == "__main__":
    devices = [
        ('/dev/ttyUSB0', 'Display'),
        ('/dev/ttyUSB1', 'Voltmeter')
    ]
    
    print("=== Teste Simples ESP32 ===\n")
    
    # Primeiro testa funcionalidade básica
    for device, name in devices:
        if test_basic_functionality(device, name):
            print(f"✅ {name} funcionando\n")
        else:
            print(f"❌ {name} com problemas\n")
    
    # Pergunta se quer carregar código de teste
    response = input("Carregar código de teste simples? (y/N): ").strip().lower()
    if response in ['y', 'yes', 's', 'sim']:
        for device, name in devices:
            load_simple_test_code(device, name)
            time.sleep(2)
