import unittest
from unittest.mock import patch

from Deck import Card, Deck, Hand
from Participant import Player, Dealer
from Game import Game, GameState


class TestCard(unittest.TestCase):
    def test_number_card_value(self):
        self.assertEqual(Card(7, "Hearts").value(), 7)

    def test_face_card_value(self):
        self.assertEqual(Card(11, "Spades").value(), 10)  # Jack
        self.assertEqual(Card(12, "Spades").value(), 10)  # Queen
        self.assertEqual(Card(13, "Spades").value(), 10)  # King

    def test_ace_value(self):
        self.assertEqual(Card(1, "Clubs").value(), 11)

    def test_card_is_frozen(self):
        card = Card(5, "Hearts")
        with self.assertRaises(Exception):
            card.rank = 9

    def test_str_uses_face_names(self):
        self.assertEqual(str(Card(1, "Hearts")), "Ace of Hearts")
        self.assertEqual(str(Card(13, "Spades")), "King of Spades")
        self.assertEqual(str(Card(7, "Clubs")), "7 of Clubs")


class TestDeck(unittest.TestCase):
    def test_deck_has_52_unique_cards(self):
        deck = Deck()
        self.assertEqual(len(deck.cards), 52)
        self.assertEqual(len(set(deck.cards)), 52)

    def test_draw_removes_a_card(self):
        deck = Deck()
        deck.draw()
        self.assertEqual(len(deck.cards), 51)

    def test_remaining_cards_is_a_copy(self):
        deck = Deck()
        snapshot = deck.remaining_cards
        snapshot.append(Card(1, "Hearts"))
        self.assertEqual(len(deck.cards), 52)  # original untouched


class TestHand(unittest.TestCase):
    def test_empty_hand_value_is_zero(self):
        self.assertEqual(Hand().value_in_hand, 0)

    def test_simple_value(self):
        hand = Hand()
        hand.add_card(Card(7, "Hearts"))
        hand.add_card(Card(5, "Clubs"))
        self.assertEqual(hand.value_in_hand, 12)

    def test_single_ace_counts_as_eleven_when_safe(self):
        hand = Hand()
        hand.add_card(Card(1, "Hearts"))
        hand.add_card(Card(9, "Clubs"))
        self.assertEqual(hand.value_in_hand, 20)

    def test_ace_downgrades_to_avoid_bust(self):
        hand = Hand()
        hand.add_card(Card(1, "Hearts"))
        hand.add_card(Card(9, "Clubs"))
        hand.add_card(Card(5, "Spades"))
        self.assertEqual(hand.value_in_hand, 15)  # 11+9+5=25 -> ace becomes 1

    def test_two_aces_only_one_downgrades(self):
        hand = Hand()
        hand.add_card(Card(1, "Hearts"))
        hand.add_card(Card(1, "Spades"))
        hand.add_card(Card(9, "Clubs"))
        self.assertEqual(hand.value_in_hand, 21)  # 11+1+9

    def test_clear_empties_hand(self):
        hand = Hand()
        hand.add_card(Card(1, "Hearts"))
        hand.clear()
        self.assertEqual(hand.cards_in_hand, [])
        self.assertEqual(hand.value_in_hand, 0)


class TestParticipants(unittest.TestCase):
    def test_player_starts_with_default_money_and_not_passed(self):
        player = Player()
        self.assertEqual(player.money, 500)
        self.assertFalse(player.passed)

    def test_player_hit_draws_from_deck_into_hand(self):
        deck = Deck()
        starting = len(deck.cards)
        player = Player()
        player.hit(deck)
        self.assertEqual(len(player.hand.cards_in_hand), 1)
        self.assertEqual(len(deck.cards), starting - 1)

    def test_player_stand_sets_passed(self):
        player = Player()
        player.stand()
        self.assertTrue(player.passed)

    def test_dealer_draws_until_seventeen(self):
        dealer = Dealer()
        # rig a deck so we know exactly what the dealer will draw.
        # draw() pops from the END of the list, so cards come out
        # right-to-left: 2, then 6, then 9.
        deck = Deck()
        deck.cards = [Card(9, "Hearts"), Card(6, "Clubs"), Card(2, "Spades")]
        dealer.play(deck)
        # 2 -> 2, still <17. +6 -> 8, still <17. +9 -> 17, stop.
        self.assertEqual(dealer.hand.value_in_hand, 17)
        self.assertEqual(len(deck.cards), 0)  # all three cards were needed


