from machine import Pin
import time
import sys
sys.path.append('/common')
from constants import DISPLAY_PINS, DIGIT_PATTERNS

class Display7Segment:
    def __init__(self, display_name):
        """Inicializa um display de 7 segmentos"""
        self.display_name = display_name
        self.pins = DISPLAY_PINS[display_name]
        self.gpio_pins = {}
        
        # Configura os pinos GPIO
        for segment, pin_num in self.pins.items():
            self.gpio_pins[segment] = Pin(pin_num, Pin.OUT)
        
        # Limpa o display
        self.clear()
    
    def clear(self):
        """Limpa o display (todos os segmentos apagados)"""
        for pin in self.gpio_pins.values():
            pin.value(1)  # Ânodo comum - 1 = apagado
    
    def display_digit(self, digit):
        """Exibe um dígito no display"""
        if str(digit) in DIGIT_PATTERNS:
            pattern = DIGIT_PATTERNS[str(digit)]
            for segment, value in pattern.items():
                if segment in self.gpio_pins:
                    self.gpio_pins[segment].value(value)
        else:
            self.clear()
    
    def display_char(self, char):
        """Exibe um caractere no display"""
        self.display_digit(char)
    
    def test_segments(self):
        """Testa todos os segmentos do display"""
        print(f"Testando display {self.display_name}...")
        segments = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'dp']
        
        for segment in segments:
            self.clear()
            if segment in self.gpio_pins:
                self.gpio_pins[segment].value(0)  # Acende o segmento
                print(f"Segmento {segment} aceso")
                time.sleep(0.5)
        
        self.clear()

class DisplayController:
    def __init__(self):
        """Inicializa o controlador dos 3 displays"""
        self.displays = {}
        
        # Inicializa os 3 displays
        for display_name in ['display1', 'display2', 'display3']:
            try:
                self.displays[display_name] = Display7Segment(display_name)
                print(f"Display {display_name} inicializado")
            except Exception as e:
                print(f"Erro ao inicializar {display_name}: {e}")
        
        self.current_values = ['', '', '']
    
    def display_voltage(self, display_index, voltage):
        """Exibe uma tensão em um display específico (formato X.XX)"""
        if display_index < 0 or display_index >= 3:
            return False
        
        display_name = f"display{display_index + 1}"
        if display_name not in self.displays:
            return False
        
        # Formata a tensão para exibição
        voltage_str = f"{voltage:.2f}"
        
        # Se a tensão tem mais de 3 caracteres (incluindo ponto), trunca
        if len(voltage_str) > 3:
            if '.' in voltage_str:
                # Mantém apenas 1 casa decimal se necessário
                voltage_str = f"{voltage:.1f}"
                if len(voltage_str) > 3:
                    voltage_str = voltage_str[:3]
            else:
                voltage_str = voltage_str[:3]
        
        # Exibe o valor no display
        self.display_text(display_index, voltage_str)
        return True
    
    def display_text(self, display_index, text):
        """Exibe texto em um display específico"""
        if display_index < 0 or display_index >= 3:
            return False
        
        display_name = f"display{display_index + 1}"
        if display_name not in self.displays:
            return False
        
        # Limita o texto a 3 caracteres
        text = str(text)[:3]
        self.current_values[display_index] = text
        
        # Se o texto tem apenas 1 caractere, exibe no display
        if len(text) == 1:
            self.displays[display_name].display_char(text)
        else:
            # Para texto com múltiplos caracteres, exibe o primeiro
            # (em uma implementação mais avançada, poderia fazer scroll)
            self.displays[display_name].display_char(text[0] if text else ' ')
        
        return True
    
    def display_voltages(self, voltages):
        """Exibe as 3 tensões nos 3 displays"""
        success = True
        for i, voltage in enumerate(voltages[:3]):
            if not self.display_voltage(i, voltage):
                success = False
        return success
    
    def display_texts(self, texts):
        """Exibe textos nos 3 displays"""
        success = True
        for i, text in enumerate(texts[:3]):
            if not self.display_text(i, text):
                success = False
        return success
    
    def clear_all(self):
        """Limpa todos os displays"""
        for display in self.displays.values():
            display.clear()
        self.current_values = ['', '', '']
    
    def test_all_displays(self):
        """Testa todos os displays"""
        print("Testando todos os displays...")
        
        # Teste de segmentos
        for display in self.displays.values():
            display.test_segments()
            time.sleep(1)
        
        # Teste de dígitos
        print("Testando dígitos...")
        for digit in range(10):
            for display in self.displays.values():
                display.display_digit(digit)
            print(f"Dígito {digit} em todos os displays")
            time.sleep(0.5)
        
        # Teste de caracteres especiais
        special_chars = ['.', '-', ' ']
        for char in special_chars:
            for display in self.displays.values():
                display.display_char(char)
            print(f"Caractere '{char}' em todos os displays")
            time.sleep(0.5)
        
        self.clear_all()
        print("Teste concluído")
    
    def get_current_values(self):
        """Retorna os valores atualmente exibidos"""
        return self.current_values.copy()
