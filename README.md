# 📰 Intelligent News Summarizer with RAG

> A production-ready Retrieval-Augmented Generation (RAG) system for real-time news analysis, summarization, and intelligent question answering.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Overview

This project implements a complete end-to-end RAG system that continuously ingests news from multiple sources, processes and indexes content using advanced NLP techniques, and provides intelligent question-answering capabilities with high-confidence responses (77-79% confidence scores achieved).

### ✨ Key Features

- **🔄 Real-time News Ingestion**: Automated data collection from NewsAPI and RSS feeds
- **🧠 Advanced Text Processing**: Language detection, smart chunking with semantic overlap
- **🔍 Vector Search**: FAISS-powered similarity search with 384-dimensional embeddings
- **💬 Intelligent Q&A**: RAG-based question answering about current events
- **📊 Analytics Dashboard**: Trending topics analysis and daily news briefings
- **⚡ Production-Ready**: FastAPI backend with monitoring and deployment configurations
- **🎨 Modern UI**: Interactive Streamlit interface with real-time updates

## 🏗️ Architecture

```
📁 News RAG System
├── 📥 Data Ingestion → NewsAPI + RSS feeds
├── 🔤 Text Processing → Cleaning + Chunking + Language Detection
├── 🧮 Embeddings → SentenceTransformers (all-MiniLM-L6-v2)
├── 🗃️ Vector Database → FAISS Index with Metadata
├── 🤖 RAG Generation → Context Retrieval + LLM Response
├── 🌐 API Layer → FastAPI with comprehensive endpoints
├── 🖥️ User Interface → Streamlit Dashboard
└── 📊 Monitoring → MLOps metrics and system health
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- 4GB+ RAM (for embeddings)
- NewsAPI key (optional, has fallback)

### Installation

1. **Clone the repository**
git clone https://github.com/yourusername/news-rag-system.git
cd news-rag-system

2. **Install dependencies**
pip install -r requirements.txt

3. **Set up environment variables** (optional)
echo "NEWSAPI_KEY=your_api_key_here" > .env
echo "OPENAI_API_KEY=your_openai_key_here" >> .env

4. **Initialize the system**
Run the complete pipeline
python main.py # Initial data ingestion
python test_text_processing.py # Process articles
python test_embeddings.py # Generate embeddings
python test_faiss.py # Build vector index
python test_rag_system.py # Test RAG system

### Running the Application

**Option 1: Development Mode**
Terminal 1: Start API server
python start_api.py

Terminal 2: Start Streamlit UI
streamlit run ui/streamlit_app.py

**Option 2: Production Mode**
python deploy/production_setup.py
python run_system.py

Access the application at:
- **API**: http://localhost:8000
- **UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

## 📚 Usage Examples

### API Endpoints
Health check
curl http://localhost:8000/

Ask a question
curl -X POST "http://localhost:8000/query"
-H "Content-Type: application/json"
-d '{"question": "What are the latest AI developments?"}'

Get trending topics
curl http://localhost:8000/trending

Generate daily briefing
curl http://localhost:8000/briefing

### Python Integration
from llm_integration.news_summarizer import IntelligentNewsSummarizer

Initialize summarizer
summarizer = IntelligentNewsSummarizer()

Ask questions about current news
response = summarizer.answer_news_question(
"What are the recent developments in artificial intelligence?"
)

print(f"Answer: {response.answer}")
print(f"Confidence: {response.confidence_score:.2%}")
print(f"Sources: {response.sources}")


## 🎯 System Performance

- **Response Time**: <500ms average for queries
- **Confidence Scores**: 77-79% on news analysis tasks
- **Data Processing**: 11 high-quality chunks from 15+ articles
- **Vector Search**: 384-dimensional embeddings with exact similarity search
- **Scalability**: Handles concurrent requests with FastAPI async support

## 📊 Project Structure
```
News_RAG_system/
├── 📁 api                        # FastAPI backend
├── 📁 config                     # Configuration management
├── 📁 data_ingestion             # News scraping and storage
├── 📁 embeddings                 # Vector generation
├── 📁 llm_integration            # RAG and LLM components
├── 📁 monitoring                 # MLOps monitoring
├── 📁 text_processing            # NLP pipeline
├── 📁 ui                         # Streamlit interface
├── 📁 vector_db                  # FAISS database
├── 📁 tests                      # Test scripts
├── 📁 deploy                     # Production deployment
└── 📄 requirements.txt           # Dependencies
```

## 🛠️ Technology Stack

**Backend & API**
- FastAPI - High-performance async web framework
- SQLite - Lightweight database for articles and metadata
- Uvicorn - ASGI server for production deployment

**AI & ML**
- SentenceTransformers - Text embeddings generation
- FAISS - Vector similarity search
- LangDetect - Language identification
- OpenAI API - LLM integration (optional)

**Frontend & Visualization**
- Streamlit - Interactive web interface
- Plotly - Data visualization and charts
- Pandas - Data manipulation and analysis

**Infrastructure & Monitoring**
- Gunicorn - Production WSGI server
- Psutil - System monitoring
- Logging - Comprehensive application logging

## 🔧 Configuration

Key configuration options in `config/settings.py`:
Data Sources
NEWSAPI_KEY = "your_api_key"
RSS_FEEDS = ["BBC", "CNN", "Reuters", "TechCrunch"]

Model Settings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 512
OVERLAP_SIZE = 50

Vector Database
FAISS_INDEX_TYPE = "IndexFlatL2"
SIMILARITY_THRESHOLD = 0.2

API Settings
API_HOST = "0.0.0.0"
API_PORT = 8000
MAX_REQUESTS = 1000


## 📈 Monitoring & MLOps

The system includes comprehensive monitoring:

- **System Health**: CPU, memory, disk usage tracking
- **Performance Metrics**: Response times, query success rates
- **Data Quality**: Freshness, processing rates, embedding coverage
- **Alerting**: Automated alerts for system issues
- **Backup**: Automated daily backups of data and models

Access monitoring dashboard: `http://localhost:8000/monitoring/health`

## 🧪 Testing

Run the complete test suite:
Unit tests
python -m pytest tests/

Integration tests
python test_connection.py # API connectivity
python test_rag_system.py # End-to-end RAG pipeline
python verify_data.py # Data validation


## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [SentenceTransformers](https://www.sbert.net/) for excellent embedding models
- [FAISS](https://github.com/facebookresearch/faiss) for efficient vector search
- [FastAPI](https://fastapi.tiangolo.com/) for the amazing web framework
- [Streamlit](https://streamlit.io/) for rapid UI development
- [NewsAPI](https://newsapi.org/) for reliable news data access

## 📊 Stats

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-777BB4?style=for-the-badge&logo=numpy&logoColor=white)

---

⭐ **Star this repository if you found it helpful!** ⭐

*Built with ❤️ for intelligent news analysis and AI-powered summarization.*
