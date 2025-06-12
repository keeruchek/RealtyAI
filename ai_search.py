import streamlit as st
import requests
import os

# Get Hugging Face API key securely
HF_TOKEN = st.secrets.get("HF_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

def query_flant5(question):
    response = requests.post(API_URL, headers=headers, json={"inputs": question})
    try:
        result = response.json()
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]
        elif "error" in result:
            return f"Error: {result['error']}"
        else:
            return "Unexpected response format."
    except Exception as e:
        return f"Error parsing response: {e}"

def ai_search_component():
    st.header("AI Search Assistant")
    question = st.text_input("Ask me anything")

    if st.button("Get Answer"):
        if not question:
            st.warning("Please enter a question.")
            return

        with st.spinner("Thinking..."):
            answer = query_flant5(question)
            st.markdown(f"**Answer:** {answer}")
