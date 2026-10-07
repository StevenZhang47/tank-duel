from tank_duel.env import TankDuelEnv

env = TankDuelEnv()
obs, info = env.reset(seed=0)

print("Shape:", obs.shape)
print("Type:", obs.dtype)
print("Valid observation:", env.observation_space.contains(obs))
print("Game ticks:", env.game.ticks)

obs, reward, terminated, truncated, info = env.step(14)

print("Position:", env.game.tanks[0].position)
print("Reward:", reward)
print("Ending flags:", terminated, truncated)
print("Info:", info)