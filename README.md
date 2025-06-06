# Projeto Display 7 Segmentos com Bluetooth

Este projeto implementa um sistema de comunicação BLE entre dois nós ESP32 (NodeMCU):
- **Nó Display**: Controla 3 displays de 7 segmentos
- **Nó Voltímetro**: Lê 3 canais analógicos e transmite via BLE

## Estrutura do Projeto

```
projeto/
├── display_node/           # Nó que controla os displays
│   ├── main.py            # Arquivo principal do nó display
│   ├── display_controller.py  # Controlador dos displays de 7 segmentos
│   └── ble_server.py      # Servidor BLE para receber dados
├── voltmeter_node/        # Nó que lê tensões
│   ├── main.py            # Arquivo principal do nó voltímetro
│   ├── adc_reader.py      # Leitor de canais ADC
│   └── ble_client.py      # Cliente/Servidor BLE
├── common/                # Código compartilhado
│   ├── constants.py       # Constantes do projeto
│   └── ble_utils.py       # Utilitários BLE
└── README.md             # Este arquivo
```

## Funcionalidades

### Nó Display
- Controla 3 displays de 7 segmentos (ânodo comum)
- Recebe dados via BLE do nó voltímetro
- Aceita múltiplas conexões BLE simultâneas
- Suporta comandos via BLE para exibir texto customizado
- LED de status indica funcionamento

### Nó Voltímetro
- Lê 3 canais ADC (pinos 36, 39, 34)
- Transmite dados via BLE para o nó display
- Funciona como servidor BLE para conexões de computador
- Filtragem por média móvel nas leituras
- Calibração automática de canais
- Reconexão automática ao display

## Configuração de Hardware

### Nó Display (ESP32 #1)

#### Displays de 7 Segmentos (Ânodo Comum)
**Display 1:**
- Segmento A: GPIO 2
- Segmento B: GPIO 4
- Segmento C: GPIO 5
- Segmento D: GPIO 18
- Segmento E: GPIO 19
- Segmento F: GPIO 21
- Segmento G: GPIO 22
- Ponto Decimal: GPIO 23

**Display 2:**
- Segmento A: GPIO 25
- Segmento B: GPIO 26
- Segmento C: GPIO 27
- Segmento D: GPIO 14
- Segmento E: GPIO 12
- Segmento F: GPIO 13
- Segmento G: GPIO 15
- Ponto Decimal: GPIO 32

**Display 3:**
- Segmento A: GPIO 33
- Segmento B: GPIO 34
- Segmento C: GPIO 35
- Segmento D: GPIO 36
- Segmento E: GPIO 39
- Segmento F: GPIO 37
- Segmento G: GPIO 38
- Ponto Decimal: GPIO 0

#### Conexões dos Displays
- Conecte cada segmento através de resistores de 220Ω-330Ω
- Conecte o ânodo comum ao 3.3V
- Para displays de cátodo comum, inverta a lógica no código

### Nó Voltímetro (ESP32 #2)

#### Canais ADC
- Canal 1: GPIO 36 (VP)
- Canal 2: GPIO 39 (VN)
- Canal 3: GPIO 34

#### Considerações para Leitura de Tensão
- Tensão máxima de entrada: 3.3V
- Para tensões maiores, use divisores de tensão
- Exemplo para 12V: R1=10kΩ, R2=3.3kΩ (fator ~4)

## Instalação

### 1. Preparar o MicroPython
```bash
# Instale o esptool
pip install esptool

# Apague a flash (substitua COM3 pela sua porta)
esptool.py --chip esp32 --port COM3 erase_flash

# Instale o MicroPython
esptool.py --chip esp32 --port COM3 --baud 460800 write_flash -z 0x1000 esp32-micropython.bin
```

### 2. Carregar o Código
Use uma ferramenta como Thonny, ampy ou rshell para transferir os arquivos:

```bash
# Exemplo com ampy
ampy --port COM3 put common/ /common
ampy --port COM3 put display_node/main.py /main.py  # Para nó display
# OU
ampy --port COM3 put voltmeter_node/main.py /main.py  # Para nó voltímetro
```

## Uso

### Inicialização
1. Carregue o código do display no primeiro ESP32
2. Carregue o código do voltímetro no segundo ESP32
3. Ligue ambos os dispositivos
4. O voltímetro automaticamente procurará e conectará ao display

### Comandos BLE

#### Para o Nó Display
Conecte-se à característica `COMMAND_CHAR_UUID` e envie:

- `TEXT:1.23,4.56,7.89` - Exibe texto nos 3 displays
- `VOLT:1.23,4.56,7.89` - Exibe tensões específicas
- `CLEAR` - Limpa todos os displays
- `TEST` - Executa teste dos displays

#### Para o Nó Voltímetro
Conecte-se à característica `VOLTAGE_CHAR_UUID` para ler tensões em tempo real.

### Conexões Múltiplas
- Cada nó suporta até 3 conexões BLE simultâneas
- Você pode conectar computador + outros dispositivos
- Os dados são transmitidos para todas as conexões ativas

## Calibração

### Calibração Manual do Voltímetro
```python
# No nó voltímetro, via REPL
node.calibrate_channel(0, 5.00)  # Canal 1 com 5.00V conhecidos
node.calibrate_channel(1, 3.30)  # Canal 2 com 3.30V conhecidos
node.calibrate_channel(2, 1.50)  # Canal 3 com 1.50V conhecidos
```

### Ajuste do Intervalo de Envio
```python
# Envia dados a cada 2 segundos (padrão: 1 segundo)
node.set_send_interval(2.0)
```

## Troubleshooting

### LED de Status
- **Display**: LED constante = OK, piscando = funcionando
- **Voltímetro**: Pisca rápido = conectado ao display, pisca lento = não conectado

### Problemas Comuns

1. **Displays não funcionam**
   - Verifique as conexões dos segmentos
   - Confirme se são displays de ânodo comum
   - Teste com `node.display_controller.test_all_displays()`

2. **BLE não conecta**
   - Verifique se ambos dispositivos estão ligados
   - Reinicie ambos os nós
   - Verifique a distância entre dispositivos

3. **Leituras ADC incorretas**
   - Verifique as conexões dos pinos ADC
   - Execute calibração manual
   - Verifique divisores de tensão se usados

4. **Erro de memória**
   - O código inclui limpeza automática de memória
   - Reinicie o dispositivo se necessário

### Debug
Monitore a saída serial para mensagens de debug:
```
[timestamp] Mensagem de debug
```

## UUIDs BLE

- **Display Service**: `12345678-1234-1234-1234-123456789abc`
- **Voltmeter Service**: `87654321-4321-4321-4321-cba987654321`
- **Display Characteristic**: `12345678-1234-1234-1234-123456789abd`
- **Voltage Characteristic**: `87654321-4321-4321-4321-cba987654322`
- **Command Characteristic**: `11111111-1111-1111-1111-111111111111`

## Expansões Futuras

1. **Interface Web**: Adicionar servidor HTTP para controle via browser
2. **Mais Displays**: Expandir para mais de 3 displays
3. **Outros Sensores**: Adicionar temperatura, umidade, etc.
4. **Data Logging**: Salvar dados em cartão SD
5. **Alarmes**: Notificações quando tensões saem de faixa

## Licença

Este projeto é disponibilizado sob licença MIT. Veja o arquivo LICENSE para detalhes.
