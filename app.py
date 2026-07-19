import streamlit as st
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh
from src.history import (
    create_table,
    save_quiz_result,
    get_quiz_history,
    clear_quiz_history
)
from src.database import load_data
from src.generator import generate_quiz
from src.quiz_parser import parse_quiz

# =================================
# PAGE CONFIGURATION
# =================================
st.set_page_config(
    page_title="AI Sports Quiz Generator",
    page_icon="🏆",
    layout="wide"
)

st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: bold;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
    '<div class="main-title">🏆 AI Sports Quiz Generator</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Generate quizzes using historical facts, latest sports news, and AI.</div>',
    unsafe_allow_html=True
)

# =================================
# SESSION STATE INITIALIZATION
# =================================
if "active_page" not in st.session_state:
    st.session_state.active_page = "Quiz"
if "questions" not in st.session_state:
    st.session_state.questions = []
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
if "context" not in st.session_state:
    st.session_state.context = ""
if "answer_submitted" not in st.session_state:
    st.session_state.answer_submitted = False
if "selected_answer" not in st.session_state:
    st.session_state.selected_answer = None
if "answer_history" not in st.session_state:
    st.session_state.answer_history = []
if "result_saved" not in st.session_state:
    st.session_state.result_saved = False
if "question_start_time" not in st.session_state:
    st.session_state.question_start_time = None
# =================================
# INITIALIZE DATABASES
# =================================
@st.cache_resource
def initialize_database():

    load_data()

initialize_database()
create_table()

# =================================
# SIDEBAR SETTINGS
# =================================
def get_quiz_settings(difficulty):

    if difficulty == "Easy":
        return 5, 30
    elif difficulty == "Medium":
        return 7, 25
    else:
        return 10, 20
st.sidebar.header("⚙️ Quiz Settings")

sport = st.sidebar.selectbox(
    "Choose Sport",
    [
        "Cricket",
        "Football",
        "Badminton",
        "Tennis",
        "Hockey"
    ]
)

