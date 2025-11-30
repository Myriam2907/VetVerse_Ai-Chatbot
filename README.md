# 🐾 FREE VET Chatbot - Complete Setup Guide

## 100% Free, No API Costs, Runs Locally
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31.0-orange?style=flat-square&logo=streamlit)](https://streamlit.io/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.4.22-red?style=flat-square)](https://www.trychroma.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
---
## 💡 Features

🐶 Local AI-powered veterinary assistant

⚠️ Emergency detection with hybrid keyword & embedding similarity

📚 Retrieval-Augmented Generation (RAG) for accurate answers

🆓 Fully offline, no subscription or API required

🌐 Interactive Streamlit web interface with sources and disclaimers

## 🚀 Quick Start 

### Step 1: Install Ollama (Free Local LLM)

**macOS / Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from: https://ollama.com/download

**Start Ollama:**
```bash
ollama serve
```
(Keep this running in a separate terminal)

---

### Step 2: Download Free LLM Model

```bash
# Recommended: Fast and good quality (2GB)
ollama pull llama3.2:3b

# Alternative: Smallest model (1GB) - for limited RAM
ollama pull llama3.2:1b

# Alternative: Best quality (4GB) - if you have good specs
ollama pull mistral:7b
```

---

### Step 3: Install Python Dependencies

```bash
pip install langchain chromadb sentence-transformers streamlit ollama
```

**Or use requirements.txt:**

```txt
langchain==0.1.9
chromadb==0.4.22
sentence-transformers==2.3.1
streamlit==1.31.0
ollama==0.1.6
```

```bash
pip install -r requirements.txt
```

---

### Step 4: Project Structure

Create this folder structure:

```
vet-chatbot/
├── vet_chatbot_dataset.json  
├── evaluation_dataset.json  
├── free_rag_pipeline.py        
├── app.py         
├── evalutaion.py             
├── requirements.txt            
├── README.md                   
└── screenshots_demo               
```

---

### Step 5: Run the Chatbot

```bash
streamlit run app.py
```


Progress will show:
```
🚀 Initializing FREE VET Chatbot...
📚 Loading dataset...
✅ Loaded Q&A pairs
🔧 Loading embedding model...
✅ Embedding model ready
📝 Creating new vector database...
⚙️ Generating embeddings for all Q&As...
  Processed 50/X...
  Processed 100/X...
  ...
✅ Vector database populated!
✅ Chatbot ready!
```

---
## 💡 Usage Examples

![Q1](screenshots_demo/Q4.png)  
![Q2](screenshots_demo/Q1.png) 
![Q3](screenshots_demo/Q2.png) 
![Q4](screenshots_demo/Q3.png) 

## evaluation (add something here to be pro)

![Evaluation](screenshots_demo/eva.png) 

## Architecture Overview
The FREE VET Chatbot uses a Retrieval-Augmented Generation (RAG) approach powered by a local LLM. The workflow is:

![Architecture](screenshots_demo/archi.png) 

## ⚠️ Disclaimer

This tool provides general pet health information only.
It is not a substitute for professional veterinary advice. Always consult your veterinarian for:

🆘 Emergencies

💉 Diagnosis

🩺 Treatment plans

⚕️ Medical guidance




