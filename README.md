# 🧠 Chat AI + Data Visualization App

An interactive **Streamlit-based AI analytics app** that allows you to:
- 📂 Upload and view CSV files  
- 🧹 Clean your data interactively  
- 📊 Generate different types of charts  
- 💬 Ask questions in a chat window about your data or generated charts  

---

## 📁 Project Structure

```
.
├── app.py
├── components/
│   ├── chart_generator.py
│   ├── chat_window.py
│   ├── data_cleaner.py
│   └── data_loader.py
├── Pipfile
├── assets/
│   └── sample_data.csv
└── .streamlit/
    └── secrets.toml
```

---

## ⚙️ Setup Instructions

### 1️⃣ Create and Activate Environment

Use **Pipenv** to manage dependencies and virtual environments.

```bash
pip install pipenv
```

Create and activate the environment:

```bash
pipenv install
pipenv shell
```

---

### 2️⃣ Add Groq API Key

The app uses **Groq API** for the chat assistant.

1. Get your **Groq API key** from:  
   🔗 [https://console.groq.com](https://console.groq.com)

2. Create or edit the `.streamlit/secrets.toml` file and add:

```toml
[secrets]
GROQ_API_KEY = "your_groq_api_key_here"
```

> ⚠️ Make sure the `.streamlit/` folder is in your project root.

---

### 3️⃣ Run the App

After activating the environment:

```bash
streamlit run app.py
```

---

## 🧩 Components Overview

| File | Description |
|------|--------------|
| **app.py** | Main entry point integrating all components and handling the app layout and session state. |
| **components/data_loader.py** | Handles CSV upload, file validation, and encoding-safe reading. |
| **components/data_cleaner.py** | Provides data cleaning utilities (remove nulls, duplicates, renaming, etc.) and updates `st.session_state["cleaned_df"]`. |
| **components/chart_generator.py** | Enables users to select columns and generate interactive plots (bar, line, scatter, etc.). |
| **components/chat_window.py** | Hosts an AI-powered chat interface (Groq API) that can answer questions about your dataset or generated charts. |

---

## 🧠 Key Features

- ✅ **Upload CSV** — Upload and view dataset instantly  
- 🧹 **Clean Data** — Interactively clean and transform data  
- 📈 **Generate Charts** — Choose columns to visualize patterns  
- 💬 **Chat AI** — Ask queries over your data and charts  
- 🔁 **Session Persistence** — Retains cleaned data and chart selections in `st.session_state`

---

## 🧪 Sample Data

You can test the app using the **sample dataset**:

```
assets/sample_data.csv
```
