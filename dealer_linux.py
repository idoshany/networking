#!/usr/bin/python3
import socket
import threading
import random
import concurrent.futures

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
    def run(self):
        client_Socket, sock_ip = server_Socket.accept()
        while True:
            if len(self.deck.deck) == 0:
                client_Socket.send(str.encode('f'))
                if self.amount_Won > 0:
                    client_Socket.send(str.encode("The game has ended!\nPlayer won: {}$\nPlayer is the winner!\nWould you like to play againn".format(self.amount_Won)))
                elif self.amount_Won < 0:
                    client_Socket.send(str.encode("The game has ended!\nPlayer lost: {}$\nDealer is the winner!\nWould you like to play again?".format(self.amount_Won*-1)))
                client_input = client_Socket.recv(1024).decode('utf-8')
                if client_input == 'no':
                    break
                elif client_input =='yes':
                    self.deck = Deck()
            client_card = self.deck.rand_Card()
            client_Socket.send(str.encode(client_card.name))
            player_bet = client_Socket.recv(1024)
            if player_bet.decode('utf-8') == 'quit':
                if self.amount_Won > 0 :
                    client_Socket.send(str.encode("The game has ended on round {}!\nThe player quit.\nThe player won - {}\nThank you for playing!".format(self.round, self.amount_Won)))
                elif self.amount_Won < 0:
                    client_Socket.send(str.encode("The game has ended on round {}!\nThe player quit.\nThe player lost - {}\nThank you for playing!".format(self.round, -1*self.amount_Won)))
                else:
                    client_Socket.send(str.encode("The game has ended on round {}!\nThe Game has ended in a tie!\nThank you for playing!"))
                break
            elif player_bet.decode('utf-8') == 'status':
                if(self.amount_Won >= 0):
                    client_Socket.send(str.encode("Current Round- {}\nPlayer won- {}".format(self.round, self.amount_Won)))
                else:
                    client_Socket.send(str.encode("Current Round- {}\nPlayer lost- {}".format(self.round, -1*self.amount_Won)))
            else:
                player_bet = float(player_bet)
                cpu_card = self.deck.rand_Card()
                if cpu_card.value < client_card.value:
                    self.round += 1
                    client_Socket.send(str.encode("The Result Of Round - {} \nClient Won - {}$\nDealer's Card - {}\nClient's Card - {}".format(self.round, player_bet, cpu_card.name, client_card.name)))
                    self.amount_Won += player_bet
                elif cpu_card.value > client_card.value:
                    self.round += 1
                    client_Socket.send(str.encode("The Result Of Round - {} \nDealer Won - {}$\nDealer's Card - {}\nClient's Card - {}".format(self.round, player_bet, cpu_card.name, client_card.name)))
                    self.amount_Won -= player_bet
                else:
                    self.round += 1
                    client_Socket.send(str.encode("Its a tie! Press 0 to surrender and 1 to continue"))
                    if int(client_Socket.recv(1024).decode('utf-8')) == 0:
                        client_Socket.send(str.encode("The Result Of Round - {} \nClient Decided to quit! Both won - {}$\nDealer's Card - {}\nClient's Card - {}".format(self.round, player_bet/2, cpu_card.name, client_card.name)))
                        self.amount_Won -= (player_bet/2)
                    else:
                        for i in range(3):
                            self.deck.rand_Card()
                        client_card = self.deck.rand_Card()
                        server_card = self.deck.rand_Card()
                        if server_card.value < client_card.value:
                            self.amount_Won += player_bet
                            client_Socket.send(str.encode("Round - {} Tie Break! \nClient Won - {}$\nDealer's Card - {}\nClient's Card - {}".format(self.round, player_bet, cpu_card.name, client_card.name)))
                        elif server_card.value > client_card.value:
                            self.amount_Won -= player_bet*2
                            client_Socket.send(str.encode("Round - {} Tie Break!\nDealer Won - {}$\nDealer's Card - {}\nClient's Card - {}".format(self.round, player_bet*2, cpu_card.name, client_card.name)))
                        else:
                            self.amount_Won += player_bet*2
                            client_Socket.send(str.encode("Round - {} Tie Break!\nClient Won - {}$\nDealer's Card - {}\nClient's Card - {}".format(self.round, player_bet*2, cpu_card.name, client_card.name)))
        client_Socket.close()
        

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
