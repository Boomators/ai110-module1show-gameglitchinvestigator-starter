from logic_utils import check_guess, initial_game_state

# Starter tests. check_guess returns (outcome, message), so these unpack the
# outcome instead of comparing the whole tuple to a string.

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"


# Bug #1: the hint messages were swapped -- "Too High" told the player to go
# HIGHER. The outcome label was always right, so only the message catches this.

def test_too_high_tells_player_to_go_lower():
    outcome, message = check_guess(60, 42)
    assert outcome == "Too High"
    assert "LOWER" in message

def test_too_low_tells_player_to_go_higher():
    outcome, message = check_guess(20, 42)
    assert outcome == "Too Low"
    assert "HIGHER" in message


# Bug #3: "New Game" left status/score/history behind, so the app kept showing
# "You already won" and stopped.

def test_new_game_state_is_fully_reset():
    state = initial_game_state(1, 100)
    assert state["status"] == "playing"
    assert state["score"] == 0
    assert state["history"] == []
    assert state["attempts"] == 1

def test_new_game_secret_respects_difficulty_range():
    for _ in range(50):
        assert 1 <= initial_game_state(1, 20)["secret"] <= 20
