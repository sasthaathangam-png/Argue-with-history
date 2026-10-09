# 🏛️ Argue With History

Debate with an AI recreation of historical figures. Pick Kamarajar, Bharathiyar or Periyar, or type **any person's name** (Tamil or English), and argue with them in English or Tamil.

> ⚠️ **Disclaimer:** All replies are AI-generated recreations based on public sources (Wikipedia). They are **not actual quotes** and do not represent what the real person said.

## ✨ Features

- **3 preset figures** with hand-written personas: Kamarajar, Bharathiyar, Periyar
- **Any person search**: type a name in Tamil script, Tanglish or English (even misspelled); the app finds the right Wikipedia page for you to confirm
- **3 debate modes**: Friendly, Hard (the figure challenges your logic), Student (simple explanations)
- **English / தமிழ் language button**: replies come in the language you choose
- **Source badges** on every reply:
  - 🟢 *Based on source* (grounded in retrieved Wikipedia text)
  - 🟠 *AI inference* (the model reasoned beyond the text)
- **Living-person safety**: if the chosen person is alive, the app switches to respectful "public record commentary" mode and never puts words in their mouth
- **Auto-retry**: if one Gemini model is busy (503/429), the app retries and falls back to other models

## 🧠 How it works

```
Your argument
   │
   ▼
Retrieve relevant chunks from the person's Wikipedia text (RAG)
   │
   ▼
Persona + mode + language + retrieved context  →  Gemini
   │
   ▼
Reply with a 🟢 / 🟠 source badge
```

- **UI:** Streamlit
- **LLM:** Google Gemini (free tier works)
- **Retrieval:** simple keyword-overlap search over Wikipedia text (no vector database needed)
- **Data:** downloaded from Wikipedia on first use and cached in `data/`

## 🚀 Setup

**Requirements:** Python 3.9 or newer, and a free [Gemini API key](https://aistudio.google.com/).

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/argue-with-history.git
cd argue-with-history

# 2. Install dependencies
python -m pip install -r requirements.txt

# 3. Add your API key
#    Copy .env.example to .env, then put your key inside it:
#    GEMINI_API_KEY=your_key_here

# 4. Run
python -m streamlit run app.py
```

Then open <http://localhost:8501>.

> 🔒 Never commit your `.env` file. It is already listed in `.gitignore`.

## 📁 Project structure

```
argue-with-history/
├── app.py            # Streamlit UI, Gemini calls, retry logic
├── persona.py        # Figures, modes, languages, system prompt
├── rag.py            # Wikipedia download + keyword retrieval
├── requirements.txt
├── .env.example      # Template for your API key
└── .gitignore
```

## ➕ Adding a new preset figure

Add one entry to `FIGURES` in `persona.py`:

```python
"ambedkar": {
    "name": "B. R. Ambedkar",
    "wiki": "B. R. Ambedkar",          # exact Wikipedia page title
    "era": "1891-1956, jurist and social reformer",
    "style": "Scholarly, precise, firm.",
    "values": "Equality, education, constitutional rights.",
},
```

## ⚠️ Known limitations

- Retrieval matches English words, so questions in Tamil script may get less accurate source grounding
- People with short Wikipedia pages give weaker answers (the app shows a warning)
- Free-tier Gemini can return "high demand" errors; wait a minute and try again
- Gemini model names change over time; if you get a 404, update the `MODELS` list in `app.py`

## 🗺️ Roadmap

- [ ] ⏳ Time Machine mode ("What would Kamarajar say about UPI or AI?")
- [ ] 📊 Debate scorecard (logic, evidence, clarity)
- [ ] 🎯 "Change My Mind" persuasion meter
- [ ] 🪑 Roundtable mode (multiple figures debating each other)
- [ ] 🎙️ Tamil voice input / output

## 📄 License

MIT. Feel free to learn from it and build on it.
