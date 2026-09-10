import streamlit as st
import json
import os
import random
import streamlit.components.v1 as components

st.set_page_config(page_title="German Vocabulary Trainer", page_icon="🇩🇪", layout="centered")

DATA_FILE = "vocab_data.json"
PROGRESS_FILE = "progress.json"

# ---------- Load data ----------
@st.cache_data
def load_base_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

base_data = load_base_data()

if "progress" not in st.session_state:
    st.session_state.progress = load_progress()

# merge saved progress (status + my_sentence) into base data
data = []
for item in base_data:
    item = dict(item)
    saved = st.session_state.progress.get(str(item["id"]), {})
    item["status"] = saved.get("status", item["status"])
    item["my_sentence"] = saved.get("my_sentence", item["my_sentence"])
    data.append(item)

GENDER_COLORS = {"der": "#3B82F6", "die": "#EF4444", "das": "#22C55E"}

# ---------- Sidebar ----------
st.sidebar.title("🇩🇪 Vocabulary Trainer")
categories = ["All categories"] + sorted(set(d["category"] for d in data))
selected_cat = st.sidebar.selectbox("Category", categories)

status_filter = st.sidebar.multiselect(
    "Status filter", ["To Learn", "Learning", "Learned"],
    default=["To Learn", "Learning", "Learned"]
)

search = st.sidebar.text_input("Search a word")

filtered = [
    d for d in data
    if (selected_cat == "All categories" or d["category"] == selected_cat)
    and d["status"] in status_filter
    and (search.lower() in d["word"].lower() or search.lower() in d["english"].lower() if search else True)
]

if not filtered:
    st.sidebar.warning("No words match your filters.")
    filtered = data

total = len(data)
learned = sum(1 for d in data if d["status"] == "Learned")
learning = sum(1 for d in data if d["status"] == "Learning")
st.sidebar.progress(learned / total if total else 0)
st.sidebar.caption(f"✅ {learned} learned · 🔵 {learning} learning · out of {total} words")

if st.sidebar.button("🔀 Shuffle deck"):
    random.shuffle(filtered)
    st.session_state.order = [d["id"] for d in filtered]

# ---------- Card index state ----------
if "idx" not in st.session_state:
    st.session_state.idx = 0
if st.session_state.idx >= len(filtered):
    st.session_state.idx = 0

card = filtered[st.session_state.idx]

# ---------- Header ----------
st.title("German Vocabulary Flashcards")
st.caption(f"{card['category']}  ·  Card {st.session_state.idx + 1} of {len(filtered)}")

# ---------- Flashcard ----------
gender = card["article"]
color = GENDER_COLORS.get(gender, "#6B7280")
word_display = f"{gender} {card['word'].split(' ',1)[-1]}" if gender and card['word'].startswith(gender) else card["word"]

st.markdown(
    f"""
    <div style="border-radius:16px; padding:28px; background:{color}15; border:2px solid {color};">
        <div style="font-size:14px; font-weight:600; color:{color}; text-transform:uppercase;">
            {card['type'] if card['type'] else 'noun'} {('· ' + gender) if gender else ''}
        </div>
        <div style="font-size:34px; font-weight:800; margin-top:6px; color:#111827;">
            {word_display}
        </div>
        <div style="font-size:16px; color:#4B5563; margin-top:4px;">
            {('Plural: ' + card['plural']) if card['plural'] else ''}
        </div>
        <div style="font-size:18px; margin-top:14px; color:#111827;">
            📖 {card['sentence']}
        </div>
        <div style="font-size:16px; margin-top:8px; color:#374151;">
            🇬🇧 {card['english']}
        </div>
        <div style="font-size:16px; margin-top:4px; color:#374151;">
            🔤 উচ্চারণ: {card['bangla']}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Text to speech ----------
tts_text = card["word"].replace("sich ", "")
components.html(
    f"""
    <button onclick="speak()" style="
        margin-top:14px; padding:10px 18px; border-radius:10px; border:none;
        background:#111827; color:white; font-size:15px; cursor:pointer;">
        🔊 Listen (German)
    </button>
    <script>
    function speak() {{
        var msg = new SpeechSynthesisUtterance({json.dumps(tts_text)});
        msg.lang = "de-DE";
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(msg);
    }}
    </script>
    """,
    height=60,
)

# ---------- Your own sentence ----------
st.markdown("#### ✍️ Write your own sentence")
my_sentence = st.text_area(
    "Practice using this word yourself:",
    value=card["my_sentence"],
    key=f"sentence_{card['id']}",
    placeholder="z.B. Ich benutze dieses Wort in meinem eigenen Satz...",
    label_visibility="collapsed",
)

col_save, _ = st.columns([1, 3])
with col_save:
    if st.button("💾 Save sentence"):
        st.session_state.progress.setdefault(str(card["id"]), {})
        st.session_state.progress[str(card["id"])]["my_sentence"] = my_sentence
        save_progress(st.session_state.progress)
        st.success("Saved!")

# ---------- Status buttons ----------
st.markdown("#### Mark this word")
c1, c2, c3 = st.columns(3)

def set_status(new_status):
    st.session_state.progress.setdefault(str(card["id"]), {})
    st.session_state.progress[str(card["id"])]["status"] = new_status
    save_progress(st.session_state.progress)

with c1:
    if st.button("⚪ To Learn", use_container_width=True):
        set_status("To Learn")
        st.rerun()
with c2:
    if st.button("🔵 Learning", use_container_width=True):
        set_status("Learning")
        st.rerun()
with c3:
    if st.button("✅ Learned", use_container_width=True):
        set_status("Learned")
        st.session_state.idx = (st.session_state.idx + 1) % len(filtered)
        st.rerun()

st.markdown("---")

# ---------- Navigation ----------
n1, n2, n3 = st.columns(3)
with n1:
    if st.button("⬅️ Prev", use_container_width=True):
        st.session_state.idx = (st.session_state.idx - 1) % len(filtered)
        st.rerun()
with n2:
    if st.button("🔀 Random", use_container_width=True):
        st.session_state.idx = random.randrange(len(filtered))
        st.rerun()
with n3:
    if st.button("Next ➡️", use_container_width=True):
        st.session_state.idx = (st.session_state.idx + 1) % len(filtered)
        st.rerun()

st.caption("Legend: 🔵 der = blue · 🔴 die = red · 🟢 das = green")
