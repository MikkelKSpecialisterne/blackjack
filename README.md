# blackjack
Repository for my Blackjack program project.

This project involved developing a program that allows a user to play a typical game of BlackJack.

The program runs by typing "python -i Control.py" into the console inside the folder containing the files, and testing it with unit tests is done via "python -m coverage run --source=Deck,Participant,Game -m unittest test_blackjack", which tests the model part of the program.

The program uses a classic Model, View, Controller setup, which separates the three assignemnts for a program into separate files and groups of files. The Deck.py, Participant.py and Game.py consists of the Model part of the game, which has all the backend logic and memory of the state of the game. View.py uses the PyGame framework to display the various cards and information used by the player, and Control.py makes calls to both of them to depending on what inputs the user makes.

Noteably, the program is currently missing the "split" feature that would normally belong in a regular game of blackjack, which i might implement later if I find the time.

# Blackjack — Class Diagram

```mermaid
classDiagram
    class Card {
        +int rank
        +str suit
        +value() int
        +__str__() str
    }

    class Deck {
        +list cards
        +draw() Card
        +remaining_cards() list
    }

    class Hand {
        +list cards
        +add_card(card)
        +cards_in_hand() list
        +value_in_hand() int
        +clear()
    }

    class Participant {
        +Hand hand
    }

    class Player {
        +int id
        +int money
        +bool passed
        +str bet_value
        +bool money_error
        +RoundResult round_result
        +bool bankrupt
        +hit(deck)
        +stand()
    }

    class Dealer {
        +play(deck)
        +draw(deck)
    }

    class GameState {
        <<enumeration>>
        PLAYER_SELECT
        BETTING
        PLAYER_TURN
        ROUND_OVER
    }

    class RoundResult {
        <<enumeration>>
        WIN
        BLACKJACK
        LOSE
        TIE
        BANKRUPT
        ERROR
    }

    class Game {
        +list~Player~ players
        +Dealer dealer
        +Deck deck
        +GameState state
        +int player_turn
        +player_amount(amount)
        +next_player()
        +bet(player)
        +new_game()
        +hit(player)
        +double(player)
        +confirm_bet(player)
        +check_victory(player) RoundResult
        +round_over()
        +current_player() Player
        +remove_bankrupt() bool
        +convert_player_hand(hand) str
        +convert_dealer_hand(hand) str
    }

    class GameView {
        +Surface screen
        +Font font
        +dict card_images
        +Surface card_back
        +Rect hit_button
        +Rect double_button
        +Rect stand_button
        +Rect new_game_button
        +Rect betting_box
        +draw(game)
        +filename_for(rank, suit) str
    }

    class GameController {
        +Surface screen
        +GameView view
        +Game game
        +bool running
        +handle_event(event)
        +run()
    }

    Deck "1" *-- "52" Card : creates
    Hand "1" o-- "*" Card : holds
    Participant "1" *-- "1" Hand
    Player --|> Participant
    Dealer --|> Participant
    Game "1" *-- "0..4" Player : players
    Game "1" *-- "1" Dealer
    Game "1" *-- "1" Deck
    Game ..> GameState : uses
    Game ..> RoundResult : returns
    GameController "1" *-- "1" Game
    GameController "1" *-- "1" GameView
    GameView ..> GameState : uses
    GameView ..> RoundResult : uses
```
