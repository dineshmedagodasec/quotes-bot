import random

QUESTIONS = [
    {
        "hook": "QUICK QUESTION",
        "text": "Which type of motivation\nworks best for you?\n",
        "options": "A) Morning quotes\n\nB) Success stories\n\nC) Personal challenges\n\nD) Music\n",
        "cta": "Comment A, B, C or D below!"
    },
    {
        "hook": "FINISH THIS SENTENCE",
        "text": "Success is not about ______\nit is about ______\n",
        "options": "",
        "cta": "Drop your answer below!\nBest answer gets featured!"
    },
    {
        "hook": "DAILY QUESTION",
        "text": "What is ONE thing you would\ntell your younger self?\n",
        "options": "",
        "cta": "Share your story below!\nEvery comment gets a reply!"
    },
    {
        "hook": "THIS OR THAT",
        "text": "What do you value more?\n",
        "options": "A) Money and success\n\nB) Peace and happiness\n",
        "cta": "Comment A or B!\nShare with someone who needs this!"
    },
    {
        "hook": "THINK ABOUT THIS",
        "text": "When was the last time you did\nsomething for the FIRST time?\n",
        "options": "",
        "cta": "Share below!\nFollow for daily motivation!"
    },
    {
        "hook": "VOTE NOW",
        "text": "What stops you from\nreaching your goals?\n",
        "options": "A) Fear of failure\n\nB) Lack of motivation\n\nC) No clear plan\n\nD) Other\n",
        "cta": "Comment your answer below!"
    },
    {
        "hook": "QUICK POLL",
        "text": "Are you a morning person\nor night owl?\n",
        "options": "A) Morning person\n   rise and grind!\n\nB) Night owl\n   best work after midnight!\n",
        "cta": "Comment A or B!\nTag a friend!"
    },
    {
        "hook": "BE HONEST",
        "text": "How many quotes actually\nchanged your life?\n",
        "options": "A) None yet\n\nB) 1 to 2 quotes\n\nC) Many of them\n\nD) Every single one!\n",
        "cta": "Drop your answer!\nFollow for more!"
    },
    {
        "hook": "MOTIVATIONAL QUESTION",
        "text": "What is your biggest\ndream right now?\n",
        "options": "",
        "cta": "Share it below!\nSpeaking it makes it real!"
    },
    {
        "hook": "SELF REFLECTION",
        "text": "Are you living the life you\nimagined 5 years ago?\n",
        "options": "A) Yes and it is amazing!\n\nB) No but I am working on it\n\nC) Not yet but I will get there\n\nD) Still figuring it out\n",
        "cta": "Be honest in the comments!"
    },
]

def create_question_video():
    question = random.choice(QUESTIONS)

    if question["options"]:
        quote = f"{question['text']}\n{question['options']}"
    else:
        quote = question["text"]

    author = question["cta"]
    hook = question["hook"]

    print(f"Question: {question['hook']}")
    return quote, author, hook
