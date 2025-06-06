#!/bin/bash

# Deploy script para Voltmeter Node (Versão Corrigida para Erro BLE -18)
# Este script faz upload dos arquivos corrigidos e executa testes

echo "=== DEPLOY VOLTMETER NODE (VERSÃO CORRIGIDA) ==="

# Configurações
PORT=${1:-/dev/ttyUSB1}
BAUD_RATE=115200

echo "Porta: $PORT"
echo "Baud Rate: $BAUD_RATE"

# Verifica se a porta existe
if [ ! -e "$PORT" ]; then
    echo "❌ Erro: Porta $PORT não encontrada"
    echo "Portas disponíveis:"
    ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || echo "Nenhuma porta encontrada"
    exit 1
fi

# Verifica se ampy está instalado
if ! command -v ampy &> /dev/null; then
    echo "❌ ampy não encontrado. Instalando..."
    pip install adafruit-ampy
fi

echo ""
echo "📂 Fazendo upload dos arquivos corrigidos..."

# Upload dos arquivos comuns
echo "1. Uploading common files..."
ampy -p $PORT put common/constants.py /constants.py
ampy -p $PORT put common/ble_utils.py /ble_utils.py

# Upload dos arquivos do voltmeter node (versões corrigidas)
echo "2. Uploading voltmeter node files (FIXED versions)..."
ampy -p $PORT put voltmeter_node/ble_voltmeter_server_fixed.py /ble_voltmeter_server_fixed.py
ampy -p $PORT put voltmeter_node/adc_reader.py /adc_reader.py
ampy -p $PORT put voltmeter_node/main_fixed.py /main_fixed.py

# Upload dos arquivos de teste e correção
echo "3. Uploading test and fix files..."
ampy -p $PORT put fix_ble_error18.py /fix_ble_error18.py
ampy -p $PORT put test_ble_error18_fix.py /test_ble_error18_fix.py

echo "✓ Upload concluído"

echo ""
echo "🔧 Executando teste de correção BLE..."

# Executa teste de correção via Python
python3 -c "
import serial
import time

try:
    ser = serial.Serial('$PORT', $BAUD_RATE, timeout=10)
    time.sleep(2)
    
    print('Conectado ao ESP32. Executando teste de correção...')
    
    # Envia comando para executar teste
    ser.write(b'exec(open(\"test_ble_error18_fix.py\").read())\r\n')
    
    # Lê resposta por 30 segundos
    start_time = time.time()
    test_passed = False
    while time.time() - start_time < 30:
        if ser.in_waiting:
            response = ser.readline().decode('utf-8', errors='ignore').strip()
            if response:
                print(response)
                if 'TESTE CONCLUÍDO COM SUCESSO' in response:
                    print('✅ Teste passou!')
                    test_passed = True
                    break
                elif 'TESTE FALHOU' in response:
                    print('❌ Teste falhou!')
                    break
    
    ser.close()
    
    if test_passed:
        print('\\n🎯 Voltmeter pronto para teste de ADC...')
    
except Exception as e:
    print(f'❌ Erro no teste: {e}')
"

echo ""
echo "🧪 Testando leituras ADC..."

# Testa leituras ADC
python3 -c "
import serial
import time

try:
    ser = serial.Serial('$PORT', $BAUD_RATE, timeout=10)
    time.sleep(2)
    
    print('Testando leituras ADC...')
    
    # Envia comando para testar ADC
    ser.write(b'exec(open(\"main_fixed.py\").read()) # test\r\n')
    
    # Lê resposta do teste ADC
    start_time = time.time()
    while time.time() - start_time < 15:
        if ser.in_waiting:
            response = ser.readline().decode('utf-8', errors='ignore').strip()
            if response:
                print(response)
                if 'Teste concluído' in response:
                    print('✅ Teste ADC passou!')
                    break
    
    ser.close()
    
except Exception as e:
    print(f'❌ Erro no teste ADC: {e}')
"

