import sys
import typing

import numpy as np

from Games.Game import Game
from utils.game_utils import GameState
from .BlackJackLogic import BlackjackTable
sys.path.append('../../..')



class BlackjackGame(Game):

    def __init__(self, n: int) -> None:
        super().__init__()
        self.num_decks = n
        self.bet_multiplier = 1
        self.phase = -1  # Two game phases, 1) player's first action,
        # and 2) any subsequent actions

    def getInitialState(self) -> GameState:

        t = BlackjackTable(num_decks=self.num_decks)
        self.bet_multiplier = 1
        self.phase = -1
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
        return 3, 13, 13

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

        player_hand_expanded = np.zeros(13)
        dealer_hand_expanded = np.zeros(13)
        for idx, (face, _) in enumerate(t.deck.items()):
            for card in t.player_hand:
                if card == face:
                    player_hand_expanded[idx] += 1
            if t.dealer_hand[0] == face:
                dealer_hand_expanded[idx] += 1

        return np.array([
            np.full((13, 13), player_hand_expanded),
            np.full((13, 13), dealer_hand_expanded),
            np.full((13, 13), 0)
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
