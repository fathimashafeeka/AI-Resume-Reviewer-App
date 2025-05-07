import streamlit as st
import fitz  # PyMuPDF
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

# Function to extract text from uploaded PDF resume
def extract_text_from_pdf(uploaded_file):
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text

# Function to get LLM feedback via OpenRouter
def generate_feedback(resume_text, job_description):
    prompt = f"""
You are an expert resume reviewer.

Job Description:
{job_description}

Candidate Resume:
{resume_text}

Please provide:
1. A match score (out of 100)
2. Three key strengths of this resume
3. Three areas for improvement
"""

    headers = {
        "Authorization": f"Bearer {api_key}",  # Use the api_key here
        "HTTP-Referer": "https://localhost",  # Replace with your domain if deploying
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant for career guidance."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code} - {response.text}"

# Streamlit UI
st.set_page_config(page_title="AI Resume Reviewer", page_icon="🧠")
st.title("AI Resume Reviewer")
st.markdown("Upload your resume and paste a job description to get smart feedback.")

resume_file = st.file_uploader("Upload Resume (PDF only)", type=["pdf"])
job_description = st.text_area("Paste Job Description Here")

if st.button("Analyze") and resume_file and job_description:
    with st.spinner("Analyzing resume with Mistral..."):
        resume_text = extract_text_from_pdf(resume_file)
        feedback = generate_feedback(resume_text, job_description)
        st.success("✅ Analysis Complete!")
        st.markdown("### 📋 Feedback:")
        st.write(feedback)
