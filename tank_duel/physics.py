"""Continuous circle collision queries; no Pygame or window dependencies."""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

EPS = 1e-8
Vec = tuple[float, float]


def add(a: Vec, b: Vec) -> Vec:
    return a[0] + b[0], a[1] + b[1]


def mul(a: Vec, k: float) -> Vec:
    return a[0] * k, a[1] * k


def dot(a: Vec, b: Vec) -> float:
    return a[0] * b[0] + a[1] * b[1]


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    w: float
    h: float

    def overlaps_circle(self, p: Vec, radius: float) -> bool:
        q = (min(max(p[0], self.x), self.x + self.w),
             min(max(p[1], self.y), self.y + self.h))
        return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 < radius ** 2 - EPS


def sweep_circle(p: Vec, delta: Vec, center: Vec, radius: float):
    """First entering contact along p + t*delta, for t in [0, 1]."""
    offset = (p[0] - center[0], p[1] - center[1])
    a = dot(delta, delta)
    if a < EPS:
        return None
    b = dot(offset, delta)
    c = dot(offset, offset) - radius * radius
    disc = b * b - a * c
    if disc < 0 or b >= 0:
        return None
    t = (-b - sqrt(max(0, disc))) / a
    if -EPS <= t <= 1 + EPS:
        t = max(0, min(1, t))
        contact = add(offset, mul(delta, t))
        length = sqrt(dot(contact, contact))
        return t, mul(contact, 1 / length)
    return None


def sweep_rect(p: Vec, delta: Vec, rect: Rect, radius: float):
    """Sweep against the exact rounded rectangle (Minkowski sum).

    Faces plus circular corners avoid the false corner hits of an expanded AABB.
    Tangential/separating contacts are ignored, allowing wall sliding.
    """
    hits = []
    for axis, plane, normal, lo, hi in (
        (0, rect.x - radius, (-1., 0.), rect.y, rect.y + rect.h),
        (0, rect.x + rect.w + radius, (1., 0.), rect.y, rect.y + rect.h),
        (1, rect.y - radius, (0., -1.), rect.x, rect.x + rect.w),
        (1, rect.y + rect.h + radius, (0., 1.), rect.x, rect.x + rect.w),
    ):
        if dot(delta, normal) >= -EPS:
            continue
        t = (plane - p[axis]) / delta[axis]
        other = p[1 - axis] + t * delta[1 - axis]
        if -EPS <= t <= 1 + EPS and lo - EPS <= other <= hi + EPS:
            hits.append((max(0, min(1, t)), normal))
    for x, sx in ((rect.x, -1), (rect.x + rect.w, 1)):
        for y, sy in ((rect.y, -1), (rect.y + rect.h, 1)):
            hit = sweep_circle(p, delta, (x, y), radius)
            if hit:
                point = add(p, mul(delta, hit[0]))
                if (point[0] - x) * sx >= -EPS and (point[1] - y) * sy >= -EPS:
                    hits.append(hit)
    return min(hits, key=lambda hit: hit[0]) if hits else None


def sweep_walls(p: Vec, delta: Vec, walls: tuple[Rect, ...], radius: float):
    hits = [hit for wall in walls if (hit := sweep_rect(p, delta, wall, radius))]
    if not hits:
        return None
    t = min(hit[0] for hit in hits)
    # A junction of two walls is one impact, with all simultaneous normals.
    normals = []
    for time, normal in hits:
        if abs(time - t) < EPS and normal not in normals:
            normals.append(normal)
    return t, normals
