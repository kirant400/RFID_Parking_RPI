#!/usr/bin/env python

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import spidev
from time import sleep
import logging
import os

logging.basicConfig(filename='/home/hmd82/parking/parking.log', encoding='utf-8', level=logging.DEBUG)
rfIDs = {}
filePath = "/home/hmd82/parking/rfid.txt"

class NFC():
    def __init__(self, bus=0, device=0, spd=1000000):
        self.reader = SimpleMFRC522()
        self.close()
        self.bus = 0
        self.boards = {}
        
        self.bus = bus
        self.device = device
        self.spd = spd

    def reinit(self):
        self.reader.READER.spi = spidev.SpiDev()
        self.reader.READER.spi.open(self.bus, self.device)
        self.reader.READER.spi.max_speed_hz = self.spd
        self.reader.READER.MFRC522_Init()

    def close(self):
        self.reader.READER.spi.close()

    def addBoard(self, rid, pin):
        self.boards[rid] = pin

    def selectBoard(self, rid):
        if not rid in self.boards:
            print("readerid " + rid + " not found")
            return False

        for loop_id in self.boards:
            GPIO.output(self.boards[loop_id], loop_id == rid)
        return True

    def read(self, rid):
        if not self.selectBoard(rid):
            return None

        self.reinit()
        cid, val = self.reader.read_no_block()
        self.close()

        return cid, val

    def write(self, rid, value):
        if not self.selectBoard(rid):
            return False

        self.reinit()
        self.reader.write_no_block(value)
        self.close()
        return True
        

def loadRfids():
    with open(filePath) as myfile:
        for line in myfile:
            name, var = line.partition(" ")[::2]
            rfIDs[str(name).lower().strip()] = var
            logging.info('ID %s: %s',name.strip(),var)

def openGate():
    GPIO.output(18, True)
    sleep(1)
    GPIO.output(18, False)

def checkData(data,activity):

    if data is not None:
        data = data >>8    
        if format(data, 'x') in rfIDs:
            logging.debug('Success %s: %s:%s', activity, format(data, 'x'), rfIDs[format(data, 'x')])
            openGate()
        else:
            logging.debug('Failed %s: %s ', activity, format(data, 'x'))

if __name__ == "__main__":
    nfc = NFC()
    #GPIO.setmode(GPIO.BCM)
    GPIO.setup(18,GPIO.OUT)
    GPIO.setup(29,GPIO.OUT)
    GPIO.setup(31,GPIO.OUT)
    nfc.addBoard("entry",29)
    nfc.addBoard("exit",31)
    try:
        logging.info('Started RFID Parking')
        loadRfids()
        logging.info('Loading of RFIds completed from file %s and total %d Ids found', filePath, len(rfIDs))
        while True:
            cid, data = nfc.read("entry")
            checkData(cid,"Entry")
            sleep(1)
            cid, data = nfc.read("exit")
            checkData(cid,"Exit")
            sleep(1)
        logging.info('Exit RFID Parking')    
    except Exception as e: 
        logging.error('***: '+ str(e))
    finally:
        GPIO.cleanup()
