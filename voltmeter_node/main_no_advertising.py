"""
Main para Voltmeter Node usando solução sem advertising
Contorna o erro -18 do BLE advertising no ESP32
"""

import sys
import time
import machine
import gc

# Adiciona paths necessários
sys.path.append('/common')
sys.path.append('/voltmeter_node')

# Imports do projeto
from constants import *
from adc_reader import ADCReader
from ble_client import BLEClient

# Import da solução no advertising
sys.path.append('/')
from ble_server_no_advertising import NoAdvertisingBLEServer

class NoAdvertisingVoltmeterServer(NoAdvertisingBLEServer):
    """Servidor BLE Voltmeter sem advertising"""
    
    def __init__(self, adc_reader):
        """Inicializa servidor voltmeter"""
        self.adc_reader = adc_reader
        super().__init__(adc_reader, "voltmeter")
        
        # Configurações específicas do voltmeter
        self.last_readings = [0.0, 0.0, 0.0]
        self.reading_interval = 1.0  # Intervalo de leitura em segundos
        self.last_reading_time = 0
    
    def get_mac_address(self):
        """Retorna MAC address do dispositivo"""
        try:
            import ubinascii
            import network
            wlan = network.WLAN(network.STA_IF)
            mac = ubinascii.hexlify(wlan.config('mac')).decode()
            formatted_mac = ':'.join([mac[i:i+2] for i in range(0, len(mac), 2)])
            return formatted_mac
        except:
            return "00:00:00:00:00:00"
    
    def read_voltages(self):
        """Lê as tensões dos ADCs"""
        try:
            v1 = self.adc_reader.read_voltage_1()
            v2 = self.adc_reader.read_voltage_2() 
            v3 = self.adc_reader.read_voltage_3()
            
            # Arredonda para 2 casas decimais
            self.last_readings = [round(v1, 2), round(v2, 2), round(v3, 2)]
            self.last_reading_time = time.ticks_ms()
            
            return self.last_readings
            
        except Exception as e:
            print(f"Erro na leitura ADC: {e}")
            return self.last_readings
    
    def update_ble_characteristics(self):
        """Atualiza características BLE com leituras atuais"""
        if not self.ble or not self.connections:
            return
        
        try:
            readings = self.read_voltages()
            
            # Atualiza cada característica
            if 'voltage1' in self.handles:
                self.ble.gatts_write(self.handles['voltage1'], f"{readings[0]:.2f}V".encode())
                
            if 'voltage2' in self.handles:
                self.ble.gatts_write(self.handles['voltage2'], f"{readings[1]:.2f}V".encode())
                
            if 'voltage3' in self.handles:
                self.ble.gatts_write(self.handles['voltage3'], f"{readings[2]:.2f}V".encode())
                
            if 'status' in self.handles:
                status = f"OK:{readings[0]:.2f},{readings[1]:.2f},{readings[2]:.2f}"
                self.ble.gatts_write(self.handles['status'], status.encode())
                
            # Notifica clientes conectados se suportado
            for conn_handle in self.connections:
                try:
                    if 'voltage1' in self.handles:
                        self.ble.gatts_notify(conn_handle, self.handles['voltage1'])
                    if 'voltage2' in self.handles:
                        self.ble.gatts_notify(conn_handle, self.handles['voltage2'])
                    if 'voltage3' in self.handles:
                        self.ble.gatts_notify(conn_handle, self.handles['voltage3'])
                except:
                    pass  # Ignore notify errors
                    
        except Exception as e:
            print(f"Erro ao atualizar BLE: {e}")
    
    def run_server(self):
        """Loop principal do servidor"""
        print("=== VOLTMETER NODE (No Advertising) ===")
        print(f"MAC Address: {self.get_mac_address()}")
        print("Aguardando conexões diretas via MAC address...")
        print("Use este MAC para conectar diretamente ao voltmeter")
        print("-" * 50)
        
        while True:
            try:
                # Lê tensões periodicamente
                current_time = time.ticks_ms()
                if time.ticks_diff(current_time, self.last_reading_time) >= (self.reading_interval * 1000):
                    readings = self.read_voltages()
                    print(f"V1:{readings[0]:.2f}V V2:{readings[1]:.2f}V V3:{readings[2]:.2f}V")
                    
                    # Atualiza BLE se houver conexões
                    if self.connections:
                        self.update_ble_characteristics()
                        print(f"Dados enviados para {len(self.connections)} cliente(s)")
                
                # Pequena pausa para não sobrecarregar
                time.sleep(0.1)
                
                # Limpeza de memória ocasional
                if time.ticks_ms() % 10000 < 100:  # A cada ~10 segundos
                    gc.collect()
                    
            except KeyboardInterrupt:
                print("\nParando servidor...")
                break
            except Exception as e:
                print(f"Erro no loop principal: {e}")
                time.sleep(1)

def test_adc_only():
    """Teste apenas do ADC sem BLE"""
    print("=== TESTE ADC APENAS ===")
    try:
        adc = ADCReader()
        
        for i in range(10):
            v1 = adc.read_voltage_1()
            v2 = adc.read_voltage_2()
            v3 = adc.read_voltage_3()
            print(f"Leitura {i+1}: V1={v1:.2f}V V2={v2:.2f}V V3={v3:.2f}V")
            time.sleep(1)
            
        print("Teste ADC concluído!")
        return True
        
    except Exception as e:
        print(f"Erro no teste ADC: {e}")
        return False

def main():
    """Função principal com seleção de modo"""
    print("=== VOLTMETER NODE STARTUP ===")
    
    # Modo de operação baseado em botão ou padrão
    try:
        # Tenta ler um pino para determinar modo (opcional)
        # Por padrão, sempre tenta BLE no-advertising
        mode = "ble_no_advertising"
        
        if mode == "adc_test":
            test_adc_only()
            return
            
        elif mode == "ble_no_advertising":
            print("Modo: BLE Servidor (Sem Advertising)")
            
            # Inicializa ADC
            try:
                adc_reader = ADCReader()
                print("ADC Reader inicializado")
            except Exception as e:
                print(f"Erro ao inicializar ADC: {e}")
                print("Executando teste ADC apenas...")
                test_adc_only()
                return
            
            # Inicializa servidor BLE sem advertising
            try:
                server = NoAdvertisingVoltmeterServer(adc_reader)
                print("Servidor BLE inicializado")
                
                # Roda servidor
                server.run_server()
                
            except Exception as e:
                print(f"Erro no servidor BLE: {e}")
                print("Fallback: executando teste ADC apenas...")
                test_adc_only()
        
    except Exception as e:
        print(f"Erro geral: {e}")
        print("Executando teste básico de ADC...")
        test_adc_only()

if __name__ == "__main__":
    main()
