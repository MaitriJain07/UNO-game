import random
from abc import ABC, abstractmethod
class Card(ABC):
    def __init__(self, color, value):
        self.color = color
        self.value = value

    def matches(self, other, active_color):
        return (
            (self.color is not None and self.color == active_color)
            or (self.value == other.value)
            or (self.color is None)  # Wild cards can be played anytime
        )

    @abstractmethod
    def play(self, game, player):
        pass

    def __str__(self):
        return f"{self.color or ''} {self.value}".strip()

class NumberCard(Card):
    def play(self, game, player):
        game.top_card = self
        game.active_color = self.color

class SkipCard(Card):
    def play(self, game, player):
        game.top_card = self
        game.active_color = self.color
        game.skip_next = True

class ReverseCard(Card):
    def play(self, game, player):
        game.top_card = self
        game.active_color = self.color
        game.skip_next = True
        
class DrawTwoCard(Card):
    def play(self, game, player):
        game.top_card = self
        game.active_color = self.color
        game.pending_draw += 2
        game.force_skip_after_draw = True

class _WildBase(Card):
    COLORS = ("Red", "Blue", "Green", "Yellow")
    def _choose_color_for_ai(self, player):
        counts = {c: 0 for c in self.COLORS}
        for card in player.hand:
            if card.color in counts:
                counts[card.color] += 1
        best_colors = [c for c, count in counts.items() if count == max(counts.values())]
        return random.choice(best_colors) if best_colors else random.choice(self.COLORS)

    def _ask_human_color(self):
        while True:
            chosen = input("Choose color (Red, Blue, Green, Yellow): ").strip().capitalize()
            if chosen in self.COLORS:
                return chosen
            print("Invalid color. Try again.")

class WildCard(_WildBase):
    def play(self, game, player):
        game.top_card = self
        if player.is_human:
            chosen = self._ask_human_color()
        else:
            chosen = self._choose_color_for_ai(player)
            print(f"{player.name} chose color: {chosen}")
        game.active_color = chosen

class WildDrawFourCard(_WildBase):
    def play(self, game, player):
        game.top_card = self
        if player.is_human:
            chosen = self._ask_human_color()
        else:
            chosen = self._choose_color_for_ai(player)
            print(f"{player.name} chose color: {chosen}")
        game.active_color = chosen
        game.pending_draw += 4
        game.force_skip_after_draw = True

class Deck:
    COLORS = ["Red", "Blue", "Green", "Yellow"]
    NUMBERS = list(range(10))
    def __init__(self):
        self.cards = self._generate_deck()
        random.shuffle(self.cards)
    def _generate_deck(self):
        deck = []
        for color in self.COLORS:
            # Add number cards (0 appears once, 1-9 appear twice)
            for v in self.NUMBERS:
                deck.append(NumberCard(color, v))
                if v != 0:
                    deck.append(NumberCard(color, v))
            # Add action cards (2 of each per color)
            for _ in range(2):
                deck.append(SkipCard(color, "Skip"))
                deck.append(ReverseCard(color, "Reverse"))
                deck.append(DrawTwoCard(color, "Draw Two"))
        # Add wild cards (4 of each)
        for _ in range(4):
            deck.append(WildCard(None, "Wild"))
            deck.append(WildDrawFourCard(None, "Wild Draw Four"))
        return deck
    def draw(self):
        if not self.cards:
            raise RuntimeError("Deck is empty!")
        return self.cards.pop()

class Player:
    def __init__(self, name, is_human=False):
        self.name = name
        self.is_human = is_human
        self.hand = []
    def draw_cards(self, deck, n=1):
        for _ in range(n):
            self.hand.append(deck.draw())
    def playable_moves(self, top_card, active_color):
        return [i for i, c in enumerate(self.hand) if c.matches(top_card, active_color)]
    def show_hand_lines(self):
        return [f"{i+1}. {card}" for i, card in enumerate(self.hand)]
    def has_won(self):
        return len(self.hand) == 0