class TestGameVictory(unittest.TestCase):
    def make_game(self, player_cards, dealer_cards, bet="100"):
        game = Game()
        game.state = GameState.PLAYER_TURN
        game.bet_value = bet
        for card in player_cards:
            game.player.hand.add_card(card)
        for card in dealer_cards:
            game.dealer.hand.add_card(card)
        return game

    def test_player_wins_normal_hand(self):
        game = self.make_game(
            [Card(10, "Hearts"), Card(9, "Clubs")],      # 19
            [Card(10, "Spades"), Card(6, "Diamonds")],   # 16
        )
        starting_money = game.player.money
        game.check_victory()
        self.assertEqual(game.victory_text, "You win. Congratulations!")
        self.assertEqual(game.player.money, starting_money + 100)
        self.assertEqual(game.state, GameState.ROUND_OVER)

    def test_natural_blackjack_pays_three_to_two(self):
        game = self.make_game(
            [Card(1, "Hearts"), Card(13, "Clubs")],      # 21, 2 cards
            [Card(10, "Spades"), Card(6, "Diamonds")],   # 16
        )
        starting_money = game.player.money
        game.check_victory()
        self.assertEqual(game.victory_text, "Blackjack!")
        self.assertEqual(game.player.money, starting_money + 150)

    def test_twenty_one_via_hits_is_not_blackjack(self):
        game = self.make_game(
            [Card(7, "Hearts"), Card(7, "Clubs"), Card(7, "Spades")],  # 21, 3 cards
            [Card(10, "Spades"), Card(6, "Diamonds")],                 # 16
        )
        game.check_victory()
        self.assertEqual(game.victory_text, "You win. Congratulations!")

    def test_dealer_wins(self):
        game = self.make_game(
            [Card(10, "Hearts"), Card(6, "Clubs")],      # 16
            [Card(10, "Spades"), Card(9, "Diamonds")],   # 19
        )
        starting_money = game.player.money
        game.check_victory()
        self.assertEqual(game.victory_text, "You lose lmfao.")
        self.assertEqual(game.player.money, starting_money - 100)

    def test_player_bust_prevents_dealer_from_playing(self):
        # check_round_over() is what actually gates dealer.play() in
        # real gameplay -- it must never let the dealer draw once the
        # player has already busted, since check_victory() has no
        # branch for "both sides over 21."
        game = self.make_game(
            [Card(10, "Hearts"), Card(9, "Clubs"), Card(9, "Spades")],  # 28, bust
            [Card(10, "Spades"), Card(6, "Diamonds")],                  # 16
        )
        game.deck = Deck()
        dealer_cards_before = len(game.dealer.hand.cards_in_hand)

        game.check_round_over()

        self.assertEqual(len(game.dealer.hand.cards_in_hand), dealer_cards_before)
        self.assertEqual(game.victory_text, "You lose lmfao.")

    def test_tie(self):
        game = self.make_game(
            [Card(10, "Hearts"), Card(8, "Clubs")],      # 18
            [Card(10, "Spades"), Card(8, "Diamonds")],   # 18
        )
        starting_money = game.player.money
        game.check_victory()
        self.assertEqual(game.victory_text, "It's a tie.")
        self.assertEqual(game.player.money, starting_money)  # unchanged

    def test_losing_to_zero_gives_broke_message(self):
        game = self.make_game(
            [Card(10, "Hearts"), Card(6, "Clubs")],
            [Card(10, "Spades"), Card(9, "Diamonds")],
            bet="500",  # player's entire starting balance
        )
        game.check_victory()
        self.assertEqual(game.player.money, 0)
        self.assertEqual(game.victory_text, "You are out of money. You get nothing! You lose! Good day!")

    def test_unreachable_double_bust_branch(self):
        # In real gameplay check_round_over() never lets the dealer
        # play once the player has already busted, so both sides
        # being over 21 at once can't happen through the normal flow.
        # This manufactures that impossible state directly against
        # check_victory() purely to exercise the fallback branch.
        game = self.make_game(
            [Card(10, "Hearts"), Card(9, "Clubs"), Card(9, "Spades")],   # 28
            [Card(10, "Spades"), Card(9, "Diamonds"), Card(5, "Clubs")], # 24
        )
        game.check_victory()
        self.assertEqual(
            game.victory_text,
            "Some unforseen outcome happened and I have not accounted "
            "for it, so this is also a tie, but I dont really know why or how.",
        )


