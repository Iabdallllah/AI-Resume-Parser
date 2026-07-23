import os
import re
import pypdf
import streamlit as st
from typing import List
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq

# ==========================================
# 1. API Configuration
# ==========================================
# ضع مفتاح Groq الخاص بك هنا (مؤقتاً للتجربة) أو استخدم st.secrets
os.environ["GROQ_API_KEY"] = "gsk_YOUR_API_KEY_HERE" 

# ==========================================
# 2. Page Configuration & UI Setup
# ==========================================
st.set_page_config(page_title="AI Resume Parser", layout="wide")

custom_css = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 3. Pydantic Schemas
# ==========================================
class EducationInfo(BaseModel):
    degree: str = Field(description="Degree obtained")
    institution: str = Field(description="Institution name")
    year: str = Field(description="Year of graduation")

class ExperienceInfo(BaseModel):
    role: str = Field(description="Job role or title")
    company: str = Field(description="Company name")
    years: str = Field(description="Years worked")

class ResumeSchema(BaseModel):
    full_name: str = Field(description="Full name of the candidate")
    email: str = Field(description="Email address of the candidate")
    education: List[EducationInfo] = Field(description="List of education details")
    skills: List[str] = Field(description="List of skills")
    experience: List[ExperienceInfo] = Field(description="List of work experience details")

# ==========================================
# 4. Core Functions
# ==========================================
@st.cache_resource
def load_ai_model():
    # استخدام Groq API بدل الموديل المحلي
    return ChatGroq(temperature=0.1, model_name="mixtral-8x7b-32768")

def extract_text_from_pdf(uploaded_file) -> str:
    user_input = ""
    reader = pypdf.PdfReader(uploaded_file)
    for page in reader.pages:
        user_input += page.extract_text() + "\n"
    return user_input[:4000]

def extract_json_block(text: str) -> str:
    pattern = r'```json\s*(.*?)\s*```'
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        return matches[-1]
    
    pattern_fallback = r'\{.*\}'
    matches_fallback = re.findall(pattern_fallback, text, re.DOTALL)
    if matches_fallback:
        return matches_fallback[-1]
    return text

def process_resume(text: str, llm):
    output_parser = JsonOutputParser(pydantic_object=ResumeSchema)
    format_instructions = output_parser.get_format_instructions()
    
    prompt = f"""You are a highly precise HR assistant. Extract the candidate's profile from the following resume text.
    Respond ONLY with a valid JSON object matching this schema:
    {format_instructions}
    
    Resume Text:
    {text}"""

    try:
        response = llm.invoke(prompt)
        json_text = extract_json_block(response.content)
        parsed_data = output_parser.parse(json_text)
        return parsed_data
    except Exception as e:
        st.error(f"Failed to parse data. Error: {e}")
        return None

# ==========================================
# 5. Frontend Dashboard Structure
# ==========================================
def main():
    st.title("⚡ Fast Smart Resume Parser (Powered by Groq)")
    uploaded_file = st.file_uploader("Upload Candidate Resume (PDF)", type=["pdf"])

    if uploaded_file is not None:
        if st.button("Process Resume", type="primary", use_container_width=True):
            with st.spinner("Analyzing document instantly..."):
                raw_text = extract_text_from_pdf(uploaded_file)
                llm = load_ai_model()
                parsed_data = process_resume(raw_text, llm)
                
                if parsed_data:
                    st.success("Resume processed successfully!")
                    st.json(parsed_data)

if __name__ == "__main__":
    main()
