# tell-em-what-they-want

# 🎯 Tell 'Em What They Want — Personalized Marketing Orchestrator

A production-ready, modular AI-powered marketing orchestration platform. It leverages LLMs, LangGraph, and real-time human-in-the-loop feedback to generate personalized ads, validate campaign objectives, and optimize multichannel strategies.

---

## 🧠 Overview

**"Tell 'Em What They Want"** is designed to automate and personalize digital marketing workflows using the power of:
- **LangGraph** orchestration
- **LLMs (OpenAI, Gemini, Claude)** for content generation
- **Flask/FastAPI** for API endpoints
- **Vertex AI** for media generation (e.g., video via Veo 3)
- **Real-time decision nodes** with human feedback routing
- **A/B testing, persona segmentation, ad channel strategy**

---

## 🔧 Features

- ✅ Campaign objective validation & refinement  
- ✅ Persona segmentation & enrichment  
- ✅ Budget classification & ad channel constraints  
- ✅ Multichannel ad generation (text/image/video)  
- ✅ AB testing & multivariant scoring  
- ✅ Human review feedback loop  
- ✅ LangGraph subgraph orchestration  
- ✅ Plug-and-play modular design  
- ✅ Render-ready deployment (Docker or non-Docker)  

---

## 🚀 Deployment (Render)

You can deploy this app on [Render](https://render.com) either **with or without Docker**.

### ➤ Without Docker

1. Push code to GitHub  
2. Create new **Python Web Service** on Render  
3. Use:  
   - **Build Command:** `pip install -r requirements.txt`  
   - **Start Command:** `python flask_app/app.py`  
4. Add your `.env` variables in the Render dashboard  

### ➤ With Docker

1. Use provided `Dockerfile` and optional `render.yaml`  
2. Create a **Docker Web Service** on Render  
3. Set up `.env` secrets either in Render UI or `render.yaml`  

---

## Project Structure
tell-em-what-they-want/
├── flask_app/
│ └── app.py # Entry point for the app (Flask)
│
├── workflows/ # LangGraph subgraphs and nodes
│ ├── graphs/campaign/
│ └── ...
│
├── core/ # Core engines: LLM, chain, recommendation, etc.
├── api/ # API layer (optional FastAPI support)
├── configs/ # Config loaders (.env, constants)
├── services/ # Campaign/user management, human feedback
├── models/ # Pydantic schemas for GraphState and payloads
├── data_preprocessing_pipeline/
│ └── ... # Preprocessing logic for user data
│
├── requirements.txt
├── render.yaml # Optional Render deployment config
├── Dockerfile # Container setup for Render Docker deployment
└── .env # Secrets and API keys (excluded from repo)


---

## 🧪 Run Locally

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the Flask app
python flask_app/app.py
