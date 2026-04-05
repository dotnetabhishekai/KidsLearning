# 🌟 Fun Learning Adventure

An interactive Streamlit game designed for 7-year-old kids (1st graders) to learn **Math**, **English**, and **English Grammar** through play.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-red)

---

## Features

### 🔢 Math Games
- **Addition** — Add numbers up to 20
- **Subtraction** — Subtract with results ≥ 0
- **Counting** — Count emoji objects on screen
- **Comparing** — Choose `>` or `<` between two numbers

### 📚 English Games
- **Animals** — Identify animals by emoji (🐶 → DOG)
- **Fruits** — Identify fruits by emoji (🍎 → APPLE)
- **Colors** — Match color emojis to their names
- **Missing Letter** — Fill in the blank in a word (e.g., `_PPLE`)
- **Rhyming** — Pick the word that rhymes (CAT → HAT)

### 📖 Grammar Games
- **Nouns** — Identify nouns (person, place, thing) in sentences
- **Pronouns** — Choose the correct pronoun (he/she/me/mine)
- **Articles** — Pick the right article (a / an / the)
- **Verbs** — Select correct verb form and tense
- **Prepositions** — Fill in location words (in/on/at/over)
- **Plurals** — Form correct plurals (regular and irregular)
- **Sentences** — Identify complete sentences, punctuation, and capitalization

### 🎲 Mix Mode
A random blend of all three categories for variety.

### 🗺️ Concept Explorer
Visual picture cards for learning concepts without quizzes — just explore and learn!
- **Numbers & Counting** — Learn 1-10 with emoji visuals
- **Shapes Around Us** — Circle, square, triangle, rectangle, star
- **Addition** — See how adding works with pictures
- **Animals & Their Homes** — Dogs, cats, birds, fish, lions
- **Letters & Sounds** — Vowels, consonants, capitals, rhymes, sight words
- **Grammar Basics** — Nouns, verbs, adjectives, prepositions, articles
- **Telling Time & Days** — Days, months, seasons, parts of the day, o'clock

### General
- 🏆 Live score tracking with accuracy percentage
- 🔥 Streak counter and personal best streak
- 🔊 Sound effects — cheerful chime on correct, gentle buzz on wrong
- 🎈 Balloon animation on correct answers
- 💡 Grammar hints after every grammar question (correct or wrong)
- 🎨 Colorful, kid-friendly gradient UI

---

## Getting Started

### Prerequisites
- Python 3.8 or higher

### Installation

```bash
# Clone the project, then Create and Activate virtual environment
# Install dependencies
pip install -r requirements.txt
```

### Run the App

```bash
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`.

---

## Project Structure

```
├── app.py              # Main application (all game logic + UI)
├── requirements.txt    # Python dependencies
├── venv/               # Virtual environment (not committed)
└── README.md           # This file
```

---

## How It Works

1. **Menu Screen** — Pick a game mode: Math, English, Grammar, or Mix.
2. **Question Screen** — A question appears with multiple-choice buttons.
3. **Answer** — Click an option. Sound plays and feedback is shown instantly.
4. **Learn** — Grammar questions show a "Did you know?" hint explaining the rule.
5. **Next** — Click "Next Question" to continue. Score and streak update in the sidebar.

---

## Customization

### Adding Questions

All question data lives in `app.py`:

| Data | Variable | Format |
|------|----------|--------|
| Animals / Fruits / Colors | `ANIMALS`, `FRUITS`, `COLORS` | List of `(emoji, WORD)` tuples |
| Grammar questions | `GRAMMAR_QUESTIONS` dict | Each category is a list of `{"text", "options", "answer", "hint"}` |
| Math questions | `gen_math_question()` | Procedurally generated — edit ranges as needed |
| Rhyme pairs | Inside `gen_english_question()` | Tuples of `(word, rhyme, wrong1, wrong2)` |

### Adjusting Difficulty

- **Math range**: Change `random.randint(1, 10)` to larger/smaller ranges in `gen_math_question()`
- **More options**: Add more items to any data list
- **New grammar categories**: Add a new key to `GRAMMAR_QUESTIONS` and update `category_emojis` / `category_labels` in `gen_grammar_question()`

---

## Browser Notes

- Sound autoplay requires at least one user interaction (clicking a button satisfies this).
- Tested on Chrome, Edge, and Firefox.
- Works on tablets — great for kids to use with touch.

---

## License

Free to use for educational purposes.
