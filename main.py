import streamlit as st
import openai
import os
import httpx
from bs4 import BeautifulSoup

st.title("Chatbot z webu")

openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")

def get_web_text(url):
    try:
        response = httpx.get(url, timeout=20.0)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        # Omezíme délku kvůli limitu tokenů
        return text[:4000]
    except Exception as e:
        return f"Chyba při stahování: {e}"

# --- Stažení textu ze všech 3 webů ---
webs = [
    "https://www.jtarchinvestments.cz/",
    "https://www.jtis.cz/",
    "https://www.epholding.cz/",
]
all_text = ""
for url in webs:
    all_text += f"\n\n=== Obsah z {url} ===\n"
    all_text += get_web_text(url)

# --- Chatovací rozhraní ---
user_input = st.text_input("Zadej svou otázku:")

if user_input:
    st.write("Vaše otázka:", user_input)
    prompt = (
        f"Na základě následujících informací z webových stránek odpověz na dotaz uživatele. "
        f"Odpovídej česky a pokud odpověď v textu nenajdeš, napiš, že to nevíš."
        f"\n\n"
        f"{all_text}\n\n"
        f"Dotaz: {user_input}\nOdpověď:"
    )

    client = openai.OpenAI(api_key=openai.api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Jsi odborný chatbot pro investice a energetiku."},
            {"role": "user", "content": prompt}
        ]
    )
    answer = response.choices[0].message.content
    st.write("Odpověď chatbota:", answer)

