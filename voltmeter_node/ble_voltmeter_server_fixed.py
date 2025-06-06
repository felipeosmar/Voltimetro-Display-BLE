"""
Servidor BLE corrigido para o nó voltímetro - resolve erro -18
Implementa múltiplas estratégias de inicialização BLE
"""

import bluetooth
import time
import gc
import sys
sys.path.append('/common')
from constants import *
from ble_utils import BLEUtils, print_debug, _IRQ_CENTRAL_CONNECT, _IRQ_CENTRAL_DISCONNECT, _IRQ_GATTS_WRITE

class FixedBLEVoltmeterServer:
    """Servidor BLE corrigido para o voltímetro - resolve erro -18"""
    
    def __init__(self, adc_reader):
        """Inicializa o servidor BLE para o nó voltímetro com correções para erro -18"""
        self.adc_reader = adc_reader
        self.connections = set()
        self.voltage_handle = None
        self.command_handle = None
        self.ble = None
        
        # Inicializa BLE com estratégias múltiplas
        if self._initialize_ble_robust():
            print_debug("Servidor BLE do Voltímetro inicializado com sucesso")
        else:
            raise Exception("Falha crítica na inicialização do BLE")
    
    def _initialize_ble_robust(self):
        """Inicialização robusta do BLE com múltiplas estratégias"""
        
        strategies = [
            ("Estratégia 1: Reset + Delay", self._init_strategy_reset_delay),
            ("Estratégia 2: Conservadora", self._init_strategy_conservative),
            ("Estratégia 3: GC Intensivo", self._init_strategy_gc_heavy),
            ("Estratégia 4: Retry Exponencial", self._init_strategy_exponential_retry),
            ("Estratégia 5: Simples", self._init_strategy_simple),
        ]
        
        for strategy_name, strategy_func in strategies:
            print_debug(f"Tentando: {strategy_name}")
            
            # Force cleanup antes de cada tentativa
            self._force_cleanup()
            
            try:
                if strategy_func():
                    print_debug(f"✓ Sucesso com: {strategy_name}")
                    return True
                else:
                    print_debug(f"✗ Falha em: {strategy_name}")
                    
            except Exception as e:
                print_debug(f"✗ Erro em {strategy_name}: {e}")
                if hasattr(e, 'errno') and e.errno == -18:
                    print_debug("   -> Erro -18 detectado, tentando próxima estratégia...")
                
                # Cleanup após erro
                self._force_cleanup()
                
            # Pausa entre tentativas
            time.sleep(1)
        
        print_debug("❌ Todas as estratégias falharam")
        return False
    
    def _force_cleanup(self):
        """Força limpeza completa de recursos BLE"""
        try:
            if self.ble:
                self.ble.active(False)
                self.ble = None
        except:
            pass
        
        # Force garbage collection múltiplas vezes
        for _ in range(3):
            gc.collect()
            time.sleep(0.1)
    
    def _init_strategy_reset_delay(self):
        """Estratégia 1: Reset completo + delay"""
        try:
            # Reset prévio
            try:
                temp_ble = bluetooth.BLE()
                temp_ble.active(False)
                time.sleep(0.8)
            except:
                pass
            
            # Garbage collection
            gc.collect()
            time.sleep(0.5)
            
            # Inicialização principal
            self.ble = bluetooth.BLE()
            time.sleep(0.3)
            self.ble.active(True)
            time.sleep(1.2)
            
            return self._complete_ble_setup()
            
        except Exception as e:
            print_debug(f"Estratégia reset_delay falhou: {e}")
            return False
    
    def _init_strategy_conservative(self):
        """Estratégia 2: Abordagem conservadora"""
        try:
            self.ble = bluetooth.BLE()
            
            # Verifica estado anterior
            try:
                if self.ble.active():
                    print_debug("BLE já estava ativo, reiniciando...")
                    self.ble.active(False)
                    time.sleep(0.8)
            except:
                pass
            
            # Ativa com verificação
            self.ble.active(True)
            time.sleep(1.0)
            
            # Verifica se ativação foi bem-sucedida
            if not self.ble.active():
                print_debug("Falha na verificação de ativação")
                return False
            
            return self._complete_ble_setup()
            
        except Exception as e:
            print_debug(f"Estratégia conservadora falhou: {e}")
            return False
    
    def _init_strategy_gc_heavy(self):
        """Estratégia 3: Garbage collection intensivo"""
        try:
            # Limpeza intensiva de memória
            for i in range(4):
                gc.collect()
                time.sleep(0.1)
            
            self.ble = bluetooth.BLE()
            gc.collect()
            time.sleep(0.4)
            
            self.ble.active(True)
            gc.collect()
            time.sleep(0.8)
            
            return self._complete_ble_setup()
            
        except Exception as e:
            print_debug(f"Estratégia GC intensivo falhou: {e}")
            return False
    
    def _init_strategy_exponential_retry(self):
        """Estratégia 4: Retry com backoff exponencial"""
        max_retries = 4
        base_delay = 0.2
        
        for attempt in range(max_retries):
            try:
                print_debug(f"Retry {attempt + 1}/{max_retries}")
                
                self.ble = bluetooth.BLE()
                
                # Delay exponencial
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
                
                self.ble.active(True)
                time.sleep(delay * 1.5)
                
                # Verifica se ativou corretamente
                if self.ble.active():
                    return self._complete_ble_setup()
                else:
                    print_debug(f"BLE não ativou na tentativa {attempt + 1}")
                    
            except Exception as e:
                print_debug(f"Retry {attempt + 1} falhou: {e}")
                if attempt == max_retries - 1:
                    return False
                time.sleep(0.15)
        
        return False
    
    def _init_strategy_simple(self):
        """Estratégia 5: Inicialização simples (fallback)"""
        try:
            self.ble = bluetooth.BLE()
            self.ble.active(True)
            time.sleep(0.6)
            
            return self._complete_ble_setup()
            
        except Exception as e:
            print_debug(f"Estratégia simples falhou: {e}")
            return False
    
    def _complete_ble_setup(self):
        """Completa a configuração BLE após inicialização bem-sucedida"""
        try:
            # Verifica se BLE está realmente ativo
            if not self.ble or not self.ble.active():
                print_debug("BLE não está ativo após inicialização")
                return False
            
            # Configura handler de eventos
            self.ble.irq(self._irq_handler)
            
            # Configura os serviços e características
            self._setup_services()
            
            # Inicia o advertising
            self._start_advertising()
            
            print_debug("Configuração BLE completa")
            return True
            
        except Exception as e:
            print_debug(f"Erro na configuração BLE: {e}")
            return False
    
    def _setup_services(self):
        """Configura os serviços e características BLE"""
        try:
            # Serviço do Voltímetro
            VOLTMETER_SERVICE = (
                VOLTMETER_SERVICE_UUID,
                (
                    # Característica para ler dados de tensão
                    (VOLTAGE_CHAR_UUID, bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY),
                    # Característica para receber comandos
                    (COMMAND_CHAR_UUID, bluetooth.FLAG_WRITE | bluetooth.FLAG_READ),
                ),
            )
            
            # Registra os serviços
            ((self.voltage_handle, self.command_handle),) = self.ble.gatts_register_services((VOLTMETER_SERVICE,))
            
            print_debug("Serviços BLE do Voltímetro registrados")
            
        except Exception as e:
            print_debug(f"Erro ao registrar serviços: {e}")
            raise e
    
    def _start_advertising(self):
        """Inicia o advertising BLE"""
        try:
            payload = BLEUtils.advertising_payload(
                name=BLE_NAME_VOLTMETER,
                services=[VOLTMETER_SERVICE_UUID]
            )
            
            self.ble.gap_advertise(100, payload)
            print_debug(f"Advertising iniciado como '{BLE_NAME_VOLTMETER}'")
            
        except Exception as e:
            print_debug(f"Erro ao iniciar advertising: {e}")
            raise e
    
    def _irq_handler(self, event, data):
        """Manipula eventos BLE"""
        try:
            if event == _IRQ_CENTRAL_CONNECT:
                conn_handle, addr_type, addr = data
                self.connections.add(conn_handle)
                print_debug(f"Cliente conectado ao Voltímetro: {conn_handle}")
                
                # Continua advertising para mais conexões se há espaço
                if len(self.connections) < MAX_CONNECTIONS:
                    self._start_advertising()
            
            elif event == _IRQ_CENTRAL_DISCONNECT:
                conn_handle, addr_type, addr = data
                self.connections.discard(conn_handle)
                print_debug(f"Cliente desconectado do Voltímetro: {conn_handle}")
                
                # Reinicia advertising se há espaço
                if len(self.connections) < MAX_CONNECTIONS:
                    self._start_advertising()
            
            elif event == _IRQ_GATTS_WRITE:
                conn_handle, value_handle = data
                value = self.ble.gatts_read(value_handle)
                
                if value_handle == self.command_handle:
                    self._handle_command_data(value)
                    
        except Exception as e:
            print_debug(f"Erro no handler de eventos BLE: {e}")
    
    def _handle_command_data(self, data):
        """Processa comandos recebidos"""
        try:
            command = data.decode('utf-8')
            print_debug(f"Comando recebido no Voltímetro: {command}")
            
            if command == "GET_VOLTAGES":
                self._send_current_voltages()
            elif command == "START_MONITORING":
                print_debug("Monitoramento iniciado")
            elif command == "STOP_MONITORING":
                print_debug("Monitoramento parado")
            elif command == "STATUS":
                self._send_status()
                
        except Exception as e:
            print_debug(f"Erro ao processar comando: {e}")
    
    def send_voltage_data(self, v1, v2, v3):
        """Envia dados de tensão para clientes conectados"""
        try:
            if self.connections and self.voltage_handle:
                # Formato: "V1:12.34,V2:5.67,V3:9.10"
                voltage_str = f"V1:{v1:.2f},V2:{v2:.2f},V3:{v3:.2f}"
                
                # Envia para todas as conexões
                for conn_handle in self.connections.copy():
                    try:
                        self.ble.gatts_notify(conn_handle, self.voltage_handle, voltage_str.encode())
                    except Exception as e:
                        print_debug(f"Erro ao enviar para {conn_handle}: {e}")
                        # Remove conexão problemática
                        self.connections.discard(conn_handle)
                
                print_debug(f"Dados enviados: {voltage_str}")
                
        except Exception as e:
            print_debug(f"Erro ao enviar dados de tensão: {e}")
    
    def _send_current_voltages(self):
        """Envia tensões atuais"""
        try:
            if self.adc_reader:
                v1, v2, v3 = self.adc_reader.read_all_voltages()
                self.send_voltage_data(v1, v2, v3)
        except Exception as e:
            print_debug(f"Erro ao enviar tensões atuais: {e}")
    
    def _send_status(self):
        """Envia status atual do voltímetro"""
        try:
            if self.connections and self.voltage_handle:
                status = "VOLTMETER_OK"
                for conn_handle in self.connections:
                    try:
                        self.ble.gatts_notify(conn_handle, self.voltage_handle, status.encode())
                    except:
                        pass
                print_debug("Status do voltímetro enviado")
        except Exception as e:
            print_debug(f"Erro ao enviar status: {e}")
    
    def stop(self):
        """Para o servidor BLE"""
        try:
            if self.ble:
                self.ble.active(False)
                print_debug("Servidor BLE do Voltímetro parado")
        except Exception as e:
            print_debug(f"Erro ao parar servidor BLE: {e}")
        finally:
            self._force_cleanup()
