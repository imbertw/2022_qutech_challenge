#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 29 13:57:51 2022
BB84: For the iQuHack 
@author: alejomonbar
"""
import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, execute, BasicAer
from qiskit import Aer
from qiskit.visualization import plot_histogram
#from quantuminspire.qiskit import QI

# email, pasword = "ja.montanezbarrera@ugto.mx", "YZYKHjC6I4c7hUpTyIAo"
# QI.set_authentication_details(email=email, password=pasword)
# backend = QI.get_backend('QX single-node simulator')

morse = { 'a':'.-', 'b':'-...','c':'-.-.', 'd':'-..', 'e':'.', 
         'f':'..-.', 'g':'--.', 'h':'....', 'i':'..', 'j':'.---', 'k':'-.-', 
         'l':'.-..', 'm':'--', 'n':'-.', 'o':'---', 'p':'.--.', 'q':'--.-', 
         'r':'.-.', 's':'...', 't':'-', 'u':'..-', 'v':'...-', 'w':'.--', 
         'x':'-..-', 'y':'-.--', 'z':'--..', '1':'.----', '2':'..---', '3':'...--', 
         '4':'....-', '5':'.....', '6':'-....', '7':'--...', '8':'---..', '9':'----.', 
         '0':'-----', ', ':'--..--', '.':'.-.-.-', '?':'..--..', '/':'-..-.', '-':'-....-', 
         '(':'-.--.', ')':'-.--.-'} 

backend = Aer.get_backend("aer_simulator")

def Alice(n, key=[], basis=[]):
    qr = QuantumRegister(n, name='qr')
    cr = ClassicalRegister(n, name='cr')
    
    circuit = QuantumCircuit(qr, cr, name='Alice')
    if len(key) == 0:
        key = np.binary_repr(np.random.randint(0, high=2**n) , n)
    
    for index, digit in enumerate(key):
        if digit == '1':
            circuit.x(qr[index])
    
    if len(basis) == 0:
        for index in range(n):
            if 0.5 < np.random.random():  
                circuit.h(qr[index]) 
                basis.append('X')
            else:
                basis.append('Z') 
    else:
        for index, i in enumerate(basis):
            if i == "X":
                circuit.h(qr[index])
    print('test')
    return circuit, basis, key

    print('test')

def Bob(n, basis=[]):
    qr = QuantumRegister(n, name='qr')
    cr = ClassicalRegister(n, name='cr')
    circuit = QuantumCircuit(qr, cr, name='Bob')
    
    if len(basis) == 0:
        for index in range(n):
            if 0.5 < np.random.random():  
                circuit.h(qr[index]) 
                basis.append('X')
            else:
                basis.append('Z') 
    else:
        for index, i in enumerate(basis):
            if i == "X":
                circuit.h(qr[index])
    print('test1')
    return circuit, basis 


def interface(alice_cir, bob_circ, intruder=False):
    "This is what the interface should do."
    n = alice_cir.num_qubits
    circuit = alice_cir
    if intruder: # Eve is trying to read the key?
        circuit.measure(range(n), range(n))
    circuit = circuit.compose(bob_circ)
    circuit.measure(range(n), range(n))
    result = backend.run(circuit, shots=1).result().get_counts()
    print('test2')
    return list(result)[0][::-1]

def get_shared_key(basis_alice, basis_bob, key):
    n = len(basis_alice)
    new_key = ""
    for _ in range(n):
        if basis_alice[_] == basis_bob[_]:
            new_key += key[_]
    print('test3')
    return new_key

def encode_message(message, key):
    bin_message = message_to_bin(message)
    n = len(key)
    l = len(bin_message)
    div_message = [bin_message[i:i+n] for i in range(0, l, n)]
    encoded_message = ""
    for m in div_message:
        for j, k in enumerate(m):
            if k == key[j]:
                encoded_message += "0"
            else:
                encoded_message += "1"
    print('test4')
    return encoded_message

def decode_message(bin_message, key):
    n = len(key)
    l = len(bin_message)
    div_message = [bin_message[i:i+n] for i in range(0, l, n)]
    decoded_message = ""
    for m in div_message:
        for j, k in enumerate(m):
            if k == key[j]:
                decoded_message += "0"
            else:
                decoded_message += "1"
    decoded_message = bin_to_message(decoded_message)
    return decoded_message

def morse_to_bin(m):
    bin_ = ""
    for i in m:
        if i == ".":
            bin_ += "1"
        elif i == "-":
            bin_ += "11"
        bin_ += "0"
    bin_ += "0"
    return bin_

def bin_to_morse(bin_message):
    bin_message = bin_message.split("00")
    message = []
    for lett in bin_message:
        lett = lett.split("0")
        morse_ = ""
        for char in lett:
            if char == "11":
                morse_ += "-"
            elif char == "1":
                morse_ += "."
        message.append(morse_)
    return message

def morse_to_string(morse_message):
    message = ""
    for lett in morse_message:
        try:
            message += list(morse.keys())[list(morse.values()).index(lett)]
        except:
            pass
    return message
    
def message_to_bin(message):
    binary_mess = ""
    for char in message:
        m = morse[char]
        binary_mess += morse_to_bin(m)
    return binary_mess[:-2]

def bin_to_message(bin_message):
    morse = bin_to_morse(bin_message)
    return morse_to_string(morse)

def check_intruder(part_key_bob, part_key_alice):
    n = len(part_key_bob)
    for i in range(n):
        if part_key_alice[i] != part_key_bob[i]:
            print("Someone is trying to access the key!")
            return
    print(f"The probability that someone is accessing the info is {np.round(100*(3/4)**n,3)}%")
    
    
      
    

n = len(str(item.bit))
alice, basis_alice, key_alice = Alice(n, item.bit, item.basis)
bob, basis_bob = Bob(n)

key_bob = interface(alice, bob, intruder=False)
new_key_bob = get_shared_key(basis_alice, basis_bob, key_bob)
new_key_alice = get_shared_key(basis_alice, basis_bob, key_alice)
print(f"Alice basis: {basis_alice}")
print(f"Bob   basis: {basis_bob}")
print(f"key Bob old   {key_bob}")
print(f"key Alice old {key_alice}")
print(f"key Bob new  {new_key_bob}")
print(f"key Alice new {new_key_alice}")

bin_message = message_to_bin("qiskit")
print(bin_message)
message_encoded = encode_message("qiskit", new_key_alice)
print(message_encoded)
message_decoded = decode_message(message_encoded, new_key_bob)
print(message_decoded)
check_intruder(new_key_alice[:6], new_key_bob[:6])



import smtplib

gmail_user = 'alice.n.bob123@gmail.com'
gmail_password = 'EVEDONTHACKUS123!'

sent_from = gmail_user
to = [item.email]
subject = 'Your top secret Quantum Key. Beware of Eve.'
body = 'Hi bob, this is the result of your measuring Alices qubits in your basis. Heres the info you need: \n', "Alices Basis:" + str(basis_alice) +"\n Your Basis (Auto-generated):" + str(basis_bob) + "\n Your Key: " + str(key_bob) + "\n See you on the other end (Hopefully without eve this time)!"

email_text = """\
From: %s
To: %s
Subject: %s

%s
""" % (sent_from, ", ".join(to), subject, body)

try:
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.ehlo()
    smtp_server.login(gmail_user, gmail_password)
    smtp_server.sendmail(sent_from, to, email_text)
    smtp_server.close()
    print ("Email sent successfully!")
except Exception as ex:
    print ("Something went wrong….",ex)

