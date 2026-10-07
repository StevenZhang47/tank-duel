import gymnasium as gym
import numpy as np

from tank_duel import Game
from tank_duel.actions import ACTION_TABLE
from tank_duel.observations import observe

from tank_duel.actions import decode_action
from tank_duel.random_rollout import hold_action
from tank_duel.episodes import episode_flags, terminal_reward

class TankDuelEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self):
        self.game = Game()

        self.action_space = gym.spaces.Discrete(len(ACTION_TABLE))
        self.observation_space = gym.spaces.Box(
            low=-2.0,
            high=2.0,
            shape=(136,),
            dtype=np.float32,
        )
        
        self.max_ticks = 1200
        self.action_ticks = 12
        self.needs_reset = True

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)

        # Restart self.game.
        self.game.restart()

        # Get green's observation and convert it to a NumPy array.
        observation = np.array(observe(self.game, 0), dtype=np.float32)
        
        self.needs_reset = False
        
        return observation, {}
    
    def step(self, action_id):
        if self.needs_reset:
            raise RuntimeError("Call reset() before starting another episode.")
        
        if not self.action_space.contains(action_id):
            raise ValueError("Action ID must be an integer from 0 to 17.")
        
        # Translate the ID into an Action.
        green_action = decode_action(action_id)
        
        # Apply it for up to 12 physics ticks.
        remaining = self.max_ticks - self.game.ticks
        ticks_to_hold = min(self.action_ticks, remaining)
        hold_action(self.game, green_action, ticks_to_hold)
        # Return the new observation, reward, ending flags, and info.
        observation = np.array(observe(self.game, 0), dtype=np.float32)
        reward = terminal_reward(self.game, 0)
        terminated, truncated = episode_flags(self.game, self.max_ticks)
        
        # 4. Require a reset after either kind of ending.
        self.needs_reset = terminated or truncated
        
        info = {
            "ticks": self.game.ticks,
            "winner": self.game.winner,
        }
        
        return observation, reward, terminated, truncated, info