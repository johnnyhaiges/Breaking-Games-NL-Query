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
git clone https://github.com/johnnyhaiges/Breaking-Games-NL-Query.git
cd Breaking-Games-NL-Query
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

## 3. Point it at a database

Enter the path to any SQLite `.db` file in the app's sidebar once it's
running (step 5 below) — there's no bundled sample dataset, since the one
this was built and demoed against is private (see "About the data" above).

## 4. Check your few-shot examples

`few_shot_examples.py` ships with 4 example question→SQL pairs written
against the specific database this was built for (tables like
`fact_product_performance`, `dim_product`, `shopify_checkouts`,
`meta_campaigns`). If you point this at your own database:

1. Run the app (step 5 below).
2. Open the **"View schema"** expander in the sidebar — it shows your real
   table/column names, pulled live from the db.
3. Rewrite the examples in `few_shot_examples.py` to match.

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


