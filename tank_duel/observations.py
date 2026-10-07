from math import cos, sin
from tank_duel.simulation import WIDTH, HEIGHT, COOLDOWN


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