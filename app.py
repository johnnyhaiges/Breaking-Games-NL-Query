import os
import sqlite3

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from schema_utils import get_schema_text, list_tables
from llm_engine import generate_sql, explain_result

load_dotenv()

st.set_page_config(page_title="Breaking Games — Ask Your Data", layout="wide")
st.title("Breaking Games — Natural-Language Analytics")
st.caption(
    "Type a plain-English business question. It's translated to SQL against "
    "your Breaking Games database, grounded on the live schema so it doesn't "
    "invent tables or columns."
)

with st.sidebar:
    st.header("Database")
    db_path = st.text_input("Path to your .db file", value="../breaking_games.db")
    db_ready = os.path.exists(db_path)
    if db_ready:
        st.success(f"Connected — {len(list_tables(db_path))} tables found")
        with st.expander("View schema"):
            st.code(get_schema_text(db_path), language="text")
    else:
        st.error("File not found. Drop your .db file in this folder or fix the path above.")

    st.divider()
    explain_toggle = st.checkbox("Explain results in plain English", value=True)
    st.caption("Uses Gemini (google-genai). Set GEMINI_API_KEY in your .env file.")

question = st.text_input(
    "Ask a question",
    placeholder="e.g. Which marketing channel had the best ROI?",
    disabled=not db_ready,
)

if st.button("Run", disabled=not (db_ready and question)):
    schema_text = get_schema_text(db_path)

    with st.spinner("Generating SQL..."):
        try:
            sql = generate_sql(schema_text, question)
        except Exception as e:
            st.error(f"LLM call failed: {e}")
            st.stop()

    if sql.strip().upper().startswith("-- CANNOT_ANSWER"):
        st.warning(sql)
        st.stop()

    st.subheader("Generated SQL")
    st.code(sql, language="sql")

    def run_query(query: str) -> pd.DataFrame:
        conn = sqlite3.connect(db_path)
        try:
            return pd.read_sql_query(query, conn)
        finally:
            conn.close()

    try:
        result = run_query(sql)
    except Exception as first_error:
        # Self-correction: send the SQLite error back to the model once and
        # let it retry, instead of just failing. Worth mentioning in an
        # interview — it's what separates a toy demo from something that
        # handles the model being imperfect.
        st.info("First query failed — asking the model to fix it...")
        try:
            sql_retry = generate_sql(schema_text, question, prior_error=str(first_error))
            st.subheader("Corrected SQL")
            st.code(sql_retry, language="sql")
            result = run_query(sql_retry)
            sql = sql_retry
        except Exception as second_error:
            st.error(f"Query still failed after one retry: {second_error}")
            st.stop()

    st.subheader("Result")
    st.dataframe(result, use_container_width=True)
    st.caption(f"{len(result)} row(s)")

    if explain_toggle and not result.empty:
        with st.spinner("Explaining..."):
            try:
                preview = result.head(20).to_string(index=False)
                explanation = explain_result(question, sql, preview)
                st.subheader("What this means")
                st.write(explanation)
            except Exception as e:
                # Don't let a failed explanation hide the result table above —
                # the query already succeeded, this is just a bonus layer.
                st.caption(f"(Explanation unavailable: {e})")
