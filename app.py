import streamlit as st
import requests
from io import BytesIO
from PyPDF2 import PdfReader

# Title of the app
st.title("Parspec Doc Classifier")

local_pdf_path="temp.pdf"

import re

def text_clean(x):
    """
    Cleans text by applying light preprocessing steps:
    - Converts to lowercase
    - Removes unicode characters
    - Removes URLs
    - Removes contractions
    - Removes words with digits
    - Removes excess whitespace
    """
    try:
      x = x.lower()  # Convert to lowercase
      x = x.encode('ascii', 'ignore').decode()  # Remove non-ASCII characters
      x = re.sub(r'http[s]?://\S+', ' ', x)  # Remove URLs
      x = re.sub(r'www?\S+', ' ', x)  # Remove URLs
      x = re.sub(r"'\w+", '', x)  # Remove contractions (optional)
      # x = re.sub(r'\w*\d+\w*', '', x)  # Remove words with numbers
      x = re.sub(r'\s{2,}', ' ', x)  # Reduce multiple spaces to one
      x = re.sub(r'^\s+|\s+$', '', x)  # Trim leading/trailing spaces
      x = re.sub(r'\n|\r', ' ', x)  # Remove newlines
    except:
      print(x)
    return x

def extract_text_from_pdf(pdf_path=local_pdf_path):

    pdf_reader = PdfReader(pdf_path)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    
    cleaned_text = text_clean(text)
    return cleaned_text
    

@st.cache_resource()
def load_model():
    # Load model directly
    # Use a pipeline as a high-level helper
    from transformers import pipeline

    pipe = pipeline("text-classification", model="saurabhgssingh/bert-phishing-classifier_teacher",top_k=None, padding="max_length", truncation=True)
    return pipe

# Loading the model
pipe = load_model()

# Input for the URL of the PDF

pdf_url = st.text_input("Enter the URL of a PDF:", "")

if pdf_url:
    try:
        # Fetch the PDF from the URL
        response = requests.get(pdf_url)
        with open("temp.pdf",'wb+') as f:
            f.write(response.content)
        response.raise_for_status()  # Ensure we get a successful response
        pdf_data = BytesIO(response.content)
        
        # Display the PDF in the Streamlit app
        with st.expander("View PDF"):
            import base64
            from pathlib import Path
            pdf_path = Path("temp.pdf")
            base64_pdf = base64.b64encode(pdf_path.read_bytes()).decode("utf-8")
            pdf_display = f"""
                <iframe src="data:application/pdf;base64,{base64_pdf}" width="700px" height="2100px" type="application/pdf"></iframe>
            """
            st.markdown(pdf_display, unsafe_allow_html=True)

        # Display KPI

        
    except Exception as e:
        st.error(f"Error loading the PDF: {e}")
else:
    st.info("Enter a valid PDF URL above to load the document.")


calculate_button = st.button("Classify Document")
if calculate_button:
    text = extract_text_from_pdf()
    
    classification = pipe(text)[0]
    print(classification)
    # st.write("### KPI")
    max_label = max(classification, key=lambda x: x['score'])['label']
    st.metric(label="This PDf is of a:", value=max_label)  # Example KPI with static value
    st.subheader("Probabilities")
    probs = "\n".join([f"{x['label']}: {round(x['score'],3)}" for x in classification])
    st.text(probs)