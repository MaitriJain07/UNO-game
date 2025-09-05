# UNO-game
Uno card game built in Python using Object-Oriented Programming (OOP) concepts.

## Features
- Classic Uno game rules including number, skip, reverse, draw two, wild, and wild draw four cards.
- Human player vs AI computer player.
- AI uses strategies to choose cards based on priority rules.
- Interactive command-line gameplay with input prompts.
- Designed and implemented using Python classes for cards, deck, players, and game logic.

## How to run
1. Clone the repository:
   git clone https://github.com/MaitriJain07/UNO-game.git

2. Navigate into the project folder:
   cd UNO-game
   
3. Run the Uno game script with Python:
   python uno.py
   
## Gameplay
- The game shows the top card and active color on each turn.
- Human player can select a card to play or choose to draw a card.
- AI plays automatically with a simple priority strategy on selecting cards.
- The first player to empty their hand wins.

Example commands during play:
  Enter card index or 0 to draw: 3
  You played: Red 5

## Code structure overview

- `Card` classes define different card types and their behaviors.
- `Deck` class generates and shuffles the full Uno card deck.
- `Player` manages player's hand and playable moves.
- `UnoGame` handles the game flow, player turns, and game state.

## License

This project is licensed under the MIT License.

## Author

**Maitri Jain**  
Email: maitrijain07@gmail.com
