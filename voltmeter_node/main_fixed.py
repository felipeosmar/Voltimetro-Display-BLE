"""
Ponto de entrada principal do nó voltímetro com correções para erro BLE -18
Utiliza o servidor BLE corrigido que implementa múltiplas estratégias
"""

import time
import sys
import gc
sys.path.append('/common')

from constants import *
from adc_reader import ADCReader
from ble_voltmeter_server_fixed import FixedBLEVoltmeterServer

def main():
    """Função principal do nó voltímetro com tratamento robusto de erros"""
    print("=== INICIALIZANDO NÓ VOLTÍMETRO (VERSÃO CORRIGIDA) ===")
    
    adc_reader = None
    ble_server = None
    
    try:
        # Força limpeza inicial de memória
        gc.collect()
        
        # Inicializa leitor ADC
        print("Inicializando leitor ADC...")
        adc_reader = ADCReader()
        print("✓ Leitor ADC inicializado")
        
        # Teste inicial do ADC
        print("Testando leitura ADC...")
        v1, v2, v3 = adc_reader.read_all_voltages()
        print(f"✓ Leituras iniciais: V1={v1:.2f}V, V2={v2:.2f}V, V3={v3:.2f}V")
        
        # Inicializa servidor BLE corrigido
        print("Inicializando servidor BLE corrigido...")
        ble_server = FixedBLEVoltmeterServer(adc_reader)
        print("✓ Servidor BLE inicializado com sucesso")
        
        print("✓ Nó Voltímetro pronto para conexões")
        
        # Loop principal
        loop_count = 0
        last_reading_time = 0
        last_status_time = 0
        reading_interval = 0.5  # Leituras a cada 500ms
        status_interval = 30    # Status a cada 30 segundos
        
        while True:
            try:
                current_time = time.time()
                
                # Leitura periódica dos ADCs
                if current_time - last_reading_time >= reading_interval:
                    try:
                        # Lê tensões
                        v1, v2, v3 = adc_reader.read_all_voltages()
                        
                        # Envia via BLE se há conexões
                        if ble_server and ble_server.connections:
                            ble_server.send_voltage_data(v1, v2, v3)
                        
                        last_reading_time = current_time
                        
                    except Exception as e:
                        print(f"⚠️  Erro na leitura ADC: {e}")
                
                # Status periódico
                if current_time - last_status_time > status_interval:
                    num_connections = len(ble_server.connections) if ble_server else 0
                    print(f"Status: {num_connections} conexões, últimas leituras: V1={v1:.2f}V, V2={v2:.2f}V, V3={v3:.2f}V")
                    last_status_time = current_time
                
                # Garbage collection periódico
                loop_count += 1
                if loop_count % 2000 == 0:
                    gc.collect()
                    loop_count = 0
                
                # Delay pequeno
                time.sleep(0.01)
                
            except KeyboardInterrupt:
                print("\n⚠️  Interrupção pelo usuário")
                break
                
            except Exception as e:
                print(f"⚠️  Erro no loop principal: {e}")
                time.sleep(1)  # Pausa antes de continuar
                
    except Exception as e:
        print(f"❌ Erro crítico na inicialização: {e}")
        return False
        
    finally:
        # Limpeza final
        print("\n=== FINALIZANDO NÓ VOLTÍMETRO ===")
        
        if ble_server:
            try:
                ble_server.stop()
                print("✓ Servidor BLE parado")
            except Exception as e:
                print(f"⚠️  Erro ao parar BLE: {e}")
        
        # Limpeza final de memória
        gc.collect()
        print("✓ Recursos liberados")
    
    return True

def test_mode():
    """Modo de teste do ADC sem BLE"""
    print("=== MODO DE TESTE DO VOLTÍMETRO ===")
    
    try:
        # Inicializa apenas o ADC
        adc_reader = ADCReader()
        
        # Realiza múltiplas leituras de teste
        print("Realizando leituras de teste...")
        
        for i in range(10):
            v1, v2, v3 = adc_reader.read_all_voltages()
            print(f"Leitura {i+1:2d}: V1={v1:6.3f}V, V2={v2:6.3f}V, V3={v3:6.3f}V")
            time.sleep(1)
        
        print("✓ Teste concluído")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def calibration_mode():
    """Modo de calibração do ADC"""
    print("=== MODO DE CALIBRAÇÃO DO VOLTÍMETRO ===")
    
    try:
        adc_reader = ADCReader()
        
        print("Conecte tensões conhecidas nos canais e pressione Enter para cada leitura...")
        
        for channel in range(3):
            input(f"Pressione Enter para calibrar canal {channel + 1}...")
            
            # Múltiplas leituras para média
            readings = []
            for _ in range(10):
                if channel == 0:
                    voltage = adc_reader.read_voltage_1()
                elif channel == 1:
                    voltage = adc_reader.read_voltage_2()
                else:
                    voltage = adc_reader.read_voltage_3()
                readings.append(voltage)
                time.sleep(0.1)
            
            avg_voltage = sum(readings) / len(readings)
            print(f"Canal {channel + 1}: Média = {avg_voltage:.4f}V")
        
        print("✓ Calibração concluída")
        return True
        
    except Exception as e:
        print(f"❌ Erro na calibração: {e}")
        return False

if __name__ == "__main__":
    # Verifica modo de execução
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            success = test_mode()
        elif sys.argv[1] == "calibrate":
            success = calibration_mode()
        else:
            print("Modos disponíveis: test, calibrate")
            success = False
    else:
        success = main()
    
    if success:
        print("✅ Execução concluída com sucesso")
    else:
        print("❌ Execução falhou")
