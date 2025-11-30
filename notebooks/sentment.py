import pandas as pd
import numpy as np
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Plotting style
sns.set(style="whitegrid")

# Load spaCy model once (will raise clear error if missing)
try:
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
except OSError:
    raise OSError(
        "spaCy model 'en_core_web_sm' not found. Run in terminal:\n"
        "python -m spacy download en_core_web_sm"
    )


class SentimentThemeAnalyzer:
    def __init__(
        self,
        input_path="data/processed/reviews_processed.csv",
        output_path="data/processed/reviews_with_sentiment_themes.csv"
    ):
        self.input_path = input_path
        self.output_path = output_path
        self.df = None
        self.bank_keywords = {}

        # Theme definitions based on Ethiopian banking context
        self.THEME_KEYWORDS = {
            "Account Access Issues": [
                "login", "password", "forgot", "blocked", "locked", "access",
                "authentication", "otp", "verification", "pin", "username"
            ],
            "Transaction Performance": [
                "transfer", "payment", "transaction", "send money", "withdraw",
                "deposit", "slow", "failed", "error", "not working", "crash",
                "delay", "timeout", "declined"
            ],
            "User Interface & Experience": [
                "ui", "design", "interface", "easy", "smooth", "user friendly",
                "navigation", "layout", "good app", "nice app", "intuitive",
                "simple", "fast", "responsive"
            ],
            "Customer Support": [
                "support", "help", "call", "response", "agent", "customer care",
                "contact", "email", "slow response", "no reply", "helpline"
            ],
            "Feature Requests": [
                "add", "feature", "include", "need", "want", "should have",
                "missing", "request", "more options", "update", "improve"
            ]
        }

    def _get_vader_sentiment(self, text):
        if pd.isna(text) or str(text).strip() == "":
            return np.nan, "neutral"
        scores = SentimentIntensityAnalyzer().polarity_scores(str(text))
        compound = scores['compound']
        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"
        return compound, label

    def _clean_text(self, text):
        if pd.isna(text):
            return ""
        text = str(text).lower()
        text = re.sub(r"[^a-z\s]", " ", text)
        return " ".join(text.split())

    def _preprocess_for_keywords(self, text):
        doc = nlp(self._clean_text(text))
        tokens = [
            token.lemma_.strip()
            for token in doc
            if token.is_alpha and not token.is_stop and len(token.text) > 2
        ]
        return " ".join(tokens)

    def _extract_top_keywords(self, texts, top_n=30):
        if texts.empty or all(t == "" for t in texts):
            return []
        vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1, 2))
        try:
            X = vectorizer.fit_transform(texts)
            feature_array = np.array(vectorizer.get_feature_names_out())
            tfidf_mean = np.mean(X.toarray(), axis=0)
            top_indices = tfidf_mean.argsort()[-top_n:][::-1]
            return feature_array[top_indices].tolist()
        except ValueError:
            return []

    def _assign_theme(self, text):
        if pd.isna(text):
            return "Other"
        text = str(text).lower()
        scores = {}
        for theme, keywords in self.THEME_KEYWORDS.items():
            count = sum(1 for kw in keywords if kw in text)
            scores[theme] = count
        best_theme = max(scores, key=scores.get)
        return best_theme if scores[best_theme] > 0 else "Other"

    def analyze(self):
        if not os.path.exists(self.input_path):
            raise FileNotFoundError(f"Input file not found: {self.input_path}")
        self.df = pd.read_csv(self.input_path)
        print(f"✅ Loaded {len(self.df)} reviews from {self.input_path}")

        # Ensure 'text_length' exists (from preprocessing)
        if 'text_length' not in self.df.columns:
            self.df['text_length'] = self.df['review_text'].str.len()

        # Sentiment analysis
        print("🧠 Computing sentiment scores with VADER...")
        self.df[['sentiment_score', 'sentiment_label']] = self.df['review_text'].apply(
            lambda x: pd.Series(self._get_vader_sentiment(x))
        )

        # Preprocess text for keywords
        print("🧹 Preprocessing text for thematic analysis...")
        self.df['clean_text'] = self.df['review_text'].apply(self._preprocess_for_keywords)

        # Extract keywords per bank
        print("🔍 Extracting top keywords per bank...")
        self.bank_keywords = {}
        for bank in self.df['bank_name'].unique():
            bank_texts = self.df[self.df['bank_name'] == bank]['clean_text']
            self.bank_keywords[bank] = self._extract_top_keywords(bank_texts, top_n=25)

        # Assign themes
        print("🏷️  Assigning themes...")
        self.df['identified_theme'] = self.df['review_text'].apply(self._assign_theme)

        # Save output
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        output_cols = [
            'review_id', 'review_text', 'rating', 'bank_name',
            'sentiment_score', 'sentiment_label', 'identified_theme'
        ]
        self.df[output_cols].to_csv(self.output_path, index=False)
        print(f"💾 Saved results to {self.output_path}")

        # Print summaries
        self._print_summary()
        return self.df

    def _print_summary(self):
        print("\n" + "="*60)
        print("📊 SENTIMENT & THEMES SUMMARY")
        print("="*60)

        print("\nSentiment by Bank:")
        print(self.df.groupby('bank_name')['sentiment_label'].value_counts().unstack(fill_value=0))

        print("\nThemes by Bank:")
        print(self.df.groupby('bank_name')['identified_theme'].value_counts().unstack(fill_value=0))

        print("\nTop Keywords by Bank:")
        for bank, kws in self.bank_keywords.items():
            print(f"\n{bank}:")
            print(", ".join(kws[:10]))

    # ============ PLOTTING METHODS ============
    def plot_sentiment_by_bank(self):
        plt.figure(figsize=(10, 6))
        sns.countplot(data=self.df, x='bank_name', hue='sentiment_label', palette='viridis')
        plt.title('Sentiment Distribution by Bank')
        plt.xlabel('Bank')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.legend(title='Sentiment')
        plt.tight_layout()
        plt.show()

    def plot_themes_by_bank(self):
        plt.figure(figsize=(12, 6))
        sns.countplot(data=self.df, y='identified_theme', hue='bank_name', palette='Set2')
        plt.title('Theme Frequency by Bank')
        plt.xlabel('Count')
        plt.ylabel('Theme')
        plt.legend(title='Bank')
        plt.tight_layout()
        plt.show()

    def plot_review_length_by_sentiment(self):
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=self.df, x='sentiment_label', y='text_length', hue='bank_name')
        plt.title('Review Length by Sentiment and Bank')
        plt.xlabel('Sentiment')
        plt.ylabel('Review Length (characters)')
        plt.tight_layout()
        plt.show()

    def plot_all(self):
        """Generate all key visualizations."""
        self.plot_sentiment_by_bank()
        self.plot_themes_by_bank()
        self.plot_review_length_by_sentiment()