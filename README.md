# Tank Duel

A two-player Tank Trouble-style game in Python 3.11 and Pygame, with a separate, deterministic simulator ready for future programmatic control. No RL or training dependencies are included.

## Install and launch (Apple Silicon Mac)

From this repository:

```sh
conda activate tank-rl
"$CONDA_PREFIX/bin/python" --version   # should report Python 3.11.x
"$CONDA_PREFIX/bin/python" -m pip install -r requirements.txt
"$CONDA_PREFIX/bin/python" -m tank_duel
```

If creating the environment on another machine:

```sh
conda create -n tank-rl python=3.11
conda activate tank-rl
"$CONDA_PREFIX/bin/python" -m pip install -r requirements.txt
"$CONDA_PREFIX/bin/python" -m tank_duel
```

Pygame 2.6.1 provides a macOS Apple Silicon wheel for Python 3.11. Run the game from a local desktop terminal with keyboard focus on its window.

### If `python` still runs Python 2.7

The environment name in the prompt does not guarantee that your shell's `python` command resolves to the environment interpreter. Use the explicit interpreter commands above to bypass shell aliases and PATH ordering. On this Mac, the verified interpreter is:

```sh
/Users/stevenzhang/miniforge3/envs/tank-rl/bin/python -m tank_duel
```

Pygame 2.6.1 is already installed in that environment. There is no need to reinstall it to recover from a failed installation attempted with Python 2.7.

## Controls and rules

| Player | Forward / reverse | Rotate left / right | Fire |
| --- | --- | --- | --- |
| Green | W / S | A / D | Space |
| Red | Up / Down | Left / Right | Enter |

**R** restarts the round at any time. **Escape** or closing the window quits. Scores persist across round restarts and reset when the application closes.

Hold fire to shoot every 0.32 seconds, up to five active bullets per tank. A bullet reflects on its first wall contact and disappears on its second. After reflecting it can also destroy its shooter. One hit destroys a tank. Hits on both tanks in the same simulation tick produce a draw; draws award no points. A completed round freezes until R is pressed. A shot is refused when a wall blocks the muzzle path.

The fixed arena has a light gray floor, thick black walls, green/red tanks with rotating barrels, and black circular bullets. Scores and controls sit outside the arena.

## Code structure

- `tank_duel/simulation.py`: actions, tanks, bullets, fixed maze, round state, scores, movement, firing, and hit resolution.
- `tank_duel/physics.py`: continuous circle sweeps against circles and rectangle faces/rounded corners.
- `tank_duel/client.py`: keyboard mapping, Pygame drawing, and the fixed-step accumulator.
- `tank_duel/__main__.py`: entry point for `python -m tank_duel`.
- `tests/test_simulation.py`: headless regression tests using the standard library.

The simulation advances at 120 Hz. Swept collision detection checks the full travel path, so even bullets moving much farther than a wall's thickness in one tick cannot tunnel. Remaining bullet travel continues after its first reflection during the same tick. Simultaneous orthogonal wall contacts reflect both velocity components and count as one impact. Tiny contact separation offsets prevent repeated numerical collisions. Tanks slide along walls and use a circular hull of radius 16; the decorative barrel does not collide. Tank movement is resolved in player order, then bullets are swept against the resulting tank positions. This is a fixed-step approximation of moving targets, rather than continuous relative-motion collision detection.

### Headless use

Importing the simulator does not import Pygame or open a window:

```python
from tank_duel import Action, Game, DT

game = Game()
for _ in range(120):  # one simulated second
    game.step((Action(throttle=1, turn=0.2, shoot=True), Action()))
    if game.finished:
        break

print(game.tanks, game.bullets, game.winner, game.scores)
game.restart()
```

`step()` accepts exactly two actions and advances exactly `DT` seconds; it does nothing after a round finishes. Throttle/turn range from -1 to +1 (values outside that range are clamped). Positive turn is clockwise on the screen. State is exposed as plain dataclasses for inspection. `winner` is player index 0 or 1; `finished=True, winner=None` means a draw. `restart()` resets tanks, angles, bullets, cooldowns, outcome, and tick count while preserving scores.

## Verification

```sh
"$CONDA_PREFIX/bin/python" -m unittest discover -s tests -v
```

Tests cover forward/reverse movement and rotation, tank-wall/tank-tank contact, fast bullet sweeps, first-bounce reflection/second-contact removal, arena corners, rounded wall corners, hits, ricochet self-hits, winner scoring, simultaneous draws, cooldowns, bullet limits, blocked muzzle paths, restart state, action validation, and repeatability.

A screenshot was not available in the request received by the implementation agent, so the visual design follows the written description. Automated tests and a headless Pygame smoke check do not replace a manual check of keyboard feel and appearance on a Mac desktop. Simultaneous hits are defined at the 1/120-second tick level; tank movement uses the fixed player order described above.
