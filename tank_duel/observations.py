from math import cos, sin
from tank_duel.simulation import WIDTH, HEIGHT, COOLDOWN, BULLET_SPEED, MAX_BULLETS


def tank_features(game, player_index):
    tank = game.tanks[player_index]
    x, y = tank.position

    # Return a list containing these five numbers, in order:
    # x divided by arena width
    x = x/WIDTH
    # y divided by arena height
    y = y/HEIGHT
    # cosine of the tank angle
    dir_x = cos(tank.angle)
    # sine of the tank angle
    dir_y = sin(tank.angle)
    
    cooldown_fraction = tank.cooldown/COOLDOWN
    
    return [x, y, dir_x, dir_y, cooldown_fraction]

def observe(game, player_index):
    # Get this player's five features.
    my_features = tank_features(game, player_index)

    # Find the other player's index.
    opponent_index = 1 - player_index

    # Get the opponent's five features.
    opponent_features = tank_features(game, opponent_index)
    
    bullet_info = all_bullet_features(game, player_index)
    wall_info = wall_features(game)

    # Fixed maze: 10 tank + 70 bullet + 56 wall values = 136 inputs.
    return my_features + opponent_features + bullet_info + wall_info

def bullet_features(bullet, player_index):
    x, y = bullet.position
    vx, vy = bullet.velocity
    
    if bullet.owner == player_index:
        is_mine = 1.0
    else:
        is_mine = 0.0

    # Normalize x using WIDTH.
    x = x/WIDTH
    # Normalize y using HEIGHT.
    y = y/HEIGHT
    # Normalize vx and vy using BULLET_SPEED.
    vx = vx/BULLET_SPEED
    vy = vy/BULLET_SPEED
    # Position, velocity, ownership, and bounce state: six values.
    return [x, y, vx, vy, is_mine, float(bullet.bounces)]

def all_bullet_features(game, player_index):
    features = []
    max_slots = 2 * MAX_BULLETS

    for bullet in game.bullets:
        # Build one slot: [1.0] followed by bullet_features(...).
        slot = [1.0] + bullet_features(bullet, player_index)

        # Join this slot onto the flat features list.
        features += slot

    # Calculate how many bullet slots are still empty.
    empty_slots = max_slots - len(game.bullets)

    # Add seven zeros for each empty slot.
    features += [0.0] * (empty_slots * 7)

    return features


def wall_features(game):
    """Encode each wall as normalized top-left position, width, and height."""
    features = []
    for wall in game.walls:
        # Boundary rectangles extend outside the arena; preserve their geometry.
        # The fixed layout keeps the wall order and feature count consistent.
        features += [
            wall.x / WIDTH,
            wall.y / HEIGHT,
            wall.w / WIDTH,
            wall.h / HEIGHT,
        ]
    return features
