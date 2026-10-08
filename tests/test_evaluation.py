"""Ensure watching evaluation does not change the measured episode."""
import contextlib
import io
import os
import unittest
from unittest.mock import patch

from tank_duel.env import TankDuelEnv
from tank_duel.evaluate_random import evaluate_episode


class EvaluationTests(unittest.TestCase):
    def test_seed_repeatability(self):
        expected = {'outcome': 'loss', 'ticks': 56}
        self.assertEqual(evaluate_episode(10000), expected)
        self.assertEqual(evaluate_episode(10000), expected)

    def test_visual_matches_headless_state(self):
        with patch.dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy'):
            import pygame

            for budget in (25, 1200):
                headless, visual = TankDuelEnv(), TankDuelEnv()
                with patch('tank_duel.evaluate_random.TankDuelEnv', return_value=headless):
                    expected = evaluate_episode(10000, max_ticks=budget)
                events = [[] for _ in range(expected['ticks'])]
                events.append([pygame.event.Event(pygame.QUIT)])
                with patch('tank_duel.evaluate_random.TankDuelEnv', return_value=visual), \
                     patch('pygame.event.get', side_effect=events), \
                     patch('pygame.time.Clock'), \
                     contextlib.redirect_stdout(io.StringIO()):
                    actual = evaluate_episode(10000, visualize=True, speed=0.25,
                                              max_ticks=budget)
                self.assertEqual(actual, expected)
                self.assertEqual(visual.game.tanks, headless.game.tanks)
                self.assertEqual(visual.game.bullets, headless.game.bullets)
                self.assertEqual(visual.game.scores, headless.game.scores)
                self.assertIsNone(visual.on_tick)
                self.assertFalse(pygame.get_init())

    def test_early_exit_is_not_a_draw(self):
        with patch.dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy'):
            import pygame

            for event in (pygame.event.Event(pygame.QUIT),
                          pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)):
                with patch('pygame.event.get', return_value=[event]), \
                     contextlib.redirect_stdout(io.StringIO()):
                    actual = evaluate_episode(10000, visualize=True)
                self.assertEqual(actual, {'outcome': 'interrupted', 'ticks': 1})
                self.assertFalse(pygame.get_init())


if __name__ == '__main__':
    unittest.main()
