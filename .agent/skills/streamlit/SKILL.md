# Streamlit Skill

## Overview
Streamlit is a Python framework for rapidly building and deploying interactive web applications for data science and machine learning. Create beautiful web apps with just Python - no frontend development experience required. Apps automatically update in real-time as code changes.

## When to Use This Skill
Activate when the user:
- Wants to build a web app, dashboard, or data visualization tool
- Mentions Streamlit explicitly
- Needs to create an ML/AI demo or prototype
- Wants to visualize data interactively
- Asks for a data exploration tool
- Needs interactive widgets (sliders, buttons, file uploads)
- Wants to share analysis results with stakeholders

## Installation and Setup
Check if Streamlit is installed:

```bash
python -c "import streamlit; print(streamlit.__version__)"
```

If not installed:

```bash
pip install streamlit
```

Create and run your first app:

```bash
# Create app.py with Streamlit code
streamlit run app.py
```

The app opens automatically in your browser at `http://localhost:8501`

## Basic App Structure
Every Streamlit app follows this simple pattern:

```python
import streamlit as st

# Set page configuration (must be first Streamlit command)
st.set_page_config(
    page_title="My App",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("My Data App")
st.write("Welcome to my interactive dashboard!")
```

## Core Capabilities

### 1. Displaying Text and Data
```python
import streamlit as st, pandas as pd
# Text elements
st.title("Main Title")
st.header("Section Header")
st.subheader("Subsection Header")
st.markdown("**Bold** and *italic* text")

# Display data
df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
st.dataframe(df)  # Interactive table
```

### 2. Interactive Widgets
```python
import streamlit as st
name = st.text_input("Enter your name")
age = st.number_input("Age", min_value=0, max_value=120, value=25)
option = st.selectbox("Choose one", ["Option 1", "Option 2"])
if st.button("Click me"):
    st.write("Button clicked!")
```

### 3. Layout and Containers
```python
import streamlit as st
col1, col2 = st.columns(2)
with col1:
    st.write("Column 1")
with col2:
    st.write("Column 2")

with st.expander("More details"):
    st.write("Hidden content")
```

### 4. Caching for Performance
```python
@st.cache_data
def load_data():
    return pd.read_csv('data.csv')
```

### 5. Session State
```python
if 'count' not in st.session_state:
    st.session_state.count = 0

if st.button("Increment"):
    st.session_state.count += 1
st.write(f"Count: {st.session_state.count}")
```