class UnoGame:
    def __init__(self, player_names=None):
        self.deck = Deck()
        if player_names is None:
            player_names = ["You", "Computer"]
        self.players = [Player(player_names[0], is_human=True)] + [
            Player(name, False) for name in player_names[1:]
        ]
        self.top_card = None
        self.active_color = None
        self.skip_next = False
        self.reverse_order = False
        self.pending_draw = 0
        self.force_skip_after_draw = False
        # Deal 7 cards to each player
        for p in self.players:
            p.draw_cards(self.deck, 7)
        # Start with a number card to avoid complications
        self.top_card = self.deck.draw()
        while not isinstance(self.top_card, NumberCard):
            self.deck.cards.insert(0, self.top_card)
            random.shuffle(self.deck.cards)
            self.top_card = self.deck.draw()
        self.active_color = self.top_card.color
    def play(self):
        turn_idx = 0
        num_players = len(self.players)
        while True:
            current = self.players[turn_idx % num_players]
            print(f"\nTop card: {self.top_card} (Active color: {self.active_color})")
            if current.is_human:
                print("Your hand:")
                for line in current.show_hand_lines():
                    print(line)
                choice = input("Enter card index or 0 to draw: ").strip()
                if not choice.isdigit():
                    print("Invalid input.")
                    continue
                choice = int(choice)
                if choice == 0: # Player chooses to draw a card
                    current.draw_cards(self.deck)
                    drawn_card = current.hand[-1]
                    print(f"You drew: {drawn_card}")
                    if drawn_card.matches(self.top_card, self.active_color):
                        play_it = input("Play the drawn card? (y/n): ").strip().lower()
                        if play_it == 'y':
                            current.hand.pop()  # Remove drawn card
                            drawn_card.play(self, current)
                            print(f"You played: {self.top_card}")
                        else:
                            print("You chose not to play the drawn card. Turn ends.")
                    else:
                        print("Drawn card cannot be played. Turn ends.")
                    
                    turn_idx = (turn_idx + 1) % num_players
                    continue
                if not (1 <= choice <= len(current.hand)):
                    print("Invalid index.")
                    continue
                card = current.hand[choice - 1]
                if card.matches(self.top_card, self.active_color):
                    current.hand.pop(choice - 1)
                    card.play(self, current)
                    print(f"You played: {self.top_card}")
                else:
                    print("Invalid move!")
                    continue
            else:
                playable = current.playable_moves(self.top_card, self.active_color)
                if playable:
                    card_idx = self.ai_choose_card(current, playable)
                    card = current.hand.pop(card_idx)
                    card.play(self, current)
                    print(f"{current.name} played: {self.top_card}")
                else:
                    current.draw_cards(self.deck)
                    print(f"{current.name} drew a card.")
                print(f"{current.name} has {len(current.hand)} cards left.")
            if current.has_won():
                print(f"{current.name} won!")
                break
            if self.pending_draw > 0:
                next_player_idx = (turn_idx + 1) % num_players
                penalized_player = self.players[next_player_idx]
                penalized_player.draw_cards(self.deck, self.pending_draw)
                print(f"{penalized_player.name} drew {self.pending_draw} cards!")
                # Reset penalty and set skip flag if needed
                self.pending_draw = 0
                if self.force_skip_after_draw:
                    self.skip_next = True
                    self.force_skip_after_draw = False
            turn_idx = (turn_idx + 1) % num_players
            if self.skip_next:
                skipped_player = self.players[turn_idx % num_players]
                print(f"{skipped_player.name}'s turn skipped!")
                turn_idx = (turn_idx + 1) % num_players
                self.skip_next = False
    def ai_choose_card(self, player, playable_indices):
        # First priority: Draw Two cards to attack opponent
        for idx in playable_indices:
            card = player.hand[idx]
            if isinstance(card, DrawTwoCard):
                return idx        
        # Second priority: Skip or Reverse to disrupt opponent
        for idx in playable_indices:
            card = player.hand[idx]
            if isinstance(card, (SkipCard, ReverseCard)):
                return idx   
        # Third priority: Highest number cards to reduce hand size
        max_value = -1
        max_idx = None
        for idx in playable_indices:
            card = player.hand[idx]
            if isinstance(card, NumberCard) and card.value > max_value:
                max_value = card.value
                max_idx = idx
        if max_idx is not None:
            return max_idx        
        # Last resort: Wild cards
        for idx in playable_indices:
            card = player.hand[idx]
            if isinstance(card, (WildCard, WildDrawFourCard)):
                return idx
        # Fallback to first playable card
        return playable_indices[0]
print("Starting UNO")
if __name__ == "__main__":
    player_names = ["You", "Computer"]
    game = UnoGame(player_names)
    game.play()