# ATS CV Dashboard - Professional Streamlit Frontend

A production-ready, modular Streamlit frontend for an ATS (Applicant Tracking System) with CV processing capabilities. This application demonstrates best practices for building professional, modern web interfaces with Streamlit.

## Features

### Core Features
- **Professional UI/UX Design** - Modern, flat design with custom CSS styling
- **Responsive Layout** - Wide layout with proper spacing and visual hierarchy
- **Sidebar Navigation** - Clean navigation between application modules
- **Session State Management** - Robust state handling to prevent data loss
- **Modular Architecture** - Organized, reusable functions for maintainability

### Pages & Functionality

#### 1. **Dashboard** 
   - Key Performance Indicators (KPIs) with metrics cards
   - Recent upload history
   - Top matching candidates overview
   - System health status

#### 2. **CV Processing**
   - Single resume upload and processing
   - Job description matching
   - Batch resume processing
   - Real-time processing results with skill matching

#### 3. **Analytics**
   - Performance metrics overview
   - Detailed analysis with filters
   - Data export functionality (CSV, Excel, JSON)
   - Trend analysis placeholders

#### 4. **Settings**
   - User preferences configuration
   - Backend API integration setup
   - Database connection configuration
   - Security settings and session management

### Design Elements

- **Theme-Aware Styling** 
  - Unified dark theme with professional color palette
  - Respects Streamlit's native theming system
  - Smooth transitions and hover effects on interactive elements
  - Rounded corners and subtle shadows for depth
  - Minimal, non-intrusive custom CSS
  - Automatically adapts to system theme settings

- **Professional Components**
  - Styled metric cards with delta indicators
  - Tab-based organization for complex information
  - Alert messages with theme-appropriate colors
  - Loading spinners and progress indicators
  - Accessible text contrast ratios

- **Responsive Grid System**
  - Multi-column layouts for flexible content arrangement
  - Container-based organization
  - Proper spacing and visual separation
  - Works seamlessly across light and dark modes

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip or conda

### Step 1: Clone/Navigate to Project
```bash
cd /home/abdallah/Abdallah/Projects/ATS\ CV/
```

### Step 2: Create Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Project Structure

```
ATS CV/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── ATS_CV.ipynb             # Jupyter notebook for CV extraction logic
```

## Configuration

### Theme Configuration
The app is configured with a professional dark theme out of the box. Edit `.streamlit/config.toml` to customize:

```toml
[theme]
base = "dark"                          # Use "dark" or "light"
primaryColor = "#0066CC"               # Primary brand color
backgroundColor = "#0E1117"            # Main background
secondaryBackgroundColor = "#161B22"   # Secondary background
textColor = "#E6EDF3"                  # Text color
```

### Environment Variables (Optional)
Create a `.env` file for configuration:
```env
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
API_URL=http://localhost:8000
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### Customization

#### Change Page Title & Icon
Edit line 11 in `app.py`:
```python
st.set_page_config(
    page_title="Your App Title",
    page_icon="🎯",  # Change this
    ...
)
```

#### Modify Color Scheme
The app respects Streamlit's native theming system. To change colors:

1. Edit `.streamlit/config.toml` (recommended):
   ```toml
   [theme]
   primaryColor = "#YOUR_COLOR_HERE"
   backgroundColor = "#YOUR_BG_COLOR"
   secondaryBackgroundColor = "#YOUR_SECONDARY_COLOR"
   ```

2. Restart the app: `streamlit run app.py`

The custom CSS in `app.py` is minimal and theme-aware—it won't override these settings.

#### Add New Pages
1. Create a new function: `def page_your_page():`
2. Add to navigation options in `render_sidebar_navigation()`
3. Add routing in `main()` function

## 🔌 Backend Integration

### Connecting to FastAPI Backend
The app includes placeholder functions for backend integration:

```python
def fetch_dashboard_metrics() -> Dict[str, Any]:
    # Replace with actual API call
    response = requests.get(f"{API_URL}/metrics")
    return response.json()
```

Example FastAPI integration:
```python
import requests

API_URL = os.getenv("API_URL", "http://localhost:8000")

def fetch_data(endpoint: str):
    """Generic API call function"""
    try:
        response = requests.get(f"{API_URL}/{endpoint}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None
```

### Database Integration
For direct database connections, update the Settings page:
```python
import sqlalchemy as sa

def connect_database():
    """Connect to PostgreSQL database"""
    db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    engine = sa.create_engine(db_url)
    return engine
```

## Session State Management

The app uses Streamlit's `st.session_state` to maintain:
- Current page selection
- User inputs and form data
- Processing results
- Theme preferences
- Upload status

Example of accessing session state:
```python
st.session_state.current_page  # Current page
st.session_state.user_name     # User name
st.session_state.processing_results  # Last processing results
```

## Adding Charts & Visualizations

### Plotly Integration
```python
import plotly.express as px

def render_chart():
    df = pd.DataFrame({...})
    fig = px.histogram(df, x='match_score')
    st.plotly_chart(fig, use_container_width=True)
```

### Altair Integration
```python
import altair as alt

def render_chart():
    chart = alt.Chart(df).mark_bar().encode(x='column', y='value')
    st.altair_chart(chart, use_container_width=True)
```

Replace the placeholder comments in `page_analytics()` with actual chart implementations.

## Security Best Practices

1. **API Keys & Secrets**
   - Store in `.env` file (never commit)
   - Use `st.secrets` for production:
   ```python
   api_key = st.secrets["api_key"]
   ```

2. **Session Security**
   - Implement timeout in Settings page
   - Hash sensitive data before storage

3. **File Upload Safety**
   - Validate file types and sizes
   - Scan uploaded files for malware
   - Store in secure location

## 🚀 Deployment

### Streamlit Cloud (Recommended for Quick Deploy)
1. Push code to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect GitHub repo and deploy

### Docker Deployment
Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

Build and run:
```bash
docker build -t ats-cv-dashboard .
docker run -p 8501:8501 ats-cv-dashboard
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
streamlit run app.py --server.port 8502
```

### Module Not Found Errors
```bash
pip install --upgrade -r requirements.txt
```

### Cache Issues
```bash
streamlit cache clear
```

## 📝 Code Quality

The codebase follows:
- **PEP 8** style guide
- **Type hints** for function signatures
- **Docstrings** for all major functions
- **Modular design** with single responsibility principle
- **Comprehensive comments** for complex logic

## 🤝 Contributing

To extend the application:
1. Create new page functions following the pattern
2. Update navigation in `render_sidebar_navigation()`
3. Add routing in `main()`
4. Maintain consistent styling and modular structure

## 📚 Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [Streamlit API Reference](https://docs.streamlit.io/library/api-reference)
- [Pydantic Documentation](https://docs.pydantic.dev)
- [FastAPI Documentation](https://fastapi.tiangolo.com)

## 📄 License

This project is provided as-is for educational and commercial use.

## ✅ Checklist for Production

- [ ] Replace mock data functions with real API calls
- [ ] Implement proper error handling and logging
- [ ] Add user authentication
- [ ] Set up database connections
- [ ] Configure environment variables
- [ ] Test all file uploads
- [ ] Optimize performance
- [ ] Add user analytics
- [ ] Implement backup/recovery
- [ ] Set up monitoring and alerts
