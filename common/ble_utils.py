try:
    import bluetooth
except ImportError:
    # Para ambiente de desenvolvimento
    pass

import time
import struct

# Constantes IRQ para BLE - valores do MicroPython
_IRQ_CENTRAL_CONNECT = 1
_IRQ_CENTRAL_DISCONNECT = 2
_IRQ_GATTS_WRITE = 3
_IRQ_GATTS_READ_REQUEST = 4
_IRQ_SCAN_RESULT = 5
_IRQ_SCAN_DONE = 6
_IRQ_PERIPHERAL_CONNECT = 7
_IRQ_PERIPHERAL_DISCONNECT = 8
_IRQ_GATTC_SERVICE_RESULT = 9
_IRQ_GATTC_SERVICE_DONE = 10
_IRQ_GATTC_CHARACTERISTIC_RESULT = 11
_IRQ_GATTC_CHARACTERISTIC_DONE = 12
_IRQ_GATTC_DESCRIPTOR_RESULT = 13
_IRQ_GATTC_DESCRIPTOR_DONE = 14
_IRQ_GATTC_READ_RESULT = 15
_IRQ_GATTC_READ_DONE = 16
_IRQ_GATTC_WRITE_DONE = 17
_IRQ_GATTC_NOTIFY = 18

class BLEUtils:
    @staticmethod
    def encode_voltage_data(voltages):
        """Codifica dados de tensão para transmissão BLE"""
        # Formato: 3 floats de 32 bits cada
        return struct.pack('<fff', voltages[0], voltages[1], voltages[2])
    
    @staticmethod
    def decode_voltage_data(data):
        """Decodifica dados de tensão recebidos via BLE"""
        try:
            return struct.unpack('<fff', data)
        except:
            return (0.0, 0.0, 0.0)
    
    @staticmethod
    def encode_display_data(display_values):
        """Codifica dados do display para transmissão BLE"""
        # Formato: string com valores separados por vírgula
        return ','.join(str(v) for v in display_values).encode('utf-8')
    
    @staticmethod
    def decode_display_data(data):
        """Decodifica dados do display recebidos via BLE"""
        try:
            text = data.decode('utf-8')
            return text.split(',')
        except:
            return ['', '', '']
    
    @staticmethod
    def format_voltage(voltage):
        """Formata tensão para exibição no display"""
        return f"{voltage:.2f}"
    
    @staticmethod
    def advertising_payload(limited_disc=False, br_edr=False, name=None, services=None, appearance=0):
        """Cria payload de advertising BLE"""
        payload = bytearray()
        
        def _append(adv_type, value):
            nonlocal payload
            payload += struct.pack("BB", len(value) + 1, adv_type) + value
        
        _append(
            0x01,
            struct.pack("B", (0x01 if limited_disc else 0x02) + (0x00 if br_edr else 0x04))
        )
        
        if name:
            _append(0x09, name.encode())
        
        if services:
            for uuid in services:
                b = bytes(uuid)
                if len(b) == 2:
                    _append(0x03, b)
                elif len(b) == 4:
                    _append(0x05, b)
                elif len(b) == 16:
                    _append(0x07, b)
        
        if appearance:
            _append(0x19, struct.pack("<h", appearance))
        
        return payload

def print_debug(message):
    """Função para debug com timestamp"""
    print(f"[{time.time()}] {message}")
