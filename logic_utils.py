import random


def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    # FIXME: Logic breaks here -- bug #7. Hard (1-50) is a narrower range than
    # Normal (1-100), so "Hard" is actually easier. Not fixed in this pass.
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"
    """
    # FIX (bug #1): the two hint messages were swapped -- "Too High" returned
    # "Go HIGHER!". Found by running the game (secret 42, guess 60) and reading
    # the returns; fixed with AI chat in agent mode, verified by pytest.
    if guess == secret:
        return "Win", "🎉 Correct!"

    try:
        if guess > secret:
            return "Too High", "📉 Go LOWER!"
        else:
            return "Too Low", "📈 Go HIGHER!"
    except TypeError:
        # FIXME: Logic breaks here -- bug #2. app.py hands us a str secret on
        # even attempts, so this branch compares strings ("100" > "42" is
        # False) and silently reports the wrong outcome. Not fixed in this pass.
        g = str(guess)
        if g == secret:
            return "Win", "🎉 Correct!"
        if g > secret:
            return "Too High", "📉 Go LOWER!"
        return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        # FIXME: Logic breaks here -- bug #8. A wrong guess adds 5 points on
        # even attempts instead of subtracting. Not fixed in this pass.
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score


def initial_game_state(low: int, high: int):
    """
    Return a complete fresh-game state dict.

    Used both on first load and by the New Game button so the two can never
    drift apart.
    """
    # FIX (bug #3): "New Game" used to reset only attempts and secret, leaving
    # status/score/history behind so the game stayed stuck on "You already
    # won". Pulling the reset into one function makes it testable and keeps
    # startup and New Game in sync.
    return {
        "secret": random.randint(low, high),
        "attempts": 1,
        "score": 0,
        "status": "playing",
        "history": [],
    }
