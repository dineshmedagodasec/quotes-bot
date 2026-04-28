import os
import random
import requests
from youtube_poster import post_to_youtube
from youtube_video_maker import create_youtube_short

QUESTIONS = [
    {
        "hook": "QUICK QUESTION",
        "text": "Which type of motivation works best for you?",
        "options": "A) Morning quotes\nB) Success stories\nC) Personal challenges\nD) Music",
        "cta": "Comment A, B, C or D below!"
    },
    {
        "hook": "FINISH THIS SENTENCE",
        "text": "Success is not about ______, it is about ______",
        "options": "",
        "cta": "Drop your answer below! Best answer gets featured!"
    },
    {
        "hook": "DAILY QUESTION",
        "text": "What is ONE thing you would tell your younger self?",
        "options": "",
        "cta": "Share your story below! Every comment gets a reply!"
    },
    {
        "hook": "THIS OR THAT",
        "text": "What do you value more?",
        "options": "A) Money and success\nB) Peace and happiness",
        "cta": "Comment A or B! Share with someone who needs this!"
    },
    {
        "hook": "THINK ABOUT THIS",
        "text": "When was the last time you did something for the FIRST time?",
        "options": "",
        "cta": "Share below! Follow for daily motivation!"
    },
    {
        "hook": "VOTE NOW",
        "text": "What stops you from reaching your goals?",
        "options": "A) Fear of failure\nB) Lack of motivation\nC) No clear plan\nD) Other",
        "cta": "Comment your answer below!"
    },
    {
        "hook": "QUICK POLL",
        "text": "Are you a morning person or night owl?",
        "options": "A) Morning person - rise and grind!\nB) Night owl - best work after midnight!",
        "cta": "Comment A or B! Tag a friend!"
    },
    {
        "hook": "BE HONEST",
        "text": "How many of these quotes actually changed your life?",
        "options": "A) None yet\nB) 1-2 quotes\nC) Many of them\nD) Every single one!",
        "cta": "Drop your answer! Follow for more!"
    },
]

def create_question_video():
    question = random.choice(QUESTIONS)

    # Build the full quote text
    if question["options"]:
        quote = f"{question['text']}\n\n{question['options']}"
    else:
        quote = question["text"]

    author = question["cta"]

    print(f"Creating question video: {question['hook']}")
    return quote, author, question["hook"]
