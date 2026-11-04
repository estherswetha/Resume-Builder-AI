
import os
from dotenv import load_dotenv
from openai import OpenAI

from .prompts import build_resume_prompt


def generate_ai_resume(resume):

    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OpenAI API key is missing. Configure your .env file."
        )

    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        instructions=(
            "You are an expert resume writer. "
            "Be accurate, professional and never invent information."
        ),
        input=build_resume_prompt(resume)
    )

    return response.output_text
