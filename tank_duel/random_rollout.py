"""Run a random green tank against an idle red tank, optionally with a window."""
import argparse
import math
import random
from tank_duel import Action, Game, DT
from tank_duel.episodes import episode_flags, terminal_reward

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
    
def hold_action(game, greens_action, tick_count, on_tick=None) -> int:
    green_action = greens_action
    i = 0
    while i < tick_count:
        if game.finished:
            break
        game.step((green_action, Action()))
        i+=1
        # Drawing is optional and happens after physics, without choosing actions.
        if on_tick is not None and not on_tick(game):
            break
            
    return i
    

def run_random_rollout(seed: int = 0, max_ticks: int = 1200,
                       visualize: bool = False, speed: float = 1.0) -> dict:
    if max_ticks < 0:
        raise ValueError('max_ticks must be nonnegative')
    if not math.isfinite(speed) or speed <= 0:
        raise ValueError('speed must be finite and positive')
    rng = random.Random(seed)
    game = Game()
    
    # Preserve the RNG sequence from the original pre-loop debug sample.
    random_action(rng)
    viewer = None
    if visualize:
        # Headless imports/runs never import Pygame or create a display.
        from tank_duel.rollout_viewer import RolloutViewer
        viewer = RolloutViewer(game, seed, speed)

    try:
        while game.ticks < max_ticks and not game.finished:
            if viewer is not None and not viewer.running:
                break
            remaining = max_ticks - game.ticks
            green_action = random_action(rng)
            hold_action(game, green_action, min(remaining, 12),
                        on_tick=viewer.update if viewer is not None else None)

        terminated, truncated = episode_flags(game, max_ticks)
        result = {
            'ticks': game.ticks,
            'simulated_seconds': game.ticks * DT,
            'terminated': terminated,
            'truncated': truncated,
            'winner': game.winner,
            'reward': terminal_reward(game, 0),
            # Closing playback early is neither a game result nor a timeout.
            'interrupted': viewer is not None and not viewer.running
                           and not (terminated or truncated),
        }
        if viewer is not None:
            print(result, flush=True)
            viewer.show_result(game, truncated)
        return result
    finally:
        if viewer is not None:
            viewer.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=1)
    parser.add_argument('--max-ticks', type=int, default=1200)
    parser.add_argument('--visualize', action='store_true')
    parser.add_argument('--speed', type=float, default=1.0,
                        help='Playback speed multiplier; e.g. 0.25 for slow motion')
    args = parser.parse_args()
    if args.max_ticks < 0:
        parser.error('--max-ticks must be nonnegative')
    if not math.isfinite(args.speed) or args.speed <= 0:
        parser.error('--speed must be finite and positive')
    result = run_random_rollout(args.seed, args.max_ticks, args.visualize, args.speed)
    if not args.visualize:
        print(result)


if __name__ == "__main__":
    main()
