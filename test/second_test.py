import serial

ser = serial.Serial("COM4", timeout=1)
ser.setDTR(False)

def send(code):
    """test"""
    ser.write(code.encode("utf-8"))
while True:
    send(input('Votre nombre'))

