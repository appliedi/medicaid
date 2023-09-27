import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from wordcloud import WordCloud
from collections import defaultdict
from sklearn.feature_extraction.text import CountVectorizer
import os

# Streamlit App Title
st.title('QIT Support Evaluation Analysis')

# Upload Excel File
uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx'])

if uploaded_file is not None:
    # Load Data
    raw_data_df = pd.read_excel(uploaded_file, engine='openpyxl')
    
    # Display Data
    st.write('Data Preview:')
    st.write(raw_data_df.head())
    
    # Histograms for Rating Columns
    st.subheader('Histograms for Rating Columns')
    order = ['Very Satisfied', 'Satisfied', 'Neutral', 'Dissatisfied', 'Very Dissatisfied', 'Not Applicable']
    for col in raw_data_df.columns[:7]:
        fig, ax = plt.subplots(figsize=(10,6))
        sns.countplot(x=col, data=raw_data_df, order=order, palette='viridis', ax=ax)
        ax.set_title(col)
        ax.set_xlabel('')
        ax.set_ylabel('Frequency')
        plt.xticks(rotation=45, ha='right')
        for p in ax.patches:
            ax.annotate(f'{p.get_height()}', (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center', fontsize=12, color='black', xytext=(0, 5),
                        textcoords='offset points')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    
    # Sentiment Analysis
    st.subheader('Sentiment Analysis of Comments')
    comments_col = "Do you have additional comments or suggestions?"
    positive_keywords = ['good', 'great', 'excellent', 'positive', 'satisfied', 'helpful', 'improved', 'like']
    negative_keywords = ['bad', 'poor', 'negative', 'dissatisfied', 'unhelpful', 'worse', 'dislike']
    neutral_keywords = ['okay', 'neutral', 'average', 'sufficient']
    sentiment_counts = defaultdict(int)

    for comment in raw_data_df[comments_col].dropna():
        comment = comment.lower()
        if any(word in comment for word in positive_keywords):
            sentiment_counts['Positive'] += 1
        elif any(word in comment for word in negative_keywords):
            sentiment_counts['Negative'] += 1
        elif any(word in comment for word in neutral_keywords):
            sentiment_counts['Neutral'] += 1
        else:
            sentiment_counts['Uncategorized'] += 1

    fig, ax = plt.subplots(figsize=(10,6))
    sns.barplot(x=list(sentiment_counts.keys()), y=list(sentiment_counts.values()), palette='viridis', ax=ax)
    ax.set_title('Sentiment Analysis of Comments')
    ax.set_xlabel('Sentiment')
    ax.set_ylabel('Frequency')
    for p in ax.patches:
        ax.annotate(f'{p.get_height()}', (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', fontsize=12, color='black', xytext=(0, 5),
                    textcoords='offset points')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    
    # Word Cloud
    st.subheader('Word Cloud of Comments')
    comments_text = ' '.join(raw_data_df[comments_col].dropna())
    wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='viridis').generate(comments_text)
    fig, ax = plt.subplots(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    # Topic Modeling
    st.subheader('Top Words in Comments (Topic Modeling)')
    comments = raw_data_df[comments_col].dropna()
    vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
    X = vectorizer.fit_transform(comments)
    sum_words = X.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in vectorizer.vocabulary_.items()]
    words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
    top_words = words_freq[:10]
    top_words_labels, top_words_freq = zip(*top_words)
    
    fig, ax = plt.subplots(figsize=(10,6))
    sns.barplot(x=list(top_words_labels), y=list(top_words_freq), palette='viridis', ax=ax)
    ax.set_title('Top Words in Comments (Topic Modeling)')
    ax.set_xlabel('Words')
    ax.set_ylabel('Frequency')
    plt.xticks(rotation=45, ha='right')
    for p in ax.patches:
        ax.annotate(f'{p.get_height()}', (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', fontsize=12, color='black', xytext=(0, 5),
                    textcoords='offset points')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    
    # Categorization
    st.subheader('Categorization of Comments')
    categories_keywords = {
        'Support': ['support', 'help', 'assist'],
        'Technical Issues': ['issue', 'problem', 'error', 'bug'],
        'Response Time': ['time', 'wait', 'delay', 'response'],
        'Communication': ['communicate', 'inform', 'update', 'notify'],
        'Service Quality': ['quality', 'satisfy', 'good', 'bad', 'excellent', 'poor']
    }
    categories_counts = defaultdict(int)
    for comment in raw_data_df[comments_col].dropna():
        comment = comment.lower()
        categorized = False
        for category, keywords in categories_keywords.items():
            if any(word in comment for word in keywords):
                categories_counts[category] += 1
                categorized = True
        if not categorized:
            categories_counts['Uncategorized'] += 1
    
    fig, ax = plt.subplots(figsize=(10,6))
    sns.barplot(x=list(categories_counts.keys()), y=list(categories_counts.values()), palette='viridis', ax=ax)
    ax.set_title('Categorization of Comments')
    ax.set_xlabel('Categories')
    ax.set_ylabel('Frequency')
    plt.xticks(rotation=45, ha='right')
    for p in ax.patches:
        ax.annotate(f'{p.get_height()}', (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', fontsize=12, color='black', xytext=(0, 5),
                    textcoords='offset points')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    
    # Generate PDF Report
    if st.button('Generate PDF Report'):
        pdf_path = 'QITSupportEvaluation_Report.pdf'
        with PdfPages(pdf_path) as pdf:
            # Add visualizations to the PDF
            # ...
            st.success(f'PDF Report Generated: [Download Link]({pdf_path})')

# Running the Streamlit App
# Save the above code in a Python file (e.g., app.py) and run the following command in the terminal:
# $ streamlit run app.py
