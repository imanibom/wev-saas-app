from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from alert_keywords import check_for_alert_keywords

# Initialize VADER analyzer
analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text, pillar="general"):
    """
    Analyze sentiment using VADER and check for alert keywords
    Returns: {
        'compound': float (-1 to 1),
        'positive': float,
        'negative': float,
        'neutral': float,
        'is_negative': bool,
        'has_alert_keywords': bool,
        'alert_keywords': list,
        'needs_human_review': bool
    }
    """
    # Get VADER scores
    scores = analyzer.polarity_scores(text)

    # Check for alert keywords
    has_alert, matched_keywords = check_for_alert_keywords(text, pillar)

    # Determine if needs human review
    is_negative = scores['compound'] < -0.5  # More sensitive than -0.1
    needs_review = is_negative or has_alert

    return {
        'compound': scores['compound'],
        'positive': scores['pos'],
        'negative': scores['neg'],
        'neutral': scores['neu'],
        'is_negative': is_negative,
        'has_alert_keywords': has_alert,
        'alert_keywords': matched_keywords,
        'needs_human_review': needs_review
    }

# Test function
if __name__ == "__main__":
    test_messages = [
        "I feel great! The medicine worked perfectly.",
        "I'm experiencing severe dizziness and nausea.",
        "The rash is getting worse, I need help.",
        "Everything is fine, no issues.",
        "Chest pain and difficulty breathing - emergency!"
    ]

    for msg in test_messages:
        result = analyze_sentiment(msg, "pharmacy")
        print(f"Message: '{msg}'")
        print(f"Analysis: {result}")
        print("---")