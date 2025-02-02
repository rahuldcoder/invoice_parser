import streamlit as st
import google.generativeai as genai
import base64
import json 
import pandas as pd
import streamlit as st


api_key = st.secrets["google"]["api_key"]

# Configure Gemini API
# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "application/json",
}

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash",generation_config=generation_config)

# Streamlit app title
st.title("INVOICE EXTRACTOR")

# File uploader
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

# Function to process PDF with Gemini LLM
def process_pdf_with_gemini(pdf_data):
    doc_data = base64.standard_b64encode(pdf_data).decode("utf-8")
    prompt = "Extract line items from this invoice document"
    
    try:
        response = model.generate_content([
            {'mime_type': 'application/pdf', 'data': doc_data},
            prompt
        ])
        return response.text
    except Exception as e:
        st.error(f"Error processing PDF with Gemini: {e}")
        return None

# Function to flatten nested JSON
def flatten_json(y, parent_key='', sep='_'):
    items = []
    for k, v in y.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_json(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(flatten_json(item, f"{new_key}{sep}{i}", sep=sep).items())
                else:
                    items.append((f"{new_key}{sep}{i}", item))
        else:
            items.append((new_key, v))
    return dict(items)

# Function to display pretty JSON with collapsible sections
def display_pretty_json(data, parent_key=''):
    if isinstance(data, dict):
        # Create a list of keys to allow collapsing
        keys = list(data.keys())
        for key in keys:
            # Use selectbox for expanding sections
            with st.expander(f"{parent_key + '.' if parent_key else ''}{key}", expanded=True):
                display_pretty_json(data[key], parent_key=f"{parent_key}.{key}" if parent_key else key)
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            with st.expander(f"{parent_key}[{idx}]", expanded=True):
                display_pretty_json(item, parent_key=f"{parent_key}[{idx}]")
    else:
        st.write(data)  # Directly display the value if it's not a dict or list

# Main execution
if uploaded_file is not None:
    pdf_data = uploaded_file.read()

    if st.button("Extract Text"):
        with st.spinner("Processing PDF with Google's Gemini LLM..."):
            processed_text = process_pdf_with_gemini(pdf_data)

            if processed_text:
                

                # Attempt to parse and display JSON in tabular format
                try:
                    json_data = json.loads(processed_text)

                    st.subheader("Extracted Invoice")
                    st.json(json_data)

                    if isinstance(json_data, list):
                        flattened_data = [flatten_json(item) for item in json_data]
                        df = pd.DataFrame(flattened_data)
                    else:
                        flattened_data = flatten_json(json_data)
                        df = pd.DataFrame([flattened_data])

                    # Convert all columns to string to avoid type conversion errors
                    df = df.astype(str)

                    st.subheader("Extracted Data in Table Format")
                    st.dataframe(df)
                except json.JSONDecodeError:
                    st.warning("The extracted text is not a valid JSON format.")
            else:
                st.warning("Failed to extract text with Gemini.")