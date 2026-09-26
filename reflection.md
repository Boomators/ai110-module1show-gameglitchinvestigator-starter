# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

The first time I ran it, the game looked completely normal — no errors, no red
tracebacks, nothing in the console at all. That was the confusing part. Every
bug in this project is a silent one

Two that stood out immediately: the hints were backwards (it told me to guess
higher when my guess was already too high), and the "New Game" button appeared
to do nothing — once I won a round, the app stayed stuck on "You already won"
forever.

**Bug Reproduction Log**

| # | Input Used | Expected Behavior | Actual Behavior | Console Error / Output | Suspected Code Location |
|---|------------|-------------------|-----------------|------------------------|-------------------------|
| 1 | Secret 42, guess 60 | "Go LOWER!" (guess is too high) | "Go HIGHER!" shown. The two hint messages are swapped. | none | `check_guess`, the return messages for Too High / Too Low |
| 2 | Win or lose a game, then click New Game | Fresh game, playable | Still shows "You already won" or "Game over" and stops. Score and history also carry over. | none | `app.py` `if new_game:` block (doesn't reset status, score, history) 
| 3 | Hard difficulty | Harder than Normal | Hard is 1–50, which is *easier* than Normal's 1–100 | none | `get_range_for_difficulty` |

---

**2. How did you use AI as a teammate?**

I used Claude and Copilot to help find and fix bugs. I gave Claude the main files so it could understand how the code worked together. I also started a new chat for each bug to keep things focused.

One useful suggestion was fixing the game's HIGHER/LOWER messages. Claude found that the messages were switched in two places. I tested the fix myself and then added tests to make sure it worked.

Claude also suggested adding new features, like unlimited guesses. I didn't use them because they weren't part of the assignment. This taught me that being specific with AI helps prevent it from adding things I didn't ask for.

**3. Debugging and testing**

I didn't just trust a test because it passed. I also changed the code back to the broken version to make sure the test would actually fail.

For one bug, the game showed the wrong HIGHER/LOWER message. The original tests didn't catch it because they only checked the result, not the message the player saw. I added tests for the messages, which caught the problem.

I also fixed the New Game button so it properly resets the game. After my changes, all 7 tests passed.

AI helped me write some of the tests and understand why the original tests missed the bug. It also showed me that separating the game logic from the UI makes it easier to test.

**4. What did you learn about Streamlit and state?**

Streamlit reruns the whole program whenever you interact with the app. Because of this, normal variables can reset.

`st.session_state` lets the app remember things like the secret number, score, and attempts between reruns.

I learned that when a New Game button is pressed, it needs to reset everything related to the old game. Otherwise, old information can still affect the new game.

**5. Looking ahead**

One habit I want to keep is testing my tests. After writing a test, I put the bug back into the code to make sure the test actually failed.

I also learned to give AI very specific instructions. Instead of saying "fix the game," I can say exactly which function and behavior I want changed.

Most importantly, I learned that AI code can look correct and still be wrong. Just because the program runs without errors doesn't mean everything works. I need to test the code before trusting it.
