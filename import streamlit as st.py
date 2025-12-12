import streamlit as st
import PyPDF2
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize

# Download tokenizer once
nltk.download("punkt")


# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text


def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"\d+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def get_word_frequencies(tokens, top_n=20):
    freq = Counter(tokens)
    return freq.most_common(top_n)


# -----------------------------
# STREAMLIT UI
# -----------------------------

st.title("📄 PDF Text Analyzer — Word Cloud + Top Words")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
    st.success("PDF uploaded successfully!")

    # Extract text
    raw_text = extract_text_from_pdf(uploaded_file)

    # Preprocess
    clean_text = preprocess_text(raw_text)

    # Tokenize
    tokens = word_tokenize(clean_text)

    # -----------------------------
    # Show Frequent Words
    # -----------------------------
    st.subheader("🔠 Top Frequent Words")

    top_words = get_word_frequencies(tokens, top_n=20)

    freq_df = {
        "word": [w for w, f in top_words],
        "frequency": [f for w, f in top_words],
    }

    st.table(freq_df)

    # -----------------------------
    # Generate Word Cloud
    # -----------------------------
    st.subheader("☁️ Word Cloud")

    wc = WordCloud(width=800, height=400, background_color="white").generate(clean_text)

    fig = plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")

    st.pyplot(fig)
