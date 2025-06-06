#!/bin/bash

# Script de configuração para o projeto Display 7 Segmentos com Bluetooth
# Para uso em Linux/macOS. Para Windows, use o setup.bat

echo "=== Configuração do Projeto Display 7 Segmentos com Bluetooth ==="
echo

# Verifica se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python 3 não encontrado. Instale o Python 3 primeiro."
    exit 1
fi

# Verifica se o pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "ERRO: pip3 não encontrado. Instale o pip primeiro."
    exit 1
fi

echo "1. Instalando dependências Python..."
pip3 install esptool bleak

echo
echo "2. Verificando estrutura do projeto..."

# Verifica se os diretórios existem
if [ ! -d "display_node" ] || [ ! -d "voltmeter_node" ] || [ ! -d "common" ]; then
    echo "ERRO: Estrutura do projeto não encontrada!"
    echo "Certifique-se de estar no diretório raiz do projeto."
    exit 1
fi

echo "   ✓ Estrutura do projeto OK"

echo
echo "3. Download do MicroPython para ESP32..."

# Cria diretório para firmware se não existir
mkdir -p firmware

# Verifica se o firmware já existe
if [ ! -f "firmware/esp32-micropython.bin" ]; then
    echo "   Baixando firmware MicroPython..."
    # URL do firmware mais recente (ajustar conforme necessário)
    curl -o firmware/esp32-micropython.bin https://micropython.org/resources/firmware/esp32-20231005-v1.21.0.bin
    
    if [ $? -eq 0 ]; then
        echo "   ✓ Firmware baixado com sucesso"
    else
        echo "   ⚠ Erro ao baixar firmware. Baixe manualmente de https://micropython.org/download/esp32/"
    fi
else
    echo "   ✓ Firmware já existe"
fi

echo
echo "4. Criando scripts de deploy..."

# Script para instalar MicroPython
cat > install_micropython.sh << 'EOF'
#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Uso: $0 <porta_serial>"
    echo "Exemplo: $0 /dev/ttyUSB0"
    exit 1
fi

PORT=$1

echo "Instalando MicroPython no ESP32 via $PORT..."
echo "AVISO: Isso apagará todo o conteúdo da flash!"
read -p "Continuar? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "1. Apagando flash..."
    esptool.py --chip esp32 --port $PORT erase_flash
    
    echo "2. Instalando MicroPython..."
    esptool.py --chip esp32 --port $PORT --baud 460800 write_flash -z 0x1000 firmware/esp32-micropython.bin
    
    echo "✓ MicroPython instalado! Você pode agora carregar o código do projeto."
else
    echo "Instalação cancelada."
fi
EOF

chmod +x install_micropython.sh

# Script para carregar código do display
cat > deploy_display.sh << 'EOF'
#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Uso: $0 <porta_serial>"
    echo "Exemplo: $0 /dev/ttyUSB0"
    exit 1
fi

PORT=$1

echo "Carregando código do Display Node via $PORT..."

# Verifica se ampy está instalado
if ! command -v ampy &> /dev/null; then
    echo "Instalando ampy..."
    pip3 install adafruit-ampy
fi

echo "1. Criando diretório /common..."
ampy --port $PORT mkdir /common 2>/dev/null || true

echo "2. Copiando arquivos comuns..."
ampy --port $PORT put common/constants.py /common/constants.py
ampy --port $PORT put common/ble_utils.py /common/ble_utils.py

echo "3. Copiando arquivos do display..."
ampy --port $PORT put display_node/display_controller.py /display_controller.py
ampy --port $PORT put display_node/ble_server.py /ble_server.py
ampy --port $PORT put display_node/main.py /main.py

echo "✓ Código do Display carregado! Reinicie o ESP32."
EOF

chmod +x deploy_display.sh

# Script para carregar código do voltímetro
cat > deploy_voltmeter.sh << 'EOF'
#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Uso: $0 <porta_serial>"
    echo "Exemplo: $0 /dev/ttyUSB0"
    exit 1
fi

PORT=$1

echo "Carregando código do Voltmeter Node via $PORT..."

# Verifica se ampy está instalado
if ! command -v ampy &> /dev/null; then
    echo "Instalando ampy..."
    pip3 install adafruit-ampy
fi

echo "1. Criando diretório /common..."
ampy --port $PORT mkdir /common 2>/dev/null || true

echo "2. Copiando arquivos comuns..."
ampy --port $PORT put common/constants.py /common/constants.py
ampy --port $PORT put common/ble_utils.py /common/ble_utils.py

echo "3. Copiando arquivos do voltímetro..."
ampy --port $PORT put voltmeter_node/adc_reader.py /adc_reader.py
ampy --port $PORT put voltmeter_node/ble_client.py /ble_client.py
ampy --port $PORT put voltmeter_node/main.py /main.py

echo "✓ Código do Voltímetro carregado! Reinicie o ESP32."
EOF

chmod +x deploy_voltmeter.sh

echo "   ✓ Scripts de deploy criados"

echo
echo "=== Configuração Concluída ==="
echo
echo "Próximos passos:"
echo
echo "1. Para instalar MicroPython:"
echo "   ./install_micropython.sh /dev/ttyUSB0"
echo
echo "2. Para carregar código do Display (ESP32 #1):"
echo "   ./deploy_display.sh /dev/ttyUSB0"
echo
echo "3. Para carregar código do Voltímetro (ESP32 #2):"
echo "   ./deploy_voltmeter.sh /dev/ttyUSB0"
echo
echo "4. Para testar comunicação BLE:"
echo "   python3 test_ble_communication.py"
echo
echo "Substitua /dev/ttyUSB0 pela porta serial correta do seu ESP32."
echo "No Linux, pode ser /dev/ttyUSB0, /dev/ttyACM0, etc."
echo "No macOS, pode ser /dev/cu.usbserial-*"
echo
echo "Para mais informações, consulte o README.md"
