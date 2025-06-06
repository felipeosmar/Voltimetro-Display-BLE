#!/bin/bash
# filepath: /home/felipe/work/display7segBluetooth/projeto/deploy_no_advertising.sh

echo "=== Deploy da Solução No-Advertising ==="

DISPLAY_PORT="/dev/ttyUSB0"
VOLTMETER_PORT="/dev/ttyUSB1"

# Função para verificar porta
check_port() {
    if [ ! -e "$1" ]; then
        echo "ERRO: Porta $1 não encontrada"
        return 1
    fi
    return 0
}

# Função para upload com retry
upload_with_retry() {
    local port=$1
    local file=$2
    local target=$3
    local max_attempts=3
    
    for attempt in $(seq 1 $max_attempts); do
        echo "Tentativa $attempt de $max_attempts para $file -> $target"
        
        if mpremote connect $port cp $file :$target; then
            echo "✓ Upload de $file para $target bem-sucedido"
            return 0
        else
            echo "✗ Falha no upload (tentativa $attempt)"
            sleep 2
        fi
    done
    
    echo "✗ ERRO: Falha no upload de $file após $max_attempts tentativas"
    return 1
}

# Deploy para Display Node
echo ""
echo "1. DEPLOY DISPLAY NODE (No Advertising)"
echo "----------------------------------------"

if check_port $DISPLAY_PORT; then
    echo "Uploading arquivos para Display Node..."
    
    # Upload da solução no-advertising
    upload_with_retry $DISPLAY_PORT ble_server_no_advertising.py /ble_server_no_advertising.py
    upload_with_retry $DISPLAY_PORT display_node/main_no_advertising.py /display_node/main_no_advertising.py
    
    # Upload de arquivos base necessários
    upload_with_retry $DISPLAY_PORT display_node/display_controller.py /display_node/display_controller.py
    upload_with_retry $DISPLAY_PORT common/constants.py /common/constants.py
    upload_with_retry $DISPLAY_PORT common/ble_utils.py /common/ble_utils.py
    
    echo ""
    echo "Testando Display Node (No Advertising)..."
    echo "Conectando e executando main_no_advertising.py..."
    
    # Executa teste
    timeout 10 mpremote connect $DISPLAY_PORT exec "
import sys
sys.path.append('/display_node')
try:
    from main_no_advertising import main
    print('Módulo importado com sucesso')
    # Não executa main() para não travar o script
    print('Display Node No-Advertising pronto!')
except Exception as e:
    print(f'Erro na importação: {e}')
" || echo "Timeout no teste (normal para servidor BLE)"
    
else
    echo "Display Node não encontrado em $DISPLAY_PORT"
fi

# Deploy para Voltmeter Node
echo ""
echo "2. DEPLOY VOLTMETER NODE (No Advertising)"
echo "------------------------------------------"

if check_port $VOLTMETER_PORT; then
    echo "Uploading arquivos para Voltmeter Node..."
    
    # Upload da solução no-advertising
    upload_with_retry $VOLTMETER_PORT ble_server_no_advertising.py /ble_server_no_advertising.py
    upload_with_retry $VOLTMETER_PORT voltmeter_node/main_no_advertising.py /voltmeter_node/main_no_advertising.py
    
    # Upload de arquivos base necessários
    upload_with_retry $VOLTMETER_PORT voltmeter_node/adc_reader.py /voltmeter_node/adc_reader.py
    upload_with_retry $VOLTMETER_PORT voltmeter_node/ble_client.py /voltmeter_node/ble_client.py
    upload_with_retry $VOLTMETER_PORT common/constants.py /common/constants.py
    upload_with_retry $VOLTMETER_PORT common/ble_utils.py /common/ble_utils.py
    
    echo ""
    echo "Testando Voltmeter Node (No Advertising)..."
    echo "Conectando e testando ADC..."
    
    # Executa teste básico de ADC
    timeout 10 mpremote connect $VOLTMETER_PORT exec "
import sys
sys.path.append('/voltmeter_node')
try:
    from adc_reader import ADCReader
    adc = ADCReader()
    v1 = adc.read_voltage_1()
    v2 = adc.read_voltage_2()
    v3 = adc.read_voltage_3()
    print(f'ADC Teste: V1={v1:.2f}V V2={v2:.2f}V V3={v3:.2f}V')
    print('Voltmeter Node ADC funcionando!')
except Exception as e:
    print(f'Erro no teste ADC: {e}')
"
    
else
    echo "Voltmeter Node não encontrado em $VOLTMETER_PORT"
fi

echo ""
echo "=== INSTRUÇÕES DE USO ==="
echo "1. Para iniciar Display Node:"
echo "   mpremote connect $DISPLAY_PORT exec 'import sys; sys.path.append(\"/display_node\"); from main_no_advertising import main; main()'"
echo ""
echo "2. Para iniciar Voltmeter Node:"
echo "   mpremote connect $VOLTMETER_PORT exec 'import sys; sys.path.append(\"/voltmeter_node\"); from main_no_advertising import main; main()'"
echo ""
echo "3. Para conectar via MAC address, execute os nodes e anote os MACs exibidos"
echo ""
echo "Deploy da solução No-Advertising concluído!"
