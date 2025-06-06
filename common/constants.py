# Constantes compartilhadas entre os nós
import bluetooth

# UUIDs para os serviços BLE
DISPLAY_SERVICE_UUID = bluetooth.UUID('12345678-1234-1234-1234-123456789abc')
VOLTMETER_SERVICE_UUID = bluetooth.UUID('87654321-4321-4321-4321-cba987654321')

# UUIDs para características BLE
DISPLAY_CHAR_UUID = bluetooth.UUID('12345678-1234-1234-1234-123456789abd')
VOLTAGE_CHAR_UUID = bluetooth.UUID('87654321-4321-4321-4321-cba987654322')
COMMAND_CHAR_UUID = bluetooth.UUID('11111111-1111-1111-1111-111111111111')

# Configurações dos displays de 7 segmentos multiplexados
# Pinos dos segmentos (compartilhados por todos os displays)
SEGMENT_PINS = [13, 12, 14, 27, 26, 25, 33, 32]  # A, B, C, D, E, F, G, DP

# Pinos de controle dos dígitos para cada display (4 dígitos por display)
DIGIT_PINS = [
    [4, 16, 17, 5],     # Display 1 - 4 dígitos
    [18, 19, 21, 22],   # Display 2 - 4 dígitos  
    [23, 2, 15, 0],     # Display 3 - 4 dígitos
]

# Configurações do voltímetro (pinos ADC)
ADC_PINS = [36, 39, 34]  # VP, VN, GPIO34

# Mapeamento de dígitos para displays de 7 segmentos (ânodo comum)
DIGIT_PATTERNS = {
    '0': {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0, 'g': 1, 'dp': 1},
    '1': {'a': 1, 'b': 0, 'c': 0, 'd': 1, 'e': 1, 'f': 1, 'g': 1, 'dp': 1},
    '2': {'a': 0, 'b': 0, 'c': 1, 'd': 0, 'e': 0, 'f': 1, 'g': 0, 'dp': 1},
    '3': {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 1, 'f': 1, 'g': 0, 'dp': 1},
    '4': {'a': 1, 'b': 0, 'c': 0, 'd': 1, 'e': 1, 'f': 0, 'g': 0, 'dp': 1},
    '5': {'a': 0, 'b': 1, 'c': 0, 'd': 0, 'e': 1, 'f': 0, 'g': 0, 'dp': 1},
    '6': {'a': 0, 'b': 1, 'c': 0, 'd': 0, 'e': 0, 'f': 0, 'g': 0, 'dp': 1},
    '7': {'a': 0, 'b': 0, 'c': 0, 'd': 1, 'e': 1, 'f': 1, 'g': 1, 'dp': 1},
    '8': {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0, 'g': 0, 'dp': 1},
    '9': {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 1, 'f': 0, 'g': 0, 'dp': 1},
    '.': {'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 1, 'f': 1, 'g': 1, 'dp': 0},
    ' ': {'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 1, 'f': 1, 'g': 1, 'dp': 1},
    '-': {'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 1, 'f': 1, 'g': 0, 'dp': 1},
    'E': {'a': 0, 'b': 1, 'c': 1, 'd': 0, 'e': 0, 'f': 0, 'g': 0, 'dp': 1},
    'r': {'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 0, 'f': 1, 'g': 0, 'dp': 1},
}

# Configurações BLE
BLE_NAME_DISPLAY = "ESP32_Display" 
BLE_NAME_VOLTMETER = "ESP32_Voltmeter"
MAX_CONNECTIONS = 3

# Configurações de multiplexação
MULTIPLEX_FREQUENCY = 200  # Hz - frequência de multiplexação
DIGIT_ON_TIME = 1.25  # ms - tempo que cada dígito fica ligado (1000/200/4 = 1.25ms)
