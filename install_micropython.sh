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
    esptool.py --chip esp32 --port $PORT --baud 921600 write_flash -z 0x1000 firmware/esp32-micropython.bin
    
    echo "✓ MicroPython instalado! Você pode agora carregar o código do projeto."
else
    echo "Instalação cancelada."
fi
