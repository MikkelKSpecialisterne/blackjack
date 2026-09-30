import unittest
from unittest.mock import patch

from Deck import Card, Deck, Hand
from Participant import Player, Dealer
from Game import Game, GameState, RoundResult


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
    def test_player_starts_with_default_attributes(self):
        player = Player(1)
        self.assertEqual(player.id, 1)
        self.assertEqual(player.money, 500)
        self.assertFalse(player.passed)
        self.assertEqual(player.bet_value, "")
        self.assertFalse(player.money_error)
        self.assertIsNone(player.round_result)
        self.assertFalse(player.bankrupt)

    def test_player_hit_draws_from_deck_into_hand(self):
        deck = Deck()
        starting = len(deck.cards)
        player = Player(1)
        player.hit(deck)
        self.assertEqual(len(player.hand.cards_in_hand), 1)
        self.assertEqual(len(deck.cards), starting - 1)

    def test_player_hit_that_busts_sets_passed(self):
        deck = Deck()
        deck.cards = [Card(10, "Hearts"), Card(9, "Clubs"), Card(9, "Spades")]
        player = Player(1)
        player.hit(deck)  # 9
        self.assertFalse(player.passed)
        player.hit(deck)  # 9+9=18
        self.assertFalse(player.passed)
        player.hit(deck)  # +10 = 28, bust
        self.assertTrue(player.passed)

    def test_player_stand_sets_passed(self):
        player = Player(1)
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


class TestPlayerAmount(unittest.TestCase):
    def test_new_game_starts_at_player_select_with_no_players(self):
        game = Game()
        self.assertEqual(game.state, GameState.PLAYER_SELECT)
        self.assertEqual(game.players, [])

    def test_player_amount_creates_the_requested_number_of_players(self):
        game = Game()
        game.player_amount(3)
        self.assertEqual(len(game.players), 3)

    def test_player_amount_assigns_sequential_one_based_ids(self):
        game = Game()
        game.player_amount(4)
        self.assertEqual([p.id for p in game.players], [1, 2, 3, 4])

    def test_player_amount_gives_each_player_the_default_starting_money(self):
        game = Game()
        game.player_amount(2)
        self.assertTrue(all(p.money == 500 for p in game.players))


class TestCheckVictory(unittest.TestCase):
    def make_resolved_players(self, player_cards, dealer_cards, bet="100"):
        game = Game()
        player = Player(1)
        player.bet_value = bet
        for card in player_cards:
            player.hand.add_card(card)
        for card in dealer_cards:
            game.dealer.hand.add_card(card)
        return game, player

    def test_player_wins_normal_hand(self):
        game, player = self.make_resolved_players(
            [Card(10, "Hearts"), Card(9, "Clubs")],      # 19
            [Card(10, "Spades"), Card(6, "Diamonds")],   # 16
        )
        starting_money = player.money
        result = game.check_victory(player)
        self.assertEqual(result, RoundResult.WIN)
        self.assertEqual(player.money, starting_money + 100)

    def test_natural_blackjack_pays_three_to_two(self):
        game, player = self.make_resolved_players(
            [Card(1, "Hearts"), Card(13, "Clubs")],      # 21, 2 cards
            [Card(10, "Spades"), Card(6, "Diamonds")],   # 16
        )
        starting_money = player.money
        result = game.check_victory(player)
        self.assertEqual(result, RoundResult.BLACKJACK)
        self.assertEqual(player.money, starting_money + 150)

    def test_twenty_one_via_hits_is_not_blackjack(self):
        game, player = self.make_resolved_players(
            [Card(7, "Hearts"), Card(7, "Clubs"), Card(7, "Spades")],  # 21, 3 cards
            [Card(10, "Spades"), Card(6, "Diamonds")],                 # 16
        )
        result = game.check_victory(player)
        self.assertEqual(result, RoundResult.WIN)

    def test_dealer_wins(self):
        game, player = self.make_resolved_players(
            [Card(10, "Hearts"), Card(6, "Clubs")],      # 16
            [Card(10, "Spades"), Card(9, "Diamonds")],   # 19
        )
        starting_money = player.money
        result = game.check_victory(player)
        self.assertEqual(result, RoundResult.LOSE)
        self.assertEqual(player.money, starting_money - 100)

    def test_losing_entire_balance_sets_bankrupt(self):
        game, player = self.make_resolved_players(
            [Card(10, "Hearts"), Card(6, "Clubs")],
            [Card(10, "Spades"), Card(9, "Diamonds")],
            bet="500",  # player's entire starting balance
        )
        game.check_victory(player)
        self.assertEqual(player.money, 0)
        self.assertTrue(player.bankrupt)

    def test_tie(self):
        game, player = self.make_resolved_players(
            [Card(10, "Hearts"), Card(8, "Clubs")],      # 18
            [Card(10, "Spades"), Card(8, "Diamonds")],   # 18
        )
        starting_money = player.money
        result = game.check_victory(player)
        self.assertEqual(result, RoundResult.TIE)
        self.assertEqual(player.money, starting_money)  # unchanged

    def test_both_busted_still_resolves_to_a_loss(self):
        # round_over() never actually lets this combination arise in
        # real play (the dealer never plays once everyone's busted),
        # but check_victory()'s own "dealer > 21 and p > 21" clause
        # means a double-bust would still correctly resolve as a loss
        # for the player if it were ever reached directly.
        game, player = self.make_resolved_players(
            [Card(10, "Hearts"), Card(9, "Clubs"), Card(9, "Spades")],   # 28
            [Card(10, "Spades"), Card(9, "Diamonds"), Card(5, "Clubs")], # 24
        )
        result = game.check_victory(player)
        self.assertEqual(result, RoundResult.LOSE)


