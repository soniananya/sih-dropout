# SIH Dropout Prediction & Policy-Aware RAG System

**Smart India Hackathon 2025 — AI/ML Track Finalist**

An end-to-end AI system that combines **machine learning, Natural Language to SQL, and Retrieval-Augmented Generation (RAG)** to predict student dropout risk and generate **policy-aware, structured recommendations**.

---

## 🔍 Problem Statement

Educational institutions struggle to **identify at-risk students early** and provide **context-aware interventions** aligned with institutional policies and protocols.

This system:
- Predicts dropout probability using ML
- Interprets student inputs using NL → SQL
- Ingests institutional policies
- Uses a **LangChain agent** to reason over data + documents
- Outputs **structured, actionable insights**

---

## ✨ Key Features

- 🧠 **ML-based Dropout Risk Prediction**
- 🗣️ **Natural Language to SQL** for querying student data
- 📚 **Policy & Protocol Ingestion** (Document AI)
- 🔎 **RAG Pipeline** for grounded, explainable responses
- 🤖 **LangChain Agent** for orchestration & reasoning
- 📦 **Structured JSON Output** (API-ready)
- ⚙️ REST APIs for integration

---

## 🧠 System Architecture

1. **Student data** ingested and processed
2. **ML model** computes dropout probability
3. **Natural language queries** converted to SQL
4. **Policies & protocols** ingested into RAG store
5. **LangChain agent** reasons over:
   - ML outputs  
   - SQL query results  
   - Retrieved policy context
6. System returns **structured decision output**

---

## 📤 Sample Output

```json
{
  "dropout_probability": 0.77,
  "risk_level": "High",
  "psychological_reasons": [
    "High stress and mental exhaustion",
    "Low engagement due to distractions",
    "Lack of career clarity",
    "Low self-efficacy in academics"
  ],
  "student_strengths": [
    "No major academic gaps indicated"
  ],
  "recommended_interventions": [
    "Immediate counselling for stress",
    "Time management support",
    "Career guidance sessions",
    "Academic mentoring"
  ]
}

PROJECT STRUCTURE:
sih-dropout/
├── api.py                   # Main FastAPI server
├── api_dropout.py           # Dropout prediction endpoints
├── dropout_model.py         # ML training & inference
├── rag.py                   # RAG pipeline (policy ingestion + retrieval)
├── n2sql.py                 # Natural Language → SQL conversion
├── db.py                    # Database connection & ORM
├── populate.py              # Database population scripts
├── dropout_analysis_result.json
├── requirements.txt
└── README.md
