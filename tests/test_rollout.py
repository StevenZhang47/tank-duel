"""Rollout checks, including optional rendering through SDL's dummy driver."""
import contextlib
import io
import os
import unittest
from unittest.mock import patch

from tank_duel import Game
from tank_duel.random_rollout import run_random_rollout


class RolloutTests(unittest.TestCase):
    def test_headless_budget_and_terminal_result(self):
        short = run_random_rollout(seed=1, max_ticks=25)
        self.assertEqual(short['ticks'], 25)
        self.assertAlmostEqual(short['simulated_seconds'], 25 / 120)
        self.assertFalse(short['terminated'])
        self.assertTrue(short['truncated'])
        self.assertFalse(short['interrupted'])
        long = run_random_rollout(seed=1, max_ticks=1200)
        self.assertEqual(long['ticks'], 43)
        self.assertTrue(long['terminated'])
        self.assertEqual(long['reward'], -1.)

    def test_visual_and_headless_have_identical_state(self):
        with patch.dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy'):
            import pygame
            from tank_duel.rollout_viewer import RolloutViewer

            for budget in (25, 1200):
                headless_game, visual_game = Game(), Game()
                with patch('tank_duel.random_rollout.Game', return_value=headless_game):
                    expected = run_random_rollout(seed=1, max_ticks=budget)
                # Exercise real rendering and pacing, with an automatic quit
                # event after the last physics tick enters the result screen.
                events = [[] for _ in range(expected['ticks'])]
                events.append([pygame.event.Event(pygame.QUIT)])
                with patch('tank_duel.random_rollout.Game', return_value=visual_game), \
                     patch('pygame.event.get', side_effect=events), \
                     patch('pygame.time.Clock') as clock, \
                     contextlib.redirect_stdout(io.StringIO()):
                    actual = run_random_rollout(seed=1, max_ticks=budget,
                                                visualize=True, speed=0.25)
                    self.assertIn(((30,), {}), clock.return_value.tick.call_args_list)
                self.assertEqual(actual, expected)
                self.assertEqual(visual_game.tanks, headless_game.tanks)
                self.assertEqual(visual_game.bullets, headless_game.bullets)
                self.assertEqual(visual_game.scores, headless_game.scores)
                self.assertFalse(pygame.get_init())

    def test_visual_quit_is_interruption(self):
        with patch.dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy'):
            import pygame
            for event in (pygame.event.Event(pygame.QUIT),
                          pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)):
                with patch('pygame.event.get', return_value=[event]), \
                     contextlib.redirect_stdout(io.StringIO()):
                    result = run_random_rollout(seed=1, visualize=True)
                self.assertEqual(result['ticks'], 1)
                self.assertTrue(result['interrupted'])
                self.assertFalse(result['terminated'])
                self.assertFalse(result['truncated'])
                self.assertFalse(pygame.get_init())


if __name__ == '__main__':
    unittest.main()
