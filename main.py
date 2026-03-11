# Your code here
from phevaluator.evaluator import evaluate_cards
from logic import Move, Game, Player, HandRank, RockyPlayer, RandomPlayer
from collections import Counter
from multiprocessing import Pool, cpu_count
import random

# Feel free to set a seed for testing, otherwise leave commmented out to test your bot in a variety of random spots
# Note that you cannot set a seed and run the simulation in parallel
# random.seed(6767)

# How many heads up matches you want to simulate
MATCHES = 1
# For development I recommend not processing in parallel as it can make it much harder to find errors
PARALLEL = False


class MyPlayer(Player):
    name = "crAAcked"
    image_path = "images/your_image.png"  # Optional

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
    
    def get_hand_type_test(self, hole_cards, community_cards: list[str]) -> HandRank:
        # Handle pre flop calls
        if not community_cards:
            return (
                HandRank.ONE_PAIR
                if hole_cards[0][0] == hole_cards[1][0]
                else HandRank.HIGH_CARD
            )

        rank = evaluate_cards(*community_cards, *hole_cards)
        for hand_type in HandRank:
            if rank <= hand_type.value:
                return hand_type
        raise IndexError(f"Hand Rank Out Of Range: {rank}")
    
    def get_high_card(self):
        ranks = ['2','3','4','5','6','7','8','9','T','J','Q','K','A']
        c1 = self.cards[0][0]
        c2 = self.cards[1][0]
        if ranks.index(c1) > ranks.index(c2):
            return c1
        else:
            return c2

    def get_equity(self, community_cards: list[str], samples: int = 5000) -> float:
        """Placeholder equity calculation function. You do not have to implement a function like this but some sort of equity calculation is highly recommended."""
        ranks = ['2','3','4','5','6','7','8','9','T','J','Q','K','A']
        suits = ['s','h','d','c']

        ownHandType = self.get_hand_type(community_cards)

        winNum = 0
        chopNum = 0
        lossNum = 0

        total = 0

        for rank1 in ranks:
            for suit1 in suits:
                for rank2 in ranks:
                    for suit2 in suits:
                        handType = self.get_hand_type_test([rank1+suit1,rank2+suit2],community_cards)
                        if ownHandType < handType:
                            winNum += 1
                        elif ownHandType > handType:
                            lossNum += 1
                        else:

                            chopNum += 1
                        total += 1

        return((winNum + chopNum/2)/total)

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
        #self.update_pot(round_history)

        # self.get_hand_type(community_cards) == HandRank.THREE_OF_A_KIND
        print(self.cards)
        print(community_cards)
        print(self.get_equity(community_cards))
        if Move.CHECK in valid_moves:
            return Move.CHECK
        elif Move.CALL in valid_moves:
            return Move.CALL
        return valid_moves[0]


def run_match(_: int) -> str:
    """Run a single match and return the winner's name."""
    p1, p2 = MyPlayer(), RandomPlayer()
    game = Game(p1, p2, debug=True)
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
