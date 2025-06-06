#!/usr/bin/env python3
"""
Diagnóstico avançado dos arquivos ESP32 para identificar problemas BLE
"""

import os
import sys
import re

def check_file_exists(filepath):
    """Verifica se o arquivo existe"""
    return os.path.exists(filepath)

def check_imports(filepath):
    """Verifica importações em um arquivo Python"""
    problems = []
    
    if not check_file_exists(filepath):
        return [f"Arquivo não encontrado: {filepath}"]
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Determina o tipo de arquivo baseado no caminho
        is_main_file = filepath.endswith('/main.py')
        is_common_file = '/common/' in filepath
        is_ble_module = any(x in filepath for x in ['ble_server.py', 'ble_client.py', 'ble_voltmeter_server.py'])
        
        # Verifica imports de bluetooth (apenas relevante para módulos BLE e common)
        if is_ble_module or is_common_file:
            if 'import bluetooth' in content:
                print(f"✓ {filepath}: Import bluetooth encontrado")
            else:
                problems.append(f"Import bluetooth não encontrado em {filepath}")
        elif is_main_file:
            # main.py files não precisam importar bluetooth diretamente
            print(f"✓ {filepath}: Main file (import bluetooth via módulos BLE)")
        
        # Verifica se há conflitos de importação
        if 'from ble_server import' in content and 'from ble_client import' in content:
            problems.append(f"Possível conflito: {filepath} importa tanto server quanto client")
        
        # Verifica sys.path.append (apenas relevante para arquivos que não são common)
        if not is_common_file:
            if "sys.path.append('/common')" in content:
                print(f"✓ {filepath}: Caminho common configurado")
            else:
                problems.append(f"Caminho common não configurado em {filepath}")
        else:
            # Arquivos common não precisam configurar sys.path para si mesmos
            print(f"✓ {filepath}: Arquivo common (não precisa de sys.path)")
            
    except Exception as e:
        problems.append(f"Erro ao ler {filepath}: {e}")
    
    return problems

def check_ble_configuration():
    """Verifica configuração BLE nos arquivos"""
    print("=== Verificando Configuração BLE ===")
    
    # Arquivos para verificar
    files_to_check = [
        '/home/felipe/work/display7segBluetooth/projeto/display_node/main.py',
        '/home/felipe/work/display7segBluetooth/projeto/display_node/ble_server.py',
        '/home/felipe/work/display7segBluetooth/projeto/voltmeter_node/main.py',
        '/home/felipe/work/display7segBluetooth/projeto/voltmeter_node/ble_client.py',
        '/home/felipe/work/display7segBluetooth/projeto/voltmeter_node/ble_voltmeter_server.py',
        '/home/felipe/work/display7segBluetooth/projeto/common/constants.py',
        '/home/felipe/work/display7segBluetooth/projeto/common/ble_utils.py'
    ]
    
    all_problems = []
    
    for filepath in files_to_check:
        problems = check_imports(filepath)
        all_problems.extend(problems)
    
    return all_problems