class TestConvertHands(unittest.TestCase):
    def test_convert_player_hand_formats_every_card(self):
        game = Game()
        hand = Hand()
        hand.add_card(Card(1, "Hearts"))
        hand.add_card(Card(13, "Clubs"))
        self.assertEqual(game.convert_player_hand(hand), "Ace of Hearts, King of Clubs")

    def test_convert_dealer_hand_hides_the_first_card(self):
        game = Game()
        hand = Hand()
        hand.add_card(Card(1, "Hearts"))   # hidden
        hand.add_card(Card(13, "Clubs"))   # shown
        self.assertEqual(game.convert_dealer_hand(hand), "King of Clubs")


class TestHitAndDouble(unittest.TestCase):
    def setup_single_player_mid_hand(self):
        rigged = Deck()
        # order matters: draw() pops from the end. Sequence drawn is
        # player, player, dealer, dealer -- leaving one spare card at
        # the front for a follow-up hit() in the test itself.
        rigged.cards = [Card(9, "Clubs"), Card(2, "Hearts"), Card(3, "Hearts"), Card(9, "Clubs"), Card(8, "Hearts")]
        game = Game()
        game.player_amount(1)
        player = game.current_player()
        with patch("Game.Deck", return_value=rigged):
            game.new_game()
        player.bet_value = "50"
        return game, player

    def test_hit_adds_a_card_and_clears_money_error(self):
        game, player = self.setup_single_player_mid_hand()
        player.money_error = True
        cards_before = len(player.hand.cards_in_hand)

        game.hit(player)

        self.assertEqual(len(player.hand.cards_in_hand), cards_before + 1)
        self.assertFalse(player.money_error)

    def test_double_fails_when_unaffordable(self):
        game, player = self.setup_single_player_mid_hand()
        player.money = 10  # can't afford doubling 50
        game.double(player)
        self.assertTrue(player.money_error)
        self.assertEqual(player.bet_value, "50")  # unchanged
        self.assertFalse(player.passed)

    def test_double_succeeds_when_affordable(self):
        game, player = self.setup_single_player_mid_hand()
        cards_before = len(player.hand.cards_in_hand)
        game.double(player)
        self.assertEqual(player.bet_value, "100")
        self.assertTrue(player.passed)
        self.assertEqual(len(player.hand.cards_in_hand), cards_before + 1)


