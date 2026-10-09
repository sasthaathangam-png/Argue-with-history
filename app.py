import os
import re
import time
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
from persona import FIGURES, MODES, LANGS, build_prompt
from rag import load_figure, retrieve, fetch_wiki, slug, search_wiki

load_dotenv()
gclient = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# If one model is busy, the next one is tried
MODELS = ["gemini-flash-latest", "gemini-flash-lite-latest", "gemini-3.8-flash"]

st.set_page_config(page_title="Argue With History", page_icon="🏛️")
st.title("🏛️ Argue With History")
st.caption("AI recreation based on public sources. Not actual quotes.")


def ask(system, messages):
    chat = [
        types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[types.Part(text=m["content"])],
        )
        for m in messages
    ]
    last_error = None
    for model in MODELS:
        for attempt in range(3):
            try:
                r = gclient.models.generate_content(
                    model=model,
                    contents=chat,
                    config=types.GenerateContentConfig(system_instruction=system),
                )
                return r.text or ""
            except Exception as e:
                last_error = e
                msg = str(e)
                if "503" in msg or "429" in msg:
                    time.sleep(3 * (attempt + 1))
                    continue
                if "404" in msg:
                    break
                raise
    raise last_error


def to_english(name):
    return ask(
        "Reply with only the answer.",
        [{"role": "user", "content":
          "Convert this person's name (may be Tamil script, Tanglish or misspelled) "
          "to the most likely English Wikipedia article title. "
          f"Reply with only the title.\nName: {name}"}],
    ).strip()


def is_deceased(name, text):
    r = ask(
        "Answer only YES or NO.",
        [{"role": "user", "content":
          f"Is {name} deceased? Text:\n{text[:1500]}\nAnswer only YES or NO."}],
    )
    return "YES" in r.upper()


def set_figure(key, figure):
    if st.session_state.get("figure_key") != key:
        st.session_state.history = []
    st.session_state.figure_key = key
    st.session_state.figure = figure


def badge(text):
    text = re.sub(r"\[SOURCE\]", "\n\n🟢 **Based on source**", text)
    text = re.sub(r"\[INFERENCE\]", "\n\n🟠 **AI inference**", text)
    return text


# ---------- Sidebar ----------
lang = st.sidebar.radio("🌐 Language", list(LANGS.keys()), horizontal=True)
st.sidebar.divider()
st.sidebar.header("Who do you want to talk to?")
choice = st.sidebar.radio("Type", ["Preset figure", "Any person"])
mode = st.sidebar.selectbox("Mode", list(MODES.keys()))

if choice == "Preset figure":
    key = st.sidebar.selectbox(
        "Figure", list(FIGURES.keys()),
        format_func=lambda k: FIGURES[k]["name"],
    )
    fig = FIGURES[key]
    try:
        with st.spinner("Loading data..."):
            ok = load_figure(key, fig["wiki"])
    except Exception as e:
        ok = False
        st.sidebar.error(f"Could not connect to Wikipedia: {e}")
    if ok:
        set_figure(key, fig)
    else:
        st.sidebar.error("Could not load data.")
else:
    name = st.sidebar.text_input("Type any name (Tamil or English)")
    if st.sidebar.button("Search") and name:
        try:
            with st.spinner("Searching..."):
                st.session_state.results = search_wiki(to_english(name))
            if not st.session_state.results:
                st.sidebar.error("Not found on Wikipedia. Try a different spelling.")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

    results = st.session_state.get("results", [])
    if results:
        pick = st.sidebar.selectbox("Select the correct person", results)
        if st.sidebar.button("Start debate"):
            try:
                key = slug(pick)
                with st.spinner("Loading data..."):
                    page = fetch_wiki(pick, key)
                if not page:
                    st.sidebar.error("Could not load the page.")
                else:
                    load_figure(key)
                    living = not is_deceased(page.title, page.text)
                    set_figure(key, {"name": page.title, "living": living})
                    if living:
                        st.sidebar.warning("This person is alive. Commentary is based on public record only.")
                    if len(page.text) < 3000:
                        st.sidebar.warning("Limited data available, so answers may be limited.")
            except Exception as e:
                st.sidebar.error(f"Error: {e}")

# ---------- Chat ----------
if "figure" not in st.session_state:
    st.info("Select a figure from the left sidebar.")
    st.stop()

st.subheader(f"💬 {st.session_state.figure['name']}")

if "history" not in st.session_state:
    st.session_state.history = []

for m in st.session_state.history:
    st.chat_message(m["role"]).write(badge(m["content"]))

if q := st.chat_input("Type your argument..."):
    st.chat_message("user").write(q)
    st.session_state.history.append({"role": "user", "content": q})

    try:
        with st.spinner("Thinking..."):
            context = retrieve(st.session_state.figure_key, q)
            answer = ask(
                 build_prompt(st.session_state.figure, mode, context, lang),
                st.session_state.history,
            )
        st.chat_message("assistant").write(badge(answer))
        st.session_state.history.append({"role": "assistant", "content": answer})
    except Exception as e:
        st.error(f"Error: {e}")
        st.session_state.history.pop()