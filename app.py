import streamlit as st
import json
import os
import random
import hashlib
import streamlit.components.v1 as components

st.set_page_config(page_title="German Vocabulary Trainer", page_icon="🇩🇪", layout="centered")

DATA_FILE = "vocab_data.json"
PROGRESS_FILE = "progress.json"
CUSTOM_FILE = "custom_words.json"

# ---------------------------------------------------------------------------
# Global styling — colourful theme
# ---------------------------------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #F5F3FF 0%, #FFFFFF 250px);
}
.block-container {padding-top: 1.2rem; padding-bottom: 2rem; max-width: 780px;}
div.stButton > button {
    border-radius: 10px; padding: 0.45rem 0.9rem; font-size: 14px;
    border: 1.5px solid #E5E7EB; font-weight: 600; transition: all .15s ease;
}
div.stButton > button:hover {
    border-color: #7C3AED; color: #7C3AED; transform: translateY(-1px);
}
div[data-testid="stExpander"] {
    border-radius: 12px; border: 1.5px solid #EDE9FE;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_base_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_json_file(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {} if "progress" in path else []


def save_json_file(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


base_data = load_base_data()
if "progress" not in st.session_state:
    st.session_state.progress = load_json_file(PROGRESS_FILE)
if "custom_words" not in st.session_state:
    st.session_state.custom_words = load_json_file(CUSTOM_FILE)

all_base = base_data + st.session_state.custom_words

data = []
for item in all_base:
    item = dict(item)
    saved = st.session_state.progress.get(str(item["id"]), {})
    item["status"] = saved.get("status", item.get("status", "To Learn"))
    item["my_sentence"] = saved.get("my_sentence", item.get("my_sentence", ""))
    data.append(item)

GENDER_COLORS = {"der": "#2563EB", "die": "#DB2777", "das": "#059669", "": "#7C3AED"}
STATUS_DOT = {"To Learn": "⚪", "Learning": "🔵", "Learned": "🟢"}

# Consistent, pleasant colour per category (hash-based so custom categories
# also get a stable colour without needing to hardcode every name)
CATEGORY_PALETTE = ["#F97316", "#0EA5E9", "#8B5CF6", "#EC4899", "#10B981", "#F59E0B", "#6366F1", "#EF4444"]


def category_color(cat):
    h = int(hashlib.md5(cat.encode()).hexdigest(), 16)
    return CATEGORY_PALETTE[h % len(CATEGORY_PALETTE)]


def speak_button(text, key, lang="de-DE", label="🔊"):
    """Render a small TTS button for arbitrary text using the Web Speech API."""
    safe_text = json.dumps(text)
    components.html(
        f"""
        <button onclick="speak_{key}()" style="padding:6px 12px; border-radius:20px; border:none;
            background:#111827; color:white; font-size:13px; cursor:pointer;">{label}</button>
        <script>
        function speak_{key}() {{
            var msg = new SpeechSynthesisUtterance({safe_text});
            msg.lang = "{lang}";
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(msg);
        }}
        </script>
        """, height=40
    )


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
st.sidebar.markdown(
    "<div style='font-size:20px; font-weight:800; "
    "background: linear-gradient(90deg,#7C3AED,#EC4899); -webkit-background-clip: text; "
    "-webkit-text-fill-color: transparent;'>🇩🇪 Vocabulary Trainer</div>",
    unsafe_allow_html=True
)
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

# ---------------------------------------------------------------------------
# Tabs: flashcards vs. add-your-own-word
# ---------------------------------------------------------------------------
tab_learn, tab_add = st.tabs(["📚 Flashcards", "➕ Add your own word"])

with tab_add:
    st.markdown("### ➕ Add a new word")
    st.caption("Your word gets added to the deck immediately, saved to `custom_words.json`, and shows up under the **My Words** category.")
    with st.form("add_word_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            new_word_core = st.text_input("Word (without article)*", placeholder="e.g. Buch")
            new_article = st.selectbox("Article", ["das", "der", "die", "(none — verb/adj/adv)"])
            new_type = st.selectbox("Type", ["noun", "verb", "adjective", "adverb", "other"])
            new_plural = st.text_input("Plural (optional)", placeholder="e.g. die Bücher")
            new_icon = st.text_input("Icon / emoji (optional)", value="📘", max_chars=4)
        with c2:
            new_english = st.text_input("English meaning*", placeholder="e.g. book")
            new_bangla = st.text_input("Bangla meaning*", placeholder="e.g. বই")
            new_category = st.text_input("Category", value="My Words")
        st.markdown("**Example sentence 1** (optional but recommended)")
        s1_de = st.text_input("German", key="s1de", placeholder="Ich lese ein Buch.")
        s1c1, s1c2 = st.columns(2)
        s1_en = s1c1.text_input("English translation", key="s1en")
        s1_bn = s1c2.text_input("Bangla translation", key="s1bn")
        st.markdown("**Example sentence 2** (optional)")
        s2_de = st.text_input("German", key="s2de", placeholder="Das Buch ist sehr interessant.")
        s2c1, s2c2 = st.columns(2)
        s2_en = s2c1.text_input("English translation", key="s2en")
        s2_bn = s2c2.text_input("Bangla translation", key="s2bn")

        submitted = st.form_submit_button("💾 Save word", use_container_width=True)
        if submitted:
            if not new_word_core.strip() or not new_english.strip() or not new_bangla.strip():
                st.error("Please fill in the word, English meaning, and Bangla meaning at minimum.")
            else:
                article = "" if new_article.startswith("(none") else new_article
                full_word = f"{article} {new_word_core.strip()}".strip()
                existing_ids = [x["id"] for x in (base_data + st.session_state.custom_words)]
                new_id = max(existing_ids) + 1 if existing_ids else 1
                new_entry = {
                    "id": new_id,
                    "category": new_category.strip() or "My Words",
                    "word": full_word,
                    "article": article,
                    "type": new_type,
                    "plural": new_plural.strip(),
                    "icon": new_icon.strip() or "📘",
                    "sentence1": s1_de.strip(),
                    "sentence2": s2_de.strip(),
                    "sentence1_en": s1_en.strip(),
                    "sentence1_bn": s1_bn.strip(),
                    "sentence2_en": s2_en.strip(),
                    "sentence2_bn": s2_bn.strip(),
                    "english": new_english.strip(),
                    "bangla": new_bangla.strip(),
                    "status": "To Learn",
                    "my_sentence": ""
                }
                st.session_state.custom_words.append(new_entry)
                save_json_file(CUSTOM_FILE, st.session_state.custom_words)
                st.success(f"Saved **{full_word}** ✅ — switch to the Flashcards tab, pick 'My Words' or 'All categories' to see it.")
                st.balloons()

    if st.session_state.custom_words:
        st.markdown("---")
        st.markdown(f"**Your added words ({len(st.session_state.custom_words)})**")
        for w in st.session_state.custom_words[::-1]:
            cols = st.columns([5, 1])
            cols[0].write(f"{w.get('icon','📘')} **{w['word']}** — {w['english']} / {w['bangla']}")
            if cols[1].button("🗑️", key=f"del_{w['id']}"):
                st.session_state.custom_words = [x for x in st.session_state.custom_words if x["id"] != w["id"]]
                save_json_file(CUSTOM_FILE, st.session_state.custom_words)
                st.rerun()

with tab_learn:
    if "idx" not in st.session_state:
        st.session_state.idx = 0
    if st.session_state.idx >= len(filtered):
        st.session_state.idx = 0

    card = filtered[st.session_state.idx]
    gender = card.get("article", "")
    color = GENDER_COLORS.get(gender, "#7C3AED")
    cat_color = category_color(card["category"])

    card.setdefault("icon", "📘")
    card.setdefault("plural", "")
    card.setdefault("my_sentence", "")
    card.setdefault("status", "To Learn")
    card.setdefault("type", "")
    card.setdefault("bangla", "")
    card.setdefault("english", "")
    if "sentence1" not in card:
        card["sentence1"] = card.get("sentence", "")
    card.setdefault("sentence2", "")
    card.setdefault("sentence1_en", "")
    card.setdefault("sentence1_bn", "")
    card.setdefault("sentence2_en", "")
    card.setdefault("sentence2_bn", "")

    # ---------- Top bar: category chip + progress ----------
    st.markdown(
        f"<div style='display:flex; justify-content:space-between; align-items:center;'>"
        f"<span style='font-size:22px; font-weight:800; color:#111827;'>German Vocabulary</span>"
        f"<span style='background:{cat_color}1A; color:{cat_color}; border:1px solid {cat_color}55; "
        f"padding:3px 10px; border-radius:999px; font-size:12px; font-weight:700;'>{card['category']}</span>"
        f"</div>", unsafe_allow_html=True
    )
    st.caption(f"Card {st.session_state.idx + 1} of {len(filtered)}")

    # ---------- Colourful side-by-side card ----------
    left, right = st.columns([1, 2.2])

    with left:
        st.markdown(
            f"""
            <div style="background: linear-gradient(160deg, {color}22, {color}08);
                        border:2px solid {color}; border-radius:16px;
                        height:150px; display:flex; flex-direction:column; align-items:center;
                        justify-content:center; text-align:center; box-shadow: 0 4px 14px {color}22;">
                <div style="font-size:46px;">{card['icon']}</div>
                <div style="font-size:11px; font-weight:800; color:{color}; margin-top:4px; text-transform:uppercase; letter-spacing:0.5px;">
                    {card['type'] or 'noun'}{(' · ' + gender) if gender else ''}
                </div>
                <div style="font-size:11px; color:#6B7280; margin-top:2px;">{STATUS_DOT[card['status']]} {card['status']}</div>
            </div>
            """, unsafe_allow_html=True
        )

    with right:
        plural_line = f"<span style='color:#6B7280; font-size:13px;'>Plural: {card['plural']}</span><br>" if card['plural'] else ""
        st.markdown(
            f"""
            <div style="border:1.5px solid #E5E7EB; border-radius:16px; padding:12px 16px; height:150px;
                        display:flex; flex-direction:column; justify-content:center; background:white;">
                <div style="font-size:26px; font-weight:800; color:#111827;">{card['word']}</div>
                {plural_line}
                <div style="font-size:15px; color:#374151; margin-top:4px;">🇬🇧 {card['english']}</div>
                <div style="font-size:14px; color:#374151;">🇧🇩 {card['bangla']}</div>
            </div>
            """, unsafe_allow_html=True
        )

    speak_button(card["word"].replace("sich ", ""), key=f"word_{card['id']}", label="🔊 Listen to the word")

    # ---------- Two example sentences, each with its own listen + translations ----------
    st.markdown("<div style='margin-top:10px; font-size:13px; font-weight:700; color:#7C3AED;'>EXAMPLE SENTENCES</div>", unsafe_allow_html=True)
    s1, s2 = st.columns(2)
    sentence_pairs = [
        (s1, card["sentence1"], card["sentence1_en"], card["sentence1_bn"], "s1"),
        (s2, card["sentence2"], card["sentence2_en"], card["sentence2_bn"], "s2"),
    ]
    for col, sent, sent_en, sent_bn, tag in sentence_pairs:
        with col:
            if sent:
                st.markdown(
                    f"""<div style="background:#F9FAFB; border:1px solid #E5E7EB; border-radius:12px;
                            padding:10px 12px; font-size:14px; color:#111827; min-height:95px;">
                        <b>{sent}</b>
                        {f"<div style='font-size:12.5px; color:#4B5563; margin-top:6px;'>🇬🇧 {sent_en}</div>" if sent_en else ""}
                        {f"<div style='font-size:12.5px; color:#4B5563; margin-top:2px;'>🇧🇩 {sent_bn}</div>" if sent_bn else ""}
                        </div>""", unsafe_allow_html=True
                )
                speak_button(sent, key=f"{tag}_{card['id']}", label="🔊")
            else:
                st.markdown(
                    """<div style="background:#F9FAFB; border:1px dashed #E5E7EB; border-radius:12px;
                            padding:10px 12px; font-size:13px; color:#9CA3AF; min-height:95px;
                            display:flex; align-items:center; justify-content:center;">— no second sentence —</div>""",
                    unsafe_allow_html=True
                )

    st.write("")

    # ---------- Your sentence + status ----------
    wc1, wc2 = st.columns([1.3, 1])
    with wc1:
        st.markdown("<div style='font-size:13px; font-weight:700; color:#7C3AED;'>✍️ YOUR SENTENCE</div>", unsafe_allow_html=True)
        my_sentence = st.text_area(
            "your sentence", value=card["my_sentence"], key=f"sentence_{card['id']}",
            placeholder="Write your own sentence...", label_visibility="collapsed", height=80
        )
        if st.button("💾 Save", key="save_btn"):
            st.session_state.progress.setdefault(str(card["id"]), {})
            st.session_state.progress[str(card["id"])]["my_sentence"] = my_sentence
            save_json_file(PROGRESS_FILE, st.session_state.progress)
            st.toast("Saved!")

    with wc2:
        st.markdown("<div style='font-size:13px; font-weight:700; color:#7C3AED;'>MARK WORD</div>", unsafe_allow_html=True)

        def set_status(new_status, advance=False):
            st.session_state.progress.setdefault(str(card["id"]), {})
            st.session_state.progress[str(card["id"])]["status"] = new_status
            save_json_file(PROGRESS_FILE, st.session_state.progress)
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

    st.caption("🔵 der · 🩷 die · 🟢 das · 🟣 no article (verb/adj/adv)")