class TestConfirmBet(unittest.TestCase):
    def test_confirm_bet_rejects_empty_bet(self):
        game = Game()
        game.player_amount(1)
        player = game.current_player()
        game.bet(player)
        player.bet_value = ""
        game.confirm_bet(player)
        self.assertTrue(player.money_error)
        self.assertEqual(game.state, GameState.BETTING)

    def test_confirm_bet_rejects_bet_over_balance(self):
        game = Game()
        game.player_amount(1)
        player = game.current_player()
        game.bet(player)
        player.bet_value = str(player.money + 1)
        game.confirm_bet(player)
        self.assertTrue(player.money_error)

    def test_confirm_bet_rejects_zero_or_negative(self):
        game = Game()
        game.player_amount(1)
        player = game.current_player()
        game.bet(player)
        player.bet_value = "0"
        game.confirm_bet(player)
        self.assertTrue(player.money_error)

    def test_confirm_bet_advances_turn_when_more_players_still_betting(self):
        game = Game()
        game.player_amount(3)
        first = game.current_player()
        game.bet(first)
        first.bet_value = "50"

        game.confirm_bet(first)

        self.assertEqual(game.player_turn, 1)
        self.assertEqual(game.state, GameState.BETTING)  # round hasn't started yet

    def test_confirm_bet_starts_the_round_once_the_last_player_bets(self):
        rigged = Deck()
        # 2 players * 2 cards + dealer * 2 cards = 8 cards needed;
        # chosen so nobody has a natural 21.
        rigged.cards = [
            Card(2, "Hearts"), Card(3, "Hearts"),   # dealer's two cards
            Card(4, "Hearts"), Card(5, "Hearts"),   # player 2's two cards
            Card(6, "Hearts"), Card(7, "Hearts"),   # player 1's two cards
            Card(9, "Clubs"), Card(9, "Spades"),    # unused padding
        ]
        game = Game()
        game.player_amount(2)
        p1, p2 = game.players
        p1.bet_value = "50"
        p2.bet_value = "50"

        game.confirm_bet(p1)
        with patch("Game.Deck", return_value=rigged):
            game.confirm_bet(p2)

        self.assertEqual(game.player_turn, 0)
        self.assertIn(game.state, (GameState.PLAYER_TURN, GameState.ROUND_OVER))
        self.assertEqual(len(p1.hand.cards_in_hand), 2)
        self.assertEqual(len(p2.hand.cards_in_hand), 2)
        self.assertEqual(len(game.dealer.hand.cards_in_hand), 2)


class TestNewGame(unittest.TestCase):
    def deal_with_rigged_deck(self, rigged_cards, player_count=2):
        rigged = Deck()
        rigged.cards = rigged_cards
        game = Game()
        game.player_amount(player_count)
        with patch("Game.Deck", return_value=rigged):
            game.new_game()
        return game

    def test_new_game_deals_two_cards_to_every_player_and_the_dealer(self):
        rigged_cards = [
            Card(2, "Hearts"), Card(3, "Hearts"),
            Card(4, "Hearts"), Card(5, "Hearts"),
            Card(6, "Hearts"), Card(7, "Hearts"),
        ]
        game = self.deal_with_rigged_deck(rigged_cards)
        for p in game.players:
            self.assertEqual(len(p.hand.cards_in_hand), 2)
        self.assertEqual(len(game.dealer.hand.cards_in_hand), 2)

    def test_new_game_resets_a_player_who_had_stood_previously(self):
        game = Game()
        game.player_amount(1)
        game.current_player().stand()
        self.assertTrue(game.current_player().passed)

        rigged = Deck()
        rigged.cards = [Card(2, "Hearts"), Card(3, "Hearts"), Card(4, "Hearts"), Card(5, "Hearts")]
        with patch("Game.Deck", return_value=rigged):
            game.new_game()

        self.assertFalse(game.current_player().passed)

    def test_natural_blackjack_on_the_deal_auto_passes_that_player(self):
        # last two entries (drawn first, since draw() pops from the end)
        # go to player 1.
        rigged_cards = [
            Card(2, "Hearts"), Card(3, "Hearts"),   # dealer
            Card(4, "Hearts"), Card(5, "Hearts"),   # player 2
            Card(13, "Clubs"), Card(1, "Hearts"),   # player 1: natural 21
        ]
        game = self.deal_with_rigged_deck(rigged_cards)
        self.assertTrue(game.players[0].passed)

    def test_dealer_natural_blackjack_resolves_the_round_immediately(self):
        rigged_cards = [
            Card(13, "Clubs"), Card(1, "Hearts"),   # dealer: natural 21
            Card(4, "Hearts"), Card(5, "Hearts"),   # player 2
            Card(6, "Hearts"), Card(7, "Hearts"),   # player 1
        ]
        rigged = Deck()
        rigged.cards = rigged_cards
        game = Game()
        game.player_amount(2)
        # bets must be in place before new_game() runs, since a dealer
        # blackjack resolves everyone immediately as part of dealing
        for p in game.players:
            p.bet_value = "0"

        with patch("Game.Deck", return_value=rigged):
            game.new_game()

        self.assertEqual(game.state, GameState.ROUND_OVER)

    def test_skips_forward_past_a_player_auto_passed_by_natural_blackjack(self):
        rigged_cards = [
            Card(2, "Hearts"), Card(3, "Hearts"),   # dealer, not 21
            Card(4, "Hearts"), Card(5, "Hearts"),   # player 2, not 21
            Card(13, "Clubs"), Card(1, "Hearts"),   # player 1: natural 21
        ]
        game = self.deal_with_rigged_deck(rigged_cards)
        self.assertEqual(game.state, GameState.PLAYER_TURN)
        self.assertEqual(game.player_turn, 1)  # skipped past player 1


