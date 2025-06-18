# from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
import pandas as pd
import re

# ✅ Load .env variables
# load_dotenv()

# ✅ Get the API key from the environment
api_key = os.getenv("api_key")

# ✅ Configure the Gemini API
genai.configure(api_key=st.secrets["api_key"])
# genai.configure(api_key=api_key)

# ✅ Load Gemini model (example: gemini-1.5-flash)
model = genai.GenerativeModel("gemini-1.5-flash")


TERMS_MAP = {
    "Automotive": ["safety", "performance", "design", "comfort", "mileage"],
    # "Tech": ["battery", "performance", "display", "camera", "usability"],
    # "Fashion": ["style", "comfort", "fit", "price", "trend"]
}

def get_terms(category: str):
    return TERMS_MAP.get(category, [])

def build_single_prompt(brand: str, category: str, terms: list, prompt_df: pd.DataFrame) -> str:
    questions = []
    for _, row in prompt_df.iterrows():
        for term in terms:
            # Add a fallback in case template has unexpected keys
            try:
                q = row["Prompt Template"].format(brand=brand, category=category, attribute=term)
                questions.append(f"- {q}")
            except KeyError:
                continue

    prompt = f"""
    You are an expert brand analyst.
    
    Analyze the overall performance and market perception of the **brand {brand}** in the **{category}** category. Focus only on the brand level — not on any specific product, model, or variant.

    Consider the following key attributes:
    {chr(10).join(['- ' + t for t in terms])}

    For each attribute, evaluate it under these five analytical factors:

    1. Mention Frequency  
    2. Sentiment  
    3. Attribute Match  
    4. Placement Priority  
    5. Keyword/Source Influence  

    These are 100+ market research questions users typically ask:
    {chr(10).join(questions)}

    🎯 Provide a 1–10 score for each attribute under each factor.

    Format like this:
    
    Attribute: safety
    - Mention Frequency: 8
    - Sentiment: 9
    - Attribute Match: 7
    - Placement Priority: 6
    - Keyword/Source Influence: 7

    Attribute: mileage  
    ...
    """
    return prompt
    
    # Evaluate the brand **{brand}** in the **{category}** category for the following attributes:

def analyze_prompt(prompt: str) -> str:
    response = model.generate_content(prompt)
    print(response.text)
    return response.text  # ✅ Just return raw text

def parse_scores(response: str) -> pd.DataFrame:
    lines = response.splitlines()
    rows = []
    current_term = None

    for line in lines:
        line = line.strip()

        # Detect: "Attribute: safety"
        attr_match = re.match(r'Attribute\s*:\s*(\w+)', line, re.IGNORECASE)
        if attr_match:
            current_term = attr_match.group(1).lower()
            continue

        # Match: "- Sentiment: 8" or "* Sentiment: 8"
        score_match = re.match(r'[-*]?\s*([\w\s/]+)\s*[:：]\s*(\d+)', line)
        if score_match and current_term:
            factor = score_match.group(1).strip()
            score = int(score_match.group(2))
            rows.append({"term": current_term, "factor": factor, "score": score})

    return pd.DataFrame(rows)

def calculate_final_score(df: pd.DataFrame) -> float:
    total_score = df["score"].sum()
    max_score = df["term"].nunique() * df["factor"].nunique() * 10
    return round((total_score / max_score) * 100, 2)