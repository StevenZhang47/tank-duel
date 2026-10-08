"""Evaluate random action IDs against stationary red, optionally with playback."""
import argparse
import math

from tank_duel.env import TankDuelEnv

def idle_policy(observation):
    return 8  # No movement, rotation, or shooting.

def evaluate_episode(seed, visualize=False, speed=1.0, max_ticks=1200, policy=None):
    if max_ticks <= 0:
        raise ValueError('max_ticks must be positive')
    if not math.isfinite(speed) or speed <= 0:
        raise ValueError('speed must be finite and positive')
    env = TankDuelEnv()
    env.max_ticks = max_ticks
    viewer = None
    try:
        obs, info = env.reset(seed=seed)
        env.action_space.seed(seed)
        if visualize:
            # Use the same environment and action sampler as headless evaluation.
            from tank_duel.rollout_viewer import RolloutViewer
            viewer = RolloutViewer(env.game, seed, speed)
            env.on_tick = viewer.update

        while True:
            if policy is None:
                action_id = env.action_space.sample()
            else:
                action_id = policy(obs)

            obs, reward, terminated, truncated, info = env.step(action_id)
            
            if terminated or truncated or (
                viewer is not None and not viewer.running
            ):
                break

        # An early window close is excluded from completed evaluation outcomes.
        if not (terminated or truncated):
            outcome = "interrupted"
        elif truncated:
            outcome = "timeout"
        elif info["winner"] is None:
            outcome = "draw"
        elif info["winner"] == 0:
            outcome = "win"
        else:
            outcome = "loss"

        result = {"outcome": outcome, "ticks": info["ticks"]}
        if viewer is not None:
            print(result, flush=True)
            viewer.show_result(env.game, truncated)
        return result
    finally:
        env.on_tick = None
        if viewer is not None:
            viewer.close()
        env.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=10000)
    parser.add_argument('--visualize', action='store_true')
    parser.add_argument('--speed', type=float, default=1.0)
    parser.add_argument('--max-ticks', type=int, default=1200)
    args = parser.parse_args()
    if args.max_ticks <= 0:
        parser.error('--max-ticks must be positive')
    if not math.isfinite(args.speed) or args.speed <= 0:
        parser.error('--speed must be finite and positive')
    result = evaluate_episode(args.seed, args.visualize, args.speed, args.max_ticks)
    if not args.visualize:
        print(result)


if __name__ == "__main__":
    main()
