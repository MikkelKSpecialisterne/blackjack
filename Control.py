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
            if event.key == pygame.K_ESCAPE:
                self.running = False
                return
            if self.game.state == GameState.BETTING:
                if event.unicode.isdigit() and len(self.game.bet_value)<9:
                    self.game.bet_value += event.unicode
                elif event.key == pygame.K_BACKSPACE:
                    self.game.bet_value = self.game.bet_value[:-1]
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    self.game.confirm_bet()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.view.hit_button.collidepoint(pos) and self.game.state == GameState.PLAYER_TURN:
                self.game.hit()
            if self.view.double_button.collidepoint(pos) and self.game.state == GameState.PLAYER_TURN:
                self.game.double()
            if self.view.stand_button.collidepoint(pos) and self.game.state == GameState.PLAYER_TURN:
                self.game.player.stand()
                self.game.money_error=False
            if self.view.new_game_button.collidepoint(pos) and self.game.state == GameState.ROUND_OVER:
                self.game.bet()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            self.game.check_round_over()
            self.view.draw(self.game)
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    GameController().run()