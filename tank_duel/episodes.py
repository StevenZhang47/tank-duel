"""Episode stopping rules, separate from the game's physics."""


def episode_flags(game, max_ticks):
    """Return (terminated, truncated), giving a real game ending priority."""
    # Has the game actually ended?
    terminated = game.finished

    # Has the time limit been reached while the game is unfinished?
    truncated = game.ticks >= max_ticks and not terminated

    return terminated, truncated

def terminal_reward(game, player_index):
    """Score a final outcome from this player's perspective, without changing state."""
    # If the game hasn't finished, return 0.0.
    if not game.finished:
        return 0.0

    # If it finished as a draw, return 0.0.
    if game.winner is None:
        return 0.0

    # If this player won, return 1.0.
    if game.winner == player_index:
        return 1.0

    # Otherwise, return -1.0.
    return -1.0

