import random

QUESTIONS = [
    {
        "hook": "QUICK QUESTION",
        "text": "Which type of motivation works best for you?",
        "options": "A) Morning quotes\n
                    B) Success stories\n
                    C) Personal challenges\n
                    D) Music",
        
        "cta": "Comment A, B, C or D below!"
    },
    {
        "hook": "FINISH THIS SENTENCE",
        "text": "Success is not about ______ it is about ______",
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
        "options": "A) Money and success\n
                    B) Peace and happiness\n",
        
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
        "options": "A) Fear of failure\n
                    B) Lack of motivation\n
                    C) No clear plan\n
                    D) Other",
        
        "cta": "Comment your answer below!"
    },
    {
        "hook": "QUICK POLL",
        "text": "Are you a morning person or night owl?",
        "options": "A) Morning person - rise and grind!\n
                    B) Night owl - best work after midnight!",
        
        "cta": "Comment A or B! Tag a friend!"
    },
    {
        "hook": "BE HONEST",
        "text": "How many of these quotes actually changed your life?",
        "options": "A) None yet\n
                    B) 1 to 2 quotes\n
                    C) Many of them\n
                    D) Every single one!\n",
        
        "cta": "Drop your answer! Follow for more!"
    },
    {
        "hook": "MOTIVATIONAL QUESTION",
        "text": "What is your biggest dream right now?",
        "options": "",
        
        "cta": "Share it below! Speaking it makes it real!"
    },
    {
        "hook": "SELF REFLECTION",
        "text": "Are you living the life you imagined 5 years ago?",
        "options": "A) Yes and it is amazing!\n
                    B) No but I am working on it\n
                    C) Not yet but I will get there\nD) Still figuring it out",
        
        "cta": "Be honest in the comments!"
    },
]

def create_question_video():
    question = random.choice(QUESTIONS)

    if question["options"]:
        quote = f"{question['text']}\n\n{question['options']}"
    else:
        quote = question["text"]

    author = question["cta"]
    hook = question["hook"]

    print(f"Question: {question['hook']}")
    return quote, author, hook
