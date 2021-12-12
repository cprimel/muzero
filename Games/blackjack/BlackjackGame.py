import random
import sys
import typing

import numpy as np

from Games.Game import Game
from utils.game_utils import GameState

sys.path.append('../../..')


class Card:
    values = {
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "6": 6,
        "7": 7,
        "8": 8,
        "9": 9,
        "10": 10,
        "J": 10,
        "Q": 10,
        "K": 10,
        "A": 11,
    }

    def __init__(self, face: str):
        self.face = face
        self.value = self.values[face]

    def __str__(self):
        return self.face

    def __repr__(self):
        return str(self.face)


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


class BlackjackGame(Game):

    def __init__(self, n: int) -> None:
        super().__init__()
        self.num_decks = n
        self.bet_multiplier = 1
        self.phase = -1  # Two game phases, 1) player's first action,
        # and 2) any subsequent actions

    def getInitialState(self) -> GameState:

        t = BlackjackTable(num_decks=self.num_decks)

        t.dealer_hand.append(t.deal_card())
        t.player_hand.append(t.deal_card())
        t.hole_card = t.deal_card()
        t.player_hand.append(t.deal_card())

        next_state = GameState(canonical_state=(t.dealer_hand, t.player_hand, t.deck, t.hole_card), observation=None,
                               action=-1,
                               player=1, done=False)
        next_state.observation = self.buildObservation(next_state)
        return next_state

    def getDimensions(self) -> typing.Tuple[int, int, int]:
        return 3, 3, 3

    def getActionSize(self) -> int:
        return 4 if self.phase < 0 else 2

    def getNextState(self, state: GameState, action: int, **kwargs) -> typing.Tuple[GameState, float]:

        t = BlackjackTable(self.num_decks)
        (t.dealer_hand, t.player_hand, t.deck, t.hole_card) = state.canonical_state

        if action == 0:
            t.player_hand.append(t.deal_card())
            if t.is_busted():
                state.done = True
            else:
                state.phase = 1
        if action == 1:
            state.done = True
            t.dealer_plays()
        if action == 2:
            self.bet_multiplier = 2
            t.player_hand.append(t.deal_card())
            t.dealer_plays()
            state.done = True
        if action == 3:
            state.done = True

        # Debugging
        # t.print()
        # print(f"Action Chosen: {state.action}")

        next_state = GameState(canonical_state=(t.dealer_hand, t.player_hand, t.deck, t.hole_card), observation=None,
                               action=action,
                               player=state.player, done=state.done)

        z = self.getGameEnded(next_state)
        next_state.observation = self.buildObservation(state)
        next_state.done = bool(z)

        return next_state, z

    def getLegalMoves(self, state: GameState) -> np.ndarray:
        if self.phase > 0:
            return np.array([1, 1, 0, 0])
        return np.array([1, 1, 1, 1])

    def getGameEnded(self, state: GameState, **kwargs) -> float:
        t = BlackjackTable(self.num_decks)
        (t.dealer_hand, t.player_hand, _, _) = state.canonical_state

        player_hand_val = t.get_hand_value(t.player_hand)
        dealer_hand_val = t.get_hand_value(t.dealer_hand)

        if not state.done:  # Game not finished
            return 0.0

        if state.action == 3:  # Surrender
            return -0.5

        if 21 >= player_hand_val > dealer_hand_val:
            return 1.0 * self.bet_multiplier
        if player_hand_val > 21:
            return -1.0 * self.bet_multiplier
        if player_hand_val == dealer_hand_val and len(t.player_hand) <= len(t.dealer_hand):
            return 1.0 * self.bet_multiplier
        if dealer_hand_val > 21:
            return 1.0 * self.bet_multiplier

        return -1.0 * self.bet_multiplier

    def buildObservation(self, state: GameState) -> np.ndarray:
        t = BlackjackTable(self.num_decks)
        (t.dealer_hand, t.player_hand, _, _) = state.canonical_state

        return np.array([
            np.full((3, 3), t.get_hand_value(t.player_hand)),
            np.full((3, 3), t.get_hand_value([t.dealer_hand[0]])),
            np.full((3, 3), self.phase)
        ])

    def getSymmetries(self, state: GameState, pi: np.ndarray) -> typing.List:
        return [(state.observation, pi)]

    def getHash(self, state: GameState) -> bytes:
        return state.canonical_state.tobytes()

    def stringRepresentationReadable(self, state: GameState) -> str:

        t = BlackjackTable(self.num_decks)
        (t.dealer_hand, t.player_hand, _, t.hole_card) = state.canonical_state

        if t.hole_card:
            dealer_representation = "Dealer hand: [" + t.dealer_hand[0].face + ", ?], Value: ?"
        else:
            dealer_representation = "Dealer hand: " + str(t.dealer_hand) + ", Value: " + str(
                t.get_hand_value(t.dealer_hand))
        player_representation = "Player hand: " + str(t.player_hand) + ", Value: " + str(
            t.get_hand_value(t.player_hand))

        return dealer_representation + " " + player_representation

    def render(self, state: GameState):
        t_cls = BlackjackTable(self.num_decks)
        (t_cls.dealer_hand, t_cls.player_hand, t_cls.deck, t_cls.hole_card) = state.canonical_state
        t_cls.print()