def check_ble_names_and_uuids():
    """Verifica nomes e UUIDs BLE"""
    print("\n=== Verificando Nomes e UUIDs BLE ===")
    
    constants_file = '/home/felipe/work/display7segBluetooth/projeto/common/constants.py'
    problems = []
    
    if check_file_exists(constants_file):
        try:
            with open(constants_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verifica nomes BLE
            if 'BLE_NAME_DISPLAY = "ESP32_Display"' in content:
                print("✓ Nome do Display configurado: ESP32_Display")
            else:
                problems.append("Nome do Display não encontrado ou incorreto")
            
            if 'BLE_NAME_VOLTMETER = "ESP32_Voltmeter"' in content:
                print("✓ Nome do Voltímetro configurado: ESP32_Voltmeter")
            else:
                problems.append("Nome do Voltímetro não encontrado ou incorreto")
            
            # Verifica UUIDs
            uuid_pattern = r'bluetooth\.UUID\([\'"]([0-9a-f-]+)[\'"]\)'
            uuids = re.findall(uuid_pattern, content, re.IGNORECASE)
            
            if len(uuids) >= 3:
                print(f"✓ UUIDs encontrados: {len(uuids)}")
                for i, uuid in enumerate(uuids):
                    print(f"  - UUID {i+1}: {uuid}")
            else:
                problems.append(f"UUIDs insuficientes encontrados: {len(uuids)}")
                
        except Exception as e:
            problems.append(f"Erro ao verificar constants.py: {e}")
    else:
        problems.append("Arquivo constants.py não encontrado")
    
    return problems

def check_advertising_logic():
    """Verifica lógica de advertising"""
    print("\n=== Verificando Lógica de Advertising ===")
    
    problems = []
    
    # Verifica servidor do display
    display_server = '/home/felipe/work/display7segBluetooth/projeto/display_node/ble_server.py'
    if check_file_exists(display_server):
        try:
            with open(display_server, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '_start_advertising' in content:
                print("✓ Display: Método _start_advertising encontrado")
            else:
                problems.append("Display: Método _start_advertising não encontrado")
            
            if 'gap_advertise' in content:
                print("✓ Display: Chamada gap_advertise encontrada")
            else:
                problems.append("Display: Chamada gap_advertise não encontrada")
                
        except Exception as e:
            problems.append(f"Erro ao verificar ble_server.py: {e}")
    
    # Verifica servidor do voltímetro
    voltmeter_server = '/home/felipe/work/display7segBluetooth/projeto/voltmeter_node/ble_voltmeter_server.py'
    if check_file_exists(voltmeter_server):
        try:
            with open(voltmeter_server, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '_start_advertising' in content:
                print("✓ Voltímetro: Método _start_advertising encontrado")
            else:
                problems.append("Voltímetro: Método _start_advertising não encontrado")
            
            if 'gap_advertise' in content:
                print("✓ Voltímetro: Chamada gap_advertise encontrada")
            else:
                problems.append("Voltímetro: Chamada gap_advertise não encontrada")
                
        except Exception as e:
            problems.append(f"Erro ao verificar ble_voltmeter_server.py: {e}")
    
    return problems

def check_potential_conflicts():
    """Verifica conflitos potenciais"""
    print("\n=== Verificando Conflitos Potenciais ===")
    
    problems = []
    
    # Verifica se voltímetro usa cliente e servidor juntos
    voltmeter_main = '/home/felipe/work/display7segBluetooth/projeto/voltmeter_node/main.py'
    if check_file_exists(voltmeter_main):
        try:
            with open(voltmeter_main, 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_client = 'BLEVoltmeterClient' in content
            has_server = 'BLEVoltmeterServer' in content
            
            if has_client and has_server:
                problems.append("CONFLITO: Voltímetro usa cliente E servidor BLE simultaneamente")
                print("⚠️  Voltímetro tenta usar cliente e servidor BLE juntos")
            elif has_client:
                print("✓ Voltímetro: Apenas cliente BLE configurado")
            elif has_server:
                print("✓ Voltímetro: Apenas servidor BLE configurado")
            else:
                problems.append("Voltímetro: Nenhum BLE configurado")
                
        except Exception as e:
            problems.append(f"Erro ao verificar main.py do voltímetro: {e}")
    
    return problems

def main():
    """Função principal do diagnóstico"""
    print("=== DIAGNÓSTICO AVANÇADO DOS ARQUIVOS ESP32 ===")
    print("Verificando possíveis problemas na configuração BLE...\n")
    
    all_problems = []
    
    # Executa todas as verificações
    all_problems.extend(check_ble_configuration())
    all_problems.extend(check_ble_names_and_uuids())
    all_problems.extend(check_advertising_logic())
    all_problems.extend(check_potential_conflicts())
    
    # Relata resultados
    print("\n" + "="*60)
    
    if all_problems:
        print(f"❌ PROBLEMAS ENCONTRADOS ({len(all_problems)}):")
        for i, problem in enumerate(all_problems, 1):
            print(f"{i}. {problem}")
        
        print("\n💡 POSSÍVEIS SOLUÇÕES:")
        
        # Analisa problemas e sugere soluções
        conflict_problems = [p for p in all_problems if "CONFLITO" in p]
        if conflict_problems:
            print("- CONFLITO BLE: Modifique o voltímetro para usar apenas servidor BLE")
            print("  ou apenas cliente BLE, não ambos")
        
        import_problems = [p for p in all_problems if "Import" in p or "import" in p]
        if import_problems:
            print("- IMPORTS: Verifique se todos os imports estão corretos")
            print("  e se os arquivos estão no local certo")
        
        uuid_problems = [p for p in all_problems if "UUID" in p or "Nome" in p]
        if uuid_problems:
            print("- CONFIGURAÇÃO: Verifique nomes BLE e UUIDs em constants.py")
        
    else:
        print("✅ NENHUM PROBLEMA ENCONTRADO NA CONFIGURAÇÃO!")
        print("\nSe os ESP32s ainda não aparecem no scan, verifique:")
        print("1. Se os ESP32s estão realmente executando o código")
        print("2. Se há erros de runtime nos ESP32s")
        print("3. Se o módulo bluetooth está funcionando no hardware")

if __name__ == "__main__":
    main()
