#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import mfrc522
import signal
import time
import RPi.GPIO as GPIO
import LiquidCrystalPi
import time as time
from keypad import keypad
import requests


products = {
    '208.3.60.37.202': 1,
    '19.6.184.195.110': 2
}


kp = keypad()


# LCD

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
 
LCD = LiquidCrystalPi.LCD(7, 8, 35, 36, 37, 38)
 
LCD.begin(16,2)
 

def lcd_menu_initial():
    time.sleep(0.5)
    LCD.clear()
    LCD.write("Controle de")
    LCD.nextline()
    LCD.write("estoque")

def lcd_prod(prod_name):
    LCD.clear()
    LCD.write(prod_name)
    time.sleep(2)

def lcd_menu_tag():
    LCD.clear()
    LCD.write("*: Adicionar")
    LCD.nextline()
    LCD.write("#: Remover")

def lcd_menu_value():
    LCD.clear()
    LCD.write("Digite a ")
    LCD.nextline()
    LCD.write("quantidade:")

def lcd_ok():
    print ('Operação realizada com sucesso')
    LCD.clear()
    LCD.write("Registrado!")
    time.sleep(5)
    lcd_menu_initial()

def lcd_op_inv():
    print ('Operação inválida')
    LCD.clear()
    LCD.write("Operacao")
    LCD.nextline()
    LCD.write("Invalida")
    time.sleep(5)
    lcd_menu_initial()

def lcd_error():
    print ('Erro!')
    LCD.clear()
    LCD.write("Erro")
    time.sleep(5)
    lcd_menu_initial()


# Teclado

def get_val():

    digit = None
    while digit == None:
        digit = kp.getKey()

    return digit

def get_mult_val():
    time.sleep(0.5)
    val = '' 
    v = -1
    while v not in ['*', '#']:
        v = get_val()
        time.sleep(0.5)

        if v not in ['*', '#', -1]:
            val = val + str(v)
            v = -1

    return int(val)


# API

BASE_URL = 'https://despensaapi.herokuapp.com/produto/'


def request_get_prod(id):
    url = BASE_URL+str(id)
    print (url)
    r = requests.get(url)
    data = r.json()
    return data['nome']


def request_add(id, val):
    url = BASE_URL+str(id)+'/quantidade/?ind=0&qtd='+str(val)
    print (url)
    r = requests.put(url)
    return r

def request_sub(id, val):
    url = BASE_URL+str(id)+'/quantidade/?ind=1&qtd='+str(val)
    print (url)
    r = requests.put(url)
    return r



#RFID

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print ("Ctrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()


# Setup

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)
 
# Create an object of the class MFRC522
MIFAREReader = mfrc522.MFRC522()


print ("Pressione Ctrl-C para parar.")

continue_reading = True
 
while continue_reading:

    lcd_menu_initial()
    
    # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
 
    # If a card is found
    if status == MIFAREReader.MI_OK:
        print ("Cartão detectado!")

    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()
 
    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:
 
        # Print UID
        print ("UID: "+str(uid[0])+"."+str(uid[1])+"."+str(uid[2])+"."+str(uid[3])+'.'+str(uid[4]))
        
        tag = str(uid[0])+"."+str(uid[1])+"."+str(uid[2])+"."+str(uid[3])+'.'+str(uid[4])
        
        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)
        
        #Configure LED Output Pin
        LED = 18
        GPIO.setup(LED, GPIO.OUT)
        GPIO.output(LED, GPIO.LOW)


        prod_id = str(products[tag])
        prod_name = request_get_prod(prod_id)
        lcd_prod(prod_name)
        print ('Produto: ' + str(prod_name))

        #LCD.clear()
        #LCD.write(tag)
        lcd_menu_tag()
        op = get_val()

        if op == '*':
            print ('Adicionar')
            op = 0
            lcd_menu_value()
            val = get_mult_val()
            print ('Quantidade: ' + str(val))
            response = request_add(prod_id, val)
            if response.ok:
                lcd_ok()
            else:
                lcd_error()
        elif op == '#':
            print ('Remover')
            op = 1
            lcd_menu_value()
            val = get_mult_val()
            print ('Quantidade: ' + str(val))
            response = request_sub(prod_id, val)
            if response.ok:
                lcd_ok()
            else:
                lcd_error()
        else:
            lcd_op_inv()

        

        

        