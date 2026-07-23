# ATS CV Dashboard - Streamlit Frontend

Live Demo: https://cv-parser.streamlit.app/

A modular Streamlit frontend for an ATS (Applicant Tracking System) with CV processing capabilities. The application provides a professional interface for resume analysis, job matching, analytics, and backend integration.

## Features

### Core Features

- Modern Streamlit-based UI with custom styling
- Responsive wide layout
- Sidebar navigation
- Session state management
- Modular and maintainable architecture

## Pages

### Dashboard

- KPI metrics overview
- Recent upload history
- Top candidate matches
- System status monitoring

### CV Processing

- Single CV upload and processing
- Job description matching
- Batch resume processing
- Skill matching results

### Analytics

- Performance metrics
- Filtering and analysis tools
- Data export support (CSV, Excel, JSON)
- Trend analysis support

### Settings

- User preferences
- Backend API configuration
- Database configuration
- Security settings

## Design

- Theme-aware interface
- Dark mode support
- Custom metric cards
- Tab-based layouts
- Responsive grid system
- Consistent spacing and styling

## Installation

### Requirements

- Python 3.8+
- pip or conda

### Setup

Clone or navigate to the project:

```bash
cd /home/abdallah/Abdallah/Projects/ATS\ CV/
```

Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run application:

```bash
streamlit run app.py
```

Application will be available at:

```text
http://localhost:8501
```

## Project Structure

```text
ATS CV/
├── app.py
├── requirements.txt
├── README.md
└── ATS_CV.ipynb
```

## Configuration

### Streamlit Theme

Create:

```text
.streamlit/config.toml
```

Example:

```toml
[theme]
base = "dark"
primaryColor = "#0066CC"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#161B22"
textColor = "#E6EDF3"
```

### Environment Variables

Create a `.env` file:

```env
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
API_URL=http://localhost:8000
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## Backend Integration

The frontend is designed to integrate with a FastAPI backend.

Example API request:

```python
import requests

API_URL = "http://localhost:8000"

def fetch_data(endpoint):
    response = requests.get(
        f"{API_URL}/{endpoint}",
        timeout=10
    )
    response.raise_for_status()
    return response.json()
```

## Database Integration

SQLAlchemy can be used for database connections:

```python
import sqlalchemy as sa

engine = sa.create_engine(
    "postgresql://user:password@host:port/database"
)
```

## Session Management

The application uses Streamlit session state to manage:

- Current page
- User inputs
- Processing results
- Upload status
- Application preferences

Example:

```python
st.session_state.current_page
st.session_state.processing_results
```

## Visualization

Supported libraries:

- Plotly
- Altair

Example:

```python
import plotly.express as px

fig = px.histogram(
    data,
    x="match_score"
)

st.plotly_chart(
    fig,
    use_container_width=True
)
```

## Security

- Store secrets in `.env` or `st.secrets`
- Validate uploaded files
- Restrict file size and type
- Secure API endpoints
- Avoid storing sensitive information in session state

## Deployment

### Docker

Build image:

```bash
docker build -t ats-cv-dashboard .
```

Run container:

```bash
docker run -p 8501:8501 ats-cv-dashboard
```

### Streamlit Cloud

1. Push the project to GitHub
2. Connect repository to Streamlit Cloud
3. Deploy application

## Development Guidelines

The project follows:

- PEP 8 style guidelines
- Type hints
- Modular architecture
- Clear separation of responsibilities
- Reusable components

## Future Improvements

- Connect real backend APIs
- Add authentication
- Add database persistence
- Improve monitoring and logging
- Add automated testing
- Optimize performance

## License

This project is provided for educational and commercial use.
