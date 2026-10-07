"""Deterministic fixed-step game state. Importable without Pygame."""
from __future__ import annotations

from dataclasses import dataclass
from math import cos, sin, pi
from typing import Sequence

from .physics import Rect, Vec, add, mul, dot, sweep_circle, sweep_walls

DT = 1 / 120
WIDTH, HEIGHT = 900, 600
TANK_RADIUS = 16.0
BULLET_RADIUS = 4.0
MOVE_SPEED = 145.0
TURN_SPEED = 2.8
BULLET_SPEED = 420.0
COOLDOWN = 0.32
MAX_BULLETS = 5
MUZZLE_DISTANCE = 29.0

# All passages are at least 90 px across. Walls connect into a fixed maze.
DEFAULT_WALLS = (
    Rect(-20, -20, WIDTH + 40, 20), Rect(-20, HEIGHT, WIDTH + 40, 20),
    Rect(-20, 0, 20, HEIGHT), Rect(WIDTH, 0, 20, HEIGHT),
    Rect(180, 0, 12, 200), Rect(180, 290, 12, 200),
    Rect(180, 290, 180, 12), Rect(350, 110, 12, 192),
    Rect(350, 400, 12, 200), Rect(450, 110, 270, 12),
    Rect(540, 210, 12, 280), Rect(540, 480, 180, 12),
    Rect(710, 110, 12, 190), Rect(710, 390, 12, 102),
)


@dataclass(frozen=True)
class Action:
    """throttle and turn are clamped to [-1, 1]; shoot may be held."""
    throttle: float = 0.0
    turn: float = 0.0
    shoot: bool = False


@dataclass
class Tank:
    position: Vec
    angle: float
    alive: bool = True
    cooldown: float = 0.0


@dataclass
class Bullet:
    position: Vec
    velocity: Vec
    owner: int
    bounces: int = 0


class Game:
    def __init__(self, walls: Sequence[Rect] = DEFAULT_WALLS):
        self.walls = tuple(walls)
        self.scores = [0, 0]
        self.restart()

    def restart(self):
        """Reset all round state; match scores intentionally persist."""
        self.tanks = [Tank((90., 90.), 0.), Tank((810., 510.), pi)]
        self.bullets: list[Bullet] = []
        self.finished = False
        self.winner: int | None = None
        self.ticks = 0

    def _move(self, index: int, delta: Vec):
        tank = self.tanks[index]
        other = self.tanks[1 - index]
        # Sweep and project remaining movement onto contact tangents for sliding.
        for _ in range(4):
            wall_hit = sweep_walls(tank.position, delta, self.walls, TANK_RADIUS)
            tank_hit = sweep_circle(tank.position, delta, other.position, 2 * TANK_RADIUS) if other.alive else None
            contacts = []
            if wall_hit:
                contacts.append(wall_hit)
            if tank_hit:
                contacts.append((tank_hit[0], [tank_hit[1]]))
            if not contacts:
                tank.position = add(tank.position, delta)
                break
            time = min(hit[0] for hit in contacts)
            normals = [n for t, ns in contacts if abs(t - time) < 1e-8 for n in ns]
            tank.position = add(tank.position, mul(delta, time))
            delta = mul(delta, 1 - time)
            for normal in normals:
                tank.position = add(tank.position, mul(normal, 1e-6))
                inward = dot(delta, normal)
                if inward < 0:
                    delta = add(delta, mul(normal, -inward))

    def _fire(self, index: int):
        tank = self.tanks[index]
        if tank.cooldown > 1e-8 or sum(b.owner == index for b in self.bullets) >= MAX_BULLETS:
            return
        direction = (cos(tank.angle), sin(tank.angle))
        muzzle_delta = mul(direction, MUZZLE_DISTANCE)
        # Sweep the whole barrel path with bullet radius; reject blocked shots.
        # This prevents spawning through a wall, even when its far side is clear.
        if sweep_walls(tank.position, muzzle_delta, self.walls, BULLET_RADIUS):
            return
        self.bullets.append(Bullet(add(tank.position, muzzle_delta), mul(direction, BULLET_SPEED), index))
        tank.cooldown = COOLDOWN

    def _advance_bullet(self, bullet: Bullet, victims: set[int]) -> bool:
        remaining = DT
        for _ in range(3):  # At most two wall contacts; then the bullet is removed.
            delta = mul(bullet.velocity, remaining)
            wall_hit = sweep_walls(bullet.position, delta, self.walls, BULLET_RADIUS)
            tank_hits = []
            for index, tank in enumerate(self.tanks):
                # The shooter becomes a valid target immediately after a bounce.
                if tank.alive and (index != bullet.owner or bullet.bounces > 0):
                    offset = (bullet.position[0] - tank.position[0], bullet.position[1] - tank.position[1])
                    if dot(offset, offset) <= (TANK_RADIUS + BULLET_RADIUS) ** 2:
                        tank_hits.append((0., index))
                    elif hit := sweep_circle(bullet.position, delta, tank.position, TANK_RADIUS + BULLET_RADIUS):
                        tank_hits.append((hit[0], index))
            first_tank = min(tank_hits, default=None)
            if first_tank and (not wall_hit or first_tank[0] < wall_hit[0] - 1e-8):
                victims.update(index for time, index in tank_hits if abs(time - first_tank[0]) < 1e-8)
                return False
            if not wall_hit:
                bullet.position = add(bullet.position, delta)
                return True
            time, normals = wall_hit
            bullet.position = add(bullet.position, mul(delta, time))
            if bullet.bounces == 1:
                return False
            bullet.bounces += 1
            # Orthogonal corner faces flip both components in one bounce.
            for normal in normals:
                inward = dot(bullet.velocity, normal)
                if inward < 0:
                    bullet.velocity = add(bullet.velocity, mul(normal, -2 * inward))
                bullet.position = add(bullet.position, mul(normal, 1e-6))
            remaining *= 1 - time
        return False

    def step(self, actions: Sequence[Action] = (Action(), Action())):
        """Advance exactly DT seconds. Supply one Action per player.

        Hits are committed together at the end of the tick, so simultaneous
        destruction produces a draw independent of bullet list order.
        """
        if len(actions) != 2:
            raise ValueError('Provide exactly two actions')
        if self.finished:
            return
        self.ticks += 1
        for index, (tank, action) in enumerate(zip(self.tanks, actions)):
            tank.cooldown = max(0., tank.cooldown - DT)
            tank.angle = (tank.angle + max(-1., min(1., action.turn)) * TURN_SPEED * DT) % (2 * pi)
            throttle = max(-1., min(1., action.throttle))
            self._move(index, mul((cos(tank.angle), sin(tank.angle)), throttle * MOVE_SPEED * DT))
        for index, action in enumerate(actions):
            if action.shoot:
                self._fire(index)
        victims: set[int] = set()
        self.bullets = [bullet for bullet in self.bullets if self._advance_bullet(bullet, victims)]
        for index in victims:
            self.tanks[index].alive = False
        if victims:
            self.finished = True
            survivors = [i for i, tank in enumerate(self.tanks) if tank.alive]
            self.winner = survivors[0] if len(survivors) == 1 else None
            if self.winner is not None:
                self.scores[self.winner] += 1
