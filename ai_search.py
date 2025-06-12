import streamlit as st
import requests

def ai_search_component():
    st.header("AI Search Assistant")
    question = st.text_input("Ask me anything")

    if st.button("Get Answer"):
        if not question:
            st.warning("Please enter a question.")
            return

        with st.spinner("Thinking..."):
            try:
                API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"
                headers = {
                    "Authorization": f"Bearer {st.secrets['hf_api_key']}"
                }
                payload = {
                    "inputs": f"Question: {question} Answer:"
                }
                response = requests.post(API_URL, headers=headers, json=payload)
                response.raise_for_status()  # Raises an error for bad responses

                # Robust JSON handling
                if response.headers.get("Content-Type", "").startswith("application/json"):
                    result = response.json()
                else:
                    st.error(f"Received non-JSON response:\n{response.text}")
                    return

                # Handle the result
                if isinstance(result, list) and "generated_text" in result[0]:
                    st.markdown(f"**Answer:** {result[0]['generated_text']}")
                elif "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.error("Unexpected response format from Hugging Face.")

            except requests.exceptions.HTTPError as http_err:
                st.error(f"HTTP error: {http_err}\nRaw response: {response.text}")
            except Exception as e:
                st.error(f"Error: {e}")
