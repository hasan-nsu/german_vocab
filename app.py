import streamlit as st
import json
import os
import random
import streamlit.components.v1 as components

st.set_page_config(page_title="German Vocabulary Trainer", page_icon="🇩🇪", layout="centered")

DATA_FILE = "vocab_data.json"
PROGRESS_FILE = "progress.json"

st.markdown("""
<style>
.block-container {padding-top: 2rem; padding-bottom: 2rem; max-width: 760px;}
div.stButton > button {border-radius: 8px; padding: 0.35rem 0.8rem; font-size: 14px;}
</style>
""", unsafe_allow_html=True)

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

data = []
for item in base_data:
    item = dict(item)
    saved = st.session_state.progress.get(str(item["id"]), {})
    item["status"] = saved.get("status", item["status"])
    item["my_sentence"] = saved.get("my_sentence", item["my_sentence"])
    data.append(item)

GENDER_COLORS = {"der": "#2563EB", "die": "#DC2626", "das": "#16A34A"}
STATUS_DOT = {"To Learn": "⚪", "Learning": "🔵", "Learned": "🟢"}

# ---------- Sidebar ----------
st.sidebar.markdown("### 🇩🇪 Vocabulary Trainer")
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
    and (not search or search.lower() in d["word"].lower() or search.lower() in d["english"].lower())
]
if not filtered:
    st.sidebar.warning("No words match your filters.")
    filtered = data

total = len(data)
learned = sum(1 for d in data if d["status"] == "Learned")
learning = sum(1 for d in data if d["status"] == "Learning")
st.sidebar.progress(learned / total if total else 0)
st.sidebar.caption(f"🟢 {learned} learned · 🔵 {learning} learning · {total} total")

if st.sidebar.button("🔀 Shuffle deck", use_container_width=True):
    random.shuffle(filtered)
    st.session_state.idx = 0

if "idx" not in st.session_state:
    st.session_state.idx = 0
if st.session_state.idx >= len(filtered):
    st.session_state.idx = 0

card = filtered[st.session_state.idx]
gender = card.get("article", "")
color = GENDER_COLORS.get(gender, "#6B7280")

# Backward-compatible defaults in case an older vocab_data.json is loaded
card.setdefault("icon", "📘")
card.setdefault("plural", "")
card.setdefault("my_sentence", "")
card.setdefault("status", "To Learn")
card.setdefault("type", "")
card.setdefault("bangla", "")
card.setdefault("english", "")
if "sentence1" not in card:
    card["sentence1"] = card.get("sentence", "")
if "sentence2" not in card:
    card["sentence2"] = ""

# ---------- Top bar: title + progress ----------
st.markdown(
    f"<div style='display:flex; justify-content:space-between; align-items:baseline;'>"
    f"<span style='font-size:22px; font-weight:700;'>German Vocabulary</span>"
    f"<span style='font-size:13px; color:#6B7280;'>{card['category']} · {st.session_state.idx + 1}/{len(filtered)}</span>"
    f"</div>", unsafe_allow_html=True
)
st.write("")

# ---------- Compact side-by-side card ----------
left, right = st.columns([1, 2.2])

with left:
    st.markdown(
        f"""
        <div style="background:{color}12; border:1.5px solid {color}; border-radius:12px;
                    height:150px; display:flex; flex-direction:column; align-items:center;
                    justify-content:center; text-align:center;">
            <div style="font-size:44px;">{card['icon']}</div>
            <div style="font-size:11px; font-weight:700; color:{color}; margin-top:4px; text-transform:uppercase;">
                {card['type'] or 'noun'}{(' · ' + gender) if gender else ''}
            </div>
            <div style="font-size:11px; color:#9CA3AF;">{STATUS_DOT[card['status']]} {card['status']}</div>
        </div>
        """, unsafe_allow_html=True
    )

