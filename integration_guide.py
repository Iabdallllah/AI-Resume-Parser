"""
Integration Guide: Connecting CV Extraction Notebook to Streamlit Frontend

This file demonstrates how to integrate the CV extraction logic from ATS_CV.ipynb
with the Streamlit frontend (app.py).
"""

import streamlit as st
import pandas as pd
import json
from typing import Dict, Any
import torch
import gc
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
import pypdf
import re


# ============================================================================
# STEP 1: EXTRACT CV PROCESSING LOGIC FROM NOTEBOOK
# ============================================================================

class EducationInfo(BaseModel):
    degree: str = Field(description="Degree obtained")
    institution: str = Field(description="Institution name")
    year: int = Field(description="Year of graduation")


class ExperienceInfo(BaseModel):
    role: str = Field(description="Job role or title")
    company: str = Field(description="Company name")
    years: str = Field(description="Years worked")


class ResumeSchema(BaseModel):
    full_name: str = Field(description="Full name of the candidate")
    email: str = Field(description="Email address of the candidate")
    education: list[EducationInfo] = Field(description="List of education details")
    skills: list[str] = Field(description="List of skills")
    experience: list[ExperienceInfo] = Field(description="List of work experience details")


# ============================================================================
# STEP 2: MODEL INITIALIZATION (Call once at app startup)
# ============================================================================

@st.cache_resource
def load_model_and_tokenizer():
    """
    Load and cache the Mistral model to avoid reloading on every rerun.
    This is critical for Streamlit performance.
    """
    model_name = "mistralai/Mistral-7B-Instruct-v0.2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4"
    )
    
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=quantization_config,
        device_map="auto"
    )
    
    return model, tokenizer


# ============================================================================
# STEP 3: TEXT GENERATION FUNCTION
# ============================================================================

def generate_text(prompt: str, model, tokenizer, max_length: int = 2000,
                 num_return_sequences: int = 1) -> list[str]:
    """
    Generate text using the loaded model.
    
    Args:
        prompt: Input prompt for the model
        model: Loaded LLM model
        tokenizer: Model tokenizer
        max_length: Maximum length of generated text
        num_return_sequences: Number of sequences to generate
    
    Returns:
        List of generated text strings
    """
    torch.cuda.empty_cache()
    gc.collect()
    
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    input_length = inputs.input_ids.shape[1]
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=800,
            num_return_sequences=num_return_sequences,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=0.3,
            pad_token_id=tokenizer.eos_token_id
        )
    
    return [tokenizer.decode(output[input_length:], skip_special_tokens=True)
            for output in outputs]


# ============================================================================
# STEP 4: CV EXTRACTION FUNCTION
# ============================================================================

def extract_json_block(text: str) -> str:
    """
    Extract JSON content from model response.
    
    Tries multiple patterns:
    1. ```json...``` code blocks
    2. Fallback to raw JSON object
    """
    pattern = r'```json\s*(.*?)\s*```'
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        return matches[-1]
    
    pattern_fallback = r'\{.*\}'
    matches_fallback = re.findall(pattern_fallback, text, re.DOTALL)
    if matches_fallback:
        return matches_fallback[-1]
    
    return text


def process_resume_cv(pdf_file, model, tokenizer) -> Dict[str, Any]:
    """
    Process a resume PDF and extract structured information.
    
    Args:
        pdf_file: Uploaded PDF file object
        model: Loaded LLM model
        tokenizer: Model tokenizer
    
    Returns:
        Dictionary with extracted resume information
    """
    # Extract text from PDF
    user_input = ""
    reader = pypdf.PdfReader(pdf_file)
    for page in reader.pages:
        user_input += page.extract_text() + "\n\n"
    
    # Limit input size
    user_input = user_input[:4000]
    
    # Create output parser and format instructions
    output_parser = JsonOutputParser(pydantic_object=ResumeSchema)
    format_instructions = output_parser.get_format_instructions()
    
    # Create prompt
    cv_extraction_template = """
    You are an HR assistant that extracts candidate profiles from resume snippets.
    Extract the information and respond ONLY in valid JSON format.
    {format_instructions}
    
    Input:
    "{user_input}"
    """
    
    prompt = PromptTemplate(
        template=cv_extraction_template,
        input_variables=["user_input", "format_instructions"]
    ).format(user_input=user_input, format_instructions=format_instructions)
    
    # Generate response
    response = generate_text(prompt, model, tokenizer)[0]
    
    # Parse JSON
    json_text = extract_json_block(response)
    output_data = output_parser.parse(json_text)
    
    return output_data.dict()


