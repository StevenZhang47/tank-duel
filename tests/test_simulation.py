import math
import unittest

from tank_duel import Action, Game, DT
from tank_duel.physics import Rect, sweep_rect
from tank_duel.simulation import Bullet, Tank, DEFAULT_WALLS, TANK_RADIUS, MAX_BULLETS


class SimulationTests(unittest.TestCase):
    def test_forward_reverse_and_rotation(self):
        game = Game(walls=[])
        for _ in range(120):
            game.step((Action(throttle=1), Action()))
        self.assertAlmostEqual(game.tanks[0].position[0], 235)
        for _ in range(120):
            game.step((Action(throttle=-1), Action()))
        self.assertAlmostEqual(game.tanks[0].position[0], 90)
        game.step((Action(turn=1), Action()))
        self.assertAlmostEqual(game.tanks[0].angle, 2.8 * DT)

    def test_tank_wall_and_other_tank(self):
        game = Game(walls=[Rect(150, 0, 12, 600)])
        for _ in range(200):
            game.step((Action(throttle=1), Action()))
        self.assertLessEqual(game.tanks[0].position[0], 150 - TANK_RADIUS)
        game = Game(walls=[])
        game.tanks[1].position = (150, 90)
        for _ in range(100):
            game.step((Action(throttle=1), Action()))
        self.assertGreaterEqual(math.dist(*(t.position for t in game.tanks)), 2 * TANK_RADIUS - 1e-5)

    def test_fast_bullet_first_bounce_second_disappears(self):
        game = Game(walls=[Rect(200, 0, 12, 600), Rect(0, 0, 12, 600)])
        game.tanks = [Tank((400, 400), 0), Tank((600, 400), 0)]
        bullet = Bullet((100, 100), (30000, 0), 0)
        game.bullets = [bullet]
        game.step()
        self.assertEqual(bullet.bounces, 1)
        self.assertLess(bullet.velocity[0], 0)
        self.assertEqual(len(game.bullets), 1)
        game.step()
        self.assertEqual(game.bullets, [])

    def test_boundary_corner_counts_as_one_bounce(self):
        game = Game(walls=DEFAULT_WALLS[:4])
        bullet = Bullet((890, 590), (1200, 1200), 0)
        game.bullets = [bullet]
        game.step()
        self.assertEqual(bullet.bounces, 1)
        self.assertEqual(bullet.velocity, (-1200, -1200))
        self.assertEqual(len(game.bullets), 1)

    def test_rounded_wall_corner(self):
        hit = sweep_rect((90, 90), (20, 20), Rect(100, 100, 20, 20), 4)
        self.assertIsNotNone(hit)
        self.assertAlmostEqual(hit[0], (10 - 4 / math.sqrt(2)) / 20)
        self.assertIsNone(sweep_rect((95, 95), (1, 0), Rect(100, 100, 20, 20), 4))

    def test_fast_hit_winner_score_and_frozen_round(self):
        game = Game(walls=[])
        game.tanks[1].position = (180, 90)
        game.bullets = [Bullet((120, 90), (20000, 0), 0)]
        game.step()
        self.assertTrue(game.finished)
        self.assertEqual(game.winner, 0)
        self.assertEqual(game.scores, [1, 0])
        self.assertFalse(game.tanks[1].alive)
        game.step()
        self.assertEqual(game.scores, [1, 0])

    def test_shooter_ignored_until_ricochet_then_destroyed(self):
        game = Game(walls=[Rect(150, 0, 12, 600)])
        game.bullets = [Bullet((90, 90), (420, 0), 0)]
        game.step()
        self.assertTrue(game.tanks[0].alive)
        for _ in range(50):
            game.step()
        self.assertFalse(game.tanks[0].alive)
        self.assertEqual(game.winner, 1)

    def test_simultaneous_draw_and_restart(self):
        game = Game(walls=[])
        game.bullets = [Bullet((60, 90), (2400, 0), 1), Bullet((840, 510), (-2400, 0), 0)]
        game.step()
        self.assertTrue(game.finished)
        self.assertIsNone(game.winner)
        self.assertEqual(game.scores, [0, 0])
        game.scores = [2, 3]
        game.restart()
        self.assertFalse(game.finished)
        self.assertIsNone(game.winner)
        self.assertEqual(game.bullets, [])
        self.assertEqual(game.ticks, 0)
        self.assertTrue(all(t.alive and t.cooldown == 0 for t in game.tanks))
        self.assertEqual(game.tanks[0].position, (90, 90))
        self.assertEqual(game.scores, [2, 3])

    def test_shot_direction_cooldown_limit_and_blocked_muzzle(self):
        game = Game(walls=[])
        game.tanks[0].angle = math.pi / 2
        game.step((Action(shoot=True), Action()))
        self.assertAlmostEqual(game.bullets[0].velocity[0], 0)
        self.assertAlmostEqual(game.bullets[0].velocity[1], 420)
        for _ in range(10):
            game.step((Action(shoot=True), Action()))
        self.assertEqual(len(game.bullets), 1)
        for _ in range(300):
            game.step((Action(shoot=True), Action()))
        self.assertEqual(len(game.bullets), MAX_BULLETS)
        game = Game(walls=[Rect(112, 0, 12, 600)])
        game.step((Action(shoot=True), Action()))
        self.assertEqual(game.bullets, [])
        self.assertEqual(game.tanks[0].cooldown, 0)

    def test_wall_slide_and_connected_arena(self):
        game = Game(walls=[Rect(150, 0, 12, 600)])
        game.tanks[0].angle = math.pi / 4
        for _ in range(120):
            game.step((Action(throttle=1), Action()))
        self.assertLessEqual(game.tanks[0].position[0], 134)
        self.assertGreater(game.tanks[0].position[1], 190)
        # Flood fill tank-safe sample positions; verify the maze has no islands.
        free = {(x, y) for x in range(20, 900, 10) for y in range(20, 600, 10)
                if not any(w.overlaps_circle((x, y), TANK_RADIUS) for w in DEFAULT_WALLS)}
        visited = {(90, 90)}
        pending = [(90, 90)]
        while pending:
            x, y = pending.pop()
            for point in ((x + 10, y), (x - 10, y), (x, y + 10), (x, y - 10)):
                if point in free and point not in visited:
                    visited.add(point)
                    pending.append(point)
        self.assertEqual(visited, free)
        self.assertIn((810, 510), visited)

    def test_repeatability_and_action_validation(self):
        a, b = Game(), Game()
        for _ in range(200):
            actions = (Action(1, 0.2, True), Action(-1, -0.3, True))
            a.step(actions)
            b.step(actions)
        self.assertEqual(a.tanks, b.tanks)
        self.assertEqual(a.bullets, b.bullets)
        with self.assertRaises(ValueError):
            a.step([Action()])


if __name__ == '__main__':
    unittest.main()
