from tank_duel.env import TankDuelEnv
from gymnasium.utils.env_checker import check_env

env = TankDuelEnv()
env.max_ticks = 25
env.reset(seed=0)

for decision in range(3):
    obs, reward, terminated, truncated, info = env.step(8)
    print("Decision:", decision + 1)
    print("Ticks:", info["ticks"])
    print("Ending flags:", terminated, truncated)
    
try:
    env.step(8)
except RuntimeError as error:
    print("Extra step blocked:", error)

obs, info = env.reset()

print("Ticks after reset:", env.game.ticks)
print("Needs reset:", env.needs_reset)
print("Bullet count:", len(env.game.bullets))

check_env(TankDuelEnv(), skip_render_check=True)
print("Gymnasium interface check passed.")