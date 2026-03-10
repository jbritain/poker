# AUCS: Texas Hack'em
![AUCS Logo](https://www.ausa.org.uk/asset/Organisation/26976/LogoColoured.png?thumbnail_width=480&thumbnail_height=100&resize_type=ResizeWidth)

## Overview
Welcome to Texas Hack'em!
Your goal is to build a **heads-up (1v1) No-Limit Texas Hold'em poker bot** capable of defeating other bots through strategy and decision making.

Each bot begins with **10,000 chips** and competes over a series of hands. The objective is to bust your opponent (take all their chips) before the hand limit is reached.

If neither player busts within **10,000 hands**, the player with the largest chip stack wins.

Your task is to implement the decision-making logic for your bot.

## Learning Resources

If you're unfamiliar with Texas Hold'em check out these resources:
- https://bicyclecards.com/how-to-play/texas-holdem-poker 
- https://www.888poker.com/magazine/poker-terms/heads-up

## Poker Terminology
### Button
The **button** refers to the player who is *in position*, meaning thy act **last after the flop**, which is an advantage.

### Blinds
Blinds are forced bets that ensure every hand has chips in the pot.
In this heads-up game, the button will post (put into the pot) the small blind, and the other player will post the big blind.

### Chips
Since the chips are unitless, it's hard to value them, it is better to think of the amount of chips in terms of big blinds (BBs) as this is much more useful (*e.g.*, 6740 chips is 67.4 BBs since the big blind is 100 chips).

## Game Rules
### Structure
- Each bot starts with **10,000 chips** (100 BBs).
- Blinds are fixed at **50/100** (Small Blind / Big Blind).
- A match consists of up to **10,000 hands**. If a player's chip count reaches 0, they lose immediately.

### Hand Flow
Each hand proceeds through the standard Texas Hold'em streets:
1. Pre-Flop: players receive 2 cards
2. Flop: 3 community cards revealed
3. Turn: 1 community card revealed
4. River: final community card revealed
5. Showdown: best 5-card [poker hand](https://www.poker.org/poker-hands-ranking-chart/) wins

Showdown – best 5-card hand wins

## Legal Moves
Your bot must return any of the following moves **only if it appears in the `valid_moves` list**:

| Move | Description |
|-|-|
| `Move.CHECK` | Pass the action with no bet (only when no bet is pending). |
| `Move.CALL` | Match the current bet. |
| `Move.BET` | Place a bet when no bet has been made. Return as `(Move.BET, amount)`. |
| `Move.RAISE` | Increase the current bet. Return as `(Move.RAISE, amount)`. |
| `Move.ALL_IN` | Commit all remaining chips. |
| `Move.FOLD` | Surrender the hand and forfeit any chips already in the pot. |

> **Important:** If your bot returns an invalid move (a move not in `valid_moves` or a malformed return value), it will be **forced to fold**.

### Example
```python
# Raise the current bet to 500 chips, the opponent now must call the 500, raise, go all in, or fold their hand.
return (Move.RAISE, 500)
```

## Card Notation
Cards use standard poker shorthand, *i.e.*, a **rank** character followed by a **suit** character:
- Ranks: `2 3 4 5 6 7 8 9 T J Q K A`
- Suits: `d` (diamonds), `h` (hearts), `s` (spades), `c` (clubs)
- Examples: `As` = Ace of Spades, `Td` = Ten of Diamonds, `3c` = Three of Clubs

## Built-in Example Bots
Two basic bots are included as examples of how your bot should return moves.
### RockyPlayer
Extremely tight strategy, only plays 4 hands (AA, KK, QQ, JJ) and folds everything else.
This strategy is **very exploitable**, if you simply raise every single hand but fold whenever the opponent does not fold then you will win almost every hand.

### RandomPlayer
This player simply makes a random move from the `valid_moves` list.
This strategy is also **very exploitable**, just be extremely aggressive with the top 50% of hands you will win most of the time.

Your bot should be able to consistently beat both of these players.

## Creating Your Bot
All bots inherit from the `Player` class:
```python
class MyPlayer(Player):
    name = 'Name your bot/Team name'

    def move(
        self, community_cards: list[str], valid_moves: list[Move],
        round_history: list[tuple[Move, int]], min_bet: int, max_bet: int
    ) -> tuple[Move, int] | Move:

        return Move.FOLD
```
Your bot receives several pieces of information for each decision:
### community_cards
The shared board cards that you and your opponent both have access to.

Example community cards on the flop:
```python
['Ah', 'Kd', '7s']
```

### valid_moves
A list of moves that are legal in the current position.

If the opponent has just bet then your valid moves will be:
```python
[Move.CALL, Move.RAISE, Move.ALL_IN, Move.FOLD]
```

### round_history
These are the actions taken during the current street.

Example actions on the turn:
```python
[(Move.BET, 100), (Move.RAISE, 300), (Move.RAISE, 1200)]
```
Here, the opponent started with the minimum bet of 100 chips (1 BB).
You then raised to 300 (3 BBs) chips, however, your opponent then followed up with yet another raise to 1200 chips (12 BBs).

### min_bet
The minimum legal bet or raise amount.

For example, taking the `round_history` above, your minimum raise would now be $1200 + (1200 - 300) = 2100$.
It is worth noting that `min_bet` can be more than the amount of chips you actually have.
In this case your only legal moves will be `Move.FOLD` and `Move.ALL_IN`.

### max_bet
The maximum amount you can bet (*i.e.*, your stack).
In the case that you bet more than your opponent has, you will get refunded any excess chips if they end up going all in.

## `Player` variables
You also have access to the following variables:
### self.cards
Your two cards for the current hand, *e.g.*, `['As', 'Qd']` which represents the ace of spades and the queen of diamonds.

### self.chips
Your current chip count.

### self.pot_commitment
Chips you have currently committed to the pot on the current street.
Think of `self.chips` like your *available* balance, whereas `self.pot_commitment` contains the extra chips you currently have staked.

### self.hands_shown
This is a list which tracks the hands you have seen your opponent show during showdown along with the rank of their made 5-card hand.

Example:
```python
[(['As', 'Ks'], HandRank.ROYAL_FLUSH), (['7d', '2c'], HandRank.HIGH_CARD)]
```

## Getting Started
Python >= 3.10 is required, if you do not have it installed then follow the instructions on https://www.python.org/downloads/

If you need any help setting up the environment then just ask, we'll be happy to help!

1. Install dependencies:
```bash
python -m pip install -r requirements.txt
```
2. Run the simulation:
```bash
python main.py
```
By default, it runs **1,000** matches and reports the best bot's win rate.

## Useful Tips
- Use your opponent's showdown history (`self.hands_shown`) to adapt your strategy to their play-style over time.
- Calculate your chance of winning assuming your opponent could have any random hand (i.e., how many hands beat your current hand), this is known as your *equity*.
- Position matters, the button acting last post-flop provides an informational advantage.
- Good bet sizing could either reel your opponents in, or scare them off. Choosing a good size for what you want to achieve is a fundamental skill in poker.

## Submission
- Submit your completed `main.py` file into the #hackathon-submissions channel in the AUCS discord.
- Ensure to give a unique name to your bot by changing the `name` variable in `MyPlayer`.

Do not use any external APIs, do not obfuscate your code, do not write to any files.
You can use standard Python libraries such as `itertools` if it helps with your solution, but do not use any external libraries (ones you need to install with `pip`).

I will be reading the code of the winning submissions to validate them.

Note that you or your team can be disqualified for any reason deemed fit by an AUCS Board Member, such as trying to find a loophole in the rules.
Just be a good sportsman and enjoy the hackathon!

### Scoring
Each bot will have 1,000 heads-up matches against each other bot, for example, if there are 10 submissions then there will be 45 matchups and 45,000 games, which will be hundreds of millions of individual hands!

The bots will then be scored based on the number of wins, in the event that multiple bots have the same amount of wins additional tie-breaker games will be played.

### Notes On Cheating
While I have implemented some basic sanity checks (checking that a player hasn't given themselves chips or changed their cards), this was mainly just to make it easier to find bugs during development.

I am fully aware that it is possible to use Python's garbage collector (among other methods) to hook into things you are not meant to have access to.
For example, while you could access the opponent's bot and override their move function to always fold, doing this just takes the fun out of the event for everyone involved (you'll also be disqualified).

If you are unsure about anything or have any questions, ask a member of AUCS, we're happy to help!
