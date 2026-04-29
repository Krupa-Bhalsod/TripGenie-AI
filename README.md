# ✈️ TripGenie AI

> **An Agentic AI Travel Planner powered by Deep Multi-Agent Collaboration**  
Plan personalized trips using autonomous agents that collaborate on budgeting, itinerary generation, accommodations, and activities.

---

## 🌍 Overview

TripGenie AI is a full-stack **agentic travel planning platform** built using **FastAPI**, **Next.js**, **LangGraph Deep Agents**, **Groq**, and **MongoDB**.

Instead of relying on a single LLM prompt, TripGenie uses **specialized cooperating agents** orchestrated by a central planning agent to generate optimized travel itineraries under real-world constraints like:

- Budget
- Trip duration
- User preferences
- Location
- Activity interests

Example prompt:

```text
Plan a 3-day Goa trip under ₹10,000 focused on beaches, food, and nightlife.
```

TripGenie autonomously decomposes that into sub-problems, solves them via agents, and returns a structured itinerary.

---

# 🚀 Features

## 🤖 Deep Agent Architecture
- LangGraph-powered orchestrated agents
- Task decomposition and delegation
- Multi-agent collaboration
- Shared context + state passing

---

## 🧭 Specialized Travel Agents

### 1. Orchestrator Agent
Coordinates all agents and composes final itinerary.

### 2. Planner Agent
Generates day-by-day trip plans.

### 3. Budget Agent
Optimizes spending across:
- Stay
- Food
- Transportation
- Activities

### 4. Hotel Agent
Recommends accommodations based on:
- Budget
- Location
- Trip style

### 5. Activity Agent
Suggests:
- Attractions
- Food spots
- Experiences
- Hidden gems

---

## 🔎 Search-Augmented Planning
Uses Tavily for:
- Web search
- Destination research
- Activity discovery
- Travel recommendations

---

## 🧠 Memory + Retrieval (Optional RAG)
Supports:
- User preference memory
- Travel knowledge retrieval
- Vector search using FAISS

---

## 🔐 Authentication
- JWT login/register
- Protected trip history
- User-specific itineraries

---

# 🏗 Tech Stack

## Frontend
- Next.js
- TypeScript
- shadcn/ui
- Tailwind CSS

---

## Backend
- FastAPI
- LangChain
- LangGraph
- Groq
- Tavily Search

---

## Database
- MongoDB

---

## AI / Embeddings
- HuggingFace Sentence Transformers
- FAISS Vector Store

Embedding model:

```python
sentence-transformers/all-MiniLM-L6-v2
```

---

# 🧩 Architecture

```text
User
 ↓
Next.js Frontend
 ↓
FastAPI API Layer
 ↓
LangGraph Orchestrator Agent
 ├── Planner Agent
 ├── Budget Agent
 ├── Hotel Agent
 └── Activity Agent
 ↓
Tool Calls / Search / Retrieval
 ↓
MongoDB + FAISS
```

---

# 🔄 Agent Workflow

```text
User Request
↓
Orchestrator parses goal
↓
Subtasks delegated to agents
↓
Agents reason + call tools
↓
Outputs merged
↓
Final itinerary returned
```

---

# 📂 Project Structure

```bash
tripgenie-ai/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── agents/
│   │   ├── tools/
│   │   ├── db/
│   │   ├── auth/
│   │   └── core/
│   │
│   └── main.py
│
├── frontend/
│   ├── app/
│   ├── components/
│   └── lib/
│
└── README.md
```

---

# 📡 API Endpoints

## Auth
```http
POST /auth/register
POST /auth/login
GET  /auth/profile
```

## Trips
```http
POST /trip/plan
GET  /trip/history
GET  /trip/{id}
```

---

# 🗃 Database Schema

## users
```json
{
  "name": "",
  "email": "",
  "password_hash": ""
}
```

---

## trips
```json
{
  "user_id": "",
  "destination": "Goa",
  "budget": 10000,
  "days": 3,
  "itinerary": {}
}
```

---

## agent_logs (optional)
```json
{
  "agent_name": "",
  "input": {},
  "output": {},
  "timestamp": ""
}
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/tripgenie-ai.git
cd tripgenie-ai
```

---

## Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

---

## Environment Variables

Create `.env`

```env
GROQ_API_KEY=your_key
TAVILY_API_KEY=your_key
MONGODB_URI=your_uri
JWT_SECRET=your_secret
```

---

## Run Backend

```bash
python -m uvicorn app.main:app --reload
```

---

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

# 🧠 Example Output

```json
{
 "destination":"Goa",
 "budget":10000,
 "days":[
   {
     "day":1,
     "activities":[
       "Baga Beach",
       "Fort Aguada",
       "Local seafood dinner"
     ],
     "cost":2500
   }
 ]
}
```

---

# 🔍 Search + Recommendation Strategy

## Activities
Uses:
- Tavily Search
- LLM reasoning
- Destination context

---

## Hotels
Hybrid approach:
- Structured local dataset
- LLM ranking and reasoning

Avoids hallucinated hotel suggestions.

---

# 🛠 Future Roadmap
- Real-time hotel APIs
- Live pricing
- Flight integration
- Personalized memory agents
- Voice travel planner
- Booking assistant agents

---

# 🎯 Why This Project
TripGenie showcases:

- Multi-agent systems
- Tool-using AI agents
- Deep agent orchestration
- Retrieval augmented generation
- Full-stack AI product engineering

---

# 👨‍💻 Built With
- FastAPI
- LangGraph
- Groq
- MongoDB
- Next.js

---

## ⭐ If you like this project, consider starring the repo.