# GitHub Scraper - AI-Powered Code Extraction & Microservices Generation

## 🚀 Project Overview
GitHub Scraper is an AI-driven system that discovers, fetches, and processes public repository code from GitHub. It uses a **generalized GitHub scraper** and an **AI-powered agent** to extract code and transform it into **Pydantic-based input/output specifications and microservices**. The extracted models and services can be dynamically loaded, making this an ideal solution for **automated API generation** and **microservices architecture**.

## ✨ Features
- 🔍 **Automated GitHub Repository Scraping** - Extracts code from public repositories.
- 🧠 **AI-Powered Code Parsing** - Converts raw code into structured Pydantic models.
- ⚡ **Dynamic Microservice Generation** - Auto-generates APIs based on extracted code.
- 🔑 **Secure API Authentication** - Uses API key authentication to restrict access.
- 📊 **Optimized Caching & Performance** - Implements async optimizations and in-memory caching.
- 🛡 **Rate Limiting & Security** - Prevents abuse with built-in rate limiting.
- 📄 **Detailed API Documentation** - Auto-generated Swagger documentation for easy exploration.
- ✅ **Automated Testing Suite** - Ensures reliability with unit and integration tests.

## 🏗 Project Structure
```
📂 Github Scraper
 ├── 📂 models               # Auto-generated Pydantic models
 ├── 📂 microservices        # Dynamically created microservices
 ├── 📂 tests                # Unit & integration tests
 ├── 📄 main.py              # FastAPI application entry point
 ├── 📄 requirements.txt      # Python dependencies
 ├── 📄 Dockerfile            # Docker containerization setup
 ├── 📄 README.md             # Project documentation
 ├── 📄 .env                  # Environment variables (API keys, etc.)
```

## 🔧 Setup & Installation
### 1️⃣ Prerequisites
- **Python 3.11+**
- **pip** (Python package manager)
- **Redis** (For caching, optional but recommended)
- **Docker** (Optional for containerization)

### 2️⃣ Clone the Repository
```sh
https://github.com/Keensight-GPT-Applications-2/GitHub-AI-App---Scraper-and-Agent
cd github-scraper
```

### 3️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

### 4️⃣ Set Up Environment Variables
Create a **.env** file in the project root with:
```
API_KEY=your_secure_api_key
```

### 5️⃣ Run the FastAPI Server
```sh
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 6️⃣ Access API Documentation
Once the server is running, open your browser and visit:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Redoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 🔐 API Authentication
All API endpoints are secured using API key authentication.
Include the API key in your request headers:
```
X-API-KEY: your_secure_api_key
```

## 🛠 API Endpoints
### ✅ Root Endpoint
```http
GET /
```
**Response:**
```json
{
  "message": "Welcome to the Pydantic Microservice!"
}
```

### ✅ List Available Models
```http
GET /models
```
**Response:**
```json
{
  "models": ["Model1", "Model2", "Model3"]
}
```

### ✅ Fetch a Specific Model Schema
```http
GET /models/{model_name}
```
**Response:**
```json
{
  "title": "Model1",
  "type": "object",
  "properties": { ... }
}
```

## 🧪 Running Tests
Run all test cases using:
```sh
pytest tests/
```

## 🚀 Docker Deployment (Optional)
### 1️⃣ Build the Docker Image
```sh
docker build -t github_scraper .
```

### 2️⃣ Run the Docker Container
```sh
docker run -d -p 8000:8000 --name github_scraper_container github_scraper
```

### 3️⃣ Verify the Running Container
```sh
docker ps
```

## 📌 Future Improvements
- 🔗 **GitHub Webhooks Integration** for real-time repository tracking.
- 📡 **Enhanced AI Model** to improve code parsing accuracy.
- 🌍 **Multi-Language Support** for extracting and analyzing code in multiple languages.
- ☁ **Cloud Deployment** with Kubernetes for scalable deployments.
