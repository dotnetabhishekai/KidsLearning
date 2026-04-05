import streamlit as st
import random
import struct
import math
import io
import base64
import streamlit.components.v1 as components

# Helper: use st.html if available, else fall back to components.html
def _html(content, **kwargs):
    try:
        st.html(content)
    except AttributeError:
        components.html(content, height=kwargs.get("height", 0), scrolling=False)


def generate_tone(frequency, duration_ms, sample_rate=22050, volume=0.5):
    """Generate a WAV tone as bytes."""
    n_samples = int(sample_rate * duration_ms / 1000)
    buf = io.BytesIO()
    # WAV header
    data_size = n_samples * 2
    buf.write(b'RIFF')
    buf.write(struct.pack('<I', 36 + data_size))
    buf.write(b'WAVE')
    buf.write(b'fmt ')
    buf.write(struct.pack('<IHHIIHH', 16, 1, 1, sample_rate, sample_rate * 2, 2, 16))
    buf.write(b'data')
    buf.write(struct.pack('<I', data_size))
    for i in range(n_samples):
        t = i / sample_rate
        # Apply fade-out envelope for the last 20% to avoid clicks
        envelope = min(1.0, (n_samples - i) / (n_samples * 0.2))
        sample = volume * envelope * math.sin(2 * math.pi * frequency * t)
        buf.write(struct.pack('<h', int(sample * 32767)))
    return buf.getvalue()


def make_correct_sound():
    """Happy ascending two-tone chime."""
    tone1 = generate_tone(523, 150, volume=0.4)  # C5
    tone2 = generate_tone(659, 150, volume=0.4)  # E5
    tone3 = generate_tone(784, 250, volume=0.5)  # G5
    # Combine into one WAV
    sr = 22050
    samples = []
    for tone in [tone1, tone2, tone3]:
        data = tone[44:]  # skip header
        samples.append(data)
    combined_data = b''.join(samples)
    buf = io.BytesIO()
    buf.write(b'RIFF')
    buf.write(struct.pack('<I', 36 + len(combined_data)))
    buf.write(b'WAVE')
    buf.write(b'fmt ')
    buf.write(struct.pack('<IHHIIHH', 16, 1, 1, sr, sr * 2, 2, 16))
    buf.write(b'data')
    buf.write(struct.pack('<I', len(combined_data)))
    buf.write(combined_data)
    return base64.b64encode(buf.getvalue()).decode()


def make_wrong_sound():
    """Descending two-tone buzz."""
    tone1 = generate_tone(350, 200, volume=0.4)
    tone2 = generate_tone(250, 300, volume=0.35)
    sr = 22050
    combined_data = tone1[44:] + tone2[44:]
    buf = io.BytesIO()
    buf.write(b'RIFF')
    buf.write(struct.pack('<I', 36 + len(combined_data)))
    buf.write(b'WAVE')
    buf.write(b'fmt ')
    buf.write(struct.pack('<IHHIIHH', 16, 1, 1, sr, sr * 2, 2, 16))
    buf.write(b'data')
    buf.write(struct.pack('<I', len(combined_data)))
    buf.write(combined_data)
    return base64.b64encode(buf.getvalue()).decode()


def play_sound(b64_audio):
    """Inject auto-playing audio via HTML."""
    _html(f"""
        <audio autoplay>
            <source src="data:audio/wav;base64,{b64_audio}" type="audio/wav">
        </audio>
    """, height=0)

# --- Page Config ---
st.set_page_config(page_title="🌟 Fun Learning for Kids!", page_icon="🎮", layout="centered")

