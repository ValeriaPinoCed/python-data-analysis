import joblib
import re
import pandas as pd
import streamlit as st

# page configurator
st.set_page_config(
    page_title="Fake News Detector",
    page_icon="📰",
    layout="wide")
# Load the saved vectorizer and classifier


@st.cache_resource
def load_model():
    vectorizer = joblib.load('vectorizer.pkl')
    classifier = joblib.load('classifier.pkl')
    return vectorizer, classifier


vectorizer, classifier = load_model()


# Cleaning function used before prediction
def clean_source(text):
    text = str(text)

    # Remove agency/location prefixes like:
    # WASHINGTON (Reuters) -
    # SEATTLE/WASHINGTON (Reuters) -
    # WEST PALM BEACH, Fla./WASHINGTON (Reuters) -
    text = re.sub(
        r'^[A-Z][A-Za-z\s,./-]*\((Reuters|AP|AFP|Bloomberg)\)\s*-\s*',
        '',
        text,
        flags=re.IGNORECASE
    )

    # Remove generic agency prefixes anywhere near the start
    text = re.sub(
        r'^\s*.*?\((Reuters|AP|AFP|Bloomberg)\)\s*-\s*',
        '',
        text,
        flags=re.IGNORECASE
    )

    # Remove common scraping leftovers
    text = re.sub(r'^Leave a reply\s+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^Next\s+Prev\s+Swipe\s+left/right\s*',
                  '', text, flags=re.IGNORECASE)
    text = re.sub(r'^Next\s+Swipe\s+left/right\s*',
                  '', text, flags=re.IGNORECASE)

    # Remove author bylines like "by John Smith"
    text = re.sub(r'\bby\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,4}', '', text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text


# Predict one single news article
def predict_news(text):
    cleaned = clean_source(text)
    vector = vectorizer.transform([cleaned])
    prediction = classifier.predict(vector)[0]
    score = classifier.decision_function(vector)[0]
    confidence = abs(score)
    return prediction, score, confidence, cleaned


# Predict all news articles from a CSV file
def predict_csv(df, text_column='text'):
    if text_column not in df.columns:
        raise ValueError(
            f"Column '{text_column}' was not found in the CSV file.")

    result_df = df.copy()
    result_df['cleaned_text'] = result_df[text_column].astype(
        str).apply(clean_source)

    vectors = vectorizer.transform(result_df['cleaned_text'])
    result_df['prediction'] = classifier.predict(vectors)
    result_df['score'] = classifier.decision_function(vectors)
    result_df['confidence'] = result_df['score'].abs()

    return result_df


# APP HEADER
st.title("📰 Fake News Detector")
st.write("Classify news articles as **REAL** or **FAKE** using a trained machine learning model.")

tab1, tab2, tab3 = st.tabs(
    ["Single Prediction", "Batch CSV Prediction", "Model Info"])
with tab1:
    st.subheader("Predict a single news article")

    user_text = st.text_area(
        "Paste the full text of a news article:",
        height=250,
        placeholder="Paste the article text here..."
    )

    if st.button("Predict article"):
        if not user_text.strip():
            st.warning("Please paste some article text first.")
        else:
            pred, score, confidence, cleaned = predict_news(user_text)

            if pred == "FAKE":
                st.error(f"Prediction: {pred}")
            else:
                st.success(f"Prediction: {pred}")

            st.write(f"**Score:** {score:.3f}")
            st.write(f"**Confidence:** {confidence:.3f}")

            with st.expander("Show cleaned text used for prediction"):
                st.write(cleaned)

with tab2:
    st.subheader("Predict multiple news articles from a CSV file")

    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)

            st.write("### Preview of uploaded data")
            preview_df = df.drop(columns=['text'], errors='ignore')
            st.dataframe(preview_df.head())

            text_column = st.selectbox(
                "Select the column that contains the news text:",
                options=df.columns
            )

            if st.button("Predict CSV"):
                result_df = predict_csv(df, text_column)

                st.write("### Prediction results")

                display_df = result_df.drop(
                    columns=['text'],
                    errors='ignore'
                )

                st.dataframe(display_df.head(20))

                csv_data = display_df.to_csv(index=False).encode("utf-8")

                st.download_button(
                    label="Download predictions as CSV",
                    data=csv_data,
                    file_name="predicted_news.csv",
                    mime="text/csv"
                )

        except Exception as e:
            st.error(f"Error reading the CSV file: {e}")

with tab3:
    st.subheader("Model information")

    st.write("This app uses:")
    st.write("- A saved TF-IDF vectorizer")
    st.write("- A trained classifier loaded from `classifier.pkl`")
    st.write("- A text cleaning function to preprocess input articles")

    st.info(
        "You can later improve this section by adding model metrics such as accuracy, "
        "precision, recall, F1-score, and a confusion matrix."
    )
