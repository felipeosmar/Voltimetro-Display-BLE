#!/usr/bin/env python3
"""
Script de teste rápido para verificar se o ESP32 está respondendo 
e se as correções BLE estão funcionando
"""

import serial
import time
import sys

def test_esp32_connection(port='/dev/ttyUSB0', timeout=10):
    """Testa conexão básica com ESP32"""
    print(f"=== TESTE DE CONEXÃO COM ESP32 ({port}) ===")
    
    try:
        # Conecta com o ESP32
        ser = serial.Serial(port, 115200, timeout=2)
        time.sleep(1)
        
        print("✓ Conexão serial estabelecida")
        
        # Envia um comando simples
        ser.write(b'\r\n')
        time.sleep(0.5)
        
        # Lê resposta
        response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        if '>>>' in response or 'MicroPython' in response:
            print("✓ ESP32 executando MicroPython")
            return ser
        else:
            print("⚠️  ESP32 conectado mas resposta incomum")
            print(f"Resposta: {repr(response)}")
            return ser
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return None

def test_file_exists(ser, filename):
    """Testa se um arquivo existe no ESP32"""
    try:
        command = f"import os; print('{filename}:', '{filename}' in os.listdir('/'))\r\n"
        ser.write(command.encode())
        time.sleep(1)
        
        response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        if 'True' in response:
            print(f"✓ {filename} encontrado")
            return True
        else:
            print(f"❌ {filename} não encontrado")
            return False
            
    except Exception as e:
        print(f"⚠️  Erro ao verificar {filename}: {e}")
        return False

def quick_ble_test(ser):
    """Teste rápido de inicialização BLE"""
    print("\n=== TESTE RÁPIDO DO BLE ===")
    
    try:
        # Testa import do bluetooth
        ser.write(b"import bluetooth; print('BLE module OK')\r\n")
        time.sleep(2)
        
        response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        if 'BLE module OK' in response:
            print("✓ Módulo bluetooth importado com sucesso")
        elif 'ImportError' in response:
            print("❌ Módulo bluetooth não disponível")
            return False
        
        # Testa inicialização básica do BLE
        ser.write(b"ble = bluetooth.BLE(); ble.active(True); print('BLE activated')\r\n")
        time.sleep(3)
        
        response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        if 'BLE activated' in response:
            print("✓ BLE ativado com sucesso")
            return True
        elif 'errno -18' in response or 'ESP_ERR_NOT_SUPPORTED' in response:
            print("❌ Erro -18 detectado! Necessário usar versões corrigidas")
            return False
        else:
            print(f"⚠️  Resposta inesperada: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste BLE: {e}")
        return False

def test_fixed_files(ser):
    """Testa se os arquivos corrigidos estão presentes"""
    print("\n=== VERIFICAÇÃO DOS ARQUIVOS CORRIGIDOS ===")
    
    files_to_check = [
        'main_fixed.py',
        'ble_server_fixed.py',
        'fix_ble_error18.py',
        'test_ble_error18_fix.py'
    ]
    
    all_present = True
    for filename in files_to_check:
        if not test_file_exists(ser, filename):
            all_present = False
    
    return all_present

def main():
    """Função principal de teste"""
    print("=== TESTE RÁPIDO DE VERIFICAÇÃO DO ESP32 ===")
    print(f"Data: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Testa ambas as portas se disponível
    ports_to_test = ['/dev/ttyUSB0', '/dev/ttyUSB1']
    
    for port in ports_to_test:
        print(f"\n{'='*50}")
        print(f"TESTANDO {port}")
        print('='*50)
        
        # Testa conexão
        ser = test_esp32_connection(port)
        if not ser:
            continue
        
        try:
            # Verifica arquivos corrigidos
            files_ok = test_fixed_files(ser)
            
            # Teste básico do BLE
            ble_ok = quick_ble_test(ser)
            
            # Resumo para esta porta
            print(f"\n--- RESUMO {port} ---")
            if files_ok and ble_ok:
                print("🎉 Dispositivo pronto com correções BLE!")
            elif files_ok and not ble_ok:
                print("⚠️  Arquivos presentes, mas BLE com problemas")
                print("   Execute: exec(open('fix_ble_error18.py').read())")
            elif not files_ok:
                print("❌ Arquivos corrigidos faltando - refaça o deploy")
            else:
                print("⚠️  Status indeterminado")
        
        finally:
            ser.close()
    
    print(f"\n{'='*50}")
    print("TESTE CONCLUÍDO")
    print('='*50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTeste interrompido pelo usuário")
    except Exception as e:
        print(f"\nErro durante teste: {e}")
