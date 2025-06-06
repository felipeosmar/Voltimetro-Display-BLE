#!/usr/bin/env python3
"""
Script simples para verificar comunicação com ESP32
"""

import serial
import time
import sys

def test_esp32_basic(port):
    """Teste básico de comunicação com ESP32"""
    try:
        print(f"Conectando a {port}...")
        ser = serial.Serial(port, 115200, timeout=2)
        
        print("Enviando Ctrl+C para interromper execução...")
        ser.write(b'\x03')
        time.sleep(1)
        
        print("Enviando Ctrl+D para soft reset...")
        ser.write(b'\x04')
        time.sleep(2)
        
        print("Lendo saída por 10 segundos...")
        start_time = time.time()
        got_output = False
        
        while time.time() - start_time < 10:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                try:
                    text = data.decode('utf-8', errors='replace')
                    if text.strip():
                        print("SAÍDA:", repr(text))
                        got_output = True
                except:
                    print("DADOS BINÁRIOS:", data)
                    got_output = True
            time.sleep(0.1)
        
        # Tenta enviar alguns comandos Python
        print("\nTestando comandos Python...")
        commands = [
            b"print('Hello ESP32')\r\n",
            b"import sys\r\n",
            b"print(sys.implementation)\r\n",
            b"print('MicroPython version:', sys.version)\r\n"
        ]
        
        for cmd in commands:
            ser.write(cmd)
            time.sleep(1)
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting)
                try:
                    print("RESP:", response.decode('utf-8', errors='replace').strip())
                    got_output = True
                except:
                    print("RESP BINÁRIA:", response)
                    got_output = True
        
        ser.close()
        
        if got_output:
            print("\n✓ ESP32 está respondendo!")
            return True
        else:
            print("\n✗ ESP32 não está respondendo")
            return False
            
    except Exception as e:
        print(f"Erro: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 simple_test.py <porta>")
        print("Exemplo: python3 simple_test.py /dev/ttyUSB0")
        sys.exit(1)
    
    port = sys.argv[1]
    test_esp32_basic(port)