difficulty = st.sidebar.selectbox(
    "Choose Difficulty",
    [
        "Easy",
        "Medium",
        "Hard"
    ]
)
llm_provider = st.sidebar.selectbox(
    "🤖 Choose AI Provider",
    [
        "groq",
        "gemini",
        "openai"
    ]
)
question_count, time_limit = get_quiz_settings(
    difficulty
)
generate = st.sidebar.button(
    "🚀 Generate Quiz",
    use_container_width=True
)
# =================================
# APPLICATION TABS
# =================================
quiz_tab, history_tab = st.tabs(
    [
        "🏠 Quiz",
        "📊 Quiz History"
    ]
)
# =================================
# QUIZ TAB
# =================================
with quiz_tab:
    # ---------------------------------
    # GENERATE QUIZ
    # ---------------------------------
    if generate:
        with st.spinner(
            "Retrieving facts, searching news, and generating quiz..."
        ):
            try:
                # Generate quiz
                quiz, context = generate_quiz(
                    sport,
                    difficulty,
                    question_count,
                    llm_provider
                )
                # Parse quiz
                questions = parse_quiz(
                    quiz
                )
                # Check parsed questions
                if len(questions) == 0:

                    st.error(
                        "Quiz could not be parsed. "
                        "Please try generating again."
                    )
                else:
                    # Store quiz data
                    st.session_state.questions = questions
                    st.session_state.context = context
                    st.session_state.current_question = 0
                    st.session_state.question_start_time = time.time()
                    st.session_state.score = 0
                    st.session_state.quiz_started = True
                    st.session_state.quiz_started = True
                    st.session_state.answer_submitted = False
                    st.session_state.selected_answer = None
                    st.session_state.result_saved = False
                    st.success(
                        "🎉 Quiz Generated Successfully!"
                    )
                    st.rerun()
            except Exception as e:
                error_message = str(e)
                if "429" in error_message:
                    st.error(
                        "⚠️ API quota exceeded. "
                        "Please wait and try again later."
                    )
                elif "404" in error_message:
                    st.error(
                        "❌ AI model not found. "
                        "Please check the configured model."
                    )
                elif "RESOURCE_EXHAUSTED" in error_message:
                    st.error(
                        "⚠️ API limit reached. "
                        "Please try again later."
                    )
                elif "Connection" in error_message:
                    st.error(
                        "🌐 Network connection error. "
                        "Please check your internet connection."
                    )
                else:
                    st.error(
                        f"❌ Unexpected Error: "
                        f"{error_message}"
                    )
    # ---------------------------------
    # INTERACTIVE QUIZ
    # ---------------------------------
    if (
        st.session_state.quiz_started
        and st.session_state.questions
    ):
        questions = (
            st.session_state.questions
        )
        current_index = (
            st.session_state.current_question
        )
        total_questions = len(
            questions
        )
        # =================================
        # QUIZ IN PROGRESS
        # =================================
        if current_index < total_questions:
            current = questions[current_index]
            st_autorefresh(
                interval=1000,
                key=f"timer_{current_index}"
            )
            # =================================
            # QUESTION TIMER
            # ================================
            TIME_LIMIT = time_limit
            if st.session_state.question_start_time is None:

                st.session_state.question_start_time = time.time()
            elapsed_time = (
                time.time()
                - st.session_state.question_start_time
            )
            remaining_time = max(
                0,
                TIME_LIMIT - int(elapsed_time)
            )
            st.warning(
                f"⏱️ Time Remaining: "
                f"{remaining_time} seconds"
            )
            if remaining_time == 0:
                st.error(
                    "⏰ Time's Up! Moving to next question..."
                )
                st.session_state.current_question += 1
                st.session_state.question_start_time = time.time()
                st.session_state.answer_submitted = False
                st.session_state.selected_answer = None
                st.rerun()
            # Progress bar
            st.progress(
                current_index
                / total_questions
            )
            progress_percentage = (
                (current_index + 1)
                / total_questions
            ) * 100
            st.caption(
                f"Progress: "
                f"{progress_percentage:.0f}%"
            )
            st.subheader(
                f"Question "
                f"{current_index + 1} "
                f"of "
                f"{total_questions}"
            )
            # Question
            st.write(
                f"### "
                f"{current['question']}"
            )
            # Options
            option_keys = list(
                current["options"].keys()
            )
            # ---------------------------------
            # BEFORE ANSWER SUBMISSION
            # ---------------------------------
            if not (
                st.session_state.answer_submitted
            ):
                selected = st.radio(
                    "Choose your answer:",

                    option_keys,

                    format_func=lambda key:
                        f"{key}) "
                        f"{current['options'][key]}",

                    key=f"question_{current_index}"
                )
                if st.button(
                    "✅ Submit Answer",
                    use_container_width=True
                ):
                    # Save selected answer
                    st.session_state.selected_answer = (
                        selected
                    )
                    # Mark answer submitted
                    st.session_state.answer_submitted = (
                        True
                    )
                    # Check answer
                    is_correct = (
                        selected
                        == current["answer"]
                    )
                    if is_correct:
                        st.session_state.score += 1
                    st.session_state.answer_history.append(
                        {
                            "question": current["question"],
                            "your_answer": selected,
                            "correct_answer": current["answer"],
                            "is_correct": is_correct,
                            "explanation": current["explanation"]
                        }
                    )
                    st.rerun()
            # ---------------------------------
            # AFTER ANSWER SUBMISSION
            # ---------------------------------
            else:
                selected = (
                    st.session_state.selected_answer
                )
                # Correct answer
                if (
                    selected
                    == current["answer"]
                ):
                    st.success(
                        "🎉 Correct Answer!"
                    )
                # Wrong answer
                else:
                    st.error(
                        f"❌ Wrong Answer! "
                        f"Correct Answer: "
                        f"{current['answer']}"
                    )
                # Explanation
                st.info(
                    f"💡 Explanation: "
                    f"{current['explanation']}"
                )
                # Next question
                if st.button(
                    "➡️ Next Question",
                    use_container_width=True
                ):
                    st.session_state.current_question += 1
                    st.session_state.question_start_time = time.time()
                    st.session_state.answer_submitted = False
                    st.session_state.selected_answer = (
                        None
                    )
                    st.rerun()
        # =================================
        # QUIZ COMPLETED
        # =================================
        else:
            st.balloons()
            st.success(
                "🎉 Quiz Completed!"
            )
            score = (
                st.session_state.score
            )
            percentage = (
                score
                / total_questions
            ) * 100
            # ---------------------------------
            # SAVE RESULT ONCE
            # ---------------------------------
            if not (
                st.session_state.result_saved
            ):
                save_quiz_result(
                    sport=sport,
                    difficulty=difficulty,
                    score=score,
                    total_questions=total_questions
                )
                st.session_state.result_saved = (
                    True
                )
            # ---------------------------------
            # SCORE
            # ---------------------------------
            st.subheader(
                f"🏆 Your Score: "
                f"{score}/"
                f"{total_questions}"
            )
            st.metric(
                "Percentage",
                f"{percentage:.0f}%"
            )
            # =================================
            # ANSWER REVIEW
            # =================================
            st.markdown("---")
            st.subheader(
                "📝 Answer Review"
            )
            for index, answer in enumerate(
                st.session_state.answer_history
            ):
                if answer["is_correct"]:
                    status = "✅ Correct"
                else:
                    status = "❌ Wrong"
                with st.expander(
                    f"Question {index + 1} - {status}"
                ):
                    st.write(
                        f"### {answer['question']}"
                    )
                    st.write(
                        f"🟢 Your Answer: "
                        f"**{answer['your_answer']}**"
                    )
                    st.write(
                        f"✅ Correct Answer: "
                        f"**{answer['correct_answer']}**"
                    )
                    if answer["is_correct"]:
                        st.success(
                            "🎉 Your answer is correct!"
                        )
                    else:
                          st.error(
                            "❌ Your answer is incorrect."
                        )
                    st.info(
                        f"💡 Explanation: "
                        f"{answer['explanation']}"
                    )
            # Performance message
            if percentage >= 80:
                st.success(
                    "🔥 Excellent Performance!"
                )
            elif percentage >= 50:
                st.info(
                    "👍 Good Job! "
                    "Keep Practicing."
                )
            else:
                st.warning(
                    "📚 Keep Learning "
                    "and Try Again!"
                )
            # ---------------------------------
            # RESTART QUIZ
            # ---------------------------------
            if st.button(
                "🔄 Restart Quiz",
                use_container_width=True
            ):
                st.session_state.questions = []
                st.session_state.current_question = 0
                st.session_state.score = 0
                st.session_state.quiz_started = False
                st.session_state.context = ""
                st.session_state.answer_submitted = False
                st.session_state.selected_answer = None
                st.session_state.result_saved = False
                st.session_state.question_start_time = None
                st.rerun()
    # =================================
    # RAG CONTEXT VIEWER
    # =================================
    if st.session_state.context:
        with st.expander(
            "🔍 View Retrieved RAG Context"
        ):
            st.text(
                st.session_state.context
            )
