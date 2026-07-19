import re


def parse_quiz(quiz_text):

    questions = []

    blocks = re.split(
        r"-{10,}",
        quiz_text
    )

    for block in blocks:

        block = block.strip()

        if not block:
            continue

        question_match = re.search(
            r"Question\s*\d*:\s*(.*?)(?=\nA\))",
            block,
            re.DOTALL | re.IGNORECASE
        )

        options_match = re.findall(
            r"([A-D])\)\s*(.*)",
            block
        )

        answer_match = re.search(
            r"Correct Answer:\s*([A-D])",
            block,
            re.IGNORECASE
        )

        explanation_match = re.search(
            r"Explanation:\s*(.*)",
            block,
            re.DOTALL | re.IGNORECASE
        )

        if (
            question_match
            and len(options_match) == 4
            and answer_match
        ):

            question = question_match.group(1).strip()

            options = {
                letter: text.strip()
                for letter, text in options_match
            }

            correct_answer = (
                answer_match.group(1)
                .upper()
            )

            explanation = (
                explanation_match.group(1).strip()
                if explanation_match
                else ""
            )

            questions.append(
                {
                    "question": question,
                    "options": options,
                    "answer": correct_answer,
                    "explanation": explanation
                }
            )

    return questions