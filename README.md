# Breaking Games — Natural-Language Analytics Interface

Type a plain-English business question, get SQL run against your Breaking
Games database, get the answer back — no SQL required. This is a
retrieval-augmented text-to-SQL tool: the LLM is grounded on your database's
*live* schema (read fresh at request time, not hardcoded), plus a few
worked examples, so it stays honest about what tables/columns actually
exist instead of hallucinating them.

## Demo

![demo](demo.gif)

*(The database used in the demo above is real analytics data from a
SQL/Analytics externship and isn't included in this repo — see "About the
data" below. Bring your own SQLite file to try the tool yourself.)*

## About the data

This repo is code-only. The database it was built and demoed against
contains real business data (ad spend, sales, checkout records) from a
company externship and is kept private for confidentiality — it's not
committed here, and the `.gitignore` keeps any `.db` file out of this
repo going forward. The schema-introspection design means the tool works
against **any** SQLite database — point it at your own to try it out.

## 1. Set up the environment

```bash
cd bg-rag
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Get a free Gemini API key

1. Go to https://aistudio.google.com/apikey and sign in with a Google account.
2. Create an API key (no credit card needed for the free tier).
3. Copy `.env.example` to `.env` and paste your key in:

```bash
cp .env.example .env
# then edit .env: GEMINI_API_KEY=your_actual_key
```

## 3. Add your database

Copy your `breaking_games_p2.db` (or whichever db you're using) into this
folder. If it's named something else or lives elsewhere, you can point to
it directly in the app's sidebar once it's running — you don't have to
rename anything.

## 4. Check your few-shot examples

Open `few_shot_examples.py`. It has 4 example question→SQL pairs using
column names based on what's documented from the externship (`payment_method`,
`product_title`, `category`, `spend`, `campaign_name`). Before you demo:

1. Run the app (step 5 below).
2. Open the **"View schema"** expander in the sidebar — it shows your real
   table/column names, pulled live from the db.
3. Fix any mismatches in `few_shot_examples.py`.

This step matters more than it looks like: the schema block grounds *what
exists*, but the examples teach the model *the style and the specific
names you actually use* — wrong examples quietly drag accuracy down even
though the app won't error out.

## 5. Run it

```bash
streamlit run app.py
```

It opens in your browser. Try questions like:
- "Which marketing channel had the best ROI?"
- "What's the average cart value for checkouts that reached payment?"
- "Show me the top 5 products by revenue."

## How it works (for your interview answer)

1. **Schema retrieval** (`schema_utils.py`) — reads table/column names and
   a couple of sample rows straight from the SQLite file via
   `sqlite_master` and `PRAGMA table_info`, every time you ask a question.
   This is the "retrieval" in retrieval-augmented — the model never works
   from a stale or guessed schema.
2. **Prompt construction + generation** (`llm_engine.py`) — combines the
   live schema, a few worked examples, and your question into one prompt,
   sends it to Gemini, strips markdown fences from the response.
3. **Execution + self-correction** (`app.py`) — runs the returned SQL
   against your db with `pandas.read_sql_query`. If it errors (bad column
   name, syntax issue), the error is sent back to the model once for a
   fix-up retry before giving up. That retry loop is what makes it more
   than a toy — it's handling the fact that the model is imperfect rather
   than just trusting its first output.

## Pushing to GitHub

```bash
git init
echo "venv/
.env
*.db" > .gitignore
git add .
git commit -m "Natural-language analytics interface for Breaking Games data"
git remote add origin https://github.com/johnnyhaiges/<your-repo-name>.git
git push -u origin main
```

`.gitignore` excludes your `.env` (API key) and the `.db` file (your
externship data) from the public repo — keep both local.

## Stretch (optional, if you have time)

Semantic product search with `sentence-transformers` + FAISS, so you can
also add "Vector Search / Embeddings" to your skills line. Not required —
the text-to-SQL pipeline above is already the core deliverable.
