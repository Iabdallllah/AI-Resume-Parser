import os
import re
import pypdf
import streamlit as st
from typing import List
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq

# ==========================================
# 1. Page Configuration & UI Setup
# ==========================================
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

# ==========================================
# 2. Pydantic Schemas
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
# 3. Model Loading (Groq API)
# ==========================================
@st.cache_resource(show_spinner=False)
def load_ai_model():
    groq_api_key = st.secrets["GROQ_API_KEY"]
    
    llm = ChatGroq(
        temperature=0.1, 
        model_name="llama-3.3-70b-versatile",  # الموديل المحدث والمدعوم حالياً
        api_key=groq_api_key
    )
    return llm

# ==========================================
# 4. Core Functions
# ==========================================
def extract_text_from_pdf(uploaded_file) -> str:
    user_input = ""
    reader = pypdf.PdfReader(uploaded_file)
    for page in reader.pages:
        user_input += page.extract_text() + "\n\n"
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
    
    Do not add any explanations or conversational text before or after the JSON.
    
    Resume Text:
    {text}"""

    try:
        response = llm.invoke(prompt)
        json_text = extract_json_block(response.content)
        parsed_data = output_parser.parse(json_text)
        return parsed_data
    except Exception as e:
        st.error(f"Failed to parse the extracted data. Error: {e}")
        return None

# ==========================================
# 5. Frontend Dashboard Structure
# ==========================================
def main():
    with st.sidebar:
        st.title("System Status")
        with st.status("Initializing AI Engine...", expanded=True) as status:
            st.write("Connecting to Groq API (Mixtral 8x7B)...")
            llm = load_ai_model()
            status.update(label="AI Engine Ready ⚡", state="complete", expanded=False)
        
        st.divider()
        st.info("Upload a PDF resume to extract structured data instantly using Groq.")

    st.title("⚡ Smart Resume Parser (Powered by Groq)")
    st.markdown("Extract structured data from candidate CVs with lightning speed.")

    uploaded_file = st.file_uploader("Upload Candidate Resume (PDF)", type=["pdf"])

    if uploaded_file is not None:
        if st.button("Process Resume", type="primary", use_container_width=True):
            with st.spinner("Analyzing document structure instantly..."):
                raw_text = extract_text_from_pdf(uploaded_file)
                llm = load_ai_model()
                parsed_data = process_resume(raw_text, llm)
                
                if parsed_data:
                    st.success("Resume processed successfully in record time!")
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.subheader("Candidate Profile")
                        st.metric(label="Full Name", value=parsed_data.get("full_name", "N/A"))
                        st.metric(label="Email", value=parsed_data.get("email", "N/A"))
                        
                    with col2:
                        st.subheader("Detailed Analysis")
                        tab1, tab2, tab3, tab4 = st.tabs(["Experience", "Skills", "Education", "Raw Data"])
                        
                        with tab1:
                            for exp in parsed_data.get("experience", []):
                                st.markdown(f"**{exp.get('role', 'N/A')}** at *{exp.get('company', 'N/A')}*")
                                st.caption(f"Duration: {exp.get('years', 'N/A')}")
                                st.divider()
                                
                        with tab2:
                            skills = parsed_data.get("skills", [])
                            st.write(", ".join([f"`{skill}`" for skill in skills]))
                            
                        with tab3:
                            for edu in parsed_data.get("education", []):
                                st.markdown(f"**{edu.get('degree', 'N/A')}**")
                                st.write(f"Institution: {edu.get('institution', 'N/A')} | Year: {edu.get('year', 'N/A')}")
                                st.divider()
                                
                        with tab4:
                            st.json(parsed_data)

if __name__ == "__main__":
    main()
