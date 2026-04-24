"""
AI-powered tools for enhanced agent capabilities
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime


def classify_text(text: str, categories: List[str]) -> Dict[str, Any]:
    """Classify text into categories based on keyword matching."""
    text_lower = text.lower()
    scores = {}

    for category in categories:
        keywords = category.lower().replace('_', ' ').split()
        matches = sum(1 for kw in keywords if kw in text_lower)
        scores[category] = {
            'score': matches / max(len(keywords), 1),
            'matched_keywords': [kw for kw in keywords if kw in text_lower]
        }

    best_match = max(scores.items(), key=lambda x: x[1]['score'])

    return {
        'classification': best_match[0],
        'confidence': best_match[1]['score'],
        'all_scores': scores
    }


def extract_key_phrases(text: str, n: int = 5) -> List[str]:
    """Extract key phrases from text based on frequency and position."""
    words = text.lower().split()

    stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                  'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                  'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                  'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in',
                  'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into',
                  'through', 'during', 'before', 'after', 'above', 'below',
                  'between', 'under', 'again', 'further', 'then', 'once',
                  'and', 'but', 'or', 'nor', 'so', 'yet', 'both', 'either',
                  'neither', 'not', 'only', 'own', 'same', 'than', 'too',
                  'very', 'just', 'also', 'now', 'here', 'there', 'when',
                  'where', 'why', 'how', 'all', 'each', 'every', 'both',
                  'few', 'more', 'most', 'other', 'some', 'such', 'no',
                  'any', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
                  'she', 'it', 'we', 'they', 'what', 'which', 'who', 'whom'}

    word_freq = {}
    for i, word in enumerate(words):
        clean = ''.join(c for c in word if c.isalnum())
        if clean and clean not in stop_words and len(clean) > 2:
            position_bonus = 1.5 if i < len(words) // 5 else 1.0
            word_freq[clean] = word_freq.get(clean, 0) + position_bonus

    sorted_phrases = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [phrase for phrase, _ in sorted_phrases[:n]]


def summarize_key_points(text: str, max_points: int = 5) -> List[str]:
    """Extract key points from text based on sentence position and content."""
    sentences = text.replace('!', '.').replace('?', '.').split('.')
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return []

    scored_sentences = []
    for i, sentence in enumerate(sentences):
        score = 0

        if i == 0 or i == len(sentences) - 1:
            score += 2

        if len(sentence.split()) > 5:
            score += 1

        important_words = ['important', 'key', 'significant', 'main', 'primary',
                          'essential', 'critical', 'crucial', 'fundamental',
                          'conclusion', 'result', 'finding', 'discovery']
        if any(word in sentence.lower() for word in important_words):
            score += 2

        scored_sentences.append((score, i, sentence))

    scored_sentences.sort(reverse=True)
    top_sentences = scored_sentences[:max_points]
    top_sentences.sort(key=lambda x: x[1])

    return [sentence for _, _, sentence in top_sentences]


def detect_language(text: str) -> Dict[str, Any]:
    """Detect language of text based on common words."""
    language_indicators = {
        'english': ['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'it'],
        'spanish': ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se'],
        'french': ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir'],
        'german': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich'],
        'italian': ['il', 'di', 'che', 'e', 'la', 'il', 'un', 'a', 'per', 'in'],
        'portuguese': ['o', 'de', 'a', 'em', 'um', 'para', 'com', 'não', 'uma', 'os'],
        'swahili': ['ni', 'ya', 'na', 'kwa', 'ku', 'wa', 'la', 'cha', 'vyo', 'za'],
    }

    text_lower = text.lower().split()
    scores = {}

    for language, indicators in language_indicators.items():
        matches = sum(1 for word in indicators if word in text_lower)
        scores[language] = matches

    best_match = max(scores.items(), key=lambda x: x[1])

    return {
        'language': best_match[0],
        'confidence': best_match[1] / 10,
        'all_scores': scores
    }


def sentiment_analysis(text: str) -> Dict[str, Any]:
    """Simple sentiment analysis based on word lists."""
    positive_words = {
        'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
        'awesome', 'positive', 'happy', 'joy', 'love', 'best', 'beautiful',
        'perfect', 'brilliant', 'outstanding', 'superb', 'pleasant', 'nice',
        'helpful', 'useful', 'easy', 'smooth', 'success', 'successful',
        'impressive', 'enjoy', 'enjoyable', 'delightful', 'pleasant'
    }

    negative_words = {
        'bad', 'terrible', 'awful', 'horrible', 'worst', 'negative', 'sad',
        'hate', 'angry', 'disappointing', 'disappointed', 'poor', 'wrong',
        'error', 'fail', 'failed', 'failure', 'problem', 'issue', 'difficult',
        'hard', 'broken', 'useless', 'waste', 'annoying', 'frustrated',
        'frustrating', 'confusing', 'confused', 'lacking', 'missing'
    }

    text_lower = text.lower()
    words = text_lower.split()

    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)

    total = positive_count + negative_count

    if total == 0:
        return {'sentiment': 'neutral', 'score': 0.5, 'positive': 0, 'negative': 0}

    positive_ratio = positive_count / total
    negative_ratio = negative_count / total

    if positive_ratio > negative_ratio:
        sentiment = 'positive'
        score = 0.5 + (positive_ratio - negative_ratio) / 2
    elif negative_ratio > positive_ratio:
        sentiment = 'negative'
        score = 0.5 - (negative_ratio - positive_ratio) / 2
    else:
        sentiment = 'neutral'
        score = 0.5

    return {
        'sentiment': sentiment,
        'score': round(score, 2),
        'positive_words': positive_count,
        'negative_words': negative_count
    }


def generate_tags(text: str, max_tags: int = 10) -> List[str]:
    """Generate relevant tags from text content."""
    key_phrases = extract_key_phrases(text, max_tags * 2)

    tag_blacklist = {'thing', 'things', 'stuff', 'way', 'make', 'get', 'got',
                     'know', 'like', 'want', 'take', 'come', 'see', 'use'}

    tags = []
    for phrase in key_phrases:
        if phrase not in tag_blacklist and len(phrase) > 3:
            tags.append(phrase.lower().replace(' ', '-'))

    return tags[:max_tags]


def readability_score(text: str) -> Dict[str, Any]:
    """Calculate readability metrics for text."""
    sentences = text.replace('!', '.').replace('?', '.').split('.')
    sentences = [s.strip() for s in sentences if s.strip()]

    words = text.split()
    syllable_count = 0
    for word in words:
        syllable_count += max(1, sum(1 for c in word.lower() if c in 'aeiouy'))

    avg_sentence_length = len(words) / max(len(sentences), 1)
    avg_syllables_per_word = syllable_count / max(len(words), 1)

    flesch_kincaid = 0.39 * avg_sentence_length + 11.8 * avg_syllables_per_word - 15.59
    flesch_reading = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word

    return {
        'flesch_kincaid_grade': round(flesch_kincaid, 2),
        'flesch_reading_ease': round(max(0, min(100, flesch_reading)), 2),
        'avg_sentence_length': round(avg_sentence_length, 2),
        'avg_syllables_per_word': round(avg_syllables_per_word, 2),
        'total_words': len(words),
        'total_sentences': len(sentences)
    }


def extract_entities(text: str) -> Dict[str, List[str]]:
    """Extract named entities from text (simplified pattern-based)."""
    entities = {
        'emails': [],
        'urls': [],
        'phone_numbers': [],
        'dates': [],
        'times': [],
        'money': [],
        'percentages': []
    }

    import re

    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    date_pattern = r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b|\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b'
    time_pattern = r'\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?\b'
    money_pattern = r'\$?\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b|\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|EUR|GBP|KES)\b'
    percent_pattern = r'\b\d+(?:\.\d+)?\s*%\b'

    entities['emails'] = list(set(re.findall(email_pattern, text)))
    entities['urls'] = list(set(re.findall(url_pattern, text)))
    entities['phone_numbers'] = list(set(re.findall(phone_pattern, text)))
    entities['dates'] = list(set(re.findall(date_pattern, text)))
    entities['times'] = list(set(re.findall(time_pattern, text)))
    entities['money'] = list(set(re.findall(money_pattern, text)))
    entities['percentages'] = list(set(re.findall(percent_pattern, text)))

    return {k: v for k, v in entities.items() if v}


def text_to_outline(text: str) -> List[Dict[str, str]]:
    """Convert text into a hierarchical outline structure."""
    lines = text.split('\n')
    outline = []

    heading_patterns = [
        (r'^#\s+(.+)', 1),
        (r'^##\s+(.+)', 2),
        (r'^###\s+(.+)', 3),
        (r'^####\s+(.+)', 4),
        (r'^([A-Z][^.!?]*):$', 1),
        (r'^(\d+\.\s+.+)', 1),
        (r'^(\s*[-*•]\s+.+)', 1),
    ]

    for line in lines:
        line = line.strip()
        if not line:
            continue

        for pattern, level in heading_patterns:
            match = re.match(pattern, line)
            if match:
                content = match.group(1) if match.lastindex else match.group(0)
                content = re.sub(r'^[-*•]\s*', '', content)
                content = re.sub(r'^\d+\.\s*', '', content)
                outline.append({
                    'level': level,
                    'content': content.strip('#: '),
                    'original': line
                })
                break
        else:
            if outline:
                outline.append({
                    'level': outline[-1]['level'] + 1,
                    'content': line,
                    'original': line
                })

    return outline
