from src.quiz_parser import parse_quiz


sample_quiz = """
Question 1: Who won the first Cricket World Cup?

A) India
B) West Indies
C) Australia
D) England

Correct Answer: B

Explanation: West Indies won the first Cricket World Cup.

----------------------------

Question 2: Which sport uses a racket?

A) Football
B) Cricket
C) Tennis
D) Hockey

Correct Answer: C

Explanation: Tennis is played using a racket.
"""


questions = parse_quiz(sample_quiz)


for question in questions:

    print(question)