# ============================================================================
# STEP 5: STREAMLIT UI INTEGRATION
# ============================================================================

def streamlit_cv_processing_page():
    """
    Example Streamlit page that uses the CV extraction functions.
    Integrate this into your main app.py
    """
    st.title("📄 CV Processing with AI Extraction")
    
    # Load model once
    if "model" not in st.session_state:
        with st.spinner("Loading AI model... (This happens only once)"):
            model, tokenizer = load_model_and_tokenizer()
            st.session_state.model = model
            st.session_state.tokenizer = tokenizer
    
    # File upload
    uploaded_file = st.file_uploader("Upload a resume PDF", type=["pdf"])
    
    if uploaded_file:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        with col2:
            if st.button("🚀 Extract Information"):
                with st.spinner("🔍 Processing resume with AI..."):
                    try:
                        # Process the resume
                        result = process_resume_cv(
                            uploaded_file,
                            st.session_state.model,
                            st.session_state.tokenizer
                        )
                        
                        st.session_state.extracted_data = result
                        st.success("✅ Resume processed successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Error processing resume: {str(e)}")
        
        # Display results
        if "extracted_data" in st.session_state:
            st.divider()
            st.markdown("### 📊 Extracted Information")
            
            data = st.session_state.extracted_data
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Personal Information")
                st.write(f"**Name:** {data.get('full_name', 'N/A')}")
                st.write(f"**Email:** {data.get('email', 'N/A')}")
            
            with col2:
                st.markdown("#### Skills")
                skills = data.get('skills', [])
                for skill in skills:
                    st.write(f"• {skill}")
            
            st.divider()
            
            # Education
            st.markdown("#### 🎓 Education")
            education = data.get('education', [])
            for edu in education:
                st.write(f"**{edu.get('degree')}** from {edu.get('institution')} ({edu.get('year')})")
            
            # Experience
            st.markdown("#### 💼 Experience")
            experience = data.get('experience', [])
            for exp in experience:
                st.write(f"**{exp.get('role')}** at {exp.get('company')} ({exp.get('years')})")
            
            # Export options
            st.divider()
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📋 Copy to Clipboard"):
                    st.info("📋 Copied! (Implement clipboard functionality)")
            
            with col2:
                json_str = json.dumps(data, indent=2)
                st.download_button(
                    label="📥 Download as JSON",
                    data=json_str,
                    file_name=f"{data.get('full_name', 'resume')}.json",
                    mime="application/json"
                )
            
            with col3:
                df = pd.DataFrame([data])
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"{data.get('full_name', 'resume')}.csv",
                    mime="text/csv"
                )


# ============================================================================
# STEP 6: PERFORMANCE OPTIMIZATION TIPS
# ============================================================================

"""
OPTIMIZATION CHECKLIST:

1. ✅ Use @st.cache_resource for model loading
   - Models are loaded only once and reused
   - Saves significant memory and startup time

2. ✅ Use @st.cache_data for function results
   - Cache expensive computations
   Example:
   @st.cache_data
   def expensive_function(input_data):
       return result

3. ✅ Use st.session_state to persist data
   - Avoid reprocessing on every rerun
   - Store extracted results for later use

4. ✅ Implement proper error handling
   - Use try-except blocks
   - Display user-friendly error messages

5. ✅ Monitor memory usage
   - Use torch.cuda.empty_cache() and gc.collect()
   - Monitor GPU/RAM with streamlit logs

6. ✅ Consider batch processing
   - Process multiple resumes efficiently
   - Implement progress bars for long operations

7. ✅ Add logging for debugging
   - Log model loading time
   - Log extraction errors for analysis
"""


# ============================================================================
# STEP 7: INTEGRATION CHECKLIST
# ============================================================================

"""
TO INTEGRATE WITH YOUR MAIN APP:

1. Replace mock process_resume() function in app.py with process_resume_cv()

2. In page_cv_processing(), modify the process button handler:
   ```python
   if process_button and uploaded_file:
       with st.spinner("🔍 Processing resume..."):
           if "model" not in st.session_state:
               model, tokenizer = load_model_and_tokenizer()
               st.session_state.model = model
               st.session_state.tokenizer = tokenizer
           
           results = process_resume_cv(
               uploaded_file,
               st.session_state.model,
               st.session_state.tokenizer
           )
   ```

3. Add this file to your project as: integration_guide.py

4. Test the full pipeline end-to-end

5. Deploy to production (Streamlit Cloud, Docker, etc.)
"""

if __name__ == "__main__":
    # For testing this integration
    streamlit_cv_processing_page()
