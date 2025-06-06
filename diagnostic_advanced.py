#!/usr/bin/env python3
"""
Script de diagnóstico avançado para o sistema BLE
"""

import serial
import time
import sys

def diagnose_esp32(port):
    """Diagnóstico completo do ESP32"""
    print(f"=== Diagnóstico ESP32 em {port} ===")
    
    try:
        # Teste de conexão básica
        print("1. Testando conexão serial...")
        ser = serial.Serial(port, 115200, timeout=1)
        print("✓ Conexão serial estabelecida")
        
        # Enviar Ctrl+C para interromper execução atual
        print("2. Enviando interrupção (Ctrl+C)...")
        ser.write(b'\x03')
        time.sleep(0.5)
        
        # Limpar buffer
        ser.flushInput()
        
        # Enviar comando para reiniciar
        print("3. Reiniciando ESP32...")
        ser.write(b'\x04')  # Ctrl+D (soft reset)
        time.sleep(2)
        
        # Ler saída por 15 segundos
        print("4. Lendo saída do ESP32...")
        start_time = time.time()
        all_output = []
        
        while time.time() - start_time < 15:
            if ser.in_waiting:
                try:
                    line = ser.readline().decode('utf-8', errors='replace').strip()
                    if line:
                        all_output.append(line)
                        print(f"ESP32: {line}")
                except UnicodeDecodeError:
                    continue
            time.sleep(0.1)
        
        ser.close()
        
        # Análise da saída
        print("\n=== Análise do Output ===")
        if not all_output:
            print("✗ Nenhuma saída detectada do ESP32")
            print("  Possíveis causas:")
            print("  - ESP32 não está conectado")
            print("  - Código não foi carregado corretamente")
            print("  - ESP32 em estado de erro")
            return False
        
        # Verifica por erros comuns
        errors = []
        warnings = []
        success = []
        
        for line in all_output:
            line_lower = line.lower()
            if any(err in line_lower for err in ['error', 'traceback', 'exception', 'importerror']):
                errors.append(line)
            elif any(warn in line_lower for warn in ['warning', 'failed', 'timeout']):
                warnings.append(line)
            elif any(ok in line_lower for ok in ['iniciado', 'ativo', 'configurado', 'ready']):
                success.append(line)
        
        if errors:
            print("✗ Erros detectados:")
            for error in errors:
                print(f"  {error}")
        
        if warnings:
            print("⚠ Avisos detectados:")
            for warning in warnings:
                print(f"  {warning}")
        
        if success:
            print("✓ Sucessos detectados:")
            for succ in success:
                print(f"  {succ}")
        
        # Status final
        if errors:
            print("\n🔴 Status: ERRO - ESP32 com problemas críticos")
            return False
        elif not success and warnings:
            print("\n🟡 Status: ATENÇÃO - ESP32 com avisos")
            return False
        elif success:
            print("\n🟢 Status: OK - ESP32 funcionando")
            return True
        else:
            print("\n🟡 Status: INDEFINIDO - Saída insuficiente para análise")
            return False
            
    except serial.SerialException as e:
        print(f"✗ Erro de conexão serial: {e}")
        print("  Verifique se:")
        print("  - O ESP32 está conectado")
        print("  - A porta está correta")
        print("  - Você tem permissões na porta serial")
        return False
    except Exception as e:
        print(f"✗ Erro durante diagnóstico: {e}")
        return False

def check_serial_permissions(port):
    """Verifica permissões da porta serial"""
    print(f"=== Verificando permissões de {port} ===")
    
    import os
    import stat
    
    try:
        # Verifica se o arquivo existe
        if not os.path.exists(port):
            print(f"✗ Porta {port} não existe")
            return False
        
        # Verifica permissões
        st = os.stat(port)
        mode = st.st_mode
        
        # Verifica se é legível e gravável pelo usuário
        readable = bool(mode & stat.S_IRUSR)
        writable = bool(mode & stat.S_IWUSR)
        
        print(f"Permissões: readable={readable}, writable={writable}")
        
        if readable and writable:
            print("✓ Permissões OK")
            return True
        else:
            print("✗ Permissões insuficientes")
            print("Execute: sudo chmod 666 " + port)
            return False
            
    except Exception as e:
        print(f"Erro verificando permissões: {e}")
        return False

def main():
    """Função principal de diagnóstico"""
    if len(sys.argv) != 2:
        print("Uso: python3 diagnostic_advanced.py <porta_serial>")
        print("Exemplo: python3 diagnostic_advanced.py /dev/ttyUSB0")
        sys.exit(1)
    
    port = sys.argv[1]
    
    print("=== Diagnóstico Avançado ESP32 BLE ===")
    print()
    
    # Verifica permissões primeiro
    perm_ok = check_serial_permissions(port)
    print()
    
    if not perm_ok:
        print("Resolva os problemas de permissão antes de continuar")
        return
    
    # Executa diagnóstico
    result = diagnose_esp32(port)
    
    print("\n=== Resumo ===")
    if result:
        print("✓ ESP32 está funcionando corretamente")
        print("  Você pode proceder com os testes de funcionalidade")
    else:
        print("✗ ESP32 apresenta problemas")
        print("  Verifique:")
        print("  - Se o firmware MicroPython está instalado")
        print("  - Se o código foi carregado corretamente")
        print("  - Se há erros na execução do código")

if __name__ == "__main__":
    main()
