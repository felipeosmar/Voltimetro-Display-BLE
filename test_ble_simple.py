#!/usr/bin/env python3
"""
Script simples para testar descoberta BLE dos dispositivos ESP32
"""

import asyncio
import sys
from bleak import BleakScanner

async def scan_devices():
    """Escaneia dispositivos BLE próximos"""
    print("Iniciando scan BLE...")
    print("Procurando por dispositivos ESP32...")
    
    try:
        # Scan por 10 segundos
        devices = await BleakScanner.discover(timeout=10.0)
        
        print(f"\nDispositivos encontrados: {len(devices)}")
        print("-" * 50)
        
        esp32_devices = []
        
        for device in devices:
            name = device.name or "Nome não disponível"
            address = device.address
            rssi = getattr(device, 'rssi', 'N/A')
            
            print(f"Nome: {name}")
            print(f"Endereço: {address}")
            print(f"RSSI: {rssi} dBm")
            print("-" * 30)
            
            # Verifica se é um ESP32
            if "ESP32" in name:
                esp32_devices.append((name, address, rssi))
        
        print(f"\nDispositivos ESP32 encontrados: {len(esp32_devices)}")
        
        if esp32_devices:
            print("\nESP32 Dispositivos:")
            for name, addr, rssi in esp32_devices:
                print(f"  - {name} ({addr}) RSSI: {rssi} dBm")
        else:
            print("\nNenhum dispositivo ESP32 encontrado!")
            print("\nVerifique se:")
            print("1. Os ESP32 estão ligados")
            print("2. O código está rodando nos ESP32")
            print("3. O Bluetooth está ativo nos ESP32")
            print("4. Não há erros de inicialização")
            
    except Exception as e:
        print(f"Erro durante o scan: {e}")

def main():
    """Função principal"""
    print("=== Teste Simples de Descoberta BLE ===")
    print("Este script procura por dispositivos ESP32 na rede BLE")
    print()
    
    try:
        asyncio.run(scan_devices())
    except KeyboardInterrupt:
        print("\nScan interrompido pelo usuário")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()
