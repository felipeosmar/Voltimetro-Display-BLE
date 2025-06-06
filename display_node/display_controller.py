from machine import Pin, Timer
import time
import sys
sys.path.append('/common')
from constants import SEGMENT_PINS, DIGIT_PINS, DIGIT_PATTERNS, MULTIPLEX_FREQUENCY

class MultiplexedDisplay:
    def __init__(self, display_index):
        """Inicializa um display multiplexado de 4 dígitos"""
        self.display_index = display_index
        self.digit_pins = [Pin(pin_num, Pin.OUT) for pin_num in DIGIT_PINS[display_index]]
        
        # Buffer para os 4 dígitos deste display
        self.digit_buffer = [' ', ' ', ' ', ' ']
        
        # Estado da multiplexação
        self.current_digit = 0
        
        # Desliga todos os dígitos inicialmente
        self.turn_off_all_digits()
    
    def turn_off_all_digits(self):
        """Desliga todos os dígitos do display"""
        for pin in self.digit_pins:
            pin.value(0)  # Cátodo comum - 0 = dígito desligado
    
    def turn_on_digit(self, digit_index):
        """Liga apenas um dígito específico"""
        self.turn_off_all_digits()
        if 0 <= digit_index < 4:
            self.digit_pins[digit_index].value(1)  # 1 = dígito ligado
    
    def set_text(self, text):
        """Define o texto a ser exibido (até 4 caracteres)"""
        # Limita a 4 caracteres e preenche com espaços à esquerda se necessário
        text = str(text)[:4]
        
        # Se for um número decimal, formata adequadamente
        if '.' in text and len(text) <= 4:
            # Mantém como está se já cabe
            pass
        elif text.replace('.', '').replace('-', '').isdigit():
            # É um número - alinha à direita
            text = text.rjust(4)
        else:
            # Texto normal - alinha à esquerda
            text = text.ljust(4)
        
        # Atualiza buffer
        for i in range(4):
            if i < len(text):
                self.digit_buffer[i] = text[i]
            else:
                self.digit_buffer[i] = ' '
    
    def set_voltage(self, voltage):
        """Exibe uma tensão formatada (ex: 12.34)"""
        voltage_str = f"{voltage:.2f}"
        
        # Se tem mais de 4 caracteres, reduz precisão
        if len(voltage_str) > 4:
            if voltage >= 100:
                voltage_str = f"{voltage:.1f}"
            if len(voltage_str) > 4:
                voltage_str = f"{voltage:.0f}"
            if len(voltage_str) > 4:
                voltage_str = "----"  # Overflow
        
        self.set_text(voltage_str)
    
    def get_current_text(self):
        """Retorna o texto atualmente no buffer"""
        return ''.join(self.digit_buffer).rstrip()

