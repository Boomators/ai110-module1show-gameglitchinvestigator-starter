# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
|  70   |     go Lower             go higher         app.py , check_guess
| new   |   a new game starts| Does nothing   | app.py if new_game: block
game 
| hard  | games get harder.  | gets easier   |get_range_for_difficulty
mode  

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

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
