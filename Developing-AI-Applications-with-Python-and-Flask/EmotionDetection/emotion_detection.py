"""Emotion detection module using the Watson NLP EmotionPredict service."""

import requests

EMOTION_URL = (
    "https://sn-watson-emotion.labs.skills.network/"
    "v1/watson.runtime.nlp.v1/NlpService/EmotionPredict"
)

HEADERS = {
    "grpc-metadata-mm-model-id": "emotion_aggregated-workflow_lang_en_stock"
}


def emotion_detector(text_to_analyze):
    """Return emotion scores and the dominant emotion for the supplied text."""
    payload = {
        "raw_document": {
            "text": text_to_analyze
        }
    }

    response = requests.post(
        EMOTION_URL,
        headers=HEADERS,
        json=payload,
        timeout=30
    )

    if response.status_code == 400:
        return {
            "anger": None,
            "disgust": None,
            "fear": None,
            "joy": None,
            "sadness": None,
            "dominant_emotion": None
        }

    response.raise_for_status()
    data = response.json()

    emotions = data["emotionPredictions"][0]["emotion"]

    emotion_scores = {
        "anger": emotions["anger"],
        "disgust": emotions["disgust"],
        "fear": emotions["fear"],
        "joy": emotions["joy"],
        "sadness": emotions["sadness"]
    }

    dominant_emotion = max(emotion_scores, key=emotion_scores.get)

    return {
        **emotion_scores,
        "dominant_emotion": dominant_emotion
    }
