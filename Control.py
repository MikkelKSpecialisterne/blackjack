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
            # TODO: check pos against self.view's button rects,
            # call the matching method on self.game
            pass

    def run(self):
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)

            self.view.draw(self.game)
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    GameController().run()