# --- Custom CSS ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 50%, #a1c4fd 100%); }
    .big-emoji { font-size: 80px; text-align: center; }
    .score-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; padding: 15px; border-radius: 15px;
        text-align: center; font-size: 22px; font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .question-box {
        background: white; padding: 25px; border-radius: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        text-align: center; font-size: 28px; margin: 20px 0;
    }
    div.stButton > button {
        font-size: 20px; padding: 12px 30px; border-radius: 15px;
        font-weight: bold; border: 3px solid transparent;
        transition: all 0.3s ease; width: 100%;
    }
    div.stButton > button:hover { transform: scale(1.05); }
    .correct { color: #2ecc71; font-size: 40px; text-align: center; font-weight: bold; }
    .wrong { color: #e74c3c; font-size: 40px; text-align: center; font-weight: bold; }
    .streak-text { text-align: center; font-size: 18px; color: #6c5ce7; font-weight: bold; }
    .concept-card {
        background: white; border-radius: 20px; padding: 25px; margin: 10px 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1); text-align: center;
        transition: transform 0.3s ease;
    }
    .concept-card:hover { transform: translateY(-5px); }
    .concept-scene {
        font-size: 60px; line-height: 1.4; padding: 15px;
        background: #f8f9fa; border-radius: 15px; margin: 10px 0;
    }
    .concept-title {
        font-size: 26px; font-weight: bold; color: #6c5ce7; margin: 10px 0;
    }
    .concept-desc {
        font-size: 18px; color: #636e72; line-height: 1.6;
    }
    .concept-example {
        background: #e8f5e9; padding: 12px; border-radius: 12px;
        font-size: 17px; margin: 8px 0; color: #2d3436;
    }
    .topic-header {
        font-size: 32px; text-align: center; font-weight: bold;
        color: #6c5ce7; margin: 15px 0;
    }
    .nav-pill {
        display: inline-block; padding: 8px 18px; margin: 4px;
        border-radius: 20px; font-size: 16px; font-weight: bold;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Init ---
defaults = {"score": 0, "total": 0, "streak": 0, "best_streak": 0,
            "question": None, "answered": False, "last_correct": None, "mode": "menu"}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- Data ---
ANIMALS = [
    ("🐶", "DOG"), ("🐱", "CAT"), ("🐸", "FROG"), ("🐰", "RABBIT"), ("🐻", "BEAR"),
    ("🦁", "LION"), ("🐘", "ELEPHANT"), ("🐧", "PENGUIN"), ("🦊", "FOX"), ("🐢", "TURTLE"),
    ("🐬", "DOLPHIN"), ("🦋", "BUTTERFLY"), ("🐝", "BEE"), ("🐴", "HORSE"), ("🐷", "PIG"),
]
FRUITS = [
    ("🍎", "APPLE"), ("🍌", "BANANA"), ("🍇", "GRAPES"), ("🍓", "STRAWBERRY"), ("🍊", "ORANGE"),
    ("🍉", "WATERMELON"), ("🍒", "CHERRY"), ("🥝", "KIWI"), ("🍑", "PEACH"), ("🍍", "PINEAPPLE"),
]
COLORS = [
    ("🔴", "RED"), ("🔵", "BLUE"), ("🟢", "GREEN"), ("🟡", "YELLOW"), ("🟠", "ORANGE"),
    ("🟣", "PURPLE"), ("⚫", "BLACK"), ("⚪", "WHITE"), ("🟤", "BROWN"), ("💗", "PINK"),
]

ENCOURAGEMENTS = ["Amazing! 🌟", "You're a star! ⭐", "Fantastic! 🎉", "Great job! 🏆",
                   "Wonderful! 🌈", "Super! 💪", "Brilliant! 🧠", "Keep going! 🚀"]
TRY_AGAIN = ["Almost! Try again! 💪", "So close! You got this! 🌟", "Don't give up! 🎯",
             "Keep trying, superstar! ⭐"]

# --- Grammar Data ---
GRAMMAR_QUESTIONS = {
    "pronouns": [
        {"text": "___ is my best friend.", "options": ["He", "Him", "His", "Her"], "answer": "He",
         "hint": "'He' is used as a subject — the person doing something."},
        {"text": "Please give it to ___.", "options": ["I", "me", "my", "mine"], "answer": "me",
         "hint": "'Me' is used as an object — the person receiving something."},
        {"text": "___ are going to the park.", "options": ["We", "Us", "Our", "Them"], "answer": "We",
         "hint": "'We' is a subject pronoun — it tells who is doing the action."},
        {"text": "That book is ___.", "options": ["my", "mine", "me", "I"], "answer": "mine",
         "hint": "'Mine' shows something belongs to me, without a noun after it."},
        {"text": "___ dog is very cute.", "options": ["Her", "She", "Hers", "Him"], "answer": "Her",
         "hint": "'Her' before a noun shows who the dog belongs to."},
    ],
    "articles": [
        {"text": "I saw ___ elephant at the zoo.", "options": ["a", "an", "the", "is"], "answer": "an",
         "hint": "Use 'an' before words that start with a vowel sound (a, e, i, o, u)."},
        {"text": "She has ___ red ball.", "options": ["a", "an", "the", "is"], "answer": "a",
         "hint": "Use 'a' before words that start with a consonant sound."},
        {"text": "___ sun is very bright today.", "options": ["A", "An", "The", "Is"], "answer": "The",
         "hint": "Use 'the' when talking about something specific that everyone knows."},
        {"text": "He ate ___ apple for lunch.", "options": ["a", "an", "the", "is"], "answer": "an",
         "hint": "'Apple' starts with a vowel sound, so we use 'an'."},
        {"text": "I need ___ pencil to write.", "options": ["a", "an", "the", "is"], "answer": "a",
         "hint": "'Pencil' starts with a consonant sound, so we use 'a'."},
    ],
    "verbs": [
        {"text": "She ___ to school every day.", "options": ["go", "goes", "going", "gone"], "answer": "goes",
         "hint": "With he/she/it, add -es to 'go' → 'goes'."},
        {"text": "They ___ playing in the garden.", "options": ["is", "are", "am", "was"], "answer": "are",
         "hint": "'They' is plural, so we use 'are'."},
        {"text": "I ___ a student.", "options": ["is", "are", "am", "was"], "answer": "am",
         "hint": "With 'I', always use 'am'."},
        {"text": "The cat ___ on the mat.", "options": ["sit", "sits", "sitting", "sat"], "answer": "sits",
         "hint": "The cat is one (singular), so the verb gets an 's' → 'sits'."},
        {"text": "We ___ our homework yesterday.", "options": ["do", "did", "does", "done"], "answer": "did",
         "hint": "'Yesterday' means past tense, so we use 'did'."},
        {"text": "He ___ milk every morning.", "options": ["drink", "drinks", "drinking", "drank"], "answer": "drinks",
         "hint": "With he/she/it in present tense, add -s → 'drinks'."},
    ],
    "prepositions": [
        {"text": "The cat is ___ the table.", "options": ["on", "at", "is", "an"], "answer": "on",
         "hint": "'On' means something is resting on top of a surface."},
        {"text": "She is ___ the classroom.", "options": ["in", "on", "at", "an"], "answer": "in",
         "hint": "'In' means inside an enclosed space."},
        {"text": "The bird flew ___ the tree.", "options": ["over", "on", "is", "an"], "answer": "over",
         "hint": "'Over' means above and across something."},
        {"text": "He is standing ___ the door.", "options": ["at", "on", "in", "an"], "answer": "at",
         "hint": "'At' is used for a specific point or location."},
        {"text": "The fish is ___ the water.", "options": ["in", "on", "at", "an"], "answer": "in",
         "hint": "'In' means inside something — the fish is inside the water."},
        {"text": "The ball rolled ___ the hill.", "options": ["down", "up", "in", "at"], "answer": "down",
         "hint": "'Down' means moving from a higher place to a lower place."},
        {"text": "She walked ___ the bridge.", "options": ["across", "in", "at", "on"], "answer": "across",
         "hint": "'Across' means from one side to the other."},
        {"text": "The dog is hiding ___ the bed.", "options": ["under", "over", "on", "at"], "answer": "under",
         "hint": "'Under' means below or beneath something."},
        {"text": "He sat ___ his mother and father.", "options": ["between", "on", "in", "at"], "answer": "between",
         "hint": "'Between' means in the middle of two things or people."},
        {"text": "The shop is ___ the school.", "options": ["near", "in", "on", "at"], "answer": "near",
         "hint": "'Near' means close to something, not far away."},
        {"text": "She ran ___ the house.", "options": ["around", "in", "on", "at"], "answer": "around",
         "hint": "'Around' means in a circle or on all sides of something."},
        {"text": "The picture is ___ the wall.", "options": ["on", "in", "under", "near"], "answer": "on",
         "hint": "'On' means attached to or touching a surface."},
        {"text": "We walked ___ the park.", "options": ["through", "on", "at", "in"], "answer": "through",
         "hint": "'Through' means going in one side and out the other."},
        {"text": "The plane flew ___ the clouds.", "options": ["above", "under", "in", "at"], "answer": "above",
         "hint": "'Above' means higher than something, up in the air."},
        {"text": "Put the toys ___ the box.", "options": ["into", "on", "at", "over"], "answer": "into",
         "hint": "'Into' means moving from outside to inside something."},
    ],
    "plurals": [
        {"text": "One cat, two ___.", "options": ["cats", "cat", "cates", "catis"], "answer": "cats",
         "hint": "Most words just add -s to make them plural."},
        {"text": "One box, three ___.", "options": ["boxes", "boxs", "boxen", "box"], "answer": "boxes",
         "hint": "Words ending in x, s, sh, ch add -es → 'boxes'."},
        {"text": "One child, many ___.", "options": ["children", "childs", "childes", "childrens"], "answer": "children",
         "hint": "'Child' has a special plural — 'children'. It's irregular!"},
        {"text": "One tooth, all my ___.", "options": ["teeth", "tooths", "toothes", "teeths"], "answer": "teeth",
         "hint": "'Tooth' → 'teeth' is an irregular plural. You just memorize it!"},
        {"text": "One baby, two ___.", "options": ["babies", "babys", "babyes", "babyies"], "answer": "babies",
         "hint": "Words ending in consonant + y: change y to i and add -es."},
    ],
    "nouns": [
        {"text": "Which word is a noun?\n\nThe dog is running fast.",
         "options": ["dog", "running", "fast", "is"], "answer": "dog",
         "hint": "A noun is a person, place, animal, or thing. 'Dog' is an animal!"},
        {"text": "Which word is a noun?\n\nShe reads a book.",
         "options": ["book", "reads", "she", "a"], "answer": "book",
         "hint": "A noun is a thing you can touch or see. 'Book' is a thing!"},
        {"text": "Which word is a noun?\n\nThe teacher is kind.",
         "options": ["teacher", "kind", "is", "the"], "answer": "teacher",
         "hint": "A noun can be a person. 'Teacher' is a person!"},
        {"text": "Which is a place noun?",
         "options": ["school", "happy", "run", "blue"], "answer": "school",
         "hint": "Place nouns name locations — school, park, home, city."},
        {"text": "Which word is NOT a noun?\n\ncat, jump, ball, tree",
         "options": ["jump", "cat", "ball", "tree"], "answer": "jump",
         "hint": "'Jump' is an action (verb), not a noun. Cat, ball, and tree are all things!"},
        {"text": "How many nouns are in this sentence?\n\nThe girl ate a cake.",
         "options": ["2", "1", "3", "0"], "answer": "2",
         "hint": "'Girl' (person) and 'cake' (thing) are the two nouns."},
        {"text": "Which is a proper noun?",
         "options": ["London", "city", "river", "park"], "answer": "London",
         "hint": "Proper nouns are special names and start with a capital letter!"},
        {"text": "Pick the noun:\n\nThe sun is bright.",
         "options": ["sun", "bright", "is", "the"], "answer": "sun",
         "hint": "'Sun' is a thing in the sky — that makes it a noun!"},
    ],
    "sentences": [
        {"text": "Which is a complete sentence?",
         "options": ["The dog runs fast.", "Dog fast.", "Runs the.", "Fast dog the."], "answer": "The dog runs fast.",
         "hint": "A sentence needs a subject (who) and a verb (what they do)."},
        {"text": "Which sentence is a question?",
         "options": ["Where is my bag?", "My bag is here.", "Bag is where.", "Here my bag."],
         "answer": "Where is my bag?",
         "hint": "Questions start with words like who, what, where, when, why, how and end with '?'."},
        {"text": "What punctuation ends a sentence?",
         "options": [".", "!", "?", ","], "answer": ".",
         "hint": "A regular statement ends with a period (full stop)."},
        {"text": "Which word should be capitalized?\n\njohn went to school.",
         "options": ["john", "went", "to", "school"], "answer": "john",
         "hint": "Names of people always start with a capital letter → 'John'."},
        {"text": "Which is correct?",
         "options": ["I like ice cream.", "i like ice cream.", "I like Ice Cream.", "i Like ice cream."],
         "answer": "I like ice cream.",
         "hint": "'I' is always capitalized. Regular words don't need capitals."},
    ],
}

# --- Concept Explorer Data ---
CONCEPT_TOPICS = {
    "numbers": {
        "icon": "🔢", "title": "Numbers & Counting",
        "cards": [
            {"scene": "1️⃣", "name": "One", "visual": "🍎",
             "desc": "One means a single thing.", "examples": ["I have 1 apple 🍎", "There is 1 sun ☀️"]},
            {"scene": "2️⃣", "name": "Two", "visual": "🍎🍎",
             "desc": "Two means a pair — like your two hands!", "examples": ["2 eyes 👀", "2 shoes 👟👟"]},
            {"scene": "3️⃣", "name": "Three", "visual": "🍎🍎🍎",
             "desc": "Three is one more than two.", "examples": ["A triangle has 3 sides 🔺", "3 little pigs 🐷🐷🐷"]},
            {"scene": "5️⃣", "name": "Five", "visual": "🖐️",
             "desc": "Five fingers on one hand!", "examples": ["5 fingers 🖐️", "A star has 5 points ⭐"]},
            {"scene": "🔟", "name": "Ten", "visual": "🖐️🖐️",
             "desc": "Ten is both hands together!", "examples": ["10 fingers 🖐️🖐️", "10 toes 🦶🦶"]},
        ],
    },
    "shapes": {
        "icon": "🔷", "title": "Shapes Around Us",
        "cards": [
            {"scene": "🔴", "name": "Circle", "visual": "⭕ 🍕 🎯 ⚽ 🍩",
             "desc": "A circle is round with no corners.", "examples": ["A pizza is a circle 🍕", "The sun looks like a circle ☀️"]},
            {"scene": "🟥", "name": "Square", "visual": "⬜ 🧊 🖼️ 🎲 📦",
             "desc": "A square has 4 equal sides and 4 corners.", "examples": ["A window can be square 🪟", "A dice face is square 🎲"]},
            {"scene": "🔺", "name": "Triangle", "visual": "🔺 🏔️ 📐 🍕",
             "desc": "A triangle has 3 sides and 3 corners.", "examples": ["A slice of pizza 🍕", "A mountain peak 🏔️"]},
            {"scene": "⬛", "name": "Rectangle", "visual": "📱 🚪 📺 📕 🛏️",
             "desc": "A rectangle has 4 sides — 2 long and 2 short.", "examples": ["A door is a rectangle 🚪", "A book is a rectangle 📕"]},
            {"scene": "⭐", "name": "Star", "visual": "⭐ 🌟 ✨ 💫 🌠",
             "desc": "A star has points sticking out!", "examples": ["Stars twinkle at night 🌟", "A starfish has 5 arms 🌊"]},
        ],
    },
    "addition": {
        "icon": "➕", "title": "Addition (Putting Together)",
        "cards": [
            {"scene": "🍎 + 🍎 = 🍎🍎", "name": "1 + 1 = 2", "visual": "👆 + 👆 = ✌️",
             "desc": "When we add, we put things together to get more!", "examples": ["1 cat + 1 cat = 2 cats 🐱🐱"]},
            {"scene": "🍎🍎 + 🍎 = 🍎🍎🍎", "name": "2 + 1 = 3", "visual": "✌️ + 👆 = 3️⃣",
             "desc": "Start with 2, add 1 more, now you have 3!", "examples": ["2 birds + 1 bird = 3 birds 🐦🐦🐦"]},
            {"scene": "🍎🍎 + 🍎🍎 = 🍎🍎🍎🍎", "name": "2 + 2 = 4", "visual": "✌️ + ✌️ = 4️⃣",
             "desc": "Two plus two makes four — like 4 wheels on a car!", "examples": ["2 socks + 2 socks = 4 socks 🧦🧦🧦🧦"]},
            {"scene": "🖐️ + 🖐️ = 🔟", "name": "5 + 5 = 10", "visual": "5️⃣ + 5️⃣ = 🔟",
             "desc": "Both hands together make 10 fingers!", "examples": ["5 red + 5 blue = 10 balloons 🎈"]},
            {"scene": "🍎🍎🍎 + 🍎🍎 = 🍎🍎🍎🍎🍎", "name": "3 + 2 = 5", "visual": "3️⃣ + 2️⃣ = 5️⃣",
             "desc": "Three and two together make five!", "examples": ["3 dogs + 2 dogs = 5 dogs 🐶🐶🐶🐶🐶"]},
        ],
    },
    "animals": {
        "icon": "🦁", "title": "Animals & Their Homes",
        "cards": [
            {"scene": "🐶🏠", "name": "Dog", "visual": "🐕 🦴 🏠",
             "desc": "Dogs live in houses with people. They are pets!", "examples": ["Dogs say: Woof! 🐕", "Dogs love bones 🦴"]},
            {"scene": "🐱🧶", "name": "Cat", "visual": "🐈 🧶 🐟",
             "desc": "Cats are soft and furry pets that purr.", "examples": ["Cats say: Meow! 🐱", "Cats love fish 🐟"]},
            {"scene": "🐦🌳", "name": "Bird", "visual": "🐦 🪺 🌳",
             "desc": "Birds live in nests on trees and can fly!", "examples": ["Birds say: Tweet! 🐦", "Birds lay eggs 🥚"]},
            {"scene": "🐟🌊", "name": "Fish", "visual": "🐠 🌊 🐚",
             "desc": "Fish live in water and breathe through gills.", "examples": ["Fish swim in the sea 🌊", "Fish have fins and scales 🐟"]},
            {"scene": "🦁🌍", "name": "Lion", "visual": "🦁 👑 🌿",
             "desc": "Lions are called the King of the Jungle!", "examples": ["Lions say: Roar! 🦁", "Lions live in groups called prides"]},
        ],
    },
    "alphabet": {
        "icon": "🔤", "title": "Letters & Sounds",
        "cards": [
            {"scene": "🅰️", "name": "Vowels: A E I O U", "visual": "🍎 🥚 🍦 🐙 ☂️",
             "desc": "Vowels are special letters — every word needs at least one!", "examples": ["A is for Apple 🍎", "E is for Egg 🥚", "I is for Ice cream 🍦"]},
            {"scene": "🔤", "name": "Consonants", "visual": "🐝 🐱 🐶 🐸 🦁",
             "desc": "All the other letters (B, C, D, F...) are consonants.", "examples": ["B is for Bee 🐝", "C is for Cat 🐱", "D is for Dog 🐶"]},
            {"scene": "📝", "name": "Capital Letters", "visual": "A B C vs a b c",
             "desc": "Big letters are capitals. We use them to start names and sentences.", "examples": ["My name is Sam → S is capital", "I love dogs. → I is always capital"]},
            {"scene": "🗣️", "name": "Rhyming Words", "visual": "🐱🎩  🐟🍽️  🌙🥄",
             "desc": "Rhyming words sound the same at the end!", "examples": ["Cat - Hat 🐱🎩", "Fish - Dish 🐟🍽️", "Moon - Spoon 🌙🥄"]},
            {"scene": "📖", "name": "Sight Words", "visual": "the  is  and  to  a",
             "desc": "Sight words are small words you see everywhere. Learn them by heart!", "examples": ["The cat is big.", "I go to school.", "She and I play."]},
        ],
    },
    "grammar_concepts": {
        "icon": "📖", "title": "Grammar Basics",
        "cards": [
            {"scene": "🏷️", "name": "Nouns", "visual": "🐶 dog  👧 girl  🏫 school",
             "desc": "A noun is a person, place, animal, or thing.", "examples": ["Person: teacher 👩‍🏫", "Place: park 🏞️", "Thing: ball ⚽", "Animal: cat 🐱"]},
            {"scene": "🏃", "name": "Verbs", "visual": "🏃 run  🍽️ eat  😴 sleep",
             "desc": "A verb is an action word — something you DO.", "examples": ["I run 🏃", "She eats 🍽️", "He sleeps 😴", "We play 🎮"]},
            {"scene": "🎨", "name": "Adjectives", "visual": "🔴 red  📏 big  😊 happy",
             "desc": "Adjectives describe nouns — they tell us more about things.", "examples": ["A big dog 🐕", "A red ball 🔴", "A happy girl 😊"]},
            {"scene": "📍", "name": "Prepositions", "visual": "🐱⬆️📦  🐱⬇️📦  🐱📦",
             "desc": "Prepositions tell us WHERE something is.", "examples": ["The cat is ON the box 🐱⬆️📦", "The cat is UNDER the box 🐱⬇️📦", "The cat is IN the box 🐱📦"]},
            {"scene": "📰", "name": "Articles: a, an, the", "visual": "🍎 an apple  🐶 a dog  ☀️ the sun",
             "desc": "'A' and 'an' mean any one thing. 'The' means a specific thing.", "examples": ["AN apple (starts with vowel) 🍎", "A dog (starts with consonant) 🐶", "THE sun (only one!) ☀️"]},
        ],
    },
    "time": {
        "icon": "🕐", "title": "Telling Time & Days",
        "cards": [
            {"scene": "📅", "name": "Days of the Week", "visual": "Mon Tue Wed Thu Fri Sat Sun",
             "desc": "There are 7 days in a week!", "examples": ["Monday is the first school day 🏫", "Saturday & Sunday = Weekend! 🎉"]},
            {"scene": "🗓️", "name": "Months", "visual": "Jan → Dec (12 months)",
             "desc": "There are 12 months in a year.", "examples": ["January is the first month ❄️", "Your birthday is in a month! 🎂"]},
            {"scene": "🌅🌞🌙", "name": "Parts of the Day", "visual": "🌅 Morning  ☀️ Afternoon  🌙 Night",
             "desc": "The day has three main parts.", "examples": ["Morning: wake up & breakfast 🌅", "Afternoon: school & play ☀️", "Night: dinner & sleep 🌙"]},
            {"scene": "🕐", "name": "O'Clock Time", "visual": "🕐 1:00  🕑 2:00  🕒 3:00",
             "desc": "When the long hand points to 12, we say 'o'clock'.", "examples": ["🕐 = 1 o'clock", "🕕 = 6 o'clock", "🕛 = 12 o'clock"]},
            {"scene": "🌦️", "name": "Seasons", "visual": "🌸 Spring  ☀️ Summer  🍂 Fall  ❄️ Winter",
             "desc": "There are 4 seasons in a year.", "examples": ["Spring: flowers bloom 🌸", "Summer: hot & sunny ☀️", "Fall: leaves change 🍂", "Winter: cold & snowy ❄️"]},
        ],
    },
}


# --- Question Generators ---
def gen_math_question():
    qtype = random.choice(["add", "subtract", "compare", "count",
                           "before_after", "odd_even", "place_value",
                           "number_word", "shape_sides", "word_problem"])
    if qtype == "add":
        a, b = random.randint(1, 10), random.randint(1, 10)
        answer = a + b
        wrong = [answer + random.choice([-2, -1, 1, 2]) for _ in range(3)]
        wrong = [w if w != answer and w > 0 else answer + 3 for w in wrong]
        options = wrong + [answer]
        random.shuffle(options)
        return {"text": f"What is {a} + {b} ?", "emoji": "➕", "answer": str(answer),
                "options": [str(o) for o in options]}
    elif qtype == "subtract":
        a = random.randint(5, 15)
        b = random.randint(1, a)
        answer = a - b
        wrong = [answer + random.choice([-2, -1, 1, 2]) for _ in range(3)]
        wrong = [w if w != answer and w >= 0 else answer + 3 for w in wrong]
        options = wrong + [answer]
        random.shuffle(options)
        return {"text": f"What is {a} - {b} ?", "emoji": "➖", "answer": str(answer),
                "options": [str(o) for o in options]}
    elif qtype == "compare":
        a, b = random.randint(1, 20), random.randint(1, 20)
        while a == b:
            b = random.randint(1, 20)
        answer = ">" if a > b else "<"
        return {"text": f"Which sign goes between?\n\n{a}  ___  {b}", "emoji": "⚖️",
                "answer": answer, "options": [">", "<"]}
    elif qtype == "count":
        emoji = random.choice(["⭐", "🎈", "🍎", "🌸", "🐟"])
        count = random.randint(2, 9)
        display = f"{emoji} " * count
        answer = count
        wrong = list({max(1, answer + d) for d in [-2, -1, 1, 2]} - {answer})[:3]
        options = wrong + [answer]
        random.shuffle(options)
        return {"text": f"How many {emoji} are there?\n\n{display}", "emoji": "🔢",
                "answer": str(answer), "options": [str(o) for o in options]}
    elif qtype == "before_after":
        n = random.randint(2, 19)
        direction = random.choice(["before", "after"])
        if direction == "before":
            answer = n - 1
            text = f"What number comes BEFORE {n}?"
        else:
            answer = n + 1
            text = f"What number comes AFTER {n}?"
        wrong = list({max(0, answer + d) for d in [-2, -1, 1, 2]} - {answer})[:3]
        options = (wrong + [answer])
        random.shuffle(options)
        return {"text": text, "emoji": "🔢", "answer": str(answer),
                "options": [str(o) for o in options],
                "hint": f"Numbers go in order: ...{n-1}, {n}, {n+1}..."}
    elif qtype == "odd_even":
        n = random.randint(1, 20)
        answer = "Even" if n % 2 == 0 else "Odd"
        return {"text": f"Is {n} odd or even?", "emoji": "🔢",
                "answer": answer, "options": ["Odd", "Even"],
                "hint": "Even numbers end in 0, 2, 4, 6, 8. Odd numbers end in 1, 3, 5, 7, 9."}
    elif qtype == "place_value":
        n = random.randint(11, 99)
        ask = random.choice(["tens", "ones"])
        if ask == "tens":
            answer = n // 10
            text = f"How many TENS in {n}?"
        else:
            answer = n % 10
            text = f"What is the ONES digit in {n}?"
        wrong = list({max(0, answer + d) for d in [-2, -1, 1, 2]} - {answer})[:3]
        options = (wrong + [answer])
        random.shuffle(options)
        return {"text": text, "emoji": "🔟", "answer": str(answer),
                "options": [str(o) for o in options],
                "hint": f"In {n}, the tens digit is {n // 10} and the ones digit is {n % 10}."}
    elif qtype == "number_word":
        words = {1: "ONE", 2: "TWO", 3: "THREE", 4: "FOUR", 5: "FIVE",
                 6: "SIX", 7: "SEVEN", 8: "EIGHT", 9: "NINE", 10: "TEN",
                 11: "ELEVEN", 12: "TWELVE", 13: "THIRTEEN", 14: "FOURTEEN", 15: "FIFTEEN",
                 16: "SIXTEEN", 17: "SEVENTEEN", 18: "EIGHTEEN", 19: "NINETEEN", 20: "TWENTY"}
        direction = random.choice(["to_word", "to_number"])
        n = random.randint(1, 20)
        if direction == "to_word":
            answer = words[n]
            others = random.sample([w for k, w in words.items() if k != n], 3)
            options = others + [answer]
            random.shuffle(options)
            return {"text": f"What is the word for {n}?", "emoji": "🔤", "answer": answer,
                    "options": options, "hint": f"{n} is spelled '{words[n]}'."}
        else:
            answer = str(n)
            others = [str(random.choice([k for k in words if k != n])) for _ in range(3)]
            options = list(set(others + [answer]))
            while len(options) < 4:
                options.append(str(random.randint(1, 20)))
            options = list(set(options))[:4]
            if answer not in options:
                options[-1] = answer
            random.shuffle(options)
            return {"text": f"What number is '{words[n]}'?", "emoji": "🔢", "answer": answer,
                    "options": options, "hint": f"'{words[n]}' means {n}."}
    elif qtype == "shape_sides":
        shapes = [
            ("Triangle 🔺", 3), ("Square ⬜", 4), ("Rectangle 📐", 4),
            ("Pentagon ⬠", 5), ("Hexagon ⬡", 6), ("Circle ⭕", 0),
        ]
        shape, sides = random.choice(shapes)
        if sides == 0:
            answer = "0"
            text = f"How many straight sides does a {shape} have?"
            hint = "A circle is round — it has no straight sides!"
        else:
            answer = str(sides)
            text = f"How many sides does a {shape} have?"
            hint = f"A {shape.split()[0]} has {sides} sides."
        wrong = list({max(0, int(answer) + d) for d in [-2, -1, 1, 2]} - {int(answer)})[:3]
        options = [str(w) for w in wrong] + [answer]
        random.shuffle(options)
        return {"text": text, "emoji": "📐", "answer": answer,
                "options": options, "hint": hint}
    else:  # word_problem
        problems = [
            ("Sam has {a} 🍎 apples. Mom gives him {b} more.\nHow many apples does Sam have now?",
             lambda a, b: a + b, (1, 5), (1, 5)),
            ("There are {a} 🐦 birds on a tree. {b} fly away.\nHow many birds are left?",
             lambda a, b: a - b, (5, 10), (1, 4)),
            ("A box has {a} 🖍️ red crayons and {b} 🖍️ blue crayons.\nHow many crayons in total?",
             lambda a, b: a + b, (1, 6), (1, 6)),
            ("You have {a} 🍪 cookies. You eat {b}.\nHow many cookies are left?",
             lambda a, b: a - b, (4, 10), (1, 3)),
            ("There are {a} 🚗 cars in a parking lot. {b} more arrive.\nHow many cars are there now?",
             lambda a, b: a + b, (2, 8), (1, 5)),
            ("{a} 🐸 frogs are on a log. {b} more jump on.\nHow many frogs are on the log?",
             lambda a, b: a + b, (1, 5), (1, 5)),
            ("A hen has {a} 🥚 eggs. {b} eggs hatch.\nHow many eggs are left?",
             lambda a, b: a - b, (5, 10), (1, 4)),
            ("You see {a} ⭐ stars. Then you see {b} more.\nHow many stars in all?",
             lambda a, b: a + b, (2, 7), (1, 6)),
        ]
        template, fn, (lo_a, hi_a), (lo_b, hi_b) = random.choice(problems)
        a = random.randint(lo_a, hi_a)
        b = random.randint(lo_b, min(hi_b, a))  # ensure b <= a for subtraction
        answer = fn(a, b)
        text = template.format(a=a, b=b)
        wrong = list({max(0, answer + d) for d in [-3, -1, 1, 2]} - {answer})[:3]
        options = wrong + [answer]
        random.shuffle(options)
        return {"text": text, "emoji": "📝", "answer": str(answer),
                "options": [str(o) for o in options],
                "hint": f"The answer is {answer}."}


def gen_english_question():
    qtype = random.choice(["spell_animal", "spell_fruit", "color", "missing_letter", "rhyme"])
    if qtype == "spell_animal":
        emoji, word = random.choice(ANIMALS)
        others = random.sample([w for _, w in ANIMALS if w != word], min(3, len(ANIMALS) - 1))
        options = others + [word]
        random.shuffle(options)
        return {"text": f"What animal is this?", "emoji": emoji, "answer": word, "options": options}
    elif qtype == "spell_fruit":
        emoji, word = random.choice(FRUITS)
        others = random.sample([w for _, w in FRUITS if w != word], min(3, len(FRUITS) - 1))
        options = others + [word]
        random.shuffle(options)
        return {"text": f"What fruit is this?", "emoji": emoji, "answer": word, "options": options}
    elif qtype == "color":
        emoji, word = random.choice(COLORS)
        others = random.sample([w for _, w in COLORS if w != word], min(3, len(COLORS) - 1))
        options = others + [word]
        random.shuffle(options)
        return {"text": f"What color is this?", "emoji": emoji, "answer": word, "options": options}
    elif qtype == "missing_letter":
        words = ["APPLE", "HOUSE", "WATER", "HAPPY", "TIGER", "MOUSE", "PLANT", "SMILE",
                 "CLOUD", "TRAIN", "BEACH", "LIGHT", "STONE", "BREAD", "SLEEP"]
        word = random.choice(words)
        idx = random.randint(0, len(word) - 1)
        hidden = word[:idx] + "_" + word[idx + 1:]
        correct = word[idx]
        wrongs = random.sample([c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if c != correct], 3)
        options = wrongs + [correct]
        random.shuffle(options)
        return {"text": f"Fill in the missing letter:\n\n{hidden}", "emoji": "✏️",
                "answer": correct, "options": options}
    else:  # rhyme
        pairs = [("CAT", "HAT", "DOG", "SUN"), ("FISH", "DISH", "BIRD", "TREE"),
                 ("CAKE", "LAKE", "BOOK", "FROG"), ("MOON", "SPOON", "STAR", "HAND"),
                 ("RING", "SING", "BALL", "DESK"), ("BOAT", "COAT", "SHIP", "LAMP"),
                 ("BEAR", "PEAR", "WOLF", "MILK"), ("NIGHT", "LIGHT", "DARK", "RAIN")]
        word, rhyme, w1, w2 = random.choice(pairs)
        options = [rhyme, w1, w2]
        random.shuffle(options)
        return {"text": f"Which word rhymes with {word}?", "emoji": "🎵",
                "answer": rhyme, "options": options}


def gen_grammar_question():
    category = random.choice(list(GRAMMAR_QUESTIONS.keys()))
    q = random.choice(GRAMMAR_QUESTIONS[category])
    category_emojis = {
        "pronouns": "👤", "articles": "📰", "verbs": "🏃",
        "prepositions": "📍", "plurals": "👥", "nouns": "🏷️", "sentences": "📝"
    }
    category_labels = {
        "pronouns": "Pronouns", "articles": "Articles (a/an/the)", "verbs": "Verbs",
        "prepositions": "Prepositions", "plurals": "Plurals", "nouns": "Nouns", "sentences": "Sentences"
    }
    emoji = category_emojis.get(category, "📖")
    label = category_labels.get(category, category.title())
    options = list(q["options"])
    random.shuffle(options)
    return {
        "text": q["text"],
        "emoji": emoji,
        "answer": q["answer"],
        "options": options,
        "hint": q.get("hint", ""),
        "category_label": f"📖 {label}",
    }


def new_question(mode):
    if mode == "math":
        st.session_state.question = gen_math_question()
    elif mode == "english":
        st.session_state.question = gen_english_question()
    elif mode == "grammar":
        st.session_state.question = gen_grammar_question()
    else:  # mix
        st.session_state.question = random.choice([gen_math_question, gen_english_question, gen_grammar_question])()
    st.session_state.answered = False
    st.session_state.last_correct = None


# --- Sidebar ---
with st.sidebar:
    st.markdown("## 🎮 Dashboard")
    st.markdown(f'<div class="score-box">🏆 Score: {st.session_state.score} / {st.session_state.total}</div>',
                unsafe_allow_html=True)
    st.markdown("")
    if st.session_state.total > 0:
        pct = int(st.session_state.score / st.session_state.total * 100)
        st.progress(pct / 100)
        st.markdown(f"Accuracy: {pct}%")
    st.markdown(f'<div class="streak-text">🔥 Streak: {st.session_state.streak}  |  Best: {st.session_state.best_streak}</div>',
                unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🏠 Back to Menu", use_container_width=True):
        st.session_state.mode = "menu"
        st.session_state.question = None
        st.rerun()
    if st.button("🔄 Reset Score", use_container_width=True):
        for k, v in defaults.items():
            st.session_state[k] = v
        st.rerun()
    st.markdown("---")
    st.image("Dotnetabhishekai.png", width=80)

# --- Menu Screen ---
if st.session_state.mode == "menu":
    st.markdown('<div class="big-emoji">🌟🎮🌟</div>', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; color:#6c5ce7;'>Fun Learning Adventure!</h1>",
                unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:20px; color:#636e72;'>Pick a game to start learning!</p>",
                unsafe_allow_html=True)
    st.markdown("")

    st.markdown("<p style='text-align:center; font-size:17px; color:#636e72;'>🎯 Quiz Games</p>",
                unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="big-emoji">🔢</div>', unsafe_allow_html=True)
        if st.button("Math", use_container_width=True, key="btn_math"):
            st.session_state.mode = "math"
            new_question("math")
            st.rerun()
    with col2:
        st.markdown('<div class="big-emoji">📚</div>', unsafe_allow_html=True)
        if st.button("English", use_container_width=True, key="btn_eng"):
            st.session_state.mode = "english"
            new_question("english")
            st.rerun()
    with col3:
        st.markdown('<div class="big-emoji">📖</div>', unsafe_allow_html=True)
        if st.button("Grammar", use_container_width=True, key="btn_grammar"):
            st.session_state.mode = "grammar"
            new_question("grammar")
            st.rerun()
    with col4:
        st.markdown('<div class="big-emoji">🎲</div>', unsafe_allow_html=True)
        if st.button("Mix It Up!", use_container_width=True, key="btn_mix"):
            st.session_state.mode = "mix"
            new_question("mix")
            st.rerun()

    st.markdown("---")
    st.markdown("<p style='text-align:center; font-size:17px; color:#636e72;'>🧭 Learn & Explore</p>",
                unsafe_allow_html=True)
    le1, le2 = st.columns(2)
    with le1:
        st.markdown('<div class="big-emoji">🗺️</div>', unsafe_allow_html=True)
        if st.button("🧭 Concept Explorer", use_container_width=True, key="btn_explore"):
            st.session_state.mode = "explore"
            if "explore_topic" not in st.session_state:
                st.session_state.explore_topic = None
            st.rerun()
    with le2:
        st.markdown('<div class="big-emoji">🗣️</div>', unsafe_allow_html=True)
        if st.button("🗣️ Speaking Practice", use_container_width=True, key="btn_speak"):
            st.session_state.mode = "speaking"
            st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style='text-align:center; color:#636e72; font-size:16px;'>
        🔢 <b>Math</b> — Addition, subtraction, counting & comparing<br>
        📚 <b>English</b> — Animals, fruits, colors, spelling & rhymes<br>
        📖 <b>Grammar</b> — Nouns, pronouns, articles, verbs, prepositions, plurals & sentences<br>
        🎲 <b>Mix</b> — A surprise mix of all three!<br>
        🗺️ <b>Concept Explorer</b> — Visual picture cards to learn concepts easily<br>
        🗣️ <b>Speaking Practice</b> — Listen, repeat & practice English conversations
    </div>
    """, unsafe_allow_html=True)

# --- Speaking Practice Screen ---
elif st.session_state.mode == "speaking":
    SPEAKING_CATEGORIES = {
        "greetings": {
            "icon": "👋", "title": "Greetings & Introductions",
            "conversations": [
                {"scene": "🏫", "title": "Meeting a Friend at School",
                 "lines": [
                     ("👧", "Hello! My name is Sara. What is your name?"),
                     ("👦", "Hi Sara! My name is Aayansh. Nice to meet you!"),
                     ("👧", "Nice to meet you too, Aayansh! How are you today?"),
                     ("👦", "I am fine, thank you! How are you?"),
                     ("👧", "I am great! Let's go to class together."),
                 ]},
                {"scene": "🏠", "title": "Greeting Your Family",
                 "lines": [
                     ("👦", "Good morning, Mom!"),
                     ("👩", "Good morning, dear! Did you sleep well?"),
                     ("👦", "Yes, I did! What is for breakfast?"),
                     ("👩", "We have bread and milk today."),
                     ("👦", "Yummy! Thank you, Mom!"),
                 ]},
                {"scene": "🌅", "title": "Saying Goodbye",
                 "lines": [
                     ("👧", "I have to go home now. Goodbye!"),
                     ("👦", "Goodbye! See you tomorrow!"),
                     ("👧", "Yes! See you tomorrow. Have a good evening!"),
                     ("👦", "You too! Take care!"),
                 ]},
            ]
        },
        "classroom": {
            "icon": "🏫", "title": "In the Classroom",
            "conversations": [
                {"scene": "📖", "title": "Asking the Teacher",
                 "lines": [
                     ("👦", "Excuse me, teacher. May I ask a question?"),
                     ("👩‍🏫", "Of course! What is your question?"),
                     ("👦", "How do you spell the word 'beautiful'?"),
                     ("👩‍🏫", "B-E-A-U-T-I-F-U-L. Beautiful!"),
                     ("👦", "Thank you, teacher!"),
                 ]},
                {"scene": "✏️", "title": "Borrowing a Pencil",
                 "lines": [
                     ("👧", "Can I borrow your pencil, please?"),
                     ("👦", "Sure! Here you go."),
                     ("👧", "Thank you so much!"),
                     ("👦", "You are welcome!"),
                 ]},
                {"scene": "🖐️", "title": "Asking Permission",
                 "lines": [
                     ("👦", "May I go to the bathroom, please?"),
                     ("👩‍🏫", "Yes, you may. Please come back quickly."),
                     ("👦", "Thank you, teacher. I will be quick!"),
                 ]},
            ]
        },
        "shopping": {
            "icon": "🛒", "title": "At the Shop",
            "conversations": [
                {"scene": "🍎", "title": "Buying Fruits",
                 "lines": [
                     ("👦", "Hello! I would like to buy some apples, please."),
                     ("🧑‍💼", "How many apples do you want?"),
                     ("👦", "I want five apples, please."),
                     ("🧑‍💼", "Here are five apples. That will be ten rupees."),
                     ("👦", "Here is the money. Thank you!"),
                     ("🧑‍💼", "Thank you! Come again!"),
                 ]},
                {"scene": "🍦", "title": "Buying Ice Cream",
                 "lines": [
                     ("👧", "Can I have one ice cream, please?"),
                     ("🧑‍💼", "Which flavor do you want? Chocolate or vanilla?"),
                     ("👧", "Chocolate, please!"),
                     ("🧑‍💼", "Here is your chocolate ice cream. Enjoy!"),
                     ("👧", "Thank you! It looks yummy!"),
                 ]},
            ]
        },
        "daily_life": {
            "icon": "🌞", "title": "Daily Life",
            "conversations": [
                {"scene": "🍽️", "title": "At the Dinner Table",
                 "lines": [
                     ("👩", "Dinner is ready! Please wash your hands."),
                     ("👦", "Okay, Mom! I am washing my hands now."),
                     ("👩", "What would you like to eat?"),
                     ("👦", "I would like rice and vegetables, please."),
                     ("👩", "Good choice! Here you go."),
                     ("👦", "Thank you! The food is delicious!"),
                 ]},
                {"scene": "🛏️", "title": "Bedtime",
                 "lines": [
                     ("👩", "It is time for bed. Did you brush your teeth?"),
                     ("👧", "Yes, I did! Can you read me a story?"),
                     ("👩", "Of course! Which story do you want?"),
                     ("👧", "The one about the little rabbit, please!"),
                     ("👩", "Okay! Once upon a time, there was a little rabbit..."),
                     ("👧", "I love this story! Good night, Mom."),
                     ("👩", "Good night, sweetheart. Sweet dreams!"),
                 ]},
                {"scene": "🌧️", "title": "Talking About Weather",
                 "lines": [
                     ("👦", "Look! It is raining outside!"),
                     ("👧", "Yes! I can hear the rain. Do you like rain?"),
                     ("👦", "I love rain! But I forgot my umbrella."),
                     ("👧", "You can share my umbrella!"),
                     ("👦", "Thank you! You are a good friend."),
                 ]},
            ]
        },
        "playground": {
            "icon": "🎪", "title": "At the Playground",
            "conversations": [
                {"scene": "⚽", "title": "Playing Together",
                 "lines": [
                     ("👦", "Do you want to play with me?"),
                     ("👧", "Yes! What game should we play?"),
                     ("👦", "Let's play catch! I have a ball."),
                     ("👧", "That sounds fun! Throw the ball to me!"),
                     ("👦", "Here it comes! Catch it!"),
                     ("👧", "I caught it! My turn to throw!"),
                 ]},
                {"scene": "🎢", "title": "Taking Turns",
                 "lines": [
                     ("👧", "I want to go on the slide!"),
                     ("👦", "Me too! But there is only one slide."),
                     ("👧", "Let's take turns. You go first!"),
                     ("👦", "Thank you! That is very kind of you."),
                     ("👧", "You are welcome! Friends share and take turns."),
                 ]},
            ]
        },
        "feelings": {
            "icon": "😊", "title": "Feelings & Emotions",
            "conversations": [
                {"scene": "😢", "title": "When Someone is Sad",
                 "lines": [
                     ("👦", "Why are you sad? What happened?"),
                     ("👧", "I lost my favorite toy. I am very sad."),
                     ("👦", "Oh no! Don't worry. I will help you find it."),
                     ("👧", "Really? Thank you! You are so kind."),
                     ("👦", "That's what friends are for! Let's look together."),
                     ("👧", "I found it! I am so happy now! Thank you!"),
                 ]},
                {"scene": "🎉", "title": "Celebrating",
                 "lines": [
                     ("👧", "Guess what? Today is my birthday!"),
                     ("👦", "Happy birthday! How old are you now?"),
                     ("👧", "I am seven years old today!"),
                     ("👦", "Wow! Here is a card I made for you."),
                     ("👧", "Oh, it is beautiful! Thank you so much!"),
                     ("👦", "You are welcome! I hope you have a wonderful day!"),
                 ]},
            ]
        },
    }

    # Init speaking state
    if "speak_cat" not in st.session_state:
        st.session_state.speak_cat = None
    if "speak_conv" not in st.session_state:
        st.session_state.speak_conv = None

    st.markdown("<h2 style='text-align:center; color:#6c5ce7;'>🗣️ English Speaking Practice</h2>",
                unsafe_allow_html=True)

    # Category selection
    if st.session_state.speak_cat is None:
        st.markdown("<p style='text-align:center; font-size:18px; color:#636e72;'>Pick a topic to practice speaking!</p>",
                    unsafe_allow_html=True)
        cat_keys = list(SPEAKING_CATEGORIES.keys())
        rows = [cat_keys[i:i+3] for i in range(0, len(cat_keys), 3)]
        for row in rows:
            cols = st.columns(3)
            for idx, key in enumerate(row):
                cat = SPEAKING_CATEGORIES[key]
                with cols[idx]:
                    st.markdown(f"""<div class="concept-card">
                        <div style="font-size:50px;">{cat['icon']}</div>
                        <div class="concept-title" style="font-size:18px;">{cat['title']}</div>
                        <div class="concept-desc">{len(cat['conversations'])} conversations</div>
                    </div>""", unsafe_allow_html=True)
                    if st.button(f"Practice", use_container_width=True, key=f"scat_{key}"):
                        st.session_state.speak_cat = key
                        st.rerun()

    # Conversation list
    elif st.session_state.speak_conv is None:
        cat = SPEAKING_CATEGORIES[st.session_state.speak_cat]
        st.markdown(f"<p style='text-align:center; font-size:20px;'>{cat['icon']} {cat['title']}</p>",
                    unsafe_allow_html=True)
        bc1, bc2, bc3 = st.columns([1, 2, 1])
        with bc2:
            if st.button("⬅️ Back to Topics", use_container_width=True, key="speak_back_cat"):
                st.session_state.speak_cat = None
                st.rerun()
        st.markdown("---")
        for i, conv in enumerate(cat["conversations"]):
            st.markdown(f"""<div class="concept-card">
                <div style="font-size:40px;">{conv['scene']}</div>
                <div class="concept-title" style="font-size:18px;">{conv['title']}</div>
                <div class="concept-desc">{len(conv['lines'])} lines to practice</div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"▶️ Practice: {conv['title']}", use_container_width=True, key=f"sconv_{i}"):
                st.session_state.speak_conv = i
                st.rerun()

    # Conversation practice view
    else:
        cat = SPEAKING_CATEGORIES[st.session_state.speak_cat]
        conv = cat["conversations"][st.session_state.speak_conv]

        st.markdown(f"<p style='text-align:center; font-size:22px;'>{conv['scene']} {conv['title']}</p>",
                    unsafe_allow_html=True)

        bc1, bc2, bc3 = st.columns([1, 2, 1])
        with bc2:
            if st.button("⬅️ Back to Conversations", use_container_width=True, key="speak_back_conv"):
                st.session_state.speak_conv = None
                st.rerun()

        st.markdown("---")
        st.markdown("""<div style='background:#e8f5e9; padding:12px; border-radius:12px; text-align:center;
                    font-size:16px; margin-bottom:15px;'>
            🎧 Click <b>🔊 Listen</b> to hear each line, then practice saying it out loud!
        </div>""", unsafe_allow_html=True)

        for i, (speaker, line) in enumerate(conv["lines"]):
            speech_line = line.replace("'", "\\'").replace('"', '\\"')
            bg = "#f0f0ff" if i % 2 == 0 else "#fff0f0"
            components.html(f"""
            <div style='background:{bg}; padding:16px; border-radius:14px; margin:8px 0;
                        display:flex; align-items:center; gap:12px; font-family:sans-serif;'>
                <div style='font-size:36px;'>{speaker}</div>
                <div style='flex:1;'>
                    <div style='font-size:18px; color:#2d3436;'>{line}</div>
                    <span onclick="if('speechSynthesis' in window){{ window.speechSynthesis.cancel(); var m=new SpeechSynthesisUtterance('{speech_line}'); m.rate=0.8; m.pitch=1.1; m.lang='en-US'; window.speechSynthesis.speak(m); }}"
                          style="cursor:pointer;font-size:14px;color:#6c5ce7;font-weight:bold;user-select:none;">
                        🔊 Listen
                    </span>
                </div>
            </div>
            """, height=85)

        # Read All button
        st.markdown("---")
        all_lines = '. '.join([line.replace("'", "\\'").replace('"', '\\"') for _, line in conv["lines"]])
        ra1, ra2, ra3 = st.columns([1, 2, 1])
        with ra2:
            components.html(f"""
            <div style='text-align:center; font-family:sans-serif;'>
                <span onclick="if('speechSynthesis' in window){{ window.speechSynthesis.cancel(); var m=new SpeechSynthesisUtterance('{all_lines}'); m.rate=0.75; m.pitch=1.1; m.lang='en-US'; window.speechSynthesis.speak(m); }}"
                      style="cursor:pointer;background:#6c5ce7;color:white;padding:12px 28px;
                    border-radius:14px;font-size:18px;font-weight:bold;display:inline-block;user-select:none;">
                    🔊 Read Entire Conversation
                </span>
            </div>
            """, height=60)

        # Navigation
        st.markdown("")
        n1, n2, n3 = st.columns(3)
        with n1:
            if st.session_state.speak_conv > 0:
                if st.button("⬅️ Previous", use_container_width=True, key="speak_prev"):
                    st.session_state.speak_conv -= 1
                    st.rerun()
        with n3:
            if st.session_state.speak_conv < len(cat["conversations"]) - 1:
                if st.button("Next ➡️", use_container_width=True, key="speak_next"):
                    st.session_state.speak_conv += 1
                    st.rerun()

# --- Concept Explorer Screen ---
elif st.session_state.mode == "explore":
    if "explore_topic" not in st.session_state:
        st.session_state.explore_topic = None

    # Topic selection view
    if st.session_state.explore_topic is None:
        st.markdown("<h2 style='text-align:center; color:#6c5ce7;'>🗺️ Concept Explorer</h2>",
                    unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; font-size:20px; color:#636e72;'>Pick a topic to explore with pictures!</p>",
                    unsafe_allow_html=True)
        st.markdown("")

        # Display topic buttons in a grid
        topic_keys = list(CONCEPT_TOPICS.keys())
        rows = [topic_keys[i:i+3] for i in range(0, len(topic_keys), 3)]
        for row in rows:
            cols = st.columns(3)
            for idx, key in enumerate(row):
                topic = CONCEPT_TOPICS[key]
                with cols[idx]:
                    st.markdown(f'<div class="concept-card"><div style="font-size:60px;">{topic["icon"]}</div>'
                                f'<div class="concept-title">{topic["title"]}</div>'
                                f'<div class="concept-desc">{len(topic["cards"])} picture cards</div></div>',
                                unsafe_allow_html=True)
                    if st.button(f"Explore {topic['title']}", use_container_width=True, key=f"topic_{key}"):
                        st.session_state.explore_topic = key
                        st.rerun()

    # Card view for selected topic
    else:
        topic_key = st.session_state.explore_topic
        topic = CONCEPT_TOPICS[topic_key]

        st.markdown(f"<h2 style='text-align:center; color:#6c5ce7;'>{topic['icon']} {topic['title']}</h2>",
                    unsafe_allow_html=True)

        # Back to topics button
        bc1, bc2, bc3 = st.columns([1, 2, 1])
        with bc2:
            if st.button("⬅️ Back to All Topics", use_container_width=True, key="back_topics"):
                st.session_state.explore_topic = None
                st.rerun()

        st.markdown("---")

        # Display each card
        for i, card in enumerate(topic["cards"]):
            st.markdown(f"""
            <div class="concept-card">
                <div class="concept-scene">{card['scene']}</div>
                <div class="concept-title">{card['name']}</div>
                <div style="font-size:36px; padding:10px;">{card['visual']}</div>
                <div class="concept-desc">{card['desc']}</div>
            </div>
            """, unsafe_allow_html=True)

            # Examples as expandable
            with st.expander(f"📝 See examples for {card['name']}", expanded=False):
                for ex in card["examples"]:
                    st.markdown(f"""<div class="concept-example">👉 {ex}</div>""", unsafe_allow_html=True)

            st.markdown("")

        # Navigation at bottom
        st.markdown("---")
        nb1, nb2, nb3 = st.columns([1, 2, 1])
        with nb2:
            if st.button("⬅️ Back to All Topics", use_container_width=True, key="back_topics_bottom"):
                st.session_state.explore_topic = None
                st.rerun()

# --- Game Screen ---
else:
    q = st.session_state.question
    if q is None:
        new_question(st.session_state.mode)
        st.rerun()

    mode_labels = {"math": "🔢 Math Challenge", "english": "📚 English Challenge",
                   "grammar": "📖 Grammar Challenge", "mix": "🎲 Mixed Challenge"}
    st.markdown(f"<h2 style='text-align:center; color:#6c5ce7;'>{mode_labels[st.session_state.mode]}</h2>",
                unsafe_allow_html=True)

    # Show grammar category label if present
    if q.get("category_label"):
        st.markdown(f"<p style='text-align:center; font-size:18px; color:#636e72;'>{q['category_label']}</p>",
                    unsafe_allow_html=True)

    st.markdown(f'<div class="big-emoji">{q["emoji"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="question-box">{q["text"]}</div>', unsafe_allow_html=True)

    # --- Answer Buttons ---
    if not st.session_state.answered:
        cols = st.columns(len(q["options"]))
        for i, opt in enumerate(q["options"]):
            with cols[i]:
                if st.button(opt, key=f"opt_{i}", use_container_width=True):
                    st.session_state.answered = True
                    st.session_state.total += 1
                    if opt == q["answer"]:
                        st.session_state.score += 1
                        st.session_state.streak += 1
                        st.session_state.best_streak = max(st.session_state.best_streak, st.session_state.streak)
                        st.session_state.last_correct = True
                    else:
                        st.session_state.streak = 0
                        st.session_state.last_correct = False
                    st.rerun()

    # --- Feedback ---
    if st.session_state.answered:
        if st.session_state.last_correct:
            play_sound(make_correct_sound())
            st.markdown(f'<div class="correct">{random.choice(ENCOURAGEMENTS)}</div>', unsafe_allow_html=True)
            st.balloons()
        else:
            play_sound(make_wrong_sound())
            st.markdown(f'<div class="wrong">{random.choice(TRY_AGAIN)}</div>', unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; font-size:22px;'>The correct answer was: <b>{q['answer']}</b></p>",
                        unsafe_allow_html=True)

        # Show grammar hint if available — click to read aloud
        if q.get("hint"):
            _hint_text = q['hint']
            _speech_text = ''.join(c for c in _hint_text if ord(c) < 0x1F600 or ord(c) > 0x1FAFF)
            _speech_text = _speech_text.replace("'", "\\'").replace('"', '\\"').replace('\n', ' ')

            components.html(f"""
            <div style='background:#fff9c4; padding:15px; border-radius:15px; margin:15px 0;
                        border-left:5px solid #f9a825; text-align:center; font-size:18px; font-family:sans-serif;'>
                💡 <b>Did you know?</b> {_hint_text}
                <br><span onclick="if('speechSynthesis' in window){{ window.speechSynthesis.cancel(); var m=new SpeechSynthesisUtterance('{_speech_text}'); m.rate=0.85; m.pitch=1.1; m.lang='en-US'; window.speechSynthesis.speak(m); }}"
                      style="cursor:pointer;font-size:15px;color:#6c5ce7;font-weight:bold;user-select:none;">
                    🔊 Listen to the hint!
                </span>
            </div>
            """, height=120)

        st.markdown("")
        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            if st.button("▶️ Next Question", use_container_width=True, key="next"):
                new_question(st.session_state.mode)
                st.rerun()

# ── Footer ──
import os as _os
_logo_path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "Dotnetabhishekai.png")
st.markdown("---")
_fc1, _fc2, _fc3 = st.columns([1, 1, 1])
with _fc2:
    if _os.path.exists(_logo_path):
        st.image(_logo_path, width=120)
    st.markdown("""
    <div style="text-align:center; color:#636e72; font-size:14px;">
        Made with ❤️ by <b>dotnetabhishekai</b> for my lovely sons ❤️ Krishna & Kanha!!
    </div>
    """, unsafe_allow_html=True)
