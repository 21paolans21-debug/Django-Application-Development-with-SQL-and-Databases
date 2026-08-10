# Developing AI Applications with Python and Flask

## Emotion Detector

This project implements an AI-based Emotion Detection web application using Python, Flask, and the Watson NLP EmotionPredict service.

The application analyzes English text and returns scores for:

- anger
- disgust
- fear
- joy
- sadness

It also identifies the `dominant_emotion`.

## Project structure

```text
Developing-AI-Applications-with-Python-and-Flask/
├── EmotionDetection/
│   ├── __init__.py
│   └── emotion_detection.py
├── static/
│   ├── mywebscript.js
│   └── style.css
├── templates/
│   └── index.html
├── server.py
├── test_emotion_detection.py
├── requirements.txt
└── README.md
```

## Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

## Run the application

```bash
python3 server.py
```

Open:

```text
http://127.0.0.1:5000/
```

## Run unit tests

```bash
python3 -m unittest test_emotion_detection.py
```

## Run static code analysis

```bash
pylint server.py EmotionDetection/emotion_detection.py
```

## Error handling

Blank or invalid input returns:

```text
Invalid text! Please try again!
```
