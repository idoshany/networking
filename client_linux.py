#!/usr/bin/python3
import socket
import threading
import sys
import re


##Client Side Code


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#setting up the socket, and the socket address
client.settimeout(5)
server_ip = input("Enter the server ip address: ")#^^
server_port = input("Enter the server port: ")#^^
addr = (server_ip, int(server_port))#^^
client.connect(addr)
print(client.recv(1024).decode('utf-8'))
while True:
    welcome_msg = client.recv(1024).decode('utf-8')#Getting the card drawn
    print(welcome_msg)#printing it
    if welcome_msg == 'f':
        print(client.recv(1024).decode('utf-8'))
        client_input = input()
        client.send(str.encode(client_input))
        if client_input == 'no':
            break
        else: 
            continue
    client_bet = input("Enter your bet: ")
    if client_bet == 'quit':
        client.send(str.encode('quit'))
        print(client.recv(1024).decode('utf-8'))
        break
    elif client_bet == 'status':
        client.send(str.encode('status'))
        print(client.recv(1024).decode('utf-8'))
    else:
        client.send(str.encode(client_bet))
        won_or_lost = client.recv(1024)
        if won_or_lost.decode('utf-8') != 'tie':
            print(won_or_lost.decode('utf-8'))
        if won_or_lost.decode('utf-8') == 'tie':
            print(client.recv(1024).decode('utf-8'))
            client.send(str.encode(input("Enter 0 to surrender the war, or 1 to keep the war alive: ")))
            print(client.recv(1024).decode('utf-8'))
client.close()
