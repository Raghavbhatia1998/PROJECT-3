import streamlit as st
import pypdf
import re
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
from nltk.corpus import stopwords
import nltk

# Load stopwords
nltk.download("stopwords")

st.title("🔎 Keyword-Based Paragraph Extractor + WordCloud")

# ------------------------------
# PDF Upload
# ------------------------------
uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

# ------------------------------
# Keyword Input
# ------------------------------
keywords_input = st.text_input(
    "Enter keywords (comma separated):",
    placeholder="Example: profit, revenue, growth"
)

if uploaded_file and keywords_input:

    # --------------------------------
    # Extract PDF text
    # --------------------------------
    reader = pypdf.PdfReader(uploaded_file)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() or ""

    # --------------------------------
    # Split PDF text into sentences (no need for NLTK)
    # --------------------------------
    sentences = re.split(r'(?<=[.!?])\s+', full_text)

    # Clean keywords
    keywords = [k.strip().lower() for k in keywords_input.split(",") if k.strip()]

    # --------------------------------
    # Extract ONLY sentences that contain ANY keyword
    # --------------------------------
    matched_sentences = []
    for s in sentences:
        ls = s.lower()
        if any(k in ls for k in keywords):
            matched_sentences.append(s)

    # --------------------------------
    # Group consecutive matched sentences into paragraphs
    # --------------------------------
    matched_paragraphs = []
    temp_para = ""

    for s in sentences:
        ls = s.lower()
        if any(k in ls for k in keywords):
            temp_para += s + " "
        else:
            if temp_para:
                matched_paragraphs.append(temp_para.strip())
                temp_para = ""

    if temp_para:
        matched_paragraphs.append(temp_para.strip())

    # --------------------------------
    # Display extracted paragraphs
    # --------------------------------
    st.subheader("📌 Extracted Paragraphs Containing Keywords")

    if len(matched_paragraphs) == 0:
        st.warning("No paragraphs found containing the given keywords.")
    else:
        for i, p in enumerate(matched_paragraphs, start=1):
            st.markdown(f"### Paragraph {i}")
            st.write(p)

    # --------------------------------
    # WordCloud + Frequent Words (only from keyword paragraphs)
    # --------------------------------
    if len(matched_paragraphs) > 0:

        combined_text = " ".join(matched_paragraphs)

        # Regex tokenizer (no nltk download required)
        tokens = re.findall(r"\b[a-zA-Z]{3,}\b", combined_text.lower())

        # Remove stopwords
        stop = set(stopwords.words("english"))
        tokens = [w for w in tokens if w not in stop]

        if len(tokens) == 0:
            st.error("Not enough meaningful words to generate WordCloud.")
        else:
            # WordCloud
            st.subheader("☁️ WordCloud from Extracted Paragraphs")
            wc = WordCloud(width=1000, height=500, background_color="white")
            image = wc.generate(" ".join(tokens))

            fig = plt.figure(figsize=(12, 5))
            plt.imshow(image, interpolation="bilinear")
            plt.axis("off")
            st.pyplot(fig)

            # Frequent words table
            st.subheader("🔠 Top 20 Frequent Words")
            freq = Counter(tokens).most_common(20)
            freq_df = pd.DataFrame(freq, columns=["Word", "Frequency"])
            st.table(freq_df)

else:
    st.info("Upload a PDF and enter keywords to begin.")
