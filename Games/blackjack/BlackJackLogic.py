import random

from .Card import Card

class BlackjackTable:
    def __init__(self, num_decks):
        self.dealer_hand = []
        self.hole_card = None
        self.player_hand = []
        self.deck = {
            "2": num_decks * 4,
            "3": num_decks * 4,
            "4": num_decks * 4,
            "5": num_decks * 4,
            "6": num_decks * 4,
            "7": num_decks * 4,
            "8": num_decks * 4,
            "9": num_decks * 4,
            "10": num_decks * 4,
            "J": num_decks * 4,
            "Q": num_decks * 4,
            "K": num_decks * 4,
            "A": num_decks * 4,
        }

    # Helper methods
    @staticmethod
    def get_hand_value(hand) -> int:
        value = 0
        aces = 0
        for card in hand:
            if card.face == "A":
                aces += 1
            else:
                value += card.value

        while aces:
            if aces == 1 and value <= 10:
                value += 11
            else:
                value += 1
            aces -= 1

        return value

    def deal_card(self) -> Card:
        card = Card(
            random.choice([face for _, (face, num_in_decks) in enumerate(self.deck.items()) if num_in_decks > 0]))
        self.deck[card.face] -= 1
        return card

    def dealer_plays(self):
        if self.get_hand_value(self.player_hand) > 21:
            return
        if self.get_hand_value(self.dealer_hand) == 21:
            return

        self.dealer_hand.append(self.hole_card)
        while self.get_hand_value(self.dealer_hand) <= 16:
            self.dealer_hand.append(self.deal_card())

    def is_busted(self):
        if self.get_hand_value(self.player_hand) > 21:
            return True

    def print(self):
        if self.hole_card:
            print("Dealer hand: [" + self.dealer_hand[0].face + ", ?], Value: ?")
        else:
            print("Dealer hand: " + str(self.dealer_hand) + ", Value: " + str(
                self.get_hand_value(self.dealer_hand)))
        print("Player hand: " + str(self.player_hand) + ", Value: " + str(
            self.get_hand_value(self.player_hand)))
