from math import cos, sin
from tank_duel.simulation import WIDTH, HEIGHT, COOLDOWN, BULLET_SPEED


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

    # Join the two lists into one flat list.
    return my_features + opponent_features

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
    # Return those four values as a flat list.
    return [x, y, vx, vy, is_mine, float(bullet.bounces)]
