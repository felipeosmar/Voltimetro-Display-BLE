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
