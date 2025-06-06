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
ampy --port $PORT put voltmeter_node/ble_voltmeter_server.py /ble_voltmeter_server.py

echo "✓ Código do Voltímetro carregado! Reinicie o ESP32."
