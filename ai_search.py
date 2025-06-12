# ai_search.py
import streamlit as st
from openai import OpenAI

def ai_search_component():
    st.header("AI Search Assistant")
    question = st.text_input("Ask me anything")

    if st.button("Get Answer"):
        if not question:
            st.warning("Please enter a question.")
            return

        try:
            client = OpenAI(api_key=st.secrets["openai"]["api_key"])

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": question}
                ],
                temperature=0.7,
                max_tokens=200
            )

            answer = response.choices[0].message.content
            st.markdown(f"**Answer:** {answer}")

        except Exception as e:
            st.error(f"Error: {e}")
