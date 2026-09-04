

import os
import re

import streamlit as st
from google import genai
from google.genai import types

from few_shot_examples import EXAMPLES

# Free-tier-eligible as of mid-2026. If Google retires this model name,
# swap it here — check https://ai.google.dev/gemini-api/docs/pricing for
# whichever Flash model currently shows "Free Tier".
MODEL_NAME = "gemini-3.5-flash"

SYSTEM_PROMPT = """You are a SQL generator for a SQLite analytics database.

Rules:
- Return ONLY a single valid SQLite SQL query. No explanation, no markdown
  fences, no commentary.
- Only use tables and columns that appear in the SCHEMA block below. Never
  invent a table or column name.
- Prefer explicit column lists over SELECT *.
- If the question cannot be answered with the given schema, return exactly:
  -- CANNOT_ANSWER: <one short reason>
"""


def _format_examples() -> str:
    lines = []
    for ex in EXAMPLES:
        lines.append(f"Q: {ex['question']}\nSQL: {ex['sql']}")
    return "\n\n".join(lines)


def _get_api_key() -> str | None:
    """Streamlit Community Cloud injects secrets via st.secrets; local dev
    reads GEMINI_API_KEY from .env via os.environ. Check both so the same
    code runs unmodified in both places."""
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY")


def build_prompt(schema_text: str, question: str, prior_error: str | None = None) -> str:
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"SCHEMA:\n{schema_text}\n\n"
        f"EXAMPLES:\n{_format_examples()}\n\n"
        f"QUESTION: {question}\n"
    )
    if prior_error:
        prompt += (
            f"\nNOTE: your previous SQL for this question failed with this "
            f"SQLite error, fix it:\n{prior_error}\n"
        )
    prompt += "\nSQL:"
    return prompt


def clean_sql(raw_text: str) -> str:
    """Strip markdown code fences and stray whitespace the model sometimes adds."""
    text = raw_text.strip()
    text = re.sub(r"^```(sql)?", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text).strip()
    return text


def generate_sql(schema_text: str, question: str, prior_error: str | None = None) -> str:
    api_key = _get_api_key()
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY not set. Copy .env.example to .env and add your key "
            "from https://aistudio.google.com/apikey"
        )

    client = genai.Client(api_key=api_key)
    prompt = build_prompt(schema_text, question, prior_error)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0),
    )
    return clean_sql(response.text)


def explain_result(question: str, sql: str, result_preview: str) -> str:
    """Given the original question, the SQL that answered it, and a preview
    of the result rows, ask the model for a short plain-English explanation
    a non-technical stakeholder could read — this is what turns raw query
    output into an actual answer."""
    api_key = _get_api_key()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set.")

    client = genai.Client(api_key=api_key)
    prompt = (
        "You are explaining a SQL query result to a business stakeholder "
        "who does not write SQL.\n\n"
        f"QUESTION ASKED: {question}\n\n"
        f"SQL USED:\n{sql}\n\n"
        f"RESULT (preview, may be truncated):\n{result_preview}\n\n"
        "In 2-4 plain-English sentences: answer the original question "
        "directly using the numbers in the result, and flag anything a "
        "stakeholder should notice (a standout number, a comparison, a "
        "caveat if the result looks incomplete or surprising). No SQL "
        "jargon, no restating the query."
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.3),
    )
    return response.text.strip()
