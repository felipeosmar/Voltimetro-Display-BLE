#!/bin/bash

# Deploy script para Display Node (Versão Corrigida para Erro BLE -18)
# Este script faz upload dos arquivos corrigidos e executa testes

echo "=== DEPLOY DISPLAY NODE (VERSÃO CORRIGIDA) ==="

# Configurações
PORT=${1:-/dev/ttyUSB0}
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

# Upload dos arquivos do display node (versões corrigidas)
echo "2. Uploading display node files (FIXED versions)..."
ampy -p $PORT put display_node/ble_server_fixed.py /ble_server_fixed.py
ampy -p $PORT put display_node/display_controller.py /display_controller.py
ampy -p $PORT put display_node/main_fixed.py /main_fixed.py

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
    while time.time() - start_time < 30:
        if ser.in_waiting:
            response = ser.readline().decode('utf-8', errors='ignore').strip()
            if response:
                print(response)
                if 'TESTE CONCLUÍDO COM SUCESSO' in response:
                    print('✅ Teste passou!')
                    break
                elif 'TESTE FALHOU' in response:
                    print('❌ Teste falhou!')
                    break
    
    ser.close()
    
except Exception as e:
    print(f'❌ Erro no teste: {e}')
"

echo ""
echo "🎯 Para testar manualmente:"
echo "1. Conecte com: picocom -b $BAUD_RATE $PORT"
echo "2. Execute: exec(open('test_ble_error18_fix.py').read())"
echo "3. Se o teste passar, execute: exec(open('main_fixed.py').read())"
echo ""
echo "📊 Para modo de teste do display (sem BLE):"
echo "   exec(open('main_fixed.py').read()) # com argumento 'test' se necessário"
echo ""

# Oferece execução automática
read -p "🚀 Deseja executar o display node automaticamente? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Executando display node corrigido..."
    
    python3 -c "
import serial
import time

try:
    ser = serial.Serial('$PORT', $BAUD_RATE, timeout=5)
    time.sleep(2)
    
    print('Iniciando display node corrigido...')
    
    # Envia comando para executar main corrigido
    ser.write(b'exec(open(\"main_fixed.py\").read())\r\n')
    
    print('Display node iniciado. Use Ctrl+C para parar o monitoramento.')
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
    print('Use picocom manualmente: picocom -b $BAUD_RATE $PORT')
"
else
    echo "Para executar manualmente:"
    echo "  picocom -b $BAUD_RATE $PORT"
    echo "  >>> exec(open('main_fixed.py').read())"
fi

echo ""
echo "🎉 Deploy do Display Node (corrigido) concluído!"
echo ""
echo "📋 Próximos passos:"
echo "1. Verifique se o teste BLE passou"
echo "2. Se passou, o display está pronto para receber conexões"
echo "3. Deploy do voltmeter node com: ./deploy_voltmeter_fixed.sh"
echo "4. Teste comunicação entre os nós"
