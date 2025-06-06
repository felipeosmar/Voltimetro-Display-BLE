"""
Script de exemplo para testar comunicação BLE com os nós ESP32
Requer: bleak library (pip install bleak)
"""

import asyncio
import struct
import sys
from bleak import BleakClient, BleakScanner

# UUIDs dos serviços e características
DISPLAY_SERVICE_UUID = "12345678-1234-1234-1234-123456789abc"
VOLTMETER_SERVICE_UUID = "87654321-4321-4321-4321-cba987654321"
DISPLAY_CHAR_UUID = "12345678-1234-1234-1234-123456789abd"
VOLTAGE_CHAR_UUID = "87654321-4321-4321-4321-cba987654322"
COMMAND_CHAR_UUID = "11111111-1111-1111-1111-111111111111"

# Nomes dos dispositivos
DISPLAY_NAME = "ESP32_Display"
VOLTMETER_NAME = "ESP32_Voltmeter"

async def scan_devices():
    """Escaneia dispositivos BLE disponíveis"""
    print("Escaneando dispositivos BLE...")
    print("(Aguarde até 15 segundos...)")
    
    try:
        # Aumenta timeout e tenta múltiplas vezes
        devices = await BleakScanner.discover(timeout=15.0, return_adv=True)
        
        print(f"\nTotal de dispositivos encontrados: {len(devices)}")
        
        esp32_devices = []
        all_devices = []
        
        for address, (device, adv_data) in devices.items():
            # Coleta informações do dispositivo
            name = device.name or adv_data.local_name or "Sem nome"
            rssi = adv_data.rssi if hasattr(adv_data, 'rssi') else "N/A"
            
            all_devices.append({
                'address': address,
                'name': name,
                'rssi': rssi,
                'device': device
            })
            
            # Verifica se é um ESP32
            if any(keyword in name.upper() for keyword in ["ESP32", "DISPLAY", "VOLTMETER"]):
                esp32_devices.append({
                    'address': address,
                    'name': name,
                    'rssi': rssi,
                    'device': device
                })
                print(f"ESP32 encontrado: {name} - {address} - RSSI: {rssi}")
        
        # Se não encontrou ESP32s, mostra todos os dispositivos para debug
        if not esp32_devices:
            print("\nNenhum ESP32 encontrado. Todos os dispositivos detectados:")
            for dev in sorted(all_devices, key=lambda x: x['name']):
                print(f"  {dev['name']} - {dev['address']} - RSSI: {dev['rssi']}")
            
            print(f"\nProcurando por nomes contendo: {DISPLAY_NAME}, {VOLTMETER_NAME}")
            print("Dica: Verifique se os ESP32s estão ligados e em modo advertising")
        
        return esp32_devices
        
    except Exception as e:
        print(f"Erro durante scan: {e}")
        return []

async def scan_by_service():
    """Escaneia dispositivos por UUID de serviço"""
    print("\nTentando scan por UUID de serviço...")
    
    try:
        # Scanner focado nos UUIDs dos nossos serviços
        devices = await BleakScanner.discover(
            timeout=10.0,
            service_uuids=[DISPLAY_SERVICE_UUID, VOLTMETER_SERVICE_UUID]
        )
        
        found_devices = []
        for device in devices:
            name = device.name or "Sem nome"
            found_devices.append({
                'address': device.address,
                'name': name,
                'rssi': getattr(device, 'rssi', 'N/A'),
                'device': device
            })
            print(f"Dispositivo com serviço: {name} - {device.address}")
        
        return found_devices
        
    except Exception as e:
        print(f"Erro no scan por serviço: {e}")
        return []