echo ""
echo "🎯 Para testar manualmente:"
echo "1. Conecte com: picocom -b $BAUD_RATE $PORT"
echo "2. Execute teste BLE: exec(open('test_ble_error18_fix.py').read())"
echo "3. Execute teste ADC: exec(open('main_fixed.py').read()) # com 'test'"
echo "4. Execute calibração: exec(open('main_fixed.py').read()) # com 'calibrate'"
echo "5. Execute normal: exec(open('main_fixed.py').read())"
echo ""

# Menu de opções
echo "🚀 Escolha uma opção:"
echo "1) Executar voltmeter normal (com BLE)"
echo "2) Executar modo de teste ADC (sem BLE)"
echo "3) Executar modo de calibração"
echo "4) Sair"
echo ""

read -p "Opção (1-4): " -n 1 -r
echo

case $REPLY in
    1)
        echo "Executando voltmeter node corrigido..."
        python3 -c "
import serial
import time

try:
    ser = serial.Serial('$PORT', $BAUD_RATE, timeout=5)
    time.sleep(2)
    
    print('Iniciando voltmeter node corrigido...')
    
    # Envia comando para executar main corrigido
    ser.write(b'exec(open(\"main_fixed.py\").read())\r\n')
    
    print('Voltmeter node iniciado. Monitorando saída...')
    print('Pressione Ctrl+C para sair do monitoramento...')
    
    # Monitora saída
    try:
        while True:
            if ser.in_waiting:
                response = ser.readline().decode('utf-8', errors='ignore').strip()
                if response:
                    print(response)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print('\\nMonitoramento interrompido.')
    
    ser.close()
    
except Exception as e:
    print(f'❌ Erro: {e}')
"
        ;;
    2)
        echo "Executando modo de teste ADC..."
        python3 -c "
import serial
import time

try:
    ser = serial.Serial('$PORT', $BAUD_RATE, timeout=5)
    time.sleep(2)
    
    # Simula exec com argumento test
    ser.write(b'\\n')
    ser.write(b'import sys\\n')
    ser.write(b'sys.argv = [\"main_fixed.py\", \"test\"]\\n')
    ser.write(b'exec(open(\"main_fixed.py\").read())\\n')
    
    print('Modo de teste ADC iniciado...')
    
    # Monitora por 20 segundos
    start_time = time.time()
    while time.time() - start_time < 20:
        if ser.in_waiting:
            response = ser.readline().decode('utf-8', errors='ignore').strip()
            if response:
                print(response)
        time.sleep(0.1)
    
    ser.close()
    
except Exception as e:
    print(f'❌ Erro: {e}')
"
        ;;
    3)
        echo "Executando modo de calibração..."
        echo "⚠️  No modo de calibração, siga as instruções no terminal"
        python3 -c "
import serial
import time

try:
    ser = serial.Serial('$PORT', $BAUD_RATE, timeout=5)
    time.sleep(2)
    
    # Simula exec com argumento calibrate
    ser.write(b'\\n')
    ser.write(b'import sys\\n')
    ser.write(b'sys.argv = [\"main_fixed.py\", \"calibrate\"]\\n')
    ser.write(b'exec(open(\"main_fixed.py\").read())\\n')
    
    print('Modo de calibração iniciado...')
    print('Siga as instruções no ESP32 para calibrar cada canal')
    
    # Monitora interativamente
    try:
        while True:
            if ser.in_waiting:
                response = ser.readline().decode('utf-8', errors='ignore').strip()
                if response:
                    print(response)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print('\\nCalibração interrompida.')
    
    ser.close()
    
except Exception as e:
    print(f'❌ Erro: {e}')
"
        ;;
    4)
        echo "Saindo..."
        ;;
    *)
        echo "Opção inválida"
        ;;
esac

echo ""
echo "🎉 Deploy do Voltmeter Node (corrigido) concluído!"
echo ""
echo "📋 Próximos passos:"
echo "1. Verifique se o teste BLE passou"
echo "2. Teste as leituras ADC"
echo "3. Se tudo funcionar, o voltmeter enviará dados para o display"
echo "4. Monitore os logs para verificar a comunicação BLE"
echo ""
echo "🔧 Para execução manual:"
echo "  picocom -b $BAUD_RATE $PORT"
echo "  >>> exec(open('main_fixed.py').read())"
