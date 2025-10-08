# 🧠 SmartPrepAI

**An intelligent, SaaS-ready educational platform featuring a Retrieval-Augmented Generation (RAG) pipeline for truly personalized learning.**

> **🚀 Live Application**: [https://smartprepai-149283199537.us-central1.run.app](https://smartprepai-1492831dcb3d0bc00ef8bec3d2d175c824865fcb6.us-central1.run.app)
Live Application Might be down because of the expiration of Free Tier in Google Cloud

---

## 🌟 Project Overview

SmartPrepAI is a production-ready, AI-powered study platform that has evolved beyond simple question generation. It now implements a sophisticated **Retrieval-Augmented Generation (RAG)** pipeline, creating a deeply personalized and adaptive learning experience. The application is built with a modern, cloud-native architecture and includes SaaS-ready features like a one-time free trial for its premium capabilities.

### 🎯 Key Innovation: Personalized Prep with RAG
Unlike basic quiz generators, SmartPrepAI's core innovation is its **Personalized Prep** system:
- **Learns from Mistakes:** When a user fails to meet their personally set pass score, the application saves the questions they got wrong into a dedicated **vector database**.
- **Contextual Retrieval:** For a personalized session, it retrieves the user's specific past mistakes related to a topic.
- **Targeted Generation (RAG):** The AI uses the retrieved mistakes as context to generate a brand-new, targeted quiz designed to address the user's unique weak points.

---

## ✨ Features

- **Secure JWT Authentication:** Stateful, secure user registration and login using JSON Web Tokens.
- **Standard Quiz Generation:** Create unlimited quizzes on a wide range of technical subjects with varying difficulty levels.
- **Enhanced Analytics Dashboard:** An interactive dashboard with visualizations tracking performance over time and average scores by topic.
- **Custom Pass Score:** Users can set their own personal goal for what constitutes a "passing" score.
- **Performance Alerts:** A proactive alert system that analyzes a user's last 10 questions and suggests a focused quiz if it detects a drop in performance.
- **🚀 Personalized Prep (Premium RAG Feature):**
  - Automatically saves the context of incorrectly answered questions to a user-specific FAISS vector store.
  - Generates highly targeted review quizzes based on this stored context.
  - **SaaS-Ready:** Includes a **one-time free trial** for this premium feature, with logic to disable it after use, paving the way for a subscription model.

---

## 🏗️ Architecture & Technology Stack

### **Backend & AI**
- **Python 3.12** - Core application development
- **Streamlit** - Responsive web interface
- **LangChain** - Advanced LLM orchestration and RAG pipeline framework
- **Groq API** - High-speed LLM inference for question generation
- **Authentication:** **JWT (JSON Web Tokens)** for secure, stateless sessions
- **Database:**
    - **SQLite** - User authentication, session management, and SaaS feature tracking.
    - **FAISS Vector Store** - For storing and retrieving text embeddings of user mistakes.
- **Embeddings:** `sentence-transformers` for creating vector representations of text.

### **DevOps & Infrastructure**
- **Docker** - Containerized application deployment
- **Google Cloud Run** - Serverless production deployment with auto-scaling
- **Google Container Registry** - Docker image management

---

## 🛠️ Local Development Setup

### **Prerequisites**
- Python 3.11+
- Docker Desktop

### **Quick Start**
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/PixelPioneer1807/SmartPrepAI.git](https://github.com/PixelPioneer1807/SmartPrepAI.git)
    cd SmartPrepAI
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Create a `.env` file in the root directory and add your keys:
    ```
    GROQ_API_KEY="your_groq_api_key_here"
    JWT_SECRET_KEY="your_strong_secret_key_here"
    ```

4.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

---

## ☁️ Google Cloud Production Deployment

The application is designed for easy deployment on Google Cloud Run.

1.  **Configure Google Cloud:**
    ```bash
    gcloud config set project YOUR_PROJECT_ID
    gcloud services enable run.googleapis.com containerregistry.googleapis.com
    ```
2.  **Build and Push the Docker Image:**
    ```bash
    docker build -t gcr.io/YOUR_PROJECT_ID/smartprepai:latest .
    docker push gcr.io/YOUR_PROJECT_ID/smartprepai:latest
    ```
3.  **Deploy to Cloud Run:**
    ```bash
    gcloud run deploy smartprepai \
      --image gcr.io/YOUR_PROJECT_ID/smartprepai:latest \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated \
      --set-env-vars GROQ_API_KEY="your_api_key",JWT_SECRET_KEY="your_cloud_secret_key"
    ```

---

## 🚀 Future Enhancements

- [ ] **Stripe Integration:** Implement a payment gateway to convert the free trial into a full subscription.
- [ ] **Database Migration:** Upgrade from SQLite to PostgreSQL for better concurrency and scalability.
- [ ] **Advanced User Roles:** Introduce teacher/admin roles to create and assign quizzes to students.
- [ ] **Gamification:** Add points, badges, and leaderboards to increase user engagement.

---

## 👨‍💻 Author

**Shivam Kumar Srivastava**
- GitHub: [@PixelPioneer1807](https://github.com/PixelPioneer1807)

---

**⭐ If you found this project helpful, please consider giving it a star!**
