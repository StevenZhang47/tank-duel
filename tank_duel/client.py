"""Pygame rendering and keyboard input; simulation owns all gameplay rules."""
from math import cos, sin
import pygame

from .simulation import Action, Game, DT, WIDTH, HEIGHT

OFFSET = (30, 100)
WINDOW = (WIDTH + 60, HEIGHT + 170)
GREEN, RED = (41, 168, 78), (222, 62, 54)
BACKGROUND = (232, 233, 235)
INK = (22, 24, 27)


def keyboard_actions(keys):
    return (
        Action(int(keys[pygame.K_w]) - int(keys[pygame.K_s]),
               int(keys[pygame.K_d]) - int(keys[pygame.K_a]), keys[pygame.K_SPACE]),
        Action(int(keys[pygame.K_UP]) - int(keys[pygame.K_DOWN]),
               int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT]), keys[pygame.K_RETURN]),
    )


class Renderer:
    def __init__(self, screen, *, controls=None, footer=None, outcome_hint=None):
        self.screen = screen
        self.controls = controls or (
            'Green: W/S move · A/D turn · Space fire',
            'Red: Arrows move/turn · Enter fire',
        )
        self.footer = footer or 'R  Restart round     Esc  Quit'
        self.outcome_hint = outcome_hint or 'Press R to play again'
        self.font = pygame.font.SysFont('Helvetica', 18)
        self.title = pygame.font.SysFont('Helvetica', 29, bold=True)
        # Render at 2x resolution for clean tank silhouettes and round bullets.
        self.arena = pygame.Surface((WIDTH * 2, HEIGHT * 2))

    def text(self, value, position, color=INK, large=False):
        self.screen.blit((self.title if large else self.font).render(value, True, color), position)

    def draw(self, game, *, status=None):
        self.screen.fill((249, 249, 250))
        self.text('TANK DUEL', (30, 18), large=True)
        self.text(f'GREEN  {game.scores[0]}', (645, 25), GREEN)
        self.text(f'RED  {game.scores[1]}', (810, 25), RED)
        self.text(self.controls[0], (30, 63), GREEN)
        self.text(self.controls[1], (535, 63), RED)
        self.arena.fill(BACKGROUND)
        for wall in game.walls:
            pygame.draw.rect(self.arena, (12, 12, 13), pygame.Rect(round(wall.x * 2), round(wall.y * 2), round(wall.w * 2), round(wall.h * 2)))
        for index, tank in enumerate(game.tanks):
            if not tank.alive:
                continue
            x, y = tank.position
            forward = (cos(tank.angle), sin(tank.angle))
            side = (-forward[1], forward[0])

            def point(front, lateral):
                return (round(2 * (x + forward[0] * front + side[0] * lateral)),
                        round(2 * (y + forward[1] * front + side[1] * lateral)))

            # The visible hull fits inside the circular collision footprint.
            for lateral in (-10, 10):
                pygame.draw.polygon(self.arena, INK, [point(a, b) for a, b in ((-11, lateral - 3), (11, lateral - 3), (11, lateral + 3), (-11, lateral + 3))])
            color = (GREEN, RED)[index]
            pygame.draw.polygon(self.arena, color, [point(a, b) for a, b in ((-11, -8), (11, -8), (11, 8), (-11, 8))])
            pygame.draw.line(self.arena, INK, point(0, 0), point(24, 0), 10)
            pygame.draw.line(self.arena, color, point(0, 0), point(23, 0), 6)
            pygame.draw.circle(self.arena, INK, point(0, 0), 13)
            pygame.draw.circle(self.arena, color, point(0, 0), 10)
        for bullet in game.bullets:
            pygame.draw.circle(self.arena, (0, 0, 0), (round(bullet.position[0] * 2), round(bullet.position[1] * 2)), 8)
        self.screen.blit(pygame.transform.smoothscale(self.arena, (WIDTH, HEIGHT)), OFFSET)
        pygame.draw.rect(self.screen, INK, (*OFFSET, WIDTH, HEIGHT), 6)
        self.text(self.footer, (30, HEIGHT + 122))
        if game.finished or status is not None:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((245, 245, 245, 145))
            self.screen.blit(overlay, OFFSET)
            message = status if status is not None else ('DRAW' if game.winner is None else ('GREEN WINS' if game.winner == 0 else 'RED WINS'))
            label = self.title.render(message, True, INK)
            self.screen.blit(label, label.get_rect(center=(WINDOW[0] // 2, 360)))
            label = self.font.render(self.outcome_hint, True, INK)
            self.screen.blit(label, label.get_rect(center=(WINDOW[0] // 2, 400)))
        pygame.display.flip()


def main():
    pygame.init()
    try:
        screen = pygame.display.set_mode(WINDOW)
        pygame.display.set_caption('Tank Duel')
        renderer = Renderer(screen)
        game = Game()
        clock = pygame.time.Clock()
        accumulator = 0.0
        running = True
        while running:
            # Cap stalls so dragging a window does not cause a huge catch-up burst.
            accumulator += min(clock.tick(120) / 1000., 0.1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        game.restart()
                        accumulator = 0.0
                elif event.type == pygame.WINDOWFOCUSLOST:
                    accumulator = 0.0
            actions = keyboard_actions(pygame.key.get_pressed()) if pygame.key.get_focused() else (Action(), Action())
            while accumulator >= DT:
                game.step(actions)
                accumulator -= DT
            renderer.draw(game)
    finally:
        pygame.quit()
