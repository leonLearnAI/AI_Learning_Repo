# AI Architecture Recommender

A progressive, three-version system that recommends software architecture for AI applications based on project requirements — evolving from a simple CLI tool to an intelligent web-based Agent.

## The Problem

AI startups face a recurring challenge: choosing the right architecture for each project. With variables like scalability, budget, real-time needs, data sensitivity, and team expertise, the decision space is complex. This project automates that decision with a rule-based scoring engine, progressively enhanced with LLM-powered natural language understanding.

## Three Versions, One Evolution

### Version 1 — CLI Recommender (`n.py`)

The foundation. A terminal-based tool where users answer 9 structured questions. A rule-based scoring engine evaluates 5 architecture styles and returns a recommendation with justification.

**What it does:**
- Collects 9 project parameters via terminal prompts with input validation
- Scores 5 architecture styles (Monolithic, Layered, Microservices, Event-driven, Serverless)
- Recommends cloud service model (SaaS / PaaS / IaaS) and deployment model (Public / Private / Hybrid / Community)
- Generates a human-readable explanation

### Version 2 — Terminal Agent (`agent.py`)

Same scoring engine, but now wrapped in an LLM-powered agent. Users describe their project in plain English — the agent extracts parameters, calls the scoring tool, and generates a professional report.

**What changed:**
- OpenAI Function Calling replaces manual `input()` prompts
- LLM extracts structured parameters from unstructured natural language
- If information is missing, the agent asks follow-up questions
- The scoring functions become a "tool" the LLM can invoke

### Version 3 — Web Chat Agent (`server.py` + `index.html`)

The full experience. A browser-based chat interface powered by Flask, with the same agent logic running server-side. Users interact through a polished UI that feels like ChatGPT.

**What changed:**
- Flask backend serves the chat API and handles tool execution
- Frontend sends messages via fetch, renders Markdown responses
- API key stays secure on the server (never exposed to the browser)
- Conversation memory persists across messages within a session
- Example prompts help users get started quickly

## Architecture & Scoring Logic

The scoring engine evaluates 5 architecture styles based on 6 rule categories:

| Rule Category | Key Insight |
|---------------|-------------|
| System Size | Small → Monolithic; Large → Microservices |
| Scalability | High → Microservices, Event-driven, Serverless |
| Real-time | Yes → Event-driven (+4), Microservices (+2) |
| Budget | Low → Serverless, Monolithic; High → Microservices |
| AI Workload | NLP/Vision → Microservices; Prediction → Layered |
| Cloud Expertise | Low → Monolithic, Layered; High → Microservices |

Each rule adds points to relevant architectures. The highest-scoring style wins. Cloud service model and deployment model are then determined by priority-based if-else logic.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Scoring Engine | Python (rule-based, deterministic) |
| LLM Integration | OpenAI GPT-4o via Function Calling |
| Backend | Flask (Python) |
| Frontend | Vanilla HTML/CSS/JS, Marked.js for Markdown |
| Architecture | Client-Server, RESTful API |

## Project Structure

```
AI_architecture/
├── n.py              # V1: CLI recommender (scoring engine)
├── agent.py          # V2: Terminal-based LLM agent
├── server.py         # V3: Flask backend with tool calling
├── index.html        # V3: Chat frontend
└── README.md
```

## Getting Started

### Prerequisites

```bash
pip install openai flask
```

You will need an OpenAI API key. Get one at [platform.openai.com](https://platform.openai.com).

### Run Version 1 (CLI)

```bash
python n.py
```

### Run Version 2 (Terminal Agent)

1. Add your API key in `agent.py` (line 11)
2. Run:
```bash
python agent.py
```

### Run Version 3 (Web Chat)

1. Add your API key in `server.py` (line 17)
2. Start the server:
```bash
python server.py
```
3. Open `http://localhost:5000` in your browser

## Key Concepts Demonstrated

- **Rule-based AI**: Deterministic scoring with weighted rules — predictable, explainable, auditable
- **LLM Tool Use / Function Calling**: Letting an LLM decide when and how to invoke external functions
- **Agent Architecture**: LLM as the "brain" that understands intent, with deterministic tools for computation
- **Progressive Enhancement**: Same core logic, three levels of user experience
- **Separation of Concerns**: Scoring logic isolated in `n.py`, reused across all three versions
- **Client-Server Architecture**: Frontend/backend split with secure API key handling

## What I Learned

This project taught me how AI agents actually work under the hood — the LLM doesn't compute scores itself. It reads a tool description (a JSON schema), extracts structured parameters from natural language, requests a tool call, and then interprets the results to generate a human-friendly report. The deterministic scoring engine and the LLM each do what they're best at.

## License

This project was built as part of the Engineering and Evaluating AI Systems module at NCI (National College of Ireland), Semester 2, 2026 Spring.