async def connect_to_display(address):
    """Conecta ao nó display e envia comandos"""
    print(f"\nTentando conectar ao display em {address}...")
    
    try:
        async with BleakClient(address, timeout=20.0) as client:
            print(f"Conectado ao display!")
            
            # Verifica se está realmente conectado
            if not client.is_connected:
                print("Erro: Não foi possível estabelecer conexão!")
                return
            
            # Lista serviços disponíveis
            print("Listando serviços...")
            try:
                services = await client.get_services()
                print("Serviços disponíveis:")
                for service in services:
                    print(f"  Serviço: {service.uuid}")
                    for char in service.characteristics:
                        print(f"    Característica: {char.uuid} - Propriedades: {char.properties}")
            except Exception as e:
                print(f"Erro ao listar serviços: {e}")
            
            # Testa comandos básicos
            commands = [
                ("TEST", "Teste dos displays"),
                ("TEXT:8888,8888,8888", "Mostra 8888 em todos displays"),
                ("CLEAR", "Limpa displays"),
                ("VOLT:1.23,4.56,7.89", "Mostra tensões de teste"),
                ("TEXT:Hi! ,Lo! ,Go! ", "Mostra textos curtos"),
                ("NUM:0001,0002,0003", "Mostra números formatados")
            ]
            
            for command, description in commands:
                print(f"\n{description}...")
                print(f"Enviando: {command}")
                try:
                    await client.write_gatt_char(COMMAND_CHAR_UUID, command.encode('utf-8'))
                    print("✓ Comando enviado com sucesso!")
                    await asyncio.sleep(3)  # Aguarda 3 segundos para ver o resultado
                except Exception as e:
                    print(f"✗ Erro ao enviar comando: {e}")
            
            # Tenta ler valores atuais do display
            try:
                print("\nLendo valores atuais do display...")
                data = await client.read_gatt_char(DISPLAY_CHAR_UUID)
                if data:
                    try:
                        values = data.decode('utf-8').split(',')
                        print(f"Valores nos displays: {values}")
                    except:
                        print(f"Dados brutos recebidos: {data}")
                else:
                    print("Nenhum dado recebido")
            except Exception as e:
                print(f"Erro ao ler display: {e}")
                
    except Exception as e:
        print(f"Erro de conexão: {e}")

async def connect_to_voltmeter(address):
    """Conecta ao nó voltímetro e lê tensões"""
    print(f"\nTentando conectar ao voltímetro em {address}...")
    
    def voltage_notification_handler(sender, data):
        """Handler para notificações de tensão"""
        try:
            if len(data) >= 12:  # 3 floats * 4 bytes
                voltages = struct.unpack('<fff', data[:12])
                print(f"📊 Tensões: Canal1={voltages[0]:.3f}V, Canal2={voltages[1]:.3f}V, Canal3={voltages[2]:.3f}V")
            else:
                print(f"Dados de tensão inválidos (tamanho: {len(data)}): {data}")
        except Exception as e:
            print(f"Erro ao decodificar tensões: {e}")
    
    try:
        async with BleakClient(address, timeout=20.0) as client:
            print("Conectado ao voltímetro!")
            
            # Verifica conexão
            if not client.is_connected:
                print("Erro: Não foi possível estabelecer conexão!")
                return
            
            # Lista serviços disponíveis
            try:
                services = await client.get_services()
                print("Serviços disponíveis:")
                for service in services:
                    print(f"  Serviço: {service.uuid}")
                    for char in service.characteristics:
                        print(f"    Característica: {char.uuid} - Propriedades: {char.properties}")
            except Exception as e:
                print(f"Erro ao listar serviços: {e}")
            
            # Tenta habilitar notificações
            try:
                print("\nTentando habilitar notificações de tensão...")
                await client.start_notify(VOLTAGE_CHAR_UUID, voltage_notification_handler)
                print("✓ Notificações habilitadas. Monitorando por 20 segundos...")
                
                # Monitora por 20 segundos
                await asyncio.sleep(20)
                
                await client.stop_notify(VOLTAGE_CHAR_UUID)
                print("Notificações desabilitadas.")
                
            except Exception as e:
                print(f"Erro com notificações: {e}")
            
            # Leitura manual única
            try:
                print("\nTentando leitura manual...")
                data = await client.read_gatt_char(VOLTAGE_CHAR_UUID)
                if data and len(data) >= 12:
                    voltages = struct.unpack('<fff', data[:12])
                    print(f"📖 Leitura manual: Canal1={voltages[0]:.3f}V, Canal2={voltages[1]:.3f}V, Canal3={voltages[2]:.3f}V")
                else:
                    print(f"Dados insuficientes ou inválidos: {data}")
            except Exception as e:
                print(f"Erro na leitura manual: {e}")
                
    except Exception as e:
        print(f"Erro de conexão com voltímetro: {e}")

