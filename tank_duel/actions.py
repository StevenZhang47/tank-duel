from itertools import product
from tank_duel import Action

ACTION_TABLE = list(product(
    (-1, 0, 1),    # throttle
    (-1, 0, 1),    # turn
    (False, True), # shoot
))


def decode_action(action_id):
    if not 0 <= action_id < len(ACTION_TABLE):
        raise ValueError("Action ID must be between 0 and 17")

    # Each table entry stores (throttle, turn, shoot) in that order.
    throttle, turn, shoot = ACTION_TABLE[action_id]
    return Action(throttle=throttle, turn=turn, shoot=shoot)


if __name__ == "__main__":
    print("Combinations:", len(ACTION_TABLE))
    for action_id in (0, 8, 17):
        print(action_id, decode_action(action_id))
