#!/usr/bin/env python

import RPi.GPIO as GPIO
from time import sleep
import logging
import os
import serial

logging.basicConfig(filename='/home/hmd82/parking/call.log', encoding='utf-8', level=logging.DEBUG)
phoneOn = {}
phoneAdmin = {}
latchStatus = False
fileOnPath = "/home/hmd82/parking/phoneOn.txt"
fileAdminPath = "/home/hmd82/parking/phoneAdmin.txt"
port = "/dev/ttyS0" 

def openGate():
    GPIO.output(7, True)
    sleep(1)
    GPIO.output(7, False)
    logging.debug("Gate open")

def latchGate():
    openGate()
    sleep(1)
    GPIO.output(37, True)
    sleep(1)
    GPIO.output(37, False)
    logging.debug("Gate open and looking for latch")

def releaseGate():
    global latchStatus
    if latchStatus == False:
        if GPIO.input(38) == False:
            logging.debug("Latch input received False")
            sleep(3)
            GPIO.output(36, True)
            latchStatus = True
            logging.debug("Gate latched")
    else:
        if GPIO.input(38) ==True:
            logging.debug("Latch input received True")
            sleep(3)
            GPIO.output(36, False)
            latchStatus = False
            logging.debug("Gate Released")

def loadAdminPhone():
    with open(fileAdminPath) as myfile:
        for line in myfile:
            phone,name = line.partition(" ")[::2]
            phoneAdmin[str(name).lower().strip()] = phone
            logging.info('Admin Name %s: %s',name.strip(),phone)

def loadOnPhone():
    with open(fileOnPath) as myfile:
        for line in myfile:
            phone, name = line.partition(" ")[::2]
            phoneOn[str(name).lower().strip()] = phone
            logging.info('On Name %s: %s',name.strip(),phone)

def readGSMline():
    s=gsm.readline()
    logging.debug(s);
    return s.decode()

def writeGSM(strValue):
    strcommand = "%s\r\n"%(strValue)
    gsm.write(strcommand.encode())
    logging.debug("GSM Wrote:%s",strValue)

def checkGSMready():
    while True:
        writeGSM("AT+CPIN?")
        if readGSMline().find("+CPIN: READY")>-1:
            return True

def setupGSM():
    logging.info('GSM Setting up')
    global gsm 
    gsm = serial.Serial(port,baudrate=115200,timeout=10)
    while True:
        checkGSMready()
        writeGSM("AT+CLIP=1")
        if readGSMline() != "OK":
            logging.info('GSM ready')
            return

def checkAdmin(phone):
    for key in phoneAdmin:
        if phone.find(phoneAdmin[key])>-1:
            logging.info("Latching Gate for %s with number %s",key,phoneAdmin[key])
            latchGate()

def checkOnPhone(phone):
    for key in phoneOn:
        if phone.find(phoneOn[key])>-1:
            logging.info("Opening Gate for %s with number %s",key,phoneOn[key])
            openGate()

def disconnectCall():
    writeGSM("ATH")

def setup():
    setupGSM()
    logging.info('GPIO Setting up')
    GPIO.setmode(GPIO.BOARD) 
    GPIO.setup(7,GPIO.OUT)  #GPIO04 Trigger
    GPIO.setup(36,GPIO.OUT) #GPIO16 Latch Release
    GPIO.setup(37,GPIO.OUT) #GPIO26 latch
    GPIO.setup(38,GPIO.IN)  #GPIO20 input
    logging.info('Setting up Admin Phone')
    loadAdminPhone()
    logging.info('Setting up On Phone')
    loadOnPhone()

def loop():
    s= readGSMline()
    if s.startswith("+CLIP:") == True:
        s=s[8:]
        s=s[:s.find("\"")]
        logging.debug("Phone call received from:%s",s)
        checkAdmin(s)
        checkOnPhone(s)
        disconnectCall()
    releaseGate()

if __name__ == "__main__":
    try:
        logging.info('Started Call Parking Application')
        setup()
        while True:
            loop()
        logging.info('Exit Call Parking Application')    
    except Exception as e: 
        logging.error('***: '+ str(e))
    finally:
        GPIO.cleanup()