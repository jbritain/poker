# Your code here
from phevaluator.evaluator import evaluate_cards
from logic import Move, Game, Player, HandRank, RockyPlayer, RandomPlayer
from collections import Counter
from multiprocessing import Pool, cpu_count
import math

# Feel free to set a seed for testing, otherwise leave commmented out to test your bot in a variety of random spots
# Note that you cannot set a seed and run the simulation in parallel
# random.seed(6767)

# How many heads up matches you want to simulate
MATCHES = 1000
# For development I recommend not processing in parallel as it can make it much harder to find errors
PARALLEL = False


# https://gist.github.com/laundmo/b224b1f4c8ef6ca5fe47e132c8deab56
def lerp(a: float, b: float, t: float) -> float:
    return (1 - t) * a + t * b


class MyPlayer(Player):
    name = "crAAcked"
    image_path = "images/your_image.png"  # Optional

    def __init__(self):
        super().__init__(self)
        self.opponent_aggression = 0.5
        self.average_opponent_aggression = (
            0.5  # 1 = maximally aggressive, 0.5 = minimally aggressive
        )
        self.hands_played = 0

    def get_hand_type(self, community_cards: list[str]) -> HandRank:
        # Handle pre flop calls
        if not community_cards:
            return (
                HandRank.ONE_PAIR
                if self.cards[0][0] == self.cards[1][0]
                else HandRank.HIGH_CARD
            )

        rank = evaluate_cards(*community_cards, *self.cards)
        for hand_type in HandRank:
            if rank <= hand_type.value:
                return hand_type
        raise IndexError(f"Hand Rank Out Of Range: {rank}")

    def get_equity(self, community_cards: list[str], samples: int = 5000) -> float:
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        suits = ["s", "h", "d", "c"]

        ownHandType = self.get_hand_type(community_cards)

        winNum = 0
        chopNum = 0
        lossNum = 0

        total = 0

        for rank1 in ranks:
            for suit1 in suits:
                for rank2 in ranks:
                    for suit2 in suits:
                        handType = self.get_hand_type_test(
                            [rank1 + suit1, rank2 + suit2], community_cards
                        )
                        if ownHandType < handType:
                            winNum += 1
                        elif ownHandType > handType:
                            lossNum += 1
                        else:

                            chopNum += 1
                        total += 1

        return (winNum + chopNum / 2) / total

    def aggression_heuristic(bet, min_bet):
        if bet < min_bet:
            return 0.0

        # between 1 and 3xbig blind interpolate to 0.5
        if bet < min_bet * 3:
            return lerp(min_bet, min_bet * 3, bet) * 0.5

        return max(0.0, min(1.0, lerp(min_bet * 3, min_bet * 6, bet)))

    def get_pot(self, round_history):
        if round_history == []:
            return 0
        if len(round_history) == 1:
            return round_history[0][1]
        return round_history[-1][1] + round_history[-2][1]

    def move(
        self,
        community_cards: list[str],
        valid_moves: list[Move],
        round_history: list[tuple[Move, int]],
        min_bet: int,
        max_bet: int,
    ) -> tuple[Move, int] | Move:
        """Your move code here! You are given the community cards (cards both players have access to, the objective is to use your 2 cards (self.cards) with the community cards to make the best 5-card poker hand).
        You are also given a list containing the legal moves you can currently make, for example, if the opponent has bet then you can only call, raise or fold but cannot check.
        If your bot attempts to make an illegal move it will fold its hand (forfeiting any chips already in the pot), so ensure not to do this.
        """

        # calculate aggression of opponent move
        if len(round_history > 0):
            self.opponent_aggression *= math.ceil(len(round_history) / 2) - 1
            self.opponent_aggression += self.aggression_heuristic(
                round_history[-1][1] or 0, min_bet
            )
            self.opponent_aggression /= math.ceil(len(round_history) / 2)
        else:
            self.opponent_aggression = 0.5

        equity = self.get_equity(community_cards)
        bet_amount = 

        return Move.FOLD


def run_match(_: int) -> str:
    """Run a single match and return the winner's name."""
    p1, p2 = MyPlayer(), RandomPlayer()
    game = Game(p1, p2, debug=False)
    return game.simulate_hands().name


if __name__ == "__main__":
    win_counts = Counter()
    # This runs the large number of matches in parallel, which drastically speeds up computation time
    if PARALLEL:
        with Pool(cpu_count()) as pool:
            results = pool.map(run_match, range(MATCHES))
            win_counts.update(results)
    else:
        for i in range(MATCHES):
            win_counts.update((run_match(i),))

    player_name, wins = win_counts.most_common(1)[0]
    print(
        f"{player_name} won the most with {wins}/{MATCHES} ({(wins / MATCHES) * 100:.2f}%)"
    )