class DisplayController:
    def __init__(self):
        """Inicializa o controlador dos 3 displays multiplexados"""
        # Configura pinos dos segmentos (compartilhados)
        self.segment_pins = {}
        segment_names = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'dp']
        
        for i, pin_num in enumerate(SEGMENT_PINS):
            segment_name = segment_names[i]
            self.segment_pins[segment_name] = Pin(pin_num, Pin.OUT)
            self.segment_pins[segment_name].value(0)  # Inicia apagado (cátodo comum)
        
        # Inicializa os 3 displays
        self.displays = []
        for i in range(3):
            try:
                display = MultiplexedDisplay(i)
                self.displays.append(display)
                print(f"Display {i+1} inicializado")
            except Exception as e:
                print(f"Erro ao inicializar display {i+1}: {e}")
                self.displays.append(None)
        
        # Timer para multiplexação
        self.multiplex_timer = Timer(0)
        self.current_display = 0
        self.current_digit = 0
        
        # Inicia multiplexação
        self.start_multiplexing()
        
        print(f"DisplayController inicializado com {len([d for d in self.displays if d])} displays ativos")
    
    def start_multiplexing(self):
        """Inicia o timer de multiplexação"""
        # Frequência: 200Hz total = ~16.7Hz por dígito por display (200Hz / 3 displays / 4 dígitos)
        period_us = int(1000000 / (MULTIPLEX_FREQUENCY * 3 * 4))  # Período em microssegundos
        self.multiplex_timer.init(period=period_us, mode=Timer.PERIODIC, callback=self._multiplex_callback)
    
    def stop_multiplexing(self):
        """Para a multiplexação"""
        self.multiplex_timer.deinit()
        self.clear_all_segments()
        for display in self.displays:
            if display:
                display.turn_off_all_digits()
    
    def _multiplex_callback(self, timer):
        """Callback do timer de multiplexação"""
        try:
            # Apaga tudo primeiro
            self.clear_all_segments()
            
            # Seleciona display e dígito atuais
            if self.displays[self.current_display]:
                display = self.displays[self.current_display]
                
                # Liga o dígito atual
                display.turn_on_digit(self.current_digit)
                
                # Exibe o caractere correspondente
                char = display.digit_buffer[self.current_digit]
                self.set_segments_for_char(char)
            
            # Avança para próximo dígito/display
            self.current_digit += 1
            if self.current_digit >= 4:
                self.current_digit = 0
                self.current_display += 1
                if self.current_display >= 3:
                    self.current_display = 0
                    
        except Exception as e:
            # Ignora erros no timer para não travar o sistema
            pass
    
    def clear_all_segments(self):
        """Apaga todos os segmentos"""
        for pin in self.segment_pins.values():
            pin.value(0)  # Cátodo comum - 0 = apagado
    
    def set_segments_for_char(self, char):
        """Define os segmentos para exibir um caractere"""
        if char in DIGIT_PATTERNS:
            pattern = DIGIT_PATTERNS[char]
            for segment, value in pattern.items():
                if segment in self.segment_pins:
                    # Inverte a lógica para cátodo comum: 0 vira 1, 1 vira 0
                    inverted_value = 1 - value
                    self.segment_pins[segment].value(inverted_value)
        else:
            # Caractere desconhecido - apaga tudo
            self.clear_all_segments()
    
    def display_voltage(self, display_index, voltage):
        """Exibe uma tensão em um display específico"""
        if 0 <= display_index < len(self.displays) and self.displays[display_index]:
            self.displays[display_index].set_voltage(voltage)
            return True
        return False
    
    def display_text(self, display_index, text):
        """Exibe texto em um display específico"""
        if 0 <= display_index < len(self.displays) and self.displays[display_index]:
            self.displays[display_index].set_text(text)
            return True
        return False
    
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
        for display in self.displays:
            if display:
                display.set_text("    ")  # 4 espaços
    
    def get_current_values(self):
        """Retorna os valores atualmente exibidos"""
        values = []
        for display in self.displays:
            if display:
                values.append(display.get_current_text())
            else:
                values.append("")
        return values
    
    def test_all_displays(self):
        """Testa todos os displays"""
        print("Testando displays multiplexados (cátodo comum)...")
        
        # Para a multiplexação para teste manual
        self.stop_multiplexing()
        
        try:
            # Teste 1: Todos os segmentos
            print("1. Testando todos os segmentos...")
            for display in self.displays:
                if display:
                    display.set_text("8888")
            
            # Liga manualmente cada display e dígito para teste
            for disp_idx, display in enumerate(self.displays):
                if display:
                    print(f"Testando display {disp_idx + 1}")
                    for digit in range(4):
                        display.turn_on_digit(digit)
                        self.set_segments_for_char('8')
                        time.sleep(0.5)
                        display.turn_off_all_digits()
                        time.sleep(0.1)
            
            # Teste 2: Contagem
            print("2. Testando contagem...")
            for num in range(10):
                for display in self.displays:
                    if display:
                        display.set_text(str(num) * 4)
                
                # Simula multiplexação manual para visualização
                for _ in range(20):  # 20 ciclos de multiplexação
                    for disp_idx, display in enumerate(self.displays):
                        if display:
                            for digit in range(4):
                                display.turn_on_digit(digit)
                                char = display.digit_buffer[digit]
                                self.set_segments_for_char(char)
                                time.sleep_ms(2)  # 2ms por dígito
                                display.turn_off_all_digits()
                
                time.sleep(0.3)
            
            # Teste 3: Voltagens de exemplo
            print("3. Testando exibição de voltagens...")
            test_voltages = [1.23, 45.6, 789.0]
            for i, voltage in enumerate(test_voltages):
                if i < len(self.displays) and self.displays[i]:
                    self.displays[i].set_voltage(voltage)
            
            # Simula multiplexação
            for _ in range(50):
                for disp_idx, display in enumerate(self.displays):
                    if display:
                        for digit in range(4):
                            display.turn_on_digit(digit)
                            char = display.digit_buffer[digit]
                            self.set_segments_for_char(char)
                            time.sleep_ms(2)
                            display.turn_off_all_digits()
            
            time.sleep(1)
            
        finally:
            # Reinicia multiplexação automática
            self.clear_all()
            self.start_multiplexing()
            print("Teste concluído - multiplexação reativada")
    
    def test_individual_display(self, display_index):
        """Testa um display específico"""
        if 0 <= display_index < len(self.displays) and self.displays[display_index]:
            display = self.displays[display_index]
            
            print(f"Testando display {display_index + 1} (cátodo comum)...")
            
            # Para multiplexação
            self.stop_multiplexing()
            
            try:
                # Testa cada dígito
                for digit in range(4):
                    print(f"  Dígito {digit + 1}")
                    display.turn_on_digit(digit)
                    
                    # Testa cada segmento
                    segments = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'dp']
                    for segment in segments:
                        self.clear_all_segments()
                        if segment in self.segment_pins:
                            self.segment_pins[segment].value(1)  # Cátodo comum - 1 = aceso
                            time.sleep(0.2)
                    
                    display.turn_off_all_digits()
                    time.sleep(0.2)
                    
            finally:
                self.start_multiplexing()
        else:
            print(f"Display {display_index + 1} não disponível")
