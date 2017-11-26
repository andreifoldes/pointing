
print("start...")
import numpy
import serial # you may need to install the pySerial :pyserial.sourceforge.net
import struct
import time
import random
import pandas
import re
import threading
from psychopy import core, visual, event, gui, data, iohub, monitors

# your Serial port could be different!
try:
	arduino = serial.Serial('COM3', 9600, timeout = 1)
except serial.SerialException:
	arduino = serial.Serial('COM5', 9600, timeout = 1)
except serial.SerialException:
	arduino = serial.Serial('COM4', 9600, timeout = 1)
except serial.SerialException:
	arduino = serial.Serial('COM1', 9600, timeout = 1)
except serial.SerialException:
	arduino = serial.Serial('COM2', 9600, timeout = 1)

time.sleep(3)

def waitForButton():
			
			while arduino.in_waiting:
				print arduino.read()
				
			arduino.write(struct.pack('>B',2)) #grant permission
			
			while True:
								
				if(arduino.inWaiting()>0):
					tmp = arduino.read()
					if tmp!= '':
						if int(tmp)==2:
							print "Button pressed"
							break
							
t1 = threading.Thread(target = waitForButton)
t1.start()

print "Press button"

t1.join()
