# German Vocabulary Trainer

A flashcard-style Streamlit app for learning German vocabulary — with gender
colour-coding, plural forms, example sentences, English translation, Bangla
pronunciation, a place to write your own sentence, a German text-to-speech
button, and status tracking (To Learn / Learning / Learned), mirroring your
Notion setup.

## What's included
- `app.py` — the app
- `vocab_data.json` — 120 starter words across 6 categories (Daily Life,
  Food/Drink/Shopping, World & Travel, Business & Career, People &
  Relationships, Time & Numbers), 20 words each
- `progress.json` — created automatically to save your status + written
  sentences between sessions (only works when running locally or on a
  persistent server — on some free cloud hosts this may reset)

## Run it locally (works great on phone browsers too, once hosted)
```bash
pip install streamlit
streamlit run app.py
```
Then open the Local URL it prints (usually http://localhost:8501).

## Put it on your phone
Streamlit itself just runs on your computer/server — to open it on your
phone you need a URL, not a file. Easiest free option:
1. Push this folder to a GitHub repo.
2. Go to https://share.streamlit.io, sign in, connect the repo, deploy.
3. You'll get a public URL — open that on your phone's browser like any
   website, and you can even add it to your home screen so it acts like an app.

## Growing it to 1000 words
`vocab_data.json` is a plain list — each entry is:
```json
{
  "category": "...",
  "word": "der/die/das + word",
  "article": "der / die / das / \"\" for non-nouns",
  "type": "noun / verb / adjective / adverb",
  "plural": "die ... (leave empty if not a noun or no plural)",
  "sentence": "example sentence",
  "english": "translation",
  "bangla": "approximate pronunciation",
  "status": "To Learn",
  "my_sentence": ""
}
```
Add more entries the same way — no code changes needed, the app just
reads the file. I can generate more batches of words (next 100, next 200,
etc.) whenever you want to keep growing toward 1000.

## Notes on the Bangla pronunciation
These are approximate phonetic guides, not official transliteration —
German sounds like ü, ö, ä, and ch don't map perfectly onto Bangla script.
Treat them as a rough pronunciation aid alongside the audio button, not a
100% precise guide.
