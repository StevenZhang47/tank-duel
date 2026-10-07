"""Optional display for automated rollouts; no control over tank actions."""
import pygame

from .client import Renderer, WINDOW
from .simulation import DT


class RolloutViewer:
    def __init__(self, game, seed, speed):
        pygame.init()
        try:
            screen = pygame.display.set_mode(WINDOW)
            pygame.display.set_caption(f'Tank Duel — random rollout, seed {seed}')
            self.renderer = Renderer(
                screen,
                controls=('Green: Random agent · 12 ticks per action',
                          'Red: Stationary opponent'),
                footer=f'Seed {seed}     Playback {speed:g}x     Esc  Quit',
                outcome_hint='Press Esc or close the window to exit',
            )
            self.clock = pygame.time.Clock()
            self.fps = max(1, round(speed / DT))
            self.running = True
            self.renderer.draw(game)
        except Exception:
            pygame.quit()
            raise

    def _events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                self.running = False

    def update(self, game):
        """Called after every physics tick; False requests an early stop."""
        self._events()
        if self.running:
            self.renderer.draw(game)
            # Pace playback only. The simulation always advances by the same DT.
            self.clock.tick(self.fps)
        return self.running

    def show_result(self, game, truncated):
        """Keep the final state visible, including a distinct timeout overlay."""
        if self.running:
            self.renderer.draw(game, status='TIME LIMIT' if truncated else None)
        while self.running:
            self._events()
            self.clock.tick(30)

    def close(self):
        pygame.quit()
