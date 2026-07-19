from openai import OpenAI
from google import genai
from groq import Groq

from src.config import (
    OPENAI_API_KEY,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GROQ_API_KEY,
    LLM_PROVIDER
)


# =================================
# OPENAI
# =================================

def generate_with_openai(prompt):

    client = OpenAI(
        api_key=OPENAI_API_KEY
    )

    response = client.chat.completions.create(

        model="gpt-4o-mini",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]

    )

    return response.choices[0].message.content


# =================================
# GEMINI
# =================================

def generate_with_gemini(prompt):

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    response = client.models.generate_content(

        model=GEMINI_MODEL,

        contents=prompt

    )

    return response.text


# =================================
# GROQ
# =================================

def generate_with_groq(prompt):

    client = Groq(
        api_key=GROQ_API_KEY
    )

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]

    )

    return response.choices[0].message.content


# =================================
# MAIN LLM FUNCTION
# =================================

def generate(prompt,provider=None):

    selected_provider = (
        provider
        or LLM_PROVIDER
    )


    providers = [

        selected_provider,

        "groq",

        "gemini",

        "openai"

    ]


    # Remove duplicates
    providers = list(
        dict.fromkeys(providers)
    )


    errors = []


    for provider in providers:

        try:

            print(
                f"🤖 Trying {provider.upper()}..."
            )


            if provider == "openai":

                if not OPENAI_API_KEY:

                    raise ValueError(
                        "OPENAI_API_KEY is missing"
                    )


                return generate_with_openai(
                    prompt
                )


            elif provider == "gemini":

                if not GEMINI_API_KEY:

                    raise ValueError(
                        "GEMINI_API_KEY is missing"
                    )


                return generate_with_gemini(
                    prompt
                )


            elif provider == "groq":

                if not GROQ_API_KEY:

                    raise ValueError(
                        "GROQ_API_KEY is missing"
                    )


                return generate_with_groq(
                    prompt
                )


            else:

                raise ValueError(
                    f"Unknown provider: {provider}"
                )


        except Exception as error:

            print(
                f"❌ {provider.upper()} failed:"
            )

            print(
                error
            )

            errors.append(
                f"{provider}: {error}"
            )


    raise RuntimeError(
        "All LLM providers failed:\n"
        + "\n".join(errors)
    )