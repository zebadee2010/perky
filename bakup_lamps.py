import RPi.GPIO as control
import time
import os
from os import path
from time import localtime, strftime
import Adafruit_CharLCD as LCD
import Adafruit_BMP.BMP085 as BMP085


os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

#Define variables
sensor = BMP085.BMP085()
lcd = LCD.Adafruit_CharLCDPlate()
temp1 = '/sys/bus/w1/devices/28-000008014a4b/w1_slave'  #outside temp
temp2 = '/sys/bus/w1/devices/28-00000801e4f4/w1_slave'  #doghouse temp
s1_fault = 26 #sensor1_fault unable to read
s2_fault = 19 #sensor2_fault unable to read
l1_off = 20 #lamp1 off indicator
l1_on = 21 #lamp1 on indicator
l2_off = 12 #lamp2 off indicator
l2_on = 25 #lamp2 on indicator
r1 = 5 #relay for lamp1
r2 = 6 #relay for lamp2

#set pin modes
control.setmode(control.BCM)
control.setup(s1_fault, control.OUT)
control.setup(s2_fault, control.OUT)
control.setup(l1_off, control.OUT)
control.setup(l1_on, control.OUT)
control.setup(l2_off, control.OUT)
control.setup(l2_on, control.OUT)
control.setup(r1, control.OUT)
control.setup(r2, control.OUT)

def read_outside():
	temp = open(temp1)
	text = temp.read()
	temp.close()
	data = text.split("\n")[1].split(" ")[9]
	outside = int(data[2:])
	return outside

def read_house():
	temp = open(temp2)
	text = temp.read()
	temp.close()
	data = text.split("\n")[1].split(" ")[9]
	housetemp = int(data[2:])
	return housetemp

def lamps_off():
	control.output(r1, False)
	control.output(r2, False)
	control.output(l1_on, False)
	control.output(l2_on, False)
	control.output(l1_off, True)
	control.output(l2_off, True)
	lcd.set_color(0,0,0)

def lamp1_only():
	control.output(r1, True)
	control.output(r2, False)
	control.output(l1_on, True)
	control.output(l2_on, False)
	control.output(l1_off, False)
	control.output(l2_off, True)
	lcd.set_color(0,1,1)

def both_lamps():
	control.output(r1, True)
	control.output(r2, True)
	control.output(l1_on, True)
	control.output(l2_on, True)
	control.output(l1_off, False)
	control.output(l2_off, False)
	lcd.set_color(0,0,1)

def outside_fault():
	control.output(s1_fault, True)
	lcd.set_color(1,1,0)
	os.system("modprobe -r w1-gpio")
	os.system("modprobe -r w1-therm")

def house_fault():
	control.output(s2_fault, True)
	lcd.set_color(1,1,0)
	os.system("modprobe -r w1-gpio")
	os.system("modprobe -r w1-therm")

def curtime():
	time = strftime("%H", localtime())
	return time

while True:
	while os.path.isfile(temp1):
		while os.path.isfile(temp2):
			while  6 <= int(curtime()) <= 19:
			#while True:
				out = (read_outside() / 1000) * 9 / 5 + 32
				dog = (read_house() / 1000) * 9 / 5 + 32
				inside = sensor.read_temperature() * 9 / 5 + 32
				lcd.clear()
				lcd.message("In: %.0fF Out: %.0fF \nDog: %.0fF" % (inside,out,dog))
				
				if read_outside() >= 18500:
					lamps_off()
				elif read_house() >= 16500:
					lamps_off()
			
				if 5000 <= read_outside() <= 15000:  #Between 41 and 59 outside 
					lamp1_only()
			
				if read_outside() <= 5100:	#Below 41 outside
					both_lamps()
				elif read_house() <= 10000:	#Below 50 in the doghouse
					both_lamps()

				time.sleep(1800)
			else:
				lamps_off()
		else: 
			house_fault()
	else:
		outside_fault()
else:
	control.cleanup()
