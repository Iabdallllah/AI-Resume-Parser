import os
import re
import pypdf
import streamlit as st
from typing import List
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq

st.set_page_config(
    page_title="AI Resume Parser",
    layout="wide",
    initial_sidebar_state="expanded"
)

custom_css = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    [data-testid="metric-container"] {
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
    }
    
    .stButton > button {
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
    }
    
    .stTabs {
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    hr {
        margin: 1.5rem 0;
        opacity: 0.3;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

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

@st.cache_resource(show_spinner=False)
def load_ai_model():
    groq_api_key = st.secrets["GROQ_API_KEY"]
    
    llm = ChatGroq(
        temperature=0.1, 
        model_name="mixtral-8x7b-32768",
        api_key=groq_api_key
    )
    return llm

def extract_text_from_pdf(uploaded_file) -> str:
    user_input = ""
    reader = pypdf.PdfReader(uploaded_file)
    for page in reader.pages:
        user_input += page.extract_text() + "\n\n"
    return user_input[:4000]

def extract_json_block(text: str) -> str:
    pattern = r'```json\s*(.*?)\s*
