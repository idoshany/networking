##Ido Shany - 207689746
##Omer Lindner - 313532574
#!/usr/bin/python3
import socket
import threading
import random
import concurrent.futures
import os

addr = ("127.0.0.1", 50000)
server_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Card class, it defines the cards' values
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



#Deck class, it initiats a deck
class Deck(Card):
    def __init__(self):
        self.deck = []
        suits = ['C', 'H', 'S', 'D']
        for suit in suits:
            for value in range(2,15):
                self.deck.append(Card(value,suit))
    def rand_Card(self):#Randomize a card from the deck and returns it, also removes the card
        rand = random.choice(self.deck)
        self.deck.remove(rand)
        return rand

#Game class, it represents the game instance
class Casino_War(threading.Thread):
    def __init__(self, server_Socket):##class init
        self.t = threading.Thread.__init__(self)
        self.deck = Deck()
        self.amount_Won = 0
        self.round = 0
    def quit(self):#if the player entered quit
        if self.amount_Won >=0:
            self.client_Socket.send(str.encode("The game has ended on round {}!\nThe player quit.\nPlayer won: {}$\nThanks for playing.".format(self.round, self.amount_Won)))
            print("The game has ended on round {}!\nThe player quit.\nPlayer won: {}$\nThanks for playing.".format(self.round, self.amount_Won))
        if self.amount_Won < 0:
            self.client_Socket.send(str.encode("The game has ended on round {}!\nThe player quit.\nPlayer lost: {}$\nThanks for playing.".format(self.round, -1*self.amount_Won)))
            print("The game has ended on round {}!\nThe player quit.\nPlayer lost: {}$\nThanks for playing.".format(self.round, -1*self.amount_Won))
    def status(self):#if the player entered status
        if self.amount_Won >= 0:
            self.client_Socket.send(str.encode("Current round: {}\nPlayer won: {}$".format(self.round, self.amount_Won)))
            print("Current round: {}\nPlayer won: {}$".format(self.round, self.amount_Won))
        elif self.amount_Won < 0:
            self.client_Socket.send(str.encode("Current round: {}\nPlayer lost: {}$".format(self.round, -1*self.amount_Won)))
            print("Current round: {}\nPlayer lost: {}$".format(self.round, -1*self.amount_Won))
    def player_won(self,server_card,client_card,player_bet):#If the player won the round
        self.client_Socket.send(str.encode("The result of round {}:\nPlayer won: {}$\nDealer's card: {}\nPlayer's card: {}".format(self.round, player_bet, server_card.name, client_card.name)))
        print("The result of round {}:\nPlayer won: {}$\nDealer's card: {}\nPlayer's card: {}".format(self.round, player_bet, server_card.name, client_card.name))
    def player_lost(self, server_card,client_card, player_bet):#if the player lost the round
        self.client_Socket.send(str.encode("The result of round {}:\nDealer won: {}$\nDealer's card: {}\nPlayer's card: {}".format(self.round, player_bet, server_card.name, client_card.name)))
        print("The result of round {}:\nDealer won: {}$\nDealer's card: {}\nPlayer's card: {}".format(self.round, player_bet, server_card.name, client_card.name))
    def tie(self, server_card, client_card,player_bet):#If the game is tied
        self.client_Socket.send(str.encode("tie"))
        self.client_Socket.send(str.encode("The result of round {} is a tie!\nDealer's card: {}\nClient's card: {}\nThe bet: {}$".format(self.round, server_card.name, client_card.name, player_bet)))
        print("The result of round {} is a tie!\nDealer's card: {}\nClient's card: {}\nThe bet: {}$".format(self.round, server_card.name, client_card.name, player_bet))
        keep_or_not = self.client_Socket.recv(1024)
        if int(keep_or_not) == 0:
            self.amount_Won += player_bet/2
            self.client_Socket.send(str.encode("Round {} tie breaker:\nPlayer surrendered!\nThe bet: {}$\nDealer won: {}$\nPlayer won: {}$".format(self.round, player_bet, player_bet/2, player_bet/2)))
            print("Round {} tie breaker:\nPlayer surrendered!\nThe bet: {}$\nDealer won: {}$\nPlayer won: {}$".format(self.round, player_bet, player_bet/2, player_bet/2))
        elif int(keep_or_not) == 1:
            if len(self.deck.deck) - 5 < 0:
                self.deck = Deck()
            for i in range(3):
                self.deck.rand_Card()
            client_card = self.deck.rand_Card()
            server_card = self.deck.rand_Card()
            if server_card.value > client_card.value:
                self.amount_Won -= player_bet*2
                self.client_Socket.send(str.encode("Round {} tie breaker:\nGoing to war!\n3 cards were discarded.\nOriginal bet: {}$\nNew bet: {}\nDealer's card: {}\nPlayer's card: {}\n Dealer won: {}$".format(self.round, player_bet, player_bet*2, server_card.name, client_card.name, player_bet*2)))
                print("Round {} tie breaker:\nGoing to war!\n3 cards were discarded.\nOriginal bet: {}$\nNew bet: {}\nDealer's card: {}\nPlayer's card: {}\n Dealer won: {}    $".format(self.round, player_bet, player_bet*2, server_card.name, client_card.name, player_bet*2))
            elif server_card.value < client_card.value:
                self.amount_Won += player_bet
                self.client_Socket.send(str.encode("Round {} tie breaker:\nGoing to war!\n3 cards were discarded.\nOriginal bet: {}$\nNew bet: {}\nDealer's card: {}\nPlayer's card: {}\nPlayer won won: {}$".format(self.round, player_bet, player_bet*2, server_card.name, client_card.name, player_bet)))
                print("Round {} tie breaker:\nGoing to war!\n3 cards were discarded.\nOriginal bet: {}$\nNew bet: {}\nDealer's card: {}\nPlayer's card: {}\nPlayer won won:     {}$".format(self.round, player_bet, player_bet*2, server_card.name, client_card.name, player_bet))
            else:
                self.amount_Won += player_bet*2
                self.client_Socket.send(str.encode("Round {} tie breaker:\nGoing to war!\n3 cards were discarded.\nOriginal bet: {}$\nNew bet: {}\nDealer's card: {}\nPlayer's card: {}\nPlayer won won: {}$".format(self.round, player_bet, player_bet*2, server_card.name, client_card.name, player_bet*2)))
                print("Round {} tie breaker:\nGoing to war!\n3 cards were discarded.\nOriginal bet: {}$\nNew bet: {}\nDealer's card: {}\nPlayer's card: {}\nPlayer won won:     {}$".format(self.round, player_bet, player_bet*2, server_card.name, client_card.name, player_bet*2))
    def end_of_cards(self):#If the Deck has no more cards then this function is called
        self.client_Socket.send(str.encode("f"))
        if self.amount_Won >= 0:
            self.client_Socket.send(str.encode("The game has ended\nPlayer won: {}$\nPlayer is the winner!\nWould you like to play again?".format(self.amount_Won)))
        else:
            self.client_Socket.send(str.encode("The game has ended\nPlayer lost: {}\nDealer is the winner!\nWould you like to play again?".format(-1*self.amount_Won)))
    def run(self):#Run function of the thread
        self.client_Socket, self.sock_ip = server_Socket.accept()
        self.client_Socket.send(str.encode("Welcome to Casino Game!"))
        client_card = self.deck.rand_Card()#Draw a card
        self.client_Socket.send(str.encode(client_card.name))#Send a card to the client
        print(client_card.name)
        while True:#It's the while loop that keeps the game running until fitted input is recieved
            what_to_do = self.client_Socket.recv(1024).decode('utf-8')
            if what_to_do == 'quit' :
                self.quit()
                break
            if what_to_do == 'status':
                self.status()
                self.client_Socket.send(str.encode(client_card.name))
                continue
            else:
                self.round +=1
                server_card = self.deck.rand_Card()#Draw server card
                print(what_to_do)
                if what_to_do.isdigit() == True:
                        player_bet = float(what_to_do)
                elif what_to_do == b'':#handling broken socket
                    raise RuntimeError("Socket connection is broken")
                if client_card.value > server_card.value:#Client wins the round, then the winning function is called
                    self.amount_Won +=player_bet
                    self.player_won(server_card, client_card, player_bet)
                elif client_card.value < server_card.value:#Dealer wins the round, then the dealer won function is called
                    self.amount_Won -= player_bet
                    self.player_lost(server_card, client_card, player_bet)
                else:#tie occrured
                    self.tie(server_card, client_card, player_bet)
                if len(self.deck.deck)  < 2:#checking if there are less then 2 cards in the deck, if there is then end_of_cards function is called
                    self.end_of_cards()
                    keep_or_not = self.client_Socket.recv(1024).decode('utf-8')
                    if keep_or_not == 'yes':
                        self.deck = Deck()
                    elif keep_or_not == 'no':
                        break
            client_card = self.deck.rand_Card()#Draw a new card
            self.client_Socket.send(str.encode(client_card.name))#Send a card to the client
        self.client_Socket.close()
        
if __name__ == "__main__":#main function
    server_Socket.bind(addr)
    server_Socket.listen()
    thread_list = []
    while True:#Thread loop that keeps accepting connections
        for thread in thread_list:
            if thread.isAlive() == False:#if a thread has finished then end the thread and remove it from the thread array
                thread_list.remove(thread)
        if len(thread_list) == 2:#checking the amount of threads active
                continue
        thread = Casino_War(server_Socket)
        thread_list.append(thread)
        thread.start()
    server_Socket.close()
