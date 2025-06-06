# Guia de Resolução de Problemas

## Problemas Comuns e Soluções

### 1. ESP32 não aparece na porta serial

**Sintomas:**
- ESP32 não detectado pelo computador
- Porta serial não disponível

**Soluções:**
```bash
# Linux: Verificar se está detectado
lsusb | grep -i cp210x
dmesg | tail -20

# Verificar permissões
sudo usermod -a -G dialout $USER
# Logout e login novamente

# Instalar drivers se necessário (Ubuntu/Debian)
sudo apt-get install python3-serial

# Testar conexão
python3 -c "import serial; print('Serial OK')"
```

### 2. Erro ao instalar MicroPython

**Sintomas:**
- `esptool.py` falha ao conectar
- Erro de timeout ou conexão

**Soluções:**
```bash
# Segurar botão BOOT no ESP32 durante o flash
# Tentar velocidade menor
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 115200 write_flash -z 0x1000 firmware/esp32-micropython.bin

# Verificar cabo USB (usar cabo de dados, não apenas carregamento)
# Tentar porta diferente

# Reset completo antes do flash
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
```

### 3. Imports não funcionam no MicroPython

**Sintomas:**
- `ImportError: no module named 'xxx'`
- Arquivos não encontrados

**Soluções:**
```python
# Verificar estrutura de arquivos
import os
print(os.listdir('/'))
print(os.listdir('/common'))

# Verificar path
import sys
print(sys.path)

# Adicionar paths manualmente se necessário
sys.path.append('/common')
sys.path.append('/')

# Recarregar módulo se alterado
import sys
if 'module_name' in sys.modules:
    del sys.modules['module_name']
import module_name
```

### 4. Displays de 7 segmentos não funcionam

**Sintomas:**
- Displays não acendem
- Segmentos errados acesos
- Brilho muito fraco

**Diagnóstico:**
```python
# Teste básico de GPIO
from machine import Pin
import time

# Teste um pino específico
test_pin = Pin(2, Pin.OUT)
for i in range(10):
    test_pin.value(1)
    time.sleep(0.5)
    test_pin.value(0)
    time.sleep(0.5)
```

**Soluções:**

1. **Verificar tipo de display:**
```python
# Para displays de CÁTODO COMUM, inverter lógica em constants.py
DIGIT_PATTERNS = {
    '0': {'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 1, 'f': 1, 'g': 0, 'dp': 0},
    # ... inverter todos os valores (0->1, 1->0)
}
```

2. **Verificar resistores:**
   - Use resistores de 220Ω-470Ω para limitar corrente
   - Sem resistores: displays podem queimar

3. **Verificar conexões:**
   - Ânodo comum -> 3.3V ou 5V
   - Segmentos -> GPIO através de resistores

### 5. BLE não conecta

**Sintomas:**
- Dispositivos não aparecem no scan
- Conexão falha ou desconecta

**Diagnóstico:**
```python
# Teste básico de BLE
import bluetooth
ble = bluetooth.BLE()
print(f"BLE disponível: {ble}")
ble.active(True)
print(f"BLE ativo: {ble.active()}")

# Verificar se está fazendo advertising
# Usar app de celular para verificar (nRF Connect, etc.)
```

**Soluções:**

1. **Reiniciar BLE:**
```python
import bluetooth
ble = bluetooth.BLE()
ble.active(False)
time.sleep(1)
ble.active(True)
```

2. **Verificar distância:**
   - Dispositivos muito longe
   - Interferência de outros dispositivos
   - Tentar com dispositivos próximos (< 1 metro)

3. **Verificar nomes e UUIDs:**
```python
# Verificar se os nomes estão corretos
from constants import BLE_NAME_DISPLAY, BLE_NAME_VOLTMETER
print(f"Nome Display: {BLE_NAME_DISPLAY}")
print(f"Nome Voltímetro: {BLE_NAME_VOLTMETER}")
```

### 6. ADC lê valores incorretos

**Sintomas:**
- Valores sempre 0 ou 4095
- Valores instáveis
- Valores não correspondem à tensão aplicada

**Diagnóstico:**
```python
# Teste básico de ADC
from machine import Pin, ADC
import time

adc = ADC(Pin(36))
adc.atten(ADC.ATTN_11DB)
adc.width(ADC.WIDTH_12BIT)

for i in range(10):
    raw = adc.read()
    voltage = (raw / 4095.0) * 3.3
    print(f"Raw: {raw}, Tensão: {voltage:.3f}V")
    time.sleep(0.5)
```

**Soluções:**

