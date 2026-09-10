# German Vocabulary Trainer — v2

## What changed from your version
1. **Colour & design** — gradient header, colour-coded gender cards (blue *der*,
   pink *die*, green *das*, purple for verbs/adjectives/adverbs), a coloured
   category "chip" per word (auto-assigned per category, so any new category
   you type in "Add word" gets its own consistent colour), rounded cards with
   soft shadows instead of flat grey boxes.
2. **Real Bangla meanings, not transliteration** — your original `bangla`
   field was a phonetic sounding-out of the German word (e.g. "দাস হাউস" for
   *das Haus*), per your own README's intent as a pronunciation aid. You
   asked for actual **meaning**, so all 120 entries now have the real Bangla
   translation of the word (e.g. "বাড়ি" = house).
3. **English + Bangla translation for both example sentences** — every
   `sentence1`/`sentence2` now has a matching `sentence1_en`, `sentence1_bn`,
   `sentence2_en`, `sentence2_bn`, shown right under the German sentence.
4. **Audio on sentences too** — every example sentence now has its own small
   🔊 button (same Web Speech API `de-DE` voice as the word button), not just
   the headword.
5. **"➕ Add your own word" tab** — a form to add new vocabulary (word,
   article, type, plural, icon, English/Bangla meaning, two example
   sentences with their translations). New words save to `custom_words.json`
   and instantly appear in the deck under whatever category you type
   (default "My Words"). You can delete any custom word from the list below
   the form.

## Files
- `app.py` — the app
- `vocab_data.json` — your 120 words, now with real Bangla meanings + full
  sentence translations
- `custom_words.json` — created automatically the first time you add a word
- `progress.json` — created automatically to save status + your sentences

## Run it
```bash
pip install streamlit
streamlit run app.py
```
Then open the printed local URL (usually http://localhost:8501).

## On the translation question you asked
I didn't call a translation API for this — I translated all 120 Bangla
meanings and 240 sentence translations myself directly (German → English →
Bangla), since I already know all three languages and this gives more
natural, context-aware results than a generic API for short vocab sentences.

If you want this to scale automatically as you add hundreds more words
later (rather than asking me to translate each batch), the practical
options are:
- **LibreTranslate** (self-hosted or their public API) — free/open-source,
  decent quality, has German→Bangla and German→English.
- **Google Cloud Translation API** or **DeepL API** — higher quality,
  needs an API key and has a per-character cost after a free tier. DeepL
  doesn't support Bangla directly, so you'd chain DE→EN→BN.
- Keep doing what we did: paste new words to me in a batch and I'll
  translate them directly — most reliable for idiomatic short sentences.

Any of the API options would need an API key stored as a Streamlit secret
and a `requests` call in `app.py`; happy to wire that up if you tell me
which service you'd rather use.

## On the voice/audio question
The 🔊 button uses your browser's built-in Web Speech API
(`SpeechSynthesisUtterance` with `lang = "de-DE"`) — no API key, works
offline once the page loads, and now fires for both example sentences too,
not just the headword. Quality depends on the voices installed on the
device/browser (Chrome on desktop tends to have the best German voices;
some mobile browsers have thinner voice packs).
