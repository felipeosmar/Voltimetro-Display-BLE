"""
Script de exemplo para testar comunicação BLE com os nós ESP32
Requer: bleak library (pip install bleak)
"""

import asyncio
import struct
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
    devices = await BleakScanner.discover(timeout=10.0)
    
    esp32_devices = []
    for device in devices:
        if device.name and ("ESP32" in device.name):
            esp32_devices.append(device)
            print(f"Encontrado: {device.name} - {device.address} - RSSI: {device.rssi}")
    
    return esp32_devices

async def connect_to_display(address):
    """Conecta ao nó display e envia comandos"""
    print(f"\nConectando ao display em {address}...")
    
    async with BleakClient(address) as client:
        print(f"Conectado ao display!")
        
        # Lista serviços disponíveis
        services = await client.get_services()
        print("Serviços disponíveis:")
        for service in services:
            print(f"  {service.uuid}: {service.description}")
            for char in service.characteristics:
                print(f"    {char.uuid}: {char.description} - {char.properties}")
        
        # Testa comandos
        commands = [
            "TEST",                    # Testa displays
            "TEXT:8.8.8",             # Mostra 8.8.8
            "CLEAR",                  # Limpa
            "VOLT:1.23,4.56,7.89",   # Mostra tensões
            "TEXT:Hi!,Lo!,Go!",       # Mostra textos
        ]
        
        for command in commands:
            print(f"\nEnviando comando: {command}")
            try:
                await client.write_gatt_char(COMMAND_CHAR_UUID, command.encode('utf-8'))
                print("Comando enviado com sucesso!")
                await asyncio.sleep(3)  # Aguarda 3 segundos
            except Exception as e:
                print(f"Erro ao enviar comando: {e}")
        
        # Lê valores atuais do display
        try:
            print("\nLendo valores atuais do display...")
            data = await client.read_gatt_char(DISPLAY_CHAR_UUID)
            values = data.decode('utf-8').split(',')
            print(f"Valores nos displays: {values}")
        except Exception as e:
            print(f"Erro ao ler display: {e}")

async def connect_to_voltmeter(address):
    """Conecta ao nó voltímetro e lê tensões"""
    print(f"\nConectando ao voltímetro em {address}...")
    
    def voltage_notification_handler(sender, data):
        """Handler para notificações de tensão"""
        try:
            voltages = struct.unpack('<fff', data)
            print(f"Tensões recebidas: Canal1={voltages[0]:.3f}V, Canal2={voltages[1]:.3f}V, Canal3={voltages[2]:.3f}V")
        except Exception as e:
            print(f"Erro ao decodificar tensões: {e}")
    
    async with BleakClient(address) as client:
        print("Conectado ao voltímetro!")
        
        # Lista serviços disponíveis
        services = await client.get_services()
        print("Serviços disponíveis:")
        for service in services:
            print(f"  {service.uuid}: {service.description}")
            for char in service.characteristics:
                print(f"    {char.uuid}: {char.description} - {char.properties}")
        
        # Habilita notificações de tensão
        try:
            await client.start_notify(VOLTAGE_CHAR_UUID, voltage_notification_handler)
            print("Notificações de tensão habilitadas. Lendo por 30 segundos...")
            
            # Lê tensões por 30 segundos
            await asyncio.sleep(30)
            
            await client.stop_notify(VOLTAGE_CHAR_UUID)
            print("Notificações desabilitadas.")
            
        except Exception as e:
            print(f"Erro com notificações: {e}")
        
        # Leitura manual única
        try:
            print("\nLendo tensão manualmente...")
            data = await client.read_gatt_char(VOLTAGE_CHAR_UUID)
            voltages = struct.unpack('<fff', data)
            print(f"Leitura manual: Canal1={voltages[0]:.3f}V, Canal2={voltages[1]:.3f}V, Canal3={voltages[2]:.3f}V")
        except Exception as e:
            print(f"Erro na leitura manual: {e}")

async def send_voltages_to_display(display_address, voltages):
    """Envia tensões específicas para o display"""
    print(f"\nEnviando tensões {voltages} para o display...")
    
    async with BleakClient(display_address) as client:
        # Codifica as tensões
        data = struct.pack('<fff', voltages[0], voltages[1], voltages[2])
        
        try:
            await client.write_gatt_char(VOLTAGE_CHAR_UUID, data)
            print("Tensões enviadas com sucesso!")
        except Exception as e:
            print(f"Erro ao enviar tensões: {e}")

async def main():
    """Função principal"""
    print("=== Teste de Comunicação BLE com ESP32 ===\n")
    
    # Escaneia dispositivos
    devices = await scan_devices()
    
    if not devices:
        print("Nenhum dispositivo ESP32 encontrado!")
        return
    
    # Separa displays e voltímetros
    displays = [d for d in devices if DISPLAY_NAME in str(d.name)]
    voltmeters = [d for d in devices if VOLTMETER_NAME in str(d.name)]
    
    print(f"\nEncontrados: {len(displays)} display(s), {len(voltmeters)} voltímetro(s)")
    
    # Menu de opções
    while True:
        print("\n=== MENU ===")
        print("1. Testar Display")
        print("2. Testar Voltímetro")
        print("3. Enviar tensões para Display")
        print("4. Re-escanear dispositivos")
        print("0. Sair")
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            if displays:
                await connect_to_display(displays[0].address)
            else:
                print("Nenhum display encontrado!")
        elif choice == "2":
            if voltmeters:
                await connect_to_voltmeter(voltmeters[0].address)
            else:
                print("Nenhum voltímetro encontrado!")
        elif choice == "3":
            if displays:
                try:
                    v1 = float(input("Tensão canal 1 (V): "))
                    v2 = float(input("Tensão canal 2 (V): "))
                    v3 = float(input("Tensão canal 3 (V): "))
                    await send_voltages_to_display(displays[0].address, [v1, v2, v3])
                except ValueError:
                    print("Valores inválidos!")
            else:
                print("Nenhum display encontrado!")
        elif choice == "4":
            devices = await scan_devices()
            displays = [d for d in devices if DISPLAY_NAME in str(d.name)]
            voltmeters = [d for d in devices if VOLTMETER_NAME in str(d.name)]
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário.")
    except Exception as e:
        print(f"Erro: {e}")
