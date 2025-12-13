import streamlit as st
import pypdf
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import pandas as pd

nltk.download("punkt")
nltk.download("stopwords")

st.title("🔎 Keyword Paragraph Extractor + WordCloud Generator")

# Upload PDF
uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

keywords_input = st.text_input(
    "Enter keywords (comma separated):",
    placeholder="example: profit, revenue, growth"
)

if uploaded_file and keywords_input:
    # -----------------------------
    # Extract PDF Text
    # -----------------------------
    reader = pypdf.PdfReader(uploaded_file)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() or ""

    # Split into paragraphs
    paragraphs = full_text.split("\n\n")

    # Clean keywords
    keywords = [k.strip().lower() for k in keywords_input.split(",") if k.strip()]

    # -----------------------------
    # Extract paragraphs containing ANY keyword
    # -----------------------------
    matched_paragraphs = []
    for para in paragraphs:
        lower_para = para.lower()
        if any(k in lower_para for k in keywords):
            matched_paragraphs.append(para.strip())

    # -----------------------------
    # Display Results
    # -----------------------------
    st.subheader("📌 Extracted Paragraphs Containing Keywords")
    if len(matched_paragraphs) == 0:
        st.warning("No paragraphs found containing the given keywords.")
    else:
        for i, p in enumerate(matched_paragraphs, start=1):
            st.markdown(f"### Paragraph {i}")
            st.write(p)

    # -----------------------------
    # Generate WordCloud from matched paragraphs
    # -----------------------------
    if len(matched_paragraphs) > 0:
        st.subheader("☁️ WordCloud from Extracted Paragraphs")

        combined_text = " ".join(matched_paragraphs)

        # Clean + tokenize
        combined_text = re.sub(r"[^A-Za-z\s]", " ", combined_text)
        tokens = word_tokenize(combined_text.lower())

        stop = set(stopwords.words("english"))
        tokens = [w for w in tokens if w not in stop and len(w) > 2]

        if len(tokens) == 0:
            st.error("No valid words found for WordCloud.")
        else:
            wc = WordCloud(width=1000, height=500, background_color="white")
            image = wc.generate(" ".join(tokens))

            fig = plt.figure(figsize=(12, 5))
            plt.imshow(image, interpolation="bilinear")
            plt.axis("off")
            st.pyplot(fig)

        # -----------------------------
        # Frequent word table
        # -----------------------------
        st.subheader("☁️ WordCloud from Extracted Paragraphs")

combined_text = " ".join(matched_paragraphs)

# Regex-based tokenization (NO nltk needed)
import re
tokens = re.findall(r"\b[a-zA-Z]{3,}\b", combined_text.lower())

# Remove stopwords
from nltk.corpus import stopwords
stop = set(stopwords.words("english"))
tokens = [w for w in tokens if w not in stop]

if len(tokens) == 0:
    st.error("No valid words found for WordCloud.")
else:
    wc = WordCloud(width=1000, height=500, background_color="white")
    image = wc.generate(" ".join(tokens))

    fig = plt.figure(figsize=(12, 5))
    plt.imshow(image, interpolation="bilinear")
    plt.axis("off")
    st.pyplot(fig)

    # Frequent words
    from collections import Counter
    freq = Counter(tokens).most_common(20)
    freq_df = pd.DataFrame(freq, columns=["Word", "Frequency"])
    st.subheader("🔠 Top 20 Frequent Words")
    st.table(freq_df)
