# Moroccan Legal AI Chatbot

AI-powered legal assistant for Moroccan law, featuring RAG (Retrieval Augmented Generation) with legal documents, bilingual support (French/Arabic), and a modern chat interface.

## Features

- **RAG-based Q&A**: Answers questions based on indexed legal PDF documents
- **Bilingual Support**: French and Arabic interfaces
- **Conversation Memory**: Maintains context across multiple questions
- **Source Citations**: Shows which documents were used for each answer
- **Modern UI**: ChatGPT-like interface with responsive design
- **Docker Deployment**: Ready for Azure VM deployment

## Architecture

```
your_ai_lawyer/
├── scraper/          # PDF scraper for adala.justice.gov.ma
├── backend/          # FastAPI backend with RAG engine
├── frontend/         # React frontend with chat UI
├── data/             # Legal PDF documents
├── chroma/           # Vector database
└── docker-compose.yml
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 8GB RAM (16GB recommended for Mistral 7B)
- 50GB+ free disk space

### Deployment Steps

1. **Clone and configure**
   ```bash
   cd your_ai_lawyer
   cp .env.example .env
   ```

2. **Build and start services**
   ```bash
   docker-compose up -d
   ```

3. **Wait for models to download** (first time only, ~5GB)
   ```bash
   docker-compose logs -f model-init
   ```

4. **Download legal documents**
   ```bash
   # Option A: Run the scraper
   docker-compose run backend python -m scraper.main --limit 10

   # Option B: Manually copy PDFs to data/legal_pdfs/
   ```

5. **Index documents**
   ```bash
   docker-compose exec backend python -m scripts.init_db
   ```

6. **Access the chatbot**
   - Open http://localhost in your browser
   - API docs: http://localhost:8000/docs

## Azure VM Deployment

### VM Requirements
- **Size**: Standard_D4s_v3 or higher (4 vCPUs, 16GB RAM)
- **Storage**: 128GB+ SSD
- **OS**: Ubuntu 22.04 LTS

### Setup Script
```bash
# Install Docker
sudo apt update && sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER
newgrp docker

# Clone repository
git clone <repo-url> /opt/moroccan-legal-ai
cd /opt/moroccan-legal-ai

# Configure
cp .env.example .env
nano .env  # Update CORS_ORIGINS with your domain

# Start services
docker-compose up -d

# Pull models (first time)
docker-compose logs -f model-init

# Index documents
docker-compose exec backend python -m scripts.init_db
```

### Security
- Configure Azure NSG to allow ports 80, 443
- Add HTTPS with Let's Encrypt (nginx-proxy or Traefik)
- Store secrets in Azure Key Vault

## Development

### Backend (Local)
```bash
cd backend
pip install -r requirements.txt

# Start Ollama locally
ollama serve
ollama pull mistral
ollama pull nomic-embed-text

# Run backend
uvicorn main:app --reload
```

### Frontend (Local)
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat/` | POST | Send a message |
| `/api/chat/sessions` | GET | List sessions |
| `/api/chat/session/{id}` | GET | Get session details |
| `/api/chat/session/{id}` | DELETE | Clear session |
| `/api/chat/stats` | GET | RAG statistics |
| `/api/documents/index` | POST | Start indexing |
| `/api/documents/stats` | GET | Database stats |
| `/health` | GET | Health check |

### Example Request
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Quels sont les droits fondamentaux dans la constitution?",
    "language": "fr"
  }'
```

## Configuration

Key environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://ollama:11434` | Ollama service URL |
| `LLM_MODEL` | `mistral` | LLM model name |
| `RETRIEVAL_K` | `5` | Documents per query |
| `CHUNK_SIZE` | `1200` | Text chunk size |

## Legal Document Categories

The scraper can download documents from [adala.justice.gov.ma](https://adala.justice.gov.ma/):

- **Constitutions**: الدساتير
- **Organic Laws**: القوانين التنظيمية
- **Laws**: القوانين
- **Decrees**: المراسيم
- **Circulars**: المناشير

## Tech Stack

- **Backend**: Python, FastAPI, LangChain, ChromaDB
- **Frontend**: React, TypeScript, Tailwind CSS
- **LLM**: Ollama + Mistral 7B
- **Embeddings**: nomic-embed-text
- **Deployment**: Docker, Docker Compose

## License

MIT License