1. **Verificar atenuação:**
```python
# Para tensões até 3.3V
adc.atten(ADC.ATTN_11DB)

# Para tensões menores, usar outras atenuações:
# ADC.ATTN_0DB   # 0-1.1V
# ADC.ATTN_2_5DB # 0-1.5V  
# ADC.ATTN_6DB   # 0-2.2V
# ADC.ATTN_11DB  # 0-3.3V
```

2. **Verificar pinos ADC:**
   - Nem todos os pinos GPIO são ADC
   - Pinos recomendados: 32, 33, 34, 35, 36, 39

3. **Adicionar capacitor de filtro:**
   - Capacitor de 100nF entre pino ADC e GND

### 7. Memória insuficiente

**Sintomas:**
- `MemoryError`
- Sistema trava ou reinicia
- Operações falham

**Diagnóstico:**
```python
import gc
gc.collect()
print(f"Memória livre: {gc.mem_free()}")
print(f"Memória alocada: {gc.mem_alloc()}")
```

**Soluções:**

1. **Limpar memória regularmente:**
```python
import gc
gc.collect()  # Executar periodicamente
```

2. **Otimizar código:**
   - Remover imports desnecessários
   - Usar geradores ao invés de listas
   - Evitar strings muito grandes

3. **Reduzir buffers:**
```python
# Em adc_reader.py, reduzir histórico
self.filter_samples = 5  # ao invés de 10
```

### 8. Sistema trava ou reinicia

**Sintomas:**
- ESP32 reinicia sozinho
- Código para de executar
- Watchdog timer reset

**Diagnóstico:**
```python
# Verificar causa do reset
import machine
print(f"Causa do reset: {machine.reset_cause()}")

# Adicionar delays em loops
import time
while True:
    # ... código ...
    time.sleep(0.01)  # Evita watchdog
```

**Soluções:**

1. **Adicionar tratamento de exceções:**
```python
try:
    # código que pode falhar
    pass
except Exception as e:
    print(f"Erro: {e}")
    # continuar execução
```

2. **Evitar loops sem delay:**
```python
# Ruim
while True:
    do_something()

# Bom  
while True:
    do_something()
    time.sleep(0.1)
```

### 9. Erro de compilação/sintaxe

**Sintomas:**
- `SyntaxError`
- `IndentationError`
- Código não executa

**Soluções:**

1. **Verificar indentação:**
   - Usar apenas espaços OU tabs, não misturar
   - Configurar editor para mostrar espaços

2. **Verificar caracteres especiais:**
   - Copiar/colar pode introduzir caracteres inválidos
   - Redigitar código manualmente se necessário

3. **Testar em pequenos pedaços:**
```python
# Testar funções individualmente
def test_function():
    print("Teste OK")

test_function()
```

## Ferramentas de Debug

### 1. Monitor Serial
```bash
# Conectar ao ESP32 para ver logs
screen /dev/ttyUSB0 115200
# ou
minicom -D /dev/ttyUSB0 -b 115200
```

### 2. Apps de Celular para BLE
- **nRF Connect** (Android/iOS) - Excelente para debug BLE
- **BLE Scanner** (Android/iOS) - Simples e eficiente
- **LightBlue** (iOS) - Interface limpa

### 3. Thonny IDE
- Interface gráfica para MicroPython
- Debug interativo
- Transferência fácil de arquivos

### 4. Multímetro
- Verificar tensões nos pinos
- Verificar continuidade
- Medir corrente dos displays

## Logs Importantes

### Mensagens Normais de Funcionamento:
```
[timestamp] Nó Display inicializado com sucesso!
[timestamp] Servidor BLE do Display inicializado
[timestamp] Cliente conectado: 1, Total conexões: 1
[timestamp] Tensões recebidas: (1.23, 4.56, 7.89)
```

### Mensagens de Erro Típicas:
```
[timestamp] Erro ao inicializar displays: [Errno 19] ENODEV
[timestamp] Erro ao conectar: [Errno 110] EHOSTUNREACH  
[timestamp] Erro ao processar dados de tensão: invalid literal
```

## Quando Buscar Ajuda

Se após seguir este guia o problema persistir:

1. **Documente o problema:**
   - Mensagens de erro exatas
   - Passos para reproduzir
   - Hardware utilizado

2. **Inclua informações do sistema:**
```python
import os
print(f"Sistema: {os.uname()}")
exec(open('diagnostics.py').read())
```

3. **Teste em hardware mínimo:**
   - Apenas ESP32 + 1 display
   - Apenas ESP32 + 1 canal ADC
   - Isolar o problema

4. **Verifique documentação:**
   - [MicroPython ESP32](https://docs.micropython.org/en/latest/esp32/)
   - [ESP32 Datasheet](https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf)
