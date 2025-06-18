from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llm_utils import get_terms, build_single_prompt, analyze_prompt, parse_scores, calculate_final_score
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 👇 Allow frontend (Angular) to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class BrandRequest(BaseModel):
    brand1: str
    brand2: str
    category: str

def get_brand_score(brand: str, category: str, terms, prompt_df):
    prompt = build_single_prompt(brand, category, terms, prompt_df)
    raw_response = analyze_prompt(prompt)
    result_df = parse_scores(raw_response)
    
    attempts = 0
    max_retries = 3

    while result_df.empty and attempts < max_retries:
        raw_response = analyze_prompt(prompt)
        result_df = parse_scores(raw_response)
        attempts += 1
        print(brand + " - Retrying analysis... - " + str(attempts) + " of " + str(max_retries))

    if result_df.empty:
        raise HTTPException(status_code=500, detail=brand + " - Analysis failed")
    
    final_score = calculate_final_score(result_df)
    return final_score

@app.post("/analyze")
def analyze_brand(data: BrandRequest):
    print(data)
    prompt_df = pd.read_csv("prompts.csv")
    terms = get_terms(data.category)

    brand1_score = get_brand_score(brand=data.brand1, category=data.category, terms=terms, prompt_df=prompt_df)
    brand2_score = get_brand_score(brand=data.brand2, category=data.category, terms=terms, prompt_df=prompt_df)

    result = {
        "results": [
            {
                "brand": data.brand1,
                "details": {
                    "category": data.category,
                    "score": brand1_score,
                }
            },
            {
                "brand": data.brand2,
                "details": {
                    "category": data.category,
                    "score": brand2_score,
                }
            }
        ]
    }
    
    return result
    # result = {
    #     "brand": data.brand,
    #     "category": data.category,
    #     "score": final_score,
    #     "result": result_df.to_dict(orient="records")
    # }

    # print("result", result)
    # print("=======================================================================================>8")