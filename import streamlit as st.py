import streamlit as st
from pypdf import PdfReader
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
import re
from collections import Counter
import string

# --- Configuration for Streamlit Page ---
st.set_page_config(
    page_title="PDF Word Cloud & Frequency Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. PDF Text Extraction Function ---
@st.cache_data
def extract_text_from_pdf(pdf_file):
    """Extracts text from an uploaded PDF file."""
    text = ""
    try:
        # pypdf.PdfReader is generally more reliable than PdfReader in older versions
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            text += page.extract_text() if page.extract_text() else ""
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None
    return text

# --- 2. Text Preprocessing and Analysis Function ---
@st.cache_data
def analyze_text(raw_text):
    """Cleans text, calculates frequencies, and returns cleaned text and frequencies."""
    
    # 1. Lowercasing
    text_lower = raw_text.lower()
    
    # 2. Tokenization and Punctuation/Number removal
    # Keeps only alphabetic characters
    words = re.findall(r'\b[a-z]{3,}\b', text_lower) 
    
    # 3. Stop Word Removal (Using a basic set)
    # Define a simple list of common English stop words
    STOPWORDS = set([
        "the", "and", "is", "in", "it", "to", "of", "a", "for", "on", "with",
        "as", "by", "that", "this", "be", "have", "are", "from", "was", "will",
        "can", "would", "at", "or", "an", "they", "we", "he", "she", "you",
        "their", "his", "her", "its", "i", "my", "your", "but", "so", "if", 
        "then", "about", "up", "out", "only", "no", "yes", "than", "more"
    ])
    
    # Filter out stop words
    filtered_words = [word for word in words if word not in STOPWORDS]
    
    # 4. Calculate Word Frequency
    word_counts = Counter(filtered_words)
    
    return " ".join(filtered_words), word_counts


# --- 3. Word Cloud Generation Function ---
@st.cache_data
def generate_word_cloud(text_data):
    """Generates and returns a Matplotlib figure of the Word Cloud."""
    
    # Configure WordCloud object
    wc = WordCloud(
        background_color="white",
        max_words=200,
        width=800,
        height=400,
        contour_color='steelblue',
        stopwords=set(), # Filtered words already
        collocations=False # Only look at individual words
    )
    
    # Generate the word cloud
    wc.generate(text_data)
    
    # Plotting
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off") # Hide axes
    
    return fig


# ===============================================
# === STREAMLIT APP LAYOUT & LOGIC STARTS HERE ===
# ===============================================

st.title("📄 PDF Text Analysis Tool")
st.markdown("Upload a PDF to see its Word Cloud and the most frequent words.")

# --- File Uploader ---
uploaded_file = st.file_uploader(
    "Choose a PDF file", 
    type="pdf", 
    accept_multiple_files=False
)

if uploaded_file is not None:
    
    # 1. Extract Text
    with st.spinner("Extracting text from PDF..."):
        pdf_text = extract_text_from_pdf(uploaded_file)
        
    if pdf_text and len(pdf_text.strip()) > 100: # Check if extraction was successful and has enough content
        
        # 2. Analyze Text
        with st.spinner("Analyzing text and calculating frequencies..."):
            cleaned_text, word_counts = analyze_text(pdf_text)
            
        # --- Display Results ---
        
        # Create columns for side-by-side display
        col1, col2 = st.columns([7, 3])
        
        with col1:
            st.header("☁️ Word Cloud")
            st.markdown("A visual representation of the most frequent words.")
            
            # 3. Generate and Display Word Cloud
            wordcloud_fig = generate_word_cloud(cleaned_text)
            st.pyplot(wordcloud_fig) 
            
        with col2:
            st.header("📊 Top Frequent Words")
            
            # Convert Counter object to DataFrame for display
            top_words = word_counts.most_common(20) # Get top 20
            df_freq = pd.DataFrame(top_words, columns=['Word', 'Count'])
            
            st.dataframe(
                df_freq,
                hide_index=True,
                use_container_width=True,
            )
            
            # Optional: Display Bar Chart
            st.subheader("Top 10 Words Chart")
            fig_bar, ax_bar = plt.subplots(figsize=(6, 4))
            top_10 = df_freq.head(10)
            ax_bar.barh(top_10['Word'], top_10['Count'], color='skyblue')
            ax_bar.set_xlabel("Frequency Count")
            ax_bar.invert_yaxis() # Put the most frequent word at the top
            st.pyplot(fig_bar)

        # Optional: Display Raw Extracted Text (for debugging/verification)
        with st.expander("Show Raw Extracted Text (First 1000 characters)"):
            st.text(pdf_text[:1000] + "...")

    elif pdf_text:
         st.warning("The extracted text from the PDF was too short or empty. Please try another file.")
    else:
        # Error handling is inside the extraction function, but this catches null returns
        pass
        
else:
    st.info("Please upload a PDF file to begin the analysis.")