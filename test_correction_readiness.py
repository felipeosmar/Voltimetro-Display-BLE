#!/usr/bin/env python3
"""
Script para verificar se todas as correções do erro BLE -18 estão prontas para deploy
"""

import os
import sys
import subprocess
import time

def check_file_exists(filepath, description):
    """Verifica se um arquivo existe e retorna seu tamanho"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"✓ {description}: {filepath} ({size} bytes)")
        return True
    else:
        print(f"❌ {description}: {filepath} NÃO ENCONTRADO")
        return False

def check_serial_devices():
    """Verifica dispositivos seriais disponíveis"""
    print("\n=== DISPOSITIVOS SERIAIS ===")
    devices = []
    
    for device in ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', '/dev/ttyACM1']:
        if os.path.exists(device):
            devices.append(device)
            print(f"✓ {device} disponível")
    
    if not devices:
        print("❌ Nenhum dispositivo serial encontrado")
        return []
    
    return devices

def check_ampy_installation():
    """Verifica se ampy está instalado"""
    print("\n=== VERIFICAÇÃO DO AMPY ===")
    try:
        result = subprocess.run(['ampy', '--help'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ ampy está instalado")
            return True
        else:
            print("❌ ampy não está funcionando corretamente")
            return False
    except FileNotFoundError:
        print("❌ ampy não está instalado")
        print("Execute: pip install adafruit-ampy")
        return False

def check_deploy_scripts():
    """Verifica se os scripts de deploy estão executáveis"""
    print("\n=== SCRIPTS DE DEPLOY ===")
    scripts = [
        'deploy_display_fixed.sh',
        'deploy_voltmeter_fixed.sh'
    ]
    
    all_ok = True
    for script in scripts:
        if os.path.exists(script):
            if os.access(script, os.X_OK):
                print(f"✓ {script} existe e é executável")
            else:
                print(f"⚠️  {script} existe mas não é executável")
                print(f"   Execute: chmod +x {script}")
                all_ok = False
        else:
            print(f"❌ {script} não encontrado")
            all_ok = False
    
    return all_ok

def main():
    """Função principal de verificação"""
    print("=== VERIFICAÇÃO DE PRONTIDÃO DAS CORREÇÕES BLE -18 ===")
    print("Data:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # Lista de arquivos críticos para verificar
    critical_files = [
        ('fix_ble_error18.py', 'Script principal de correção'),
        ('test_ble_error18_fix.py', 'Script de teste das correções'),
        ('display_node/ble_server_fixed.py', 'Servidor BLE corrigido do display'),
        ('display_node/main_fixed.py', 'Main corrigido do display'),
        ('voltmeter_node/ble_voltmeter_server_fixed.py', 'Servidor BLE corrigido do voltímetro'),
        ('voltmeter_node/main_fixed.py', 'Main corrigido do voltímetro'),
        ('test_system_fixed.py', 'Teste do sistema corrigido'),
        ('common/constants.py', 'Constantes do sistema'),
        ('common/ble_utils.py', 'Utilitários BLE'),
        ('CORRECAO_BLE_ERROR18.md', 'Documentação das correções')
    ]
    
    print("=== ARQUIVOS CRÍTICOS ===")
    files_ok = True
    for filepath, description in critical_files:
        if not check_file_exists(filepath, description):
            files_ok = False
    
    # Verifica dispositivos seriais
    devices = check_serial_devices()
    
    # Verifica ampy
    ampy_ok = check_ampy_installation()
    
    # Verifica scripts de deploy
    deploy_ok = check_deploy_scripts()
    
    # Resumo final
    print("\n" + "="*50)
    print("RESUMO DA VERIFICAÇÃO")
    print("="*50)
    
    if files_ok:
        print("✓ Todos os arquivos críticos estão presentes")
    else:
        print("❌ Alguns arquivos críticos estão faltando")
    
    if devices:
        print(f"✓ {len(devices)} dispositivo(s) ESP32 detectado(s): {', '.join(devices)}")
    else:
        print("❌ Nenhum dispositivo ESP32 detectado")
    
    if ampy_ok:
        print("✓ ampy está instalado e funcionando")
    else:
        print("❌ ampy precisa ser instalado/corrigido")
    
    if deploy_ok:
        print("✓ Scripts de deploy estão prontos")
    else:
        print("❌ Scripts de deploy precisam de ajustes")
    
    # Verifica se está tudo pronto
    all_ready = files_ok and bool(devices) and ampy_ok and deploy_ok
    
    print("\n" + "="*50)
    if all_ready:
        print("🎉 SISTEMA PRONTO PARA DEPLOY DAS CORREÇÕES!")
        print()
        print("Próximos passos recomendados:")
        print("1. Para deploy no display: ./deploy_display_fixed.sh /dev/ttyUSB0")
        print("2. Para deploy no voltímetro: ./deploy_voltmeter_fixed.sh /dev/ttyUSB1")
        print("3. Para teste completo: python3 test_system_fixed.py")
    else:
        print("⚠️  SISTEMA NÃO ESTÁ COMPLETAMENTE PRONTO")
        print("Corrija os problemas indicados acima antes de prosseguir")
    
    print("="*50)
    return all_ready

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nVerificação interrompida pelo usuário")
    except Exception as e:
        print(f"\nErro durante verificação: {e}")
