# Exemplos de Uso e Comandos Úteis

Este arquivo contém exemplos práticos de como usar o sistema de displays 7 segmentos com Bluetooth.

## Comandos no REPL do MicroPython

### Para o Nó Display

```python
# Conectar via terminal serial e executar no REPL

# 1. Teste básico dos displays
exec(open('diagnostics.py').read())

# 2. Controle manual dos displays
import sys
sys.path.append('/common')
from display_controller import DisplayController

controller = DisplayController()

# Exibe números
controller.display_texts(['1', '2', '3'])

# Exibe tensões
controller.display_voltages([1.23, 4.56, 7.89])

# Limpa displays
controller.clear_all()

# Teste completo
controller.test_all_displays()
```

### Para o Nó Voltímetro

```python
# Conectar via terminal serial e executar no REPL

# 1. Teste básico do ADC
exec(open('diagnostics.py').read())

# 2. Leitura manual do ADC
import sys
sys.path.append('/common')
from adc_reader import ADCReader

reader = ADCReader()

# Lê tensões uma vez
voltages = reader.read_all_voltages()
print(f"Tensões: {voltages}")

# Leitura contínua (Ctrl+C para parar)
reader.continuous_read(1000)  # A cada 1 segundo

# Calibração manual
reader.auto_calibrate(0, 5.0)  # Canal 1 com 5.0V conhecidos
```

## Comandos BLE via Computador

### Usando o script de teste

```bash
# No computador, execute:
python3 test_ble_communication.py
```

### Comandos para o Display via BLE

Conecte-se à característica `COMMAND_CHAR_UUID` e envie:

- `TEST` - Executa teste completo dos displays
- `CLEAR` - Limpa todos os displays  
- `TEXT:1,2,3` - Exibe "1", "2", "3" nos displays
- `TEXT:Hi,Lo,Go` - Exibe textos customizados
- `VOLT:1.23,4.56,7.89` - Exibe tensões específicas
- `TEXT:8.8.8` - Teste de todos os segmentos

### Leitura do Voltímetro via BLE

```python
# Exemplo usando bleak (Python)
import asyncio
import struct
from bleak import BleakClient

VOLTAGE_CHAR_UUID = "87654321-4321-4321-4321-cba987654322"

async def read_voltages(address):
    async with BleakClient(address) as client:
        data = await client.read_gatt_char(VOLTAGE_CHAR_UUID)
        voltages = struct.unpack('<fff', data)
        print(f"Tensões: {voltages}")

# Substitua pelo endereço do seu ESP32
asyncio.run(read_voltages("24:0a:c4:xx:xx:xx"))
```

## Troubleshooting

### Problema: Displays não acendem

```python
# Teste individual de cada display
import sys
sys.path.append('/common')
from display_controller import DisplayController
from constants import DISPLAY_PINS

controller = DisplayController()

# Testa display 1
controller.displays['display1'].test_segments()

# Testa display 2  
controller.displays['display2'].test_segments()

# Testa display 3
controller.displays['display3'].test_segments()
```

### Problema: ADC lê valores incorretos

```python
# Teste de canais ADC
import sys
sys.path.append('/common')
from adc_reader import ADCReader

reader = ADCReader()

# Teste detalhado
reader.test_channels()

# Leitura raw de um canal específico
raw_value = reader.read_raw_value(0)  # Canal 1
voltage = reader.raw_to_voltage(raw_value)
print(f"Canal 1 - Raw: {raw_value}, Tensão: {voltage:.3f}V")
```

### Problema: BLE não conecta

```python
# Teste básico de BLE
import bluetooth

ble = bluetooth.BLE()
ble.active(True)

print(f"BLE ativo: {ble.active()}")

# No nó display
from ble_server import BLEDisplayServer
# Verificar logs no terminal serial

# No nó voltímetro  
from ble_client import BLEVoltmeterClient
# Verificar se encontra o display
```

## Configurações Avançadas

### Ajustar Intervalo de Envio

```python
# No nó voltímetro, alterar intervalo para 0.5 segundos
node.set_send_interval(0.5)
```

### Calibração Automática

```python
# Aplicar tensão conhecida e calibrar
reader = ADCReader()

# Canal 1 com 3.3V
reader.auto_calibrate(0, 3.3)

# Canal 2 com 5.0V (usando divisor de tensão)
reader.auto_calibrate(1, 5.0)

# Canal 3 com 1.5V
reader.auto_calibrate(2, 1.5)
```

### Monitoramento de Status

```python
# Verificar status dos nós
print("=== Status do Display ===")
print(f"Conexões BLE: {node.ble_server.get_connection_count()}")
print(f"Valores atuais: {node.display_controller.get_current_values()}")

print("=== Status do Voltímetro ===") 
print(f"Conectado ao display: {node.ble_client.is_connected()}")
print(f"Clientes conectados: {node.ble_server.get_connection_count()}")
print(f"Última leitura: {node.adc_reader.get_last_readings()}")
```

## Scripts Úteis

### Reset Completo

```python
# Para resetar completamente um nó
import machine
machine.reset()
```

### Verificar Memória

```python
import gc
gc.collect()
print(f"Memória livre: {gc.mem_free()} bytes")
```

### Salvar Configuração

```python
# Salvar fatores de calibração (exemplo)
import json

calibration = {
    'channel_1': 1.05,
    'channel_2': 0.98, 
    'channel_3': 1.02
}

with open('calibration.json', 'w') as f:
    json.dump(calibration, f)
```

### Carregar Configuração

```python
# Carregar configuração salva
import json

try:
    with open('calibration.json', 'r') as f:
        calibration = json.load(f)
    
    # Aplicar calibração
    reader.set_calibration(0, calibration['channel_1'])
    reader.set_calibration(1, calibration['channel_2'])
    reader.set_calibration(2, calibration['channel_3'])
    
    print("Calibração carregada com sucesso!")
except:
    print("Arquivo de calibração não encontrado")
```

## Dicas de Desenvolvimento

### Debug em Tempo Real

```python
# Habilitar debug detalhado
import sys
sys.path.append('/common')
from ble_utils import print_debug

# Usar print_debug() para mensagens com timestamp
print_debug("Mensagem de debug")
```

### Monitoramento Contínuo

```python
# Script para monitorar sistema continuamente
import time

while True:
    # Status dos displays
    if hasattr(node, 'display_controller'):
        values = node.display_controller.get_current_values()
        print(f"Displays: {values}")
    
    # Status das tensões
    if hasattr(node, 'adc_reader'):
        voltages = node.adc_reader.read_all_voltages()
        print(f"Tensões: {voltages}")
    
    # Status BLE
    if hasattr(node, 'ble_server'):
        conns = node.ble_server.get_connection_count()
        print(f"Conexões: {conns}")
    
    time.sleep(5)
```