async def send_voltages_to_display(display_address, voltages):
    """Envia tensões específicas para o display"""
    print(f"\nEnviando tensões {voltages} para o display...")
    
    try:
        async with BleakClient(display_address, timeout=15.0) as client:
            # Codifica as tensões
            data = struct.pack('<fff', voltages[0], voltages[1], voltages[2])
            
            try:
                await client.write_gatt_char(VOLTAGE_CHAR_UUID, data)
                print("✓ Tensões enviadas com sucesso!")
                await asyncio.sleep(2)  # Aguarda para ver o resultado
            except Exception as e:
                print(f"✗ Erro ao enviar tensões: {e}")
                
    except Exception as e:
        print(f"Erro de conexão: {e}")

async def main():
    """Função principal"""
    print("=== Teste de Comunicação BLE com ESP32 ===")
    print("Versão para displays multiplexados de cátodo comum\n")
    
    # Verifica se o sistema suporta BLE
    try:
        # Teste básico de BLE
        test_devices = await BleakScanner.discover(timeout=1.0)
        print(f"Sistema BLE OK. Bluetooth detectou {len(test_devices)} dispositivos.")
    except Exception as e:
        print(f"Erro no sistema BLE: {e}")
        print("Verifique se o Bluetooth está habilitado e se você tem permissões.")
        return
    
    devices = []
    displays = []
    voltmeters = []
    
    while True:
        print("\n=== MENU ===")
        print("1. Escanear dispositivos")
        print("2. Escanear por UUID de serviço")
        print("3. Testar Display")
        print("4. Testar Voltímetro")
        print("5. Enviar tensões para Display")
        print("6. Conectar em endereço específico")
        print("0. Sair")
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == "0":
            break
            
        elif choice == "1":
            devices = await scan_devices()
            displays = [d for d in devices if DISPLAY_NAME in d['name']]
            voltmeters = [d for d in devices if VOLTMETER_NAME in d['name']]
            print(f"\nResultado: {len(displays)} display(s), {len(voltmeters)} voltímetro(s)")
            
        elif choice == "2":
            service_devices = await scan_by_service()
            if service_devices:
                devices.extend(service_devices)
                displays = [d for d in devices if DISPLAY_NAME in d['name']]
                voltmeters = [d for d in devices if VOLTMETER_NAME in d['name']]
            
        elif choice == "3":
            if displays:
                await connect_to_display(displays[0]['address'])
            else:
                print("❌ Nenhum display encontrado! Execute o scan primeiro.")
                
        elif choice == "4":
            if voltmeters:
                await connect_to_voltmeter(voltmeters[0]['address'])
            else:
                print("❌ Nenhum voltímetro encontrado! Execute o scan primeiro.")
                
        elif choice == "5":
            if displays:
                try:
                    v1 = float(input("Tensão canal 1 (V): "))
                    v2 = float(input("Tensão canal 2 (V): "))
                    v3 = float(input("Tensão canal 3 (V): "))
                    await send_voltages_to_display(displays[0]['address'], [v1, v2, v3])
                except ValueError:
                    print("❌ Valores inválidos!")
            else:
                print("❌ Nenhum display encontrado!")
                
        elif choice == "6":
            address = input("Digite o endereço MAC (ex: AA:BB:CC:DD:EE:FF): ").strip()
            if address:
                device_type = input("É um (d)isplay ou (v)oltímetro? ").strip().lower()
                if device_type.startswith('d'):
                    await connect_to_display(address)
                elif device_type.startswith('v'):
                    await connect_to_voltmeter(address)
                else:
                    print("Tipo inválido!")
        else:
            print("❌ Opção inválida!")

if __name__ == "__main__":
    try:
        # Verifica se bleak está instalado
        import bleak
        try:
            version = getattr(bleak, '__version__', 'versão desconhecida')
            print(f"Usando bleak versão: {version}")
        except:
            print("Biblioteca bleak carregada com sucesso")
    except ImportError:
        print("❌ Biblioteca 'bleak' não encontrada!")
        print("Instale com: pip install bleak")
        sys.exit(1)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Interrompido pelo usuário.")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
