import streamlit as st 
import pandas as pd
from llm_utils import get_terms, build_single_prompt, analyze_prompt, parse_scores, calculate_final_score
import re
import plotly.graph_objects as go

st.markdown(
    "<h2 style='text-align: center'>Evertune: AI Brand Analyzer</h2>",
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns([1, 8, 1])  # Centered input box

def analysisOfSingleBrand(brand, category, max_retries=2):
    st.subheader(f"**{brand}**")
    st.info(f"Started analysis for brand: **{brand}**")

    prompt_df = pd.read_csv("prompts.csv")
    terms = get_terms(category)
    prompt = build_single_prompt(brand, category, terms, prompt_df)

    # raw_response = analyze_prompt(prompt)
    
    # result_df = parse_scores(raw_response)
    # st.dataframe(result_df, use_container_width=True)
    # st.info(f"Analysis for brand: **{brand}** ended.")
    # return result_df

    result_df = pd.DataFrame()
    attempts = 0

    while result_df.empty and attempts < max_retries:
        raw_response = analyze_prompt(prompt)
        result_df = parse_scores(raw_response)
        attempts += 1

    if result_df.empty:
        st.error(f"❌ Analysis failed for {brand} after {max_retries} attempts.")
    else:
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

            # Static scores for comparison
            chatgpt_scores = [78, 80]
            meta_ai_scores = [74, 77]
            claude_ai_scores = [69, 75]
            deep_seek_scores = [70, 72]

            # Prepare DataFrame for bar_chart with "Gemini" as legend
            # score_df = pd.DataFrame({
            #     "Gemini": [final_score, final_score2]
            # }, index=[brand, brand2])

            # st.subheader("📊 Brand Visibility Chart")
            # st.bar_chart(score_df)

            # Prepare DataFrame
            score_df = pd.DataFrame({
                "Brand": [brand, brand2],
                "Gemini": [final_score, final_score2]
            })

            st.subheader("📊 Brand Visibility Chart")

            # Create a Plotly bar chart
            fig = go.Figure(data=[
                go.Bar(
                    x=score_df["Brand"],
                    y=score_df["Gemini"],
                    name="Gemini",
                    marker_color="royalblue",
                    text=score_df["Gemini"],
                    textposition='auto'
                )
            ])

            # Add static model values for comparison
            fig.add_trace(go.Bar(name='ChatGPT', x=score_df["Brand"], y=chatgpt_scores, marker_color='orange'))
            fig.add_trace(go.Bar(name='Meta.ai', x=score_df["Brand"], y=meta_ai_scores, marker_color='lightblue'))
            fig.add_trace(go.Bar(name='Claude.ai', x=score_df["Brand"], y=claude_ai_scores, marker_color='skyblue'))
            fig.add_trace(go.Bar(name='Deep Seek', x=score_df["Brand"], y=deep_seek_scores, marker_color='purple'))

            # fig.update_layout(
            #     yaxis=dict(range=[0, 100], title="Score (0-100)"),
            #     xaxis=dict(title="Brand"),
            #     legend_title="Model",
            #     plot_bgcolor='rgba(0,0,0,0)',
            #     paper_bgcolor='rgba(0,0,0,0)',
            #     height=400
            # )

            # Layout customization
            fig.update_layout(
                barmode='group',
                yaxis=dict(range=[0, 100], title="Score (0-100)"),
                xaxis=dict(title="Brand"),
                legend_title="LLM Model",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=500,
                title='Brand Visibility Comparison by LLMs'
            )

            st.plotly_chart(fig, use_container_width=True)

            st.caption("Bar represents Gemini's visibility score for selected brands.")
        else:
            st.warning("⚠️ Try again, something went wrong!")
