import streamlit as st 
import pandas as pd
from llm_utils import get_terms, build_single_prompt, analyze_prompt, parse_scores, calculate_final_score
import re

st.markdown(
    "<h2 style='text-align: center'>Evertune: AI Brand Analyzer</h2>",
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns([1, 8, 1])  # Centered input box

def analysisOfSingleBrand(brand, category):
    st.subheader(f"**{brand}**")
    st.info(f"Started analysis for brand: **{brand}**")

    prompt_df = pd.read_csv("prompts.csv")
    terms = get_terms(category)
    prompt = build_single_prompt(brand, category, terms, prompt_df)

    raw_response = analyze_prompt(prompt)
    
    result_df = parse_scores(raw_response)
    st.dataframe(result_df, use_container_width=True)
    st.info(f"Analysis for brand: **{brand}** ended.")
    return result_df

def displayResult(brand, result_df):
    final_score = calculate_final_score(result_df)
    st.success(f"✅ Gemini Brand Visibility Score for {brand}: **{final_score}/100**")
    return final_score

with col2:
    brand = st.text_input("Brand", "Maruti Suzuki")
    brand2 = st.text_input("Brand2", "Tata Motors")
    category = st.selectbox("Category", ["Automotive"])

    if st.button("Analysis"):
        st.info("🔄 Generating analysis!")

        result_df = analysisOfSingleBrand(brand, category)
        result_df2 = analysisOfSingleBrand(brand2, category)

        if not result_df.empty and not result_df2.empty:
            final_score = displayResult(brand, result_df)
            final_score2 = displayResult(brand2, result_df2)

            # Prepare DataFrame for bar_chart with "Gemini" as legend
            score_df = pd.DataFrame({
                "Gemini": [final_score, final_score2]
            }, index=[brand, brand2])

            st.subheader("📊 Brand Visibility Chart")
            st.bar_chart(score_df)

            st.caption("Bar represents Gemini's visibility score for selected brands.")
        else:
            st.warning("⚠️ Try again, something went wrong!")
