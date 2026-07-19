from src.database import search_facts
from src.search import get_live_news
from src.llm import generate
from src.quiz_parser import parse_quiz

def generate_quiz(
    sport,
    difficulty,
    question_count=5,
    provider=None,
    search_query=None
):
    """
    Generate a sports quiz using:
    ChromaDB + Web Search + LLM
    """
    # =================================
    # 1. RETRIEVE HISTORICAL FACTS
    # =================================
    historical = search_facts(
        sport,
        f"{sport} history records championships rules"
    )

    historical_context = (
        "\n".join(historical)
        if historical
        else "No historical facts found."

    )

    # =================================
    # 2. RETRIEVE LATEST NEWS
    # =================================
    search_query = None

    if not search_query:

        search_query = (
            f"{sport} recent tournament winners "
            f"championship results player achievements "
            f"records latest news 2026"
        )

    latest_news = get_live_news(
        search_query
    )
        # =================================
    # 3. COMBINE CONTEXT
    # =================================
    context = f"""

==========================
HISTORICAL FACTS
==========================

{historical_context}

==========================
LATEST NEWS
==========================

{latest_news}
"""
    # =================================
    # 4. BUILD PROMPT
    # =================================
    prompt = f"""
You are an expert Sports Quiz Generator.
Use ONLY the information provided below.
If the information is insufficient,
do not invent facts.
Context:
{context}
Generate exactly {question_count}
multiple-choice questions.
Sport: {sport}
Difficulty: {difficulty}
For every question follow this format exactly:
Question: <question>
A) <option>
B) <option>
C) <option>
D) <option>
Correct Answer: <A/B/C/D>
Explanation: <short explanation>
----------------------------------------
"""
    # =================================
    # 5. CALL LLM
    # =================================
    response_text = generate(
        prompt,
        provider
    )
    # =================================
    # 6. PARSE RESPONSE
    # =================================
    questions = parse_quiz(
        response_text
    )
    # =================================
    # 7. VALIDATE QUESTION COUNT
    # =================================
    if len(questions) != question_count:
        raise ValueError(
            f"AI generated "
            f"{len(questions)} questions, "
            f"but {question_count} "
            f"were required."
        )
    # =================================
    # 8. RETURN
    # =================================
    return response_text, context