# GUIA DE CORREÇÃO DO ERRO BLE -18

## 📋 Resumo do Problema

O erro `-18` (ESP_ERR_NOT_SUPPORTED) ocorre durante a inicialização do BLE no ESP32, indicando que uma funcionalidade BLE não é suportada ou há problemas na inicialização.

## 🛠️ Soluções Implementadas

### 1. Arquivos Corrigidos Criados

- `display_node/ble_server_fixed.py` - Servidor BLE do display com múltiplas estratégias
- `voltmeter_node/ble_voltmeter_server_fixed.py` - Servidor BLE do voltímetro corrigido
- `display_node/main_fixed.py` - Main do display usando versão corrigida
- `voltmeter_node/main_fixed.py` - Main do voltímetro usando versão corrigida
- `fix_ble_error18.py` - Script automático de correção
- `test_ble_error18_fix.py` - Teste das correções

### 2. Estratégias de Correção Implementadas

#### Estratégia 1: Reset + Delay Longo
```python
# Reset prévio completo
temp_ble = bluetooth.BLE()
temp_ble.active(False)
time.sleep(1)

# Inicialização com delays
ble = bluetooth.BLE()
time.sleep(0.5)
ble.active(True)
time.sleep(2)
```

#### Estratégia 2: Retry Exponencial
```python
max_retries = 5
base_delay = 0.3

for attempt in range(max_retries):
    delay = base_delay * (2 ** attempt)
    # Tentativa com delay crescente
```

#### Estratégia 3: Conservadora com Verificações
```python
ble = bluetooth.BLE()
if ble.active():
    ble.active(False)
    time.sleep(1)

ble.active(True)
if not ble.active():
    raise Exception("Falha na ativação")
```

#### Estratégia 4: Garbage Collection Intensivo
```python
# Limpeza intensiva de memória
for i in range(5):
    gc.collect()
    time.sleep(0.1)

# Então inicializa BLE
```

#### Estratégia 5: Inicialização Simples (Fallback)
```python
ble = bluetooth.BLE()
ble.active(True)
time.sleep(0.5)
```

## 🚀 Como Usar as Correções

### Passo 1: Teste no Hardware Real

Execute no ESP32:
```python
# Upload dos arquivos corrigidos para o ESP32
# Então execute:
exec(open('test_ble_error18_fix.py').read())
```

### Passo 2: Use os Módulos Corrigidos

**Para Display Node:**
```python
# Ao invés de:
# from ble_server import BLEDisplayServer

# Use:
from ble_server_fixed import FixedBLEDisplayServer

# Ao invés de main.py, execute:
exec(open('main_fixed.py').read())
```

**Para Voltmeter Node:**
```python
# Ao invés de:
# from ble_voltmeter_server import BLEVoltmeterServer

# Use:
from ble_voltmeter_server_fixed import FixedBLEVoltmeterServer

# Ao invés de main.py, execute:
exec(open('main_fixed.py').read())
```

### Passo 3: Monitore os Logs

Os módulos corrigidos fornecem logs detalhados:
- ✓ Indica sucesso
- ❌ Indica falha
- ⚠️ Indica warnings
- 🎉 Indica conclusão bem-sucedida

## 📊 Diagnóstico de Problemas

### Se TODAS as Estratégias Falharem:

1. **Verifique o Firmware MicroPython:**
   ```python
   import sys
   print(sys.implementation)
   ```

2. **Teste BLE Básico:**
   ```python
   import bluetooth
   ble = bluetooth.BLE()
   print("BLE disponível:", hasattr(ble, 'active'))
   ```

3. **Verifique Memória:**
   ```python
   import gc
   gc.collect()
   print("Memória livre:", gc.mem_free())
   ```

### Códigos de Erro Comuns:

- **-18**: ESP_ERR_NOT_SUPPORTED - Funcionalidade não suportada
- **-1**: Erro genérico
- **Out of memory**: Memória insuficiente

## 🔧 Configuração Manual

Se as correções automáticas não funcionarem, configure manualmente:

```python
# 1. Adicione mais delays
time.sleep(2)  # Antes de ativar BLE

# 2. Force garbage collection
import gc
gc.collect()

# 3. Use try/except robusto
try:
    ble = bluetooth.BLE()
    ble.active(True)
except Exception as e:
    if hasattr(e, 'errno') and e.errno == -18:
        # Estratégia específica para erro -18
        pass
```

## 📁 Estrutura de Arquivos Atualizada

```
projeto/
├── fix_ble_error18.py              # Script de correção automática
├── test_ble_error18_fix.py         # Teste das correções
├── display_node/
│   ├── ble_server_fixed.py         # ✅ Servidor BLE corrigido
│   ├── main_fixed.py               # ✅ Main corrigido
│   └── ...
├── voltmeter_node/
│   ├── ble_voltmeter_server_fixed.py # ✅ Servidor BLE corrigido
│   ├── main_fixed.py               # ✅ Main corrigido
│   └── ...
└── common/
    └── ...
```

## ⚡ Scripts de Deploy Atualizados

### Deploy Display (Corrigido):
```bash
# Upload arquivos corrigidos
ampy -p /dev/ttyUSB0 put display_node/ble_server_fixed.py /ble_server_fixed.py
ampy -p /dev/ttyUSB0 put display_node/main_fixed.py /main_fixed.py

# Execute versão corrigida
picocom -b 115200 /dev/ttyUSB0
>>> exec(open('main_fixed.py').read())
```

### Deploy Voltmeter (Corrigido):
```bash
# Upload arquivos corrigidos
ampy -p /dev/ttyUSB0 put voltmeter_node/ble_voltmeter_server_fixed.py /ble_voltmeter_server_fixed.py
ampy -p /dev/ttyUSB0 put voltmeter_node/main_fixed.py /main_fixed.py

# Execute versão corrigida
picocom -b 115200 /dev/ttyUSB0
>>> exec(open('main_fixed.py').read())
```

## 🧪 Testes Disponíveis

1. **Teste Básico**: `test_ble_error18_fix.py`
2. **Teste de Display**: `main_fixed.py test`
3. **Teste de Voltímetro**: `main_fixed.py test`
4. **Calibração de ADC**: `main_fixed.py calibrate`

## 📞 Resolução de Problemas

### Problema: "Import Error"
**Solução**: Verifique se todos os arquivos foram uploaded corretamente

### Problema: "Memória Insuficiente"
**Solução**: Execute `gc.collect()` antes da inicialização BLE

### Problema: "Erro -18 Persistente"
**Solução**: 
1. Teste firmware MicroPython diferente
2. Verifique se ESP32 suporta BLE
3. Use modo de teste sem BLE

### Problema: "BLE não aparece no scan"
**Solução**: 
1. Verifique se advertising está ativo
2. Teste com `test_ble_simple.py`
3. Verifique distância e interferências

## ✅ Checklist de Implementação

- [ ] Upload dos arquivos `*_fixed.py`
- [ ] Teste com `test_ble_error18_fix.py`
- [ ] Execute `main_fixed.py` ao invés de `main.py`
- [ ] Monitore logs para verificar qual estratégia funcionou
- [ ] Teste comunicação BLE entre dispositivos
- [ ] Verifique estabilidade em execução prolongada

## 🎯 Resultado Esperado

Após implementar as correções:
- ✅ Inicialização BLE sem erro -18
- ✅ Advertising funcionando
- ✅ Dispositivos detectáveis via scan BLE
- ✅ Comunicação estável entre voltímetro e display
- ✅ Logs informativos sobre qual estratégia funcionou
