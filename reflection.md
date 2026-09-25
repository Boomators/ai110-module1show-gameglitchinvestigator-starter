# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

The first time I ran it, the game looked completely normal — no errors, no red
tracebacks, nothing in the console at all. That was the confusing part. Every
bug in this project is a *silent* one: the app runs, the buttons respond, and
the numbers are simply wrong. I only started making progress once I opened the
Developer Debug Info panel so I could see the secret number, because then I
could compare what the game told me against what was actually true.

Two that stood out immediately: the hints were backwards (it told me to guess
higher when my guess was already too high), and the "New Game" button appeared
to do nothing — once I won a round, the app stayed stuck on "You already won"
forever.

**Bug Reproduction Log**

| # | Input Used | Expected Behavior | Actual Behavior | Console Error / Output | Suspected Code Location |
|---|------------|-------------------|-----------------|------------------------|-------------------------|
| 1 | Secret 42, guess 60 | "Go LOWER!" (guess is too high) | "Go HIGHER!" shown. The two hint messages are swapped. | none | `check_guess`, the return messages for Too High / Too Low |
| 2 | Secret 42, guess 100 on the first guess, or any even-numbered attempt | Outcome "Too High" | Outcome comes out "Too Low". On even attempts the secret is cast to a string, so `"100" > "42"` is `False` (string comparison). | none — the `TypeError` is caught silently by the `except` in `check_guess` | `app.py` submit block (`secret = str(...)` when `attempts % 2 == 0`), plus the `except TypeError` fallback in `check_guess` |
| 3 | Win or lose a game, then click New Game | Fresh game, playable | Still shows "You already won" or "Game over" and stops. Score and history also carry over. | none | `app.py` `if new_game:` block (doesn't reset status, score, history) |
| 4 | Set difficulty to Easy (1–20), click New Game | Secret between 1 and 20 | Secret is drawn from 1–100 | none | `app.py` `if new_game:` uses `random.randint(1, 100)` instead of `low, high` |
| 5 | Load the game on Normal (limit 8) | "Attempts left: 8" | Shows 7 before the first guess. The counter starts at 1, and New Game resets it to 0, so the two are inconsistent. | none | `app.py` `st.session_state.attempts = 1` and the `attempt_limit - attempts` display |
| 6 | Pick Easy, look at the info box | "Guess a number between 1 and 20" | Always says "between 1 and 100" | none | `app.py` `st.info(...)` (hardcoded text) |
| 7 | Hard difficulty | Harder than Normal | Hard is 1–50, which is *easier* than Normal's 1–100 | none | `get_range_for_difficulty` |
| 8 | Wrong guess on an even attempt with "Too High" | Score goes down or stays flat | Score goes **up** by 5 | none | `update_score`, the `attempt_number % 2` branch |

The thing I'd underline about this table: the "Console Error / Output" column is
empty for all eight bugs. Nothing ever crashed. I had to find every one of these
by comparing expected behavior to actual behavior by hand.

---

## 2. How did you use AI as a teammate?

**Which AI tools did you use on this project?**

Claude (in agent mode inside VS Code) and Copilot. I gave Claude `app.py`,
`logic_utils.py`, and `tests/test_game_logic.py` so it could see how the UI file
and the logic file connected, and I started a fresh chat for each bug so it
stayed focused on one problem at a time.

**An AI suggestion that was correct: the swapped hint messages.**

I described my first repro — secret 42, guess 60, the game said "Go HIGHER!"
when it should have said "Go LOWER!" — and explained what the game is supposed
to do. Claude found it in `check_guess` and pointed out something I had missed:
the messages were swapped in *two* places, the normal comparison branch and
again in the `except TypeError` fallback underneath it. If I had only fixed the
first one, the bug would still have shown up on some attempts. I accepted the
fix.

I verified it before trusting it. I called the function directly and confirmed
`check_guess(60, 42)` returns `("Too High", "📉 Go LOWER!")` and
`check_guess(20, 42)` returns `("Too Low", "📈 Go HIGHER!")`. Then I wrote
`test_too_high_tells_player_to_go_lower` and
`test_too_low_tells_player_to_go_higher` and ran `pytest`.

**A suggestion I did not accept as written: extra features I never asked for.**

Once it had access to the files, the AI started proposing additions it thought
the game should have — for example a new difficulty mode with unlimited
guesses. That suggestion wasn't wrong exactly, and it would probably have
worked, but it was out of scope. My job in this lab was to repair broken
behavior, not to grow the feature set, and every new mode would have been more
untested surface area sitting next to bugs I hadn't fixed yet. It also would
have made my diff much harder to review, which is the opposite of what I wanted
while hunting glitches.

I turned it down and re-prompted with a narrower instruction that named the
function and the bug instead of leaving the goal open-ended. To check that my
narrower version was still complete, I ran `pytest` (all tests passing) and read
the diff file by file to confirm nothing had been added beyond the two bugs I
set out to fix. The lesson I took from it: a vague prompt invites the AI to
invent scope, so I should say exactly which function and which behavior I want
changed.

---

## 3. Debugging and testing your fixes

**How I decided a bug was really fixed**

My rule was that I had to see the test fail for the right reason before I
trusted it passing. A green test proves nothing on its own — it might be green
because it isn't actually looking at the broken thing. So for each fix I wanted
two data points: the test passes now, and the test fails if I put the bug back.

I fixed two bugs in this pass: the swapped hint messages (#1) and the New Game
button that didn't reset the game (#3). Along the way I moved `check_guess`,
`parse_guess`, `update_score`, and `get_range_for_difficulty` out of `app.py`
and into `logic_utils.py`, which is what made any of this testable — you can't
`import` `app.py` in a test, because importing it runs the whole Streamlit app.

**The test that taught me the most**

For bug #1 I wrote:

```python
def test_too_high_tells_player_to_go_lower():
    outcome, message = check_guess(60, 42)
    assert outcome == "Too High"
    assert "LOWER" in message
```

Then I deliberately swapped the two return messages back to the broken version
and re-ran `pytest`. My two new tests failed and the three starter tests still
passed. That was the useful part: it showed me *why* the starter tests never
caught this bug in the first place. `check_guess` returns two things, an outcome
label and a hint message, and the outcome label was always correct — only the
message was backwards. Any test that checks the label and ignores the message is
blind to this entire class of bug. Testing what the player actually reads on
screen is what catches it.

I also hit a smaller version of the same lesson right at the start: the three
starter tests were already failing before I changed anything, because they
compare the whole return value to a string (`assert result == "Win"`) when the
function returns a tuple. I updated them to unpack the outcome rather than
changing `check_guess`, since `app.py` needs the message.

**The test for bug #3**

Bug #3 lived in Streamlit session state, which pytest can't reach directly, so
I restructured the fix to be testable: `initial_game_state(low, high)` returns
a plain dict of the fresh-game values, and both the first-load block and the
New Game button call it. The test asserts on the three fields the old code
forgot to reset:

```python
def test_new_game_state_is_fully_reset():
    state = initial_game_state(1, 100)
    assert state["status"] == "playing"
    assert state["score"] == 0
    assert state["history"] == []
```

Final result: `7 passed`, covering the three starter tests plus four new ones.

**Did AI help me design the tests?**

Yes, in two ways. It drafted the initial test cases, which saved me time on
boilerplate. More usefully, when I asked why the starter tests hadn't caught the
hint bug, it walked me through the fact that the outcome and the message are
separate values and the tests only ever looked at one of them — that's the
reasoning behind asserting on the message text. It also suggested restructuring
the New Game reset into a returnable dict so it could be tested without running
Streamlit, which is a technique I want to reuse: if logic is hard to test, that's
usually a sign it's tangled up with the UI and should be pulled out.

**Still to verify manually:** the New Game fix needs one run of
`streamlit run app.py` — win or lose a round, click New Game, and confirm the
board clears instead of showing "You already won." Unit tests confirm the state
dict is correct, but only the live app confirms Streamlit picks it up on rerun.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

I'd say: a Streamlit script is not like a normal program that starts up once and
then sits there waiting. Every single time you touch anything — click a button,
type in a box, change a dropdown — Streamlit throws away what it was doing and
runs your whole file again, top to bottom, as if you had just launched it. The
page you're looking at is the output of the most recent run, not a thing that's
being edited in place.

That's a problem, because a game needs to remember the secret number between
clicks, and a variable created at the top of the script gets recreated from
scratch on every rerun. `st.session_state` is the fix: it's a dictionary that
survives reruns. Anything you want the app to remember — the secret, the score,
the attempt count — has to live in there instead of in a normal variable. That's
also why the code is full of `if "secret" not in st.session_state:` guards; they
mean "only set this up on the very first run, don't wipe it every time the user
clicks."

Bug #3 was the clearest lesson in this for me. The New Game button reset
`attempts` and `secret` but left `status`, `score`, and `history` sitting in
session state. Since those survived the rerun, the script ran again, read
`status == "won"`, hit the guard that shows "You already won," and called
`st.stop()` — which kills the rest of the script before anything else can draw.
Nothing had "failed"; the app was faithfully remembering something I wanted it
to forget. The mental model I landed on: session state is the only thing that
persists, so a reset button has to clear *everything* it owns, not just the
parts you happen to be thinking about. That's why I moved the reset into one
`initial_game_state()` function used by both startup and the button — so there's
only one list of what a fresh game means.

---

## 5. Looking ahead: your developer habits

**One habit I want to reuse: break the fix to prove the test works.**

After writing a test that passed, I went back and deliberately re-introduced the
bug to watch the test fail, then reverted. It takes about thirty seconds and it
answers a question a passing test can't: is this test actually looking at the
thing I fixed? In this project that mattered — the three starter tests passed
happily while bug #1 was live, because they checked the outcome label and
ignored the hint message. A green suite told me nothing. If I'd only checked
that tests pass, I'd have shipped with a test suite that was decorative.

**What I'd do differently: name the function and the behavior in the prompt.**

My vague early prompts invited the AI to invent scope — at one point it offered
to add a whole new unlimited-guesses mode when I'd asked it to fix a bug.
Prompts like "fix the high/low messages in `check_guess`, don't change anything
else" got me tight diffs I could actually review. I'd also start each bug in a
fresh chat sooner than I did; a long thread carrying three bugs at once made the
AI keep re-suggesting things I'd already turned down.

**How this changed how I think about AI-generated code.**

Before this, my mental test for AI code was "does it run?" This entire app runs
perfectly and is wrong in eight different places — not one console error across
all of them. That reframed it for me: AI-generated code fails *plausibly*. It
produces code that looks like what a working solution looks like, which is a
much harder failure mode to spot than a crash, because there's no stack trace
pointing at the line. The `except TypeError` block in `check_guess` was the
thing that really landed it — an error handler that silently swallows a real
type mismatch and returns a confidently wrong answer instead. Going forward I
treat "it ran without errors" as the beginning of checking AI code, not the end,
and I want a test that fails for the right reason before I believe a fix.
