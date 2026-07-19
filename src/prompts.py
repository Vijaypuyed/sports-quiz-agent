def build_quiz_prompt(sport, difficulty, context):
    return f"""
You are an expert Sports Quiz Generator.

You MUST answer ONLY using the provided context.

If the answer is not available in the context,
say "Insufficient information."

Context:
{context}

Generate exactly 5 multiple choice questions.

Sport: {sport}
Difficulty: {difficulty}

Output Format:

Question:
A)
B)
C)
D)

Correct Answer:

Explanation:

--------------------
"""