# Superstore Sales Analysis Dashboard

An interactive data visualization dashboard built with Streamlit to analyze Superstore sales data, providing insights into category performance, temporal trends, and geographic distributions.

## Tools Used

- **Python**: Core programming language.
- **Streamlit**: Web framework for building data applications.
- **Altair**: Declarative statistical visualization library used for the interactive charts.
- **Pandas**: Data manipulation and analysis library for processing the CSV data.

## Features

- **Basic Analysis**: Filterable overview of sales by category.
- **Interactive Bar & Scatter**: Relationship between price and quantity with category filtering.
- **Temporal Analysis**: Line charts and histograms with time-period selection (brushing).
- **Geographic Insights**: US Map interaction to drill down into state-level sales data.

## Setup Instructions

### Prerequisites

- Python 3.12 or higher.

### 1. Clone the Repository
```bash
git clone <repository-url>
cd dv_lab1
```

### 2. Set Up Virtual Environment
If you don't have one already, create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
Install the required Python packages:
```bash
pip install streamlit pandas altair
```

### 4. Run the Application
Start the Streamlit server:
```bash
streamlit run app.py
```
The application will be available at `http://localhost:8501`.
