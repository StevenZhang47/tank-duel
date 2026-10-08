from tank_duel.evaluate_random import evaluate_episode, idle_policy

print(evaluate_episode(seed=10000, policy=idle_policy))