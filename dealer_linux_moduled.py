#!/usr/bin/python3
import socket
import threading
import random
import concurrent.futures
import os

addr = ("127.0.0.1", 50000)
server_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

class Card():
    def __init__(self, value, suit):
        self.suit = suit
        if value == 11:
            self.name = 'J'+suit
        elif value == 12:
            self.name = 'Q'+suit
        elif value == 13:
            self.name = 'K'+suit
        elif value == 14:
            self.name = 'A'+suit
        else:
            self.name = str(value) + suit
        self.value = value




class Deck(Card):
    def __init__(self):
        self.deck = []
        suits = ['C', 'H', 'S', 'D']
        for suit in suits:
            for value in range(2,15):
                self.deck.append(Card(value,suit))
    def rand_Card(self):
        rand = random.choice(self.deck)
        self.deck.remove(rand)
        return rand

class Casino_War(threading.Thread):
    def __init__(self, server_Socket):
        self.t = threading.Thread.__init__(self)
        self.deck = Deck()
        self.amount_Won = 0
        self.round = 0
    def quit(self):
        if self.amount_Won >=0:
            self.client_Socket.send(str.encode("The game has ended on round {}!\nThe player quit.\nPlayer won: {}$\nThanks for playing.".format(self.round, self.amount_Won)))
        if self.amount_Won < 0:
            self.client_Socket.send(str.encode("The game has ended on round {}!\nThe player quit.\nPlayer lost: {}$\nThanks for playing.".format(self.round, -1*self.amount_Won)))
    def status(self):
        if self.amount_Won >= 0:
            self.client_Socket.send(str.encode("Current round: {}\nPlayer won: {}$".format(self.round, self.amount_Won)))
        elif self.amount_Won < 0:
            self.client_Socket.send(str.encode("Current round: {}\nPlayer lost: {}$".format(self.round, -1*self.amount_Won)))
    def player_won(self,server_card,client_card,player_bet):
        self.client_Socket.send(str.encode("The result of round {}:\nPlayer won: {}$\nDealer's card: {}\nPlayer's card: {}".format(self.round, player_bet, server_card.name, client_card.name)))
    def player_lost(self, server_card,client_card, player_bet):
        self.client_Socket.send(str.encode("The result of round {}:\nDealer won: {}$\nDealer's card: {}\nPlayer's card    : {}".format(self.round, player_bet, server_card.name, client_card.name)))
    def run(self):
        self.client_Socket, self.sock_ip = server_Socket.accept()
        client_card = self.deck.rand_Card()#Draw a card
        self.client_Socket.send(str.encode(client_card.name))#Send a card to the client
        while True:
            what_to_do = self.client_Socket.recv(1024)
            if what_to_do == 'quit' :
                self.quit()
                break
            if what_to_do == 'status':
                self.status()
                what_to_do = self.client_Socket.recv(1024).decode('utf-8')
                continue
            else:
                self.round +=1
                server_card = self.deck.rand_Card()#Draw server card
                player_bet = float(what_to_do)
                if client_card.value > server_card.value:
                    self.player_won(server_card, client_card, player_bet)


            client_card = self.deck.rand_Card()#Draw a new card
            self.client_Socket.send(str.encode(client_card.name))#Send a card to the client
        self.client_Socket.close()
        
if __name__ == "__main__":
    server_Socket.bind(addr)
    server_Socket.listen()
    thread_list = []
    while True:
        for thread in thread_list:
            if thread.isAlive() == False:
                thread_list.remove(thread)
        if len(thread_list) == 2:
                continue
        thread = Casino_War(server_Socket)
        thread_list.append(thread)
        thread.start()
    server_Socket.close()
