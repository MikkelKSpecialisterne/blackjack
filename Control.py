import pygame
from View import GameView, WIDTH, HEIGHT
from Game import Game


class GameController:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Blackjack")
        self.clock = pygame.time.Clock()

        self.view = GameView(self.screen)
        self.running = True
        self.game=Game()
        self.game.new_game()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.view.hit_button.collidepoint(pos) and self.game.game_over==False:
                self.game.player.hit(self.game.deck)
            if self.view.double_button.collidepoint(pos) and self.game.game_over==False:
                self.game.player.hit(self.game.deck)
                self.game.player.stand()
            if self.view.stand_button.collidepoint(pos) and self.game.game_over==False:
                self.game.player.stand()
            if self.view.new_game_button.collidepoint(pos) and self.game.game_over== True:
                self.game.new_game()
            pass

    def run(self):
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            if (self.game.player.passed or self.game.player.hand.value_in_hand>21 and self.game.game_over == False):
                self.game.dealer.play(self.game.deck)
                self.game.check_victory()
            self.view.draw(self.game)
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    GameController().run()