# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

### The game's purpose

A Streamlit number-guessing game. The app picks a secret number inside a range
that depends on the chosen difficulty, and the player gets a limited number of
attempts to find it. After each guess the game reports whether the guess was too
high or too low, nudges the player with a hint, updates a running score, and
ends the round on a win or when attempts run out. A "New Game" button is
supposed to start a fresh round.

### Bugs I found

I played the game with the Developer Debug Info panel open so I could see the
secret, and logged eight bugs. The full reproduction table is in
[`reflection.md`](reflection.md) section 1. The short version:

| # | Bug | Where |
|---|-----|-------|
| 1 | The two hints are swapped — "too high" tells you to go HIGHER | `check_guess` |
| 2 | On even attempts the secret is cast to a string, so guesses compare as text (`"100" > "42"` is `False`) | `app.py` submit block + the `except TypeError` fallback |
| 3 | "New Game" doesn't reset the game — it stays stuck on "You already won" | `app.py` `if new_game:` block |
| 4 | "New Game" always draws from 1–100, ignoring difficulty | `app.py` `if new_game:` block |
| 5 | Attempt counter starts at 1, so a fresh Normal game shows 7 left instead of 8 | `app.py` state init + the attempts display |
| 6 | The info box always says "between 1 and 100" regardless of difficulty | `app.py` `st.info(...)` |
| 7 | Hard (1–50) is an easier range than Normal (1–100) | `get_range_for_difficulty` |
| 8 | A wrong guess *adds* 5 points on even-numbered attempts | `update_score` |

### Fixes I applied

**Bug #1 — swapped hints.** `check_guess` returned the wrong message for each
outcome. The messages were swapped in two places: the normal comparison branch
and again in the `except TypeError` fallback below it, so fixing only the first
would have left the bug reachable on some attempts.

**Bug #3 — "New Game" didn't reset.** The button reset only `attempts` and
`secret`, leaving `status`, `score`, and `history` in session state. On the next
rerun the app hit its "You already won" guard and called `st.stop()`, so the
game was unplayable after a single round. The fix was structural rather than a
patch: a new `initial_game_state(low, high)` helper returns the complete fresh
state, and both the first-load block and the New Game button build from it — so
the two can't drift apart again, which is what caused the bug in the first
place. Because both call sites now pass the real difficulty range, this
incidentally fixed bug #4 as well.

**Refactor.** `check_guess`, `parse_guess`, `update_score`, and
`get_range_for_difficulty` moved out of `app.py` into `logic_utils.py`, which
previously held `NotImplementedError` stubs. This is what makes the rules
testable at all — you can't `import app.py` from a test, because importing it
runs the whole Streamlit app.

**Still broken on purpose.** Bugs #2, #5, #6, #7, and #8 are unfixed and each is
marked with a `# FIXME` comment naming its bug number at the exact line, so the
remaining work is easy to find.

## 📸 Demo Walkthrough

A sample round on **Normal** difficulty (range 1–100, 8 attempts). The secret
this round was **42**, read from the Developer Debug Info panel.

1. **Load the app.** The info box reads "Guess a number between 1 and 100.
   Attempts left: 7." *(That 7 should be 8 — known bug #5, not fixed.)*
2. **Guess 30.** The game returns outcome `Too Low` with the hint
   "📈 Go HIGHER!" — the hint now points in the direction that actually helps.
   Before the fix this said "Go LOWER!", which sent the player away from the
   answer.
3. **Score updates to −5.** A wrong guess costs 5 points, so the running score
   goes negative early. *(Known bug #8: on some attempts a wrong guess adds 5
   instead of subtracting. Not fixed.)*
4. **Guess 70.** Outcome `Too High`, hint "📉 Go LOWER!". Score drops to −10.
   Between steps 2 and 4 the player has bracketed the answer between 30 and 70.
5. **Guess 42.** Outcome `Win`, "🎉 Correct!". Balloons fire and the app shows
   "You won! The secret was 42. Final score: 40" — the win bonus is
   `100 − 10 × attempts`, which outweighs the earlier penalties.
6. **The round ends.** Status flips to `won`, and further guesses are blocked
   with "You already won. Start a new game to play again."
7. **Click "New Game".** The board clears completely: status back to `playing`,
   score back to 0, history emptied, and a brand-new secret drawn from the
   current difficulty's range. Before the fix this step did nothing visible —
   the app kept showing "You already won" and stopped, making the game
   single-use.

**Screenshot** *(optional)*: <!-- Insert a screenshot of your fixed, winning game here -->

## 🧪 Test Results

Run with `python -m pytest tests/ -v`:

```
============================= test session starts ==============================
platform darwin -- Python 3.13.15, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/uk/Documents/Codepath/ai110-module1show-gameglitchinvestigator-starter
plugins: anyio-4.15.1
collected 7 items

tests/test_game_logic.py::test_winning_guess PASSED                      [ 14%]
tests/test_game_logic.py::test_guess_too_high PASSED                     [ 28%]
tests/test_game_logic.py::test_guess_too_low PASSED                      [ 42%]
tests/test_game_logic.py::test_too_high_tells_player_to_go_lower PASSED  [ 57%]
tests/test_game_logic.py::test_too_low_tells_player_to_go_higher PASSED  [ 71%]
tests/test_game_logic.py::test_new_game_state_is_fully_reset PASSED      [ 85%]
tests/test_game_logic.py::test_new_game_secret_respects_difficulty_range PASSED [100%]

============================== 7 passed in 0.02s ===============================
```

The three `test_winning_guess` / `test_guess_too_high` / `test_guess_too_low`
tests are the starter tests. They were failing before I started, because they
compare the return value to a string while `check_guess` returns an
`(outcome, message)` tuple. I updated the tests to unpack the tuple rather than
changing `check_guess` to return one value, since `app.py` needs the message to
display the hint.

The four tests after them are mine. The two hint tests assert on the **message
text**, not just the outcome label — that matters, because the outcome label was
always correct and only the message was backwards, which is exactly why the
starter tests never caught bug #1. I confirmed they work by re-introducing the
swap and watching those two tests fail, then reverting.

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, describe the Enhanced UI changes here — a screenshot is optional]