# =================================
# QUIZ HISTORY TAB
# =================================
with history_tab:
    st.header(
        "📊 Quiz History"
    )
    history = (
        get_quiz_history()
    )
    if history:
        # ---------------------------------
        # PREPARE DATA
        # ---------------------------------
        history_data = []
        for record in history:
            history_data.append(
                {
                    "Sport": record[0],
                    "Difficulty": record[1],
                    "Score": record[2],
                    "Total Questions": record[3],
                    "Percentage": record[4],
                    "Date": record[5]
                }
            )
        # Create DataFrame
        df = pd.DataFrame(
            history_data
        )
        csv_data = df.to_csv(
            index=False
        )
        st.download_button(
            label="📥 Download Quiz History",
            data=csv_data,
            file_name="quiz_history.csv",
            mime="text/csv",
            use_container_width=True
        )
        # ---------------------------------
        # DASHBOARD METRICS
        # ---------------------------------
        total_quizzes = len(
            df
        )
        average_score = (
            df["Percentage"].mean()
        )
        best_score = (
            df["Percentage"].max()
        )
        col1, col2, col3 = (
            st.columns(3)
        )
        with col1:

            st.metric(
                "🎯 Total Quizzes",
                total_quizzes
            )
        with col2:

            st.metric(
                "📈 Average Score",
                f"{average_score:.0f}%"
            )
        with col3:
            st.metric(
                "🏆 Best Score",
                f"{best_score:.0f}%"
            )
        # ---------------------------------
        # QUIZ ATTEMPTS
        # ---------------------------------
        st.markdown(
            "### 📋 Quiz Attempts"
        )
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
        # ---------------------------------
        # PERFORMANCE BY SPORT
        # ---------------------------------
        st.markdown(
            "### 📊 Performance by Sport"
        )
        sport_performance = (
            df
            .groupby("Sport")["Percentage"]
            .mean()
            .sort_values(
                ascending=False
            )
        )
        st.bar_chart(
            sport_performance
        )
        st.markdown("---")
        if st.button(
            "🗑️ Clear Quiz History",
            type="secondary"
        ):
            clear_quiz_history()
            st.success(
                "Quiz history cleared successfully!"
            )
            st.rerun()
    else:
        st.info(
            "No quiz history available."
        )