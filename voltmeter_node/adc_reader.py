from machine import Pin, ADC
import time
import sys
sys.path.append('/common')
from constants import ADC_PINS
from ble_utils import print_debug

class ADCReader:
    def __init__(self):
        """Inicializa o leitor de ADC para 3 canais"""
        self.adc_channels = []
        self.voltage_readings = [0.0, 0.0, 0.0]
        self.calibration_factors = [1.0, 1.0, 1.0]  # Fatores de calibração
        
        # Inicializa os canais ADC
        for i, pin_num in enumerate(ADC_PINS):
            try:
                adc = ADC(Pin(pin_num))
                adc.atten(ADC.ATTN_11DB)  # Permite leitura até 3.3V
                adc.width(ADC.WIDTH_12BIT)  # Resolução de 12 bits (0-4095)
                self.adc_channels.append(adc)
                print_debug(f"Canal ADC {i+1} inicializado no pino {pin_num}")
            except Exception as e:
                print_debug(f"Erro ao inicializar ADC no pino {pin_num}: {e}")
                self.adc_channels.append(None)
        
        # Configurações de filtragem
        self.filter_samples = 10  # Número de amostras para média móvel
        self.sample_history = [[] for _ in range(3)]  # Histórico de amostras
        
        print_debug(f"ADCReader inicializado com {len([c for c in self.adc_channels if c is not None])} canais ativos")
    
    def read_raw_value(self, channel):
        """Lê valor bruto do ADC (0-4095)"""
        if channel < 0 or channel >= len(self.adc_channels):
            return 0
        
        if self.adc_channels[channel] is None:
            return 0
        
        try:
            return self.adc_channels[channel].read()
        except Exception as e:
            print_debug(f"Erro ao ler ADC canal {channel}: {e}")
            return 0
    
    def raw_to_voltage(self, raw_value):
        """Converte valor bruto para tensão (0-3.3V)"""
        # ADC de 12 bits: 0-4095 corresponde a 0-3.3V
        return (raw_value / 4095.0) * 3.3
    
    def read_voltage(self, channel, filtered=True):
        """Lê tensão de um canal específico"""
        raw_value = self.read_raw_value(channel)
        voltage = self.raw_to_voltage(raw_value)
        
        # Aplica fator de calibração
        voltage *= self.calibration_factors[channel]
        
        if filtered and channel < len(self.sample_history):
            # Adiciona à média móvel
            self.sample_history[channel].append(voltage)
            if len(self.sample_history[channel]) > self.filter_samples:
                self.sample_history[channel].pop(0)
            
            # Retorna média das amostras
            if self.sample_history[channel]:
                voltage = sum(self.sample_history[channel]) / len(self.sample_history[channel])
        
        return voltage
    
    def read_all_voltages(self, filtered=True):
        """Lê tensões de todos os canais"""
        voltages = []
        for i in range(3):
            voltage = self.read_voltage(i, filtered)
            voltages.append(voltage)
            self.voltage_readings[i] = voltage
        
        return voltages
    
    def get_last_readings(self):
        """Retorna as últimas leituras"""
        return self.voltage_readings.copy()
    
    def set_calibration(self, channel, factor):
        """Define fator de calibração para um canal"""
        if 0 <= channel < len(self.calibration_factors):
            self.calibration_factors[channel] = factor
            print_debug(f"Calibração canal {channel+1}: fator = {factor}")
    
    def auto_calibrate(self, channel, known_voltage):
        """Auto-calibração baseada em tensão conhecida"""
        if 0 <= channel < len(self.adc_channels):
            # Lê valor atual sem calibração
            current_factor = self.calibration_factors[channel]
            self.calibration_factors[channel] = 1.0
            
            measured_voltage = self.read_voltage(channel, filtered=True)
            
            if measured_voltage > 0:
                new_factor = known_voltage / measured_voltage
                self.calibration_factors[channel] = new_factor
                print_debug(f"Auto-calibração canal {channel+1}: medido={measured_voltage:.3f}V, conhecido={known_voltage:.3f}V, fator={new_factor:.3f}")
            else:
                self.calibration_factors[channel] = current_factor
                print_debug(f"Erro na auto-calibração canal {channel+1}: tensão medida = 0")
    
    def continuous_read(self, interval_ms=100):
        """Leitura contínua das tensões"""
        print_debug(f"Iniciando leitura contínua (intervalo: {interval_ms}ms)")
        
        try:
            while True:
                voltages = self.read_all_voltages()
                print_debug(f"Tensões: Canal1={voltages[0]:.3f}V, Canal2={voltages[1]:.3f}V, Canal3={voltages[2]:.3f}V")
                time.sleep_ms(interval_ms)
        except KeyboardInterrupt:
            print_debug("Leitura contínua interrompida")
    
    def test_channels(self):
        """Testa todos os canais ADC"""
        print_debug("Testando canais ADC...")
        
        for i in range(3):
            print_debug(f"\nTeste do Canal {i+1} (Pino {ADC_PINS[i]}):")
            
            if self.adc_channels[i] is None:
                print_debug("  Canal não disponível")
                continue
            
            # Lê 20 amostras
            samples = []
            for _ in range(20):
                raw = self.read_raw_value(i)
                voltage = self.raw_to_voltage(raw)
                samples.append((raw, voltage))
                time.sleep_ms(50)
            
            # Calcula estatísticas
            raw_values = [s[0] for s in samples]
            voltages = [s[1] for s in samples]
            
            print_debug(f"  Raw: min={min(raw_values)}, max={max(raw_values)}, média={sum(raw_values)/len(raw_values):.1f}")
            print_debug(f"  Tensão: min={min(voltages):.3f}V, max={max(voltages):.3f}V, média={sum(voltages)/len(voltages):.3f}V")
        
        print_debug("Teste de canais concluído")
    
    def get_channel_info(self):
        """Retorna informações dos canais"""
        info = {
            'channels': len(self.adc_channels),
            'active_channels': len([c for c in self.adc_channels if c is not None]),
            'pins': ADC_PINS,
            'calibration_factors': self.calibration_factors,
            'filter_samples': self.filter_samples,
            'last_readings': self.voltage_readings
        }
        return info
