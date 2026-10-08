from tank_duel.evaluate_random import evaluate_episode


def evaluate_many(episodes=20, first_seed=10000, policy=None):
    counts = {
        "win": 0,
        "loss": 0,
        "draw": 0,
        "timeout": 0,
    }

    for seed in range(first_seed, first_seed + episodes):
        result = evaluate_episode(seed=seed, policy=policy)
        outcome = result["outcome"]

        # Increase the count for this outcome by one.
        if outcome == "loss":
            counts["loss"] += 1
        elif outcome == "win":
            counts["win"] += 1
        elif outcome == "draw":
            counts["draw"] += 1    
        else:
            counts["timeout"] += 1

    return counts


if __name__ == "__main__":
    from tank_duel.evaluate_random import idle_policy

    print("Random:", evaluate_many())
    print("Idle:", evaluate_many(policy=idle_policy))