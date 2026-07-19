import sqlite3
from datetime import datetime


DATABASE_NAME = "quiz_history.db"


def create_table():

    connection = sqlite3.connect(
        DATABASE_NAME
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS quiz_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sport TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            percentage REAL NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    connection.commit()

    connection.close()


def save_quiz_result(
    sport,
    difficulty,
    score,
    total_questions
):

    percentage = (
        score / total_questions
    ) * 100

    connection = sqlite3.connect(
        DATABASE_NAME
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO quiz_history (
            sport,
            difficulty,
            score,
            total_questions,
            percentage,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            sport,
            difficulty,
            score,
            total_questions,
            percentage,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
    )

    connection.commit()

    connection.close()


def get_quiz_history():

    connection = sqlite3.connect(
        DATABASE_NAME
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            sport,
            difficulty,
            score,
            total_questions,
            percentage,
            created_at
        FROM quiz_history
        ORDER BY id DESC
        """
    )

    results = cursor.fetchall()

    connection.close()

    return results
def clear_quiz_history():

    connection = sqlite3.connect(
        DATABASE_NAME
    )

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM quiz_history"
    )

    connection.commit()

    connection.close()