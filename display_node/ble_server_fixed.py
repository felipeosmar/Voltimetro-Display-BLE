"""
Servidor BLE corrigido para o nó display - resolve erro -18
Implementa múltiplas estratégias de inicialização BLE
"""

import bluetooth
import time
import gc
import sys
sys.path.append('/common')
from constants import *
from ble_utils import BLEUtils, print_debug, _IRQ_CENTRAL_CONNECT, _IRQ_CENTRAL_DISCONNECT, _IRQ_GATTS_WRITE

class FixedBLEDisplayServer:
    def __init__(self, display_controller):
        """Inicializa o servidor BLE para o nó display com correções para erro -18"""
        self.display_controller = display_controller
        self.connections = set()
        self.voltage_handle = None
        self.command_handle = None
        self.display_handle = None
        self.ble = None
        
        # Inicializa BLE com estratégias múltiplas
        if self._initialize_ble_robust():
            print_debug("Servidor BLE do Display inicializado com sucesso")
        else:
            raise Exception("Falha crítica na inicialização do BLE")
    
    def _initialize_ble_robust(self):
        """Inicialização robusta do BLE com múltiplas estratégias"""
        
        strategies = [
            ("Estratégia 1: Reset + Delay Longo", self._init_strategy_reset_delay),
            ("Estratégia 2: Retry Exponencial", self._init_strategy_exponential_retry),
            ("Estratégia 3: Conservadora", self._init_strategy_conservative),
            ("Estratégia 4: Com Garbage Collection", self._init_strategy_gc_heavy),
            ("Estratégia 5: Padrão Simples", self._init_strategy_simple),
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
        """Estratégia 1: Reset completo + delay longo"""
        try:
            # Reset prévio
            try:
                temp_ble = bluetooth.BLE()
                temp_ble.active(False)
                time.sleep(1)
            except:
                pass
            
            # Aguarda tempo extra
            time.sleep(1)
            
            # Inicialização principal
            self.ble = bluetooth.BLE()
            time.sleep(0.5)  # Delay antes de ativar
            self.ble.active(True)
            time.sleep(2)     # Delay longo após ativar
            
            return self._complete_ble_setup()
            
        except Exception as e:
            print_debug(f"Estratégia reset_delay falhou: {e}")
            return False
    
    def _init_strategy_exponential_retry(self):
        """Estratégia 2: Retry com backoff exponencial"""
        max_retries = 5
        base_delay = 0.3
        
        for attempt in range(max_retries):
            try:
                print_debug(f"Tentativa {attempt + 1}/{max_retries}")
                
                self.ble = bluetooth.BLE()
                
                # Delay exponencial
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
                
                self.ble.active(True)
                
                # Delay após ativação
                time.sleep(delay)
                
                # Verifica se ativou corretamente
                if self.ble.active():
                    return self._complete_ble_setup()
                else:
                    print_debug(f"BLE não ativou na tentativa {attempt + 1}")
                    
            except Exception as e:
                print_debug(f"Tentativa {attempt + 1} falhou: {e}")
                if attempt == max_retries - 1:
                    return False
                time.sleep(0.2)
        
        return False
    
    def _init_strategy_conservative(self):
        """Estratégia 3: Abordagem conservadora com verificações"""
        try:
            self.ble = bluetooth.BLE()
            
            # Verifica estado anterior
            try:
                if self.ble.active():
                    print_debug("BLE já estava ativo, reiniciando...")
                    self.ble.active(False)
                    time.sleep(1)
            except:
                pass
            
            # Ativa com verificação
            self.ble.active(True)
            time.sleep(1.5)
            
            # Verifica se ativação foi bem-sucedida
            if not self.ble.active():
                print_debug("Falha na verificação de ativação")
                return False
            
            return self._complete_ble_setup()
            
        except Exception as e:
            print_debug(f"Estratégia conservadora falhou: {e}")
            return False
    
    def _init_strategy_gc_heavy(self):
        """Estratégia 4: Garbage collection intensivo"""
        try:
            # Limpeza intensiva de memória
            for i in range(5):
                gc.collect()
                time.sleep(0.1)
            
            self.ble = bluetooth.BLE()
            
            # Mais garbage collection
            gc.collect()
            time.sleep(0.5)
            
            self.ble.active(True)
            
            # Cleanup final
            gc.collect()
            time.sleep(1)
            
            return self._complete_ble_setup()
            
        except Exception as e:
            print_debug(f"Estratégia GC intensivo falhou: {e}")
            return False
    
    def _init_strategy_simple(self):
        """Estratégia 5: Inicialização simples (fallback)"""
        try:
            self.ble = bluetooth.BLE()
            self.ble.active(True)
            time.sleep(0.5)
            
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
            # Serviço do Display
            DISPLAY_SERVICE = (
                DISPLAY_SERVICE_UUID,
                (
                    # Característica para receber dados de tensão
                    (VOLTAGE_CHAR_UUID, bluetooth.FLAG_WRITE | bluetooth.FLAG_NOTIFY),
                    # Característica para receber comandos de texto
                    (COMMAND_CHAR_UUID, bluetooth.FLAG_WRITE | bluetooth.FLAG_READ),
                    # Característica para ler valores atuais do display
                    (DISPLAY_CHAR_UUID, bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY),
                ),
            )
            
            # Registra os serviços
            ((self.voltage_handle, self.command_handle, self.display_handle),) = self.ble.gatts_register_services((DISPLAY_SERVICE,))
            
            print_debug("Serviços BLE registrados com sucesso")
            
        except Exception as e:
            print_debug(f"Erro ao registrar serviços: {e}")
            raise e
    
    def _start_advertising(self):
        """Inicia o advertising BLE"""
        try:
            payload = BLEUtils.advertising_payload(
                name=BLE_NAME_DISPLAY,
                services=[DISPLAY_SERVICE_UUID]
            )
            
            self.ble.gap_advertise(100, payload)
            print_debug(f"Advertising iniciado como '{BLE_NAME_DISPLAY}'")
            
        except Exception as e:
            print_debug(f"Erro ao iniciar advertising: {e}")
            raise e
    
    def _irq_handler(self, event, data):
        """Manipula eventos BLE"""
        try:
            if event == _IRQ_CENTRAL_CONNECT:
                conn_handle, addr_type, addr = data
                self.connections.add(conn_handle)
                print_debug(f"Cliente conectado: {conn_handle}, Total conexões: {len(self.connections)}")
                
                # Se ainda há espaço para mais conexões, continua advertising
                if len(self.connections) < MAX_CONNECTIONS:
                    self._start_advertising()
            
            elif event == _IRQ_CENTRAL_DISCONNECT:
                conn_handle, addr_type, addr = data
                self.connections.discard(conn_handle)
                print_debug(f"Cliente desconectado: {conn_handle}, Total conexões: {len(self.connections)}")
                
                # Reinicia advertising se há espaço
                if len(self.connections) < MAX_CONNECTIONS:
                    self._start_advertising()
            
            elif event == _IRQ_GATTS_WRITE:
                conn_handle, value_handle = data
                value = self.ble.gatts_read(value_handle)
                
                if value_handle == self.voltage_handle:
                    self._handle_voltage_data(value)
                elif value_handle == self.command_handle:
                    self._handle_command_data(value)
                    
        except Exception as e:
            print_debug(f"Erro no handler de eventos BLE: {e}")
    
    def _handle_voltage_data(self, data):
        """Processa dados de tensão recebidos"""
        try:
            # Decodifica os dados (formato: "V1:12.34,V2:5.67,V3:9.10")
            voltage_str = data.decode('utf-8')
            print_debug(f"Dados de tensão recebidos: {voltage_str}")
            
            # Parse dos dados
            voltages = {}
            for pair in voltage_str.split(','):
                if ':' in pair:
                    key, value = pair.split(':')
                    voltages[key] = float(value)
            
            # Atualiza display
            if len(voltages) >= 3:
                v1 = voltages.get('V1', 0)
                v2 = voltages.get('V2', 0)
                v3 = voltages.get('V3', 0)
                self.display_controller.update_voltages(v1, v2, v3)
                
        except Exception as e:
            print_debug(f"Erro ao processar dados de tensão: {e}")
    
    def _handle_command_data(self, data):
        """Processa comandos recebidos"""
        try:
            command = data.decode('utf-8')
            print_debug(f"Comando recebido: {command}")
            
            if command.startswith("TEXT:"):
                text = command[5:]  # Remove "TEXT:"
                self.display_controller.show_text(text)
            elif command == "CLEAR":
                self.display_controller.clear_all()
            elif command == "STATUS":
                self._send_status()
                
        except Exception as e:
            print_debug(f"Erro ao processar comando: {e}")
    
    def _send_status(self):
        """Envia status atual do display"""
        try:
            if self.connections and self.display_handle:
                status = "DISPLAY_OK"
                self.ble.gatts_notify(list(self.connections)[0], self.display_handle, status.encode())
                print_debug("Status enviado")
        except Exception as e:
            print_debug(f"Erro ao enviar status: {e}")
    
    def stop(self):
        """Para o servidor BLE"""
        try:
            if self.ble:
                self.ble.active(False)
                print_debug("Servidor BLE parado")
        except Exception as e:
            print_debug(f"Erro ao parar servidor BLE: {e}")
        finally:
            self._force_cleanup()