class TestGameActions(unittest.TestCase):
    def test_confirm_bet_rejects_empty_bet(self):
        game = Game()
        game.bet()
        game.bet_value = ""
        game.confirm_bet()
        self.assertTrue(game.money_error)
        self.assertEqual(game.state, GameState.BETTING)

    def test_confirm_bet_rejects_bet_over_balance(self):
        game = Game()
        game.bet()
        game.bet_value = str(game.player.money + 1)
        game.confirm_bet()
        self.assertTrue(game.money_error)

    def test_confirm_bet_accepts_valid_bet_and_deals(self):
        game = Game()
        game.bet()
        game.bet_value = "50"
        game.confirm_bet()
        self.assertFalse(game.money_error)
        # a natural blackjack on the deal resolves the round instantly,
        # so either state is a valid outcome of a legitimate bet/deal
        self.assertIn(game.state, (GameState.PLAYER_TURN, GameState.ROUND_OVER))
        self.assertEqual(len(game.player.hand.cards_in_hand), 2)
        self.assertEqual(len(game.dealer.hand.cards_in_hand), 2)

    def test_double_fails_when_unaffordable(self):
        game = Game()
        game.bet()
        game.bet_value = "50"
        game.confirm_bet()
        game.player.money = 10  # can't afford doubling 50
        game.double()
        self.assertTrue(game.money_error)
        self.assertEqual(game.bet_value, "50")  # unchanged
        self.assertFalse(game.player.passed)

    def test_double_succeeds_when_affordable(self):
        game = Game()
        game.bet()
        game.bet_value = "50"
        game.confirm_bet()
        game.double()
        self.assertEqual(game.bet_value, "100")
        self.assertTrue(game.player.passed)
        self.assertEqual(len(game.player.hand.cards_in_hand), 3)

    def test_check_round_over_does_nothing_mid_hand(self):
        # rig the deck so the initial deal can't accidentally produce
        # a natural blackjack, which would resolve the round early
        # and make this test flaky.
        rigged = Deck()
        rigged.cards = [Card(2, "Hearts"), Card(3, "Hearts"), Card(9, "Clubs"), Card(8, "Hearts")]
        game = Game()
        game.bet()
        game.bet_value = "50"
        with patch("Game.Deck", return_value=rigged):
            game.confirm_bet()
        game.check_round_over()
        self.assertEqual(game.state, GameState.PLAYER_TURN)

    def test_check_round_over_resolves_after_stand(self):
        game = Game()
        game.bet()
        game.bet_value = "50"
        game.confirm_bet()
        game.player.stand()
        game.check_round_over()
        self.assertEqual(game.state, GameState.ROUND_OVER)
        self.assertNotEqual(game.victory_text, "")

    def test_check_round_over_lets_dealer_play_after_a_clean_stand(self):
        # covers the path where the player stood without busting --
        # distinct from the "still mid-hand" and "player busted" cases
        # already covered above.
        game = Game()
        game.bet()
        game.bet_value = "50"
        game.confirm_bet()
        game.state = GameState.PLAYER_TURN  # in case the initial deal already resolved it
        game.player.hand.clear()
        game.player.hand.add_card(Card(10, "Hearts"))
        game.player.hand.add_card(Card(6, "Clubs"))  # 16, safely under 21
        game.player.stand()

        dealer_cards_before = len(game.dealer.hand.cards_in_hand)
        game.check_round_over()

        self.assertGreaterEqual(len(game.dealer.hand.cards_in_hand), dealer_cards_before)
        self.assertEqual(game.state, GameState.ROUND_OVER)

    def test_hit_adds_a_card_and_clears_money_error(self):
        game = Game()
        game.bet()
        game.bet_value = "50"
        game.confirm_bet()
        game.state = GameState.PLAYER_TURN
        game.money_error = True
        cards_before = len(game.player.hand.cards_in_hand)

        game.hit()

        self.assertEqual(len(game.player.hand.cards_in_hand), cards_before + 1)
        self.assertFalse(game.money_error)

    def test_bet_resets_broke_player_to_a_fresh_one(self):
        game = Game()
        game.player.money = 0
        old_player = game.player

        game.bet()

        self.assertIsNot(game.player, old_player)
        self.assertEqual(game.player.money, 500)
        self.assertEqual(game.state, GameState.BETTING)

    def test_bet_keeps_same_player_when_not_broke(self):
        game = Game()
        old_player = game.player

        game.bet()

        self.assertIs(game.player, old_player)

    def test_new_game_resets_a_player_who_had_stood(self):
        game = Game()
        game.player.stand()
        self.assertTrue(game.player.passed)

        game.new_game()

        self.assertFalse(game.player.passed)

    def test_convert_player_hand_formats_every_card(self):
        game = Game()
        game.player.hand.add_card(Card(1, "Hearts"))
        game.player.hand.add_card(Card(13, "Clubs"))
        self.assertEqual(
            game.convert_player_hand(game.player.hand),
            "Ace of Hearts, King of Clubs",
        )

    def test_convert_dealer_hand_hides_the_first_card(self):
        game = Game()
        game.dealer.hand.add_card(Card(1, "Hearts"))   # hidden
        game.dealer.hand.add_card(Card(13, "Clubs"))    # shown
        self.assertEqual(
            game.convert_dealer_hand(game.dealer.hand),
            "King of Clubs",
        )


    def test_new_game_resolves_immediately_on_natural_blackjack(self):
        # new_game() creates its own Deck() internally, so to force a
        # guaranteed natural 21 on the deal we patch Deck within the
        # Game module to hand back a pre-rigged one instead of a
        # randomly shuffled one.
        rigged = Deck()
        # draw() pops from the end, and deal order is player, player,
        # dealer, dealer -- so the last two entries go to the player.
        rigged.cards = [Card(2, "Hearts"), Card(3, "Hearts"), Card(13, "Clubs"), Card(1, "Hearts")]

        game = Game()
        game.bet_value = "50"

        with patch("Game.Deck", return_value=rigged):
            game.new_game()

        self.assertEqual(game.state, GameState.ROUND_OVER)
        self.assertEqual(game.victory_text, "Blackjack!")


if __name__ == "__main__":
    unittest.main()