class TestNextPlayer(unittest.TestCase):
    def test_next_player_advances_the_turn_index(self):
        game = Game()
        game.player_amount(3)
        game.next_player()
        self.assertEqual(game.player_turn, 1)

    def test_next_player_skips_over_players_who_already_passed(self):
        game = Game()
        game.player_amount(3)
        game.players[1].passed = True  # skip this one
        game.next_player()
        self.assertEqual(game.player_turn, 2)

    def test_next_player_ends_the_round_once_everyone_has_passed(self):
        game = Game()
        game.player_amount(2)
        for p in game.players:
            p.passed = True
            p.bet_value = "0"
        game.deck = Deck()

        game.next_player()

        self.assertEqual(game.state, GameState.ROUND_OVER)
        self.assertTrue(all(p.round_result is not None for p in game.players))


class TestRoundOver(unittest.TestCase):
    def test_round_over_skips_dealer_play_when_everyone_busted(self):
        game = Game()
        game.player_amount(2)
        for p in game.players:
            p.hand.add_card(Card(10, "Hearts"))
            p.hand.add_card(Card(9, "Clubs"))
            p.hand.add_card(Card(9, "Spades"))  # 28, bust
            p.bet_value = "0"
        dealer_cards_before = len(game.dealer.hand.cards_in_hand)

        game.round_over()

        self.assertEqual(len(game.dealer.hand.cards_in_hand), dealer_cards_before)

    def test_round_over_lets_dealer_play_when_a_player_is_still_in(self):
        rigged = Deck()
        # draw() pops from the end: dealer draws 9H first (total 9,
        # still <17), then 9S (total 18, stop).
        rigged.cards = [Card(9, "Spades"), Card(9, "Hearts")]
        game = Game()
        game.deck = rigged
        game.player_amount(1)
        game.current_player().bet_value = "0"
        # dealer starts empty (0 < 22), so round_over should call play()
        game.round_over()
        self.assertGreater(len(game.dealer.hand.cards_in_hand), 0)

    def test_round_over_sets_result_and_clears_bet_for_every_player(self):
        game = Game()
        game.player_amount(2)
        for p in game.players:
            p.bet_value = "0"
        game.deck = Deck()

        game.round_over()

        for p in game.players:
            self.assertIsNotNone(p.round_result)
            self.assertEqual(p.bet_value, "")

    def test_round_over_sets_state_and_resets_turn(self):
        game = Game()
        game.player_amount(2)
        for p in game.players:
            p.bet_value = "0"
        game.deck = Deck()
        game.player_turn = 1

        game.round_over()

        self.assertEqual(game.state, GameState.ROUND_OVER)
        self.assertEqual(game.player_turn, 0)


class TestRemoveBankrupt(unittest.TestCase):
    def test_removes_only_bankrupt_players(self):
        game = Game()
        game.player_amount(3)
        game.players[1].bankrupt = True

        still_playing = game.remove_bankrupt()

        self.assertTrue(still_playing)
        self.assertEqual(len(game.players), 2)
        self.assertTrue(all(not p.bankrupt for p in game.players))

    def test_removing_everyone_returns_false(self):
        game = Game()
        game.player_amount(2)
        for p in game.players:
            p.bankrupt = True

        still_playing = game.remove_bankrupt()

        self.assertFalse(still_playing)
        self.assertEqual(game.players, [])

    def test_survivors_keep_their_original_ids(self):
        game = Game()
        game.player_amount(3)
        game.players[0].bankrupt = True  # player id 1 removed

        game.remove_bankrupt()

        self.assertEqual([p.id for p in game.players], [2, 3])


class TestCurrentPlayer(unittest.TestCase):
    def test_current_player_returns_the_player_at_player_turn(self):
        game = Game()
        game.player_amount(3)
        game.player_turn = 2
        self.assertIs(game.current_player(), game.players[2])


if __name__ == "__main__":
    unittest.main()