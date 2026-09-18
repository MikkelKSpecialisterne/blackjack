import pygame
from View import GameView, WIDTH, HEIGHT
from Game import Game, GameState


class GameController:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Blackjack")
        self.clock = pygame.time.Clock()

        self.view = GameView(self.screen)
        self.running = True
        self.game=Game()
        self.game.bet()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return

        if event.type == pygame.KEYDOWN:
            if self.game.state == GameState.BETTING:
                if event.unicode.isdigit() and len(self.game.bet_value)<9:
                    self.game.bet_value += event.unicode
                elif event.key == pygame.K_BACKSPACE:
                    self.game.bet_value = self.game.bet_value[:-1]
                elif event.key == pygame.K_RETURN:
                    if  not self.game.bet_value == "" and int(self.game.bet_value) <= self.game.player.money:
                        self.game.new_game()
                        self.game.money_error =False
                    else:
                        self.game.money_error=True


        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.view.hit_button.collidepoint(pos) and self.game.state == GameState.PLAYER_TURN:
                self.game.player.hit(self.game.deck)
                self.game.money_error=False
            if self.view.double_button.collidepoint(pos) and self.game.state == GameState.PLAYER_TURN:
                if int(self.game.bet_value)*2 <= self.game.player.money:
                    self.game.bet_value = str(int(self.game.bet_value)*2)
                    self.game.player.hit(self.game.deck)
                    self.game.player.stand()
                else:
                    self.game.money_error=True
            if self.view.stand_button.collidepoint(pos) and self.game.state == GameState.PLAYER_TURN:
                self.game.player.stand()
                self.game.money_error=False
            if self.view.new_game_button.collidepoint(pos) and self.game.state == GameState.ROUND_OVER:
                self.game.bet()
            pass

    def run(self):
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            if ((self.game.player.passed or self.game.player.hand.value_in_hand>21) and self.game.state == GameState.PLAYER_TURN):
                if self.game.player.hand.value_in_hand<22:
                    self.game.dealer.play(self.game.deck)
                self.game.check_victory()
            self.view.draw(self.game)
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    GameController().run()