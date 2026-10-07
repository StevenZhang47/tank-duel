import random
from tank_duel import Action, Game, DT

from tank_duel.observations import tank_features, observe

from tank_duel.simulation import Bullet
from tank_duel.observations import bullet_features

rng = random.Random(0)

def random_action(rng: random.Random) -> Action:
    # Choose throttle and turn independently from (-1, 0, 1).
    # Choose shoot randomly from (False, True).
    # Return an Action containing those choices.
    throttle = rng.choice((-1, 0, 1))
    turn = rng.choice((-1, 0, 1))
    shoot = rng.choice((False, True))
    
    return Action(
        throttle=throttle,
        turn=turn,
        shoot=shoot,
    )
    
def hold_action(game, greens_action, tick_count) -> int:
    green_action = greens_action
    i = 0
    while i < tick_count:
        if game.finished:
            break
        game.step((green_action, Action()))
        i+=1
            
    return i
    

def run_random_rollout(seed: int = 0, max_ticks: int = 1200) -> dict:
    rng = random.Random(seed)
    game = Game()
    
    green_action = random_action(rng)
    red_action = Action()
    
    print("Chosen action:", green_action)
    print("Position before:", game.tanks[0].position)

    while game.ticks < max_ticks:
        if game.finished:
            break
        
        remaining = max_ticks - game.ticks
        green_action = random_action(rng)
        print("Holding for:", min(12, remaining))
        hold_action(game, green_action, min(remaining, 12))
    print("Position after:", game.tanks[0].position)
    print("Ticks advanced:", game.ticks)
    print("Round finished:", game.finished)
    

    # Advance up to max_ticks:
    #   stop if the round has finished
    #   choose green's action using random_action(rng)
    #   advance the game with green's action and an idle red action
    #
    # Return the summary described below.
    


if __name__ == "__main__":
    run_random_rollout(seed=1, max_ticks=25)
    
    game = Game()

    green_obs = observe(game, 0)
    red_obs = observe(game, 1)

    print("Green sees:", bullet_features(bullet, 0))
    print("Red sees:", bullet_features(bullet, 1))
    print("Length:", len(green_obs))
    
    bullet = Bullet(
        position=(450, 300),
        velocity=(420, 0),
        owner=0,
        bounces=0,
    )

    print("Bullet features:", bullet_features(bullet))