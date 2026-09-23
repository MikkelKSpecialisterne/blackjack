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

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
                return

            if self.game.state == GameState.PLAYER_SELECT:
                if event.unicode in ("1", "2", "3", "4"):
                    self.game.player_amount(int(event.unicode))
                    self.game.bet(self.game.current_player())
            
            elif self.game.state == GameState.BETTING:
                player = self.game.current_player()
                if event.unicode.isdigit() and len(player.bet_value)<9:
                    player.bet_value += event.unicode
                elif event.key == pygame.K_BACKSPACE:
                    player.bet_value = player.bet_value[:-1]
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    self.game.confirm_bet(player)

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.game.state == GameState.PLAYER_TURN:
                player = self.game.current_player()
                if self.view.hit_button.collidepoint(pos):
                    self.game.hit(player)
                    if player.passed:
                        self.game.next_player()
                if self.view.double_button.collidepoint(pos):
                    self.game.double(player)
                    if player.passed:
                        self.game.next_player()
                if self.view.stand_button.collidepoint(pos):
                    self.game.current_player().stand()
                    player.money_error=False
                    self.game.next_player()
            if self.game.state == GameState.ROUND_OVER:
                if self.view.new_game_button.collidepoint(pos):
                    if self.game.remove_bankrupt():
                        self.game.bet(self.game.current_player())
                    else:
                        self.game=Game()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            #self.game.check_round_over()
            self.view.draw(self.game)
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    GameController().run()