with right:
    plural_line = f"<span style='color:#6B7280; font-size:13px;'>Plural: {card['plural']}</span><br>" if card['plural'] else ""
    st.markdown(
        f"""
        <div style="border:1.5px solid #E5E7EB; border-radius:12px; padding:12px 16px; height:150px;
                    display:flex; flex-direction:column; justify-content:center;">
            <div style="font-size:26px; font-weight:800; color:#111827;">{card['word']}</div>
            {plural_line}
            <div style="font-size:15px; color:#374151; margin-top:4px;">🇬🇧 {card['english']}</div>
            <div style="font-size:14px; color:#374151;">🔤 {card['bangla']}</div>
        </div>
        """, unsafe_allow_html=True
    )

# ---------- Listen button ----------
tts_text = card["word"].replace("sich ", "")
components.html(
    f"""
    <button onclick="speak()" style="margin-top:10px; padding:8px 16px; border-radius:8px; border:none;
        background:#111827; color:white; font-size:14px; cursor:pointer;">🔊 Listen</button>
    <script>
    function speak() {{
        var msg = new SpeechSynthesisUtterance({json.dumps(tts_text)});
        msg.lang = "de-DE";
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(msg);
    }}
    </script>
    """, height=48
)

# ---------- Two example sentences side by side ----------
st.markdown("<div style='margin-top:6px; font-size:13px; font-weight:600; color:#6B7280;'>EXAMPLE SENTENCES</div>", unsafe_allow_html=True)
s1, s2 = st.columns(2)
for col, sent in zip((s1, s2), (card["sentence1"], card["sentence2"])):
    with col:
        st.markdown(
            f"""<div style="background:#F9FAFB; border:1px solid #E5E7EB; border-radius:10px;
                    padding:10px 12px; font-size:14px; color:#111827; min-height:70px;">
                {sent}</div>""", unsafe_allow_html=True
        )

st.write("")

# ---------- Your sentence + status in two columns ----------
wc1, wc2 = st.columns([1.3, 1])
with wc1:
    st.markdown("<div style='font-size:13px; font-weight:600; color:#6B7280;'>✍️ YOUR SENTENCE</div>", unsafe_allow_html=True)
    my_sentence = st.text_area(
        "your sentence", value=card["my_sentence"], key=f"sentence_{card['id']}",
        placeholder="Write your own sentence...", label_visibility="collapsed", height=80
    )
    if st.button("💾 Save", key="save_btn"):
        st.session_state.progress.setdefault(str(card["id"]), {})
        st.session_state.progress[str(card["id"])]["my_sentence"] = my_sentence
        save_progress(st.session_state.progress)
        st.toast("Saved!")

with wc2:
    st.markdown("<div style='font-size:13px; font-weight:600; color:#6B7280;'>MARK WORD</div>", unsafe_allow_html=True)

    def set_status(new_status, advance=False):
        st.session_state.progress.setdefault(str(card["id"]), {})
        st.session_state.progress[str(card["id"])]["status"] = new_status
        save_progress(st.session_state.progress)
        if advance:
            st.session_state.idx = (st.session_state.idx + 1) % len(filtered)

    if st.button("⚪ To Learn", use_container_width=True, key="tl"):
        set_status("To Learn"); st.rerun()
    if st.button("🔵 Learning", use_container_width=True, key="lg"):
        set_status("Learning"); st.rerun()
    if st.button("🟢 Learned", use_container_width=True, key="ld"):
        set_status("Learned", advance=True); st.rerun()

st.markdown("<hr style='margin:14px 0;'>", unsafe_allow_html=True)

# ---------- Navigation ----------
n1, n2, n3 = st.columns(3)
with n1:
    if st.button("⬅️ Prev", use_container_width=True):
        st.session_state.idx = (st.session_state.idx - 1) % len(filtered); st.rerun()
with n2:
    if st.button("🔀 Random", use_container_width=True):
        st.session_state.idx = random.randrange(len(filtered)); st.rerun()
with n3:
    if st.button("Next ➡️", use_container_width=True):
        st.session_state.idx = (st.session_state.idx + 1) % len(filtered); st.rerun()

st.caption("🔵 der · 🔴 die · 🟢 das")
