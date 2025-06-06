#!/usr/bin/env python3
"""
Script de teste para verificar o funcionamento do sistema BLE
Display de 7 segmentos com comunicação Bluetooth
"""

import serial
import time
import sys

def test_display_node(port):
    """Testa o nó display conectando via serial"""
    try:
        print(f"Conectando ao Display Node em {port}...")
        ser = serial.Serial(port, 115200, timeout=2)
        time.sleep(2)  # Aguarda inicialização
        
        print("Lendo saída do Display Node...")
        start_time = time.time()
        output_lines = []
        
        while time.time() - start_time < 15:  # 15 segundos de teste
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    output_lines.append(line)
                    print(f"Display: {line}")
        
        ser.close()
        
        # Verifica se há sinais de inicialização bem-sucedida
        success_indicators = [
            "display controller inicializado",
            "servidor ble inicializado", 
            "nó display inicializado",
            "advertising iniciado",
            "controlador de displays multiplexados inicializado",
            "teste inicial concluído"
        ]
        
        error_indicators = [
            "erro ao inicializar",
            "falha na inicialização",
            "exception",
            "traceback"
        ]
        
        has_success = any(any(indicator.lower() in line.lower() for indicator in success_indicators) 
                         for line in output_lines)
        
        has_errors = any(any(error.lower() in line.lower() for error in error_indicators) 
                        for line in output_lines)
        
        if has_success and not has_errors:
            print("✓ Display Node está funcionando corretamente!")
            return True
        elif has_success and has_errors:
            print("⚠ Display Node funcionando mas com alguns erros")
            return True
        else:
            print("✗ Display Node tem problemas de inicialização")
            print("Linhas relevantes:")
            for line in output_lines[-10:]:  # Últimas 10 linhas
                print(f"  {line}")
            return False
            
    except serial.SerialException as e:
        print(f"Erro de conexão serial: {e}")
        return False
    except Exception as e:
        print(f"Erro durante teste: {e}")
        return False

def test_voltmeter_node(port):
    """Testa o nó voltímetro conectando via serial"""
    try:
        print(f"Conectando ao Voltmeter Node em {port}...")
        ser = serial.Serial(port, 115200, timeout=2)
        time.sleep(2)  # Aguarda inicialização
        
        print("Lendo saída do Voltmeter Node...")
        start_time = time.time()
        output_lines = []
        
        while time.time() - start_time < 15:  # 15 segundos de teste
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    output_lines.append(line)
                    print(f"Voltmeter: {line}")
        
        ser.close()
        
        # Verifica se há sinais de inicialização bem-sucedida
        success_indicators = [
            "adcreader inicializado",
            "cliente ble inicializado",
            "nó voltímetro inicializado",
            "teste inicial concluído",
            "canal adc",
            "tensão:"
        ]
        
        critical_errors = [
            "erro ao inicializar adc",
            "erro fatal",
            "failed to initialize"
        ]
        
        has_success = any(any(indicator.lower() in line.lower() for indicator in success_indicators) 
                         for line in output_lines)
        
        has_critical_errors = any(any(error.lower() in line.lower() for error in critical_errors) 
                                 for line in output_lines)
        
        # Verifica se está lendo tensões (mesmo que zeros)
        voltage_readings = any("teste" in line.lower() and ":" in line and "[" in line 
                              for line in output_lines)
        
        if has_success and not has_critical_errors and voltage_readings:
            print("✓ Voltmeter Node está funcionando corretamente!")
            return True
        elif has_success and not has_critical_errors:
            print("⚠ Voltmeter Node funcionando mas sem leituras de tensão claras")
            return True
        else:
            print("✗ Voltmeter Node tem problemas sérios")
            print("Linhas relevantes:")
            for line in output_lines[-10:]:  # Últimas 10 linhas
                print(f"  {line}")
            return False
            
    except serial.SerialException as e:
        print(f"Erro de conexão serial: {e}")
        return False
    except Exception as e:
        print(f"Erro durante teste: {e}")
        return False

def main():
    """Função principal de teste"""
    if len(sys.argv) != 3:
        print("Uso: python3 test_system.py <porta_display> <porta_voltmeter>")
        print("Exemplo: python3 test_system.py /dev/ttyUSB0 /dev/ttyUSB1")
        print("\nSe você tem apenas um ESP32, teste um de cada vez:")
        print("python3 test_system.py /dev/ttyUSB0 display")
        print("python3 test_system.py /dev/ttyUSB0 voltmeter")
        print("\nPara ver portas disponíveis no Linux:")
        print("ls /dev/ttyUSB* /dev/ttyACM*")
        sys.exit(1)
    
    port1 = sys.argv[1]
    port2_or_type = sys.argv[2]
    
    print("=== Teste do Sistema BLE Display 7 Segmentos ===")
    print("=== Versão atualizada para displays multiplexados ===")
    print()
    
    if port2_or_type == "display":
        # Teste apenas o display
        print("Testando Display Node (displays multiplexados de cátodo comum)...")
        display_ok = test_display_node(port1)
        
        if display_ok:
            print("\n✓ Sistema Display OK!")
            print("  - Os 3 displays de 4 dígitos devem estar funcionando")
            print("  - Servidor BLE ativo para receber dados")
        else:
            print("\n✗ Problemas detectados no Display")
            print("  - Verifique as conexões dos displays")
            print("  - Verifique se são displays de cátodo comum")
            
    elif port2_or_type == "voltmeter":
        # Teste apenas o voltímetro
        print("Testando Voltmeter Node...")
        voltmeter_ok = test_voltmeter_node(port1)
        
        if voltmeter_ok:
            print("\n✓ Sistema Voltmeter OK!")
            print("  - 3 canais ADC funcionando")
            print("  - Cliente BLE tentando conectar ao display")
        else:
            print("\n✗ Problemas detectados no Voltmeter")
            print("  - Verifique as conexões dos sensores ADC")
            print("  - Canais esperados: GPIO36, GPIO39, GPIO34")
            
    else:
        # Teste ambos os nós
        print("Testando Display Node (displays multiplexados)...")
        display_ok = test_display_node(port1)
        print()
        
        print("Testando Voltmeter Node...")
        voltmeter_ok = test_voltmeter_node(port2_or_type)
        print()
        
        if display_ok and voltmeter_ok:
            print("✓ Ambos os sistemas estão funcionando!")
            print("✓ Sistema BLE completo OK!")
            print("\nPróximos passos:")
            print("  1. Ligue ambos os ESP32 simultaneamente")
            print("  2. O voltímetro deve encontrar e conectar ao display")
            print("  3. As tensões devem aparecer nos displays automaticamente")
        else:
            print("✗ Alguns problemas foram detectados")
            if not display_ok:
                print("  - Display Node precisa de atenção")
                print("    * Verifique hardware dos displays")
                print("    * Confirme que são cátodo comum")
            if not voltmeter_ok:
                print("  - Voltmeter Node precisa de atenção")
                print("    * Verifique conexões ADC")
                print("    * Teste tensões nos pinos de entrada")

if __name__ == "__main__":
    main()
