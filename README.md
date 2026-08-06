# 🚀 Hermes Agent: Automated Open-Source Good First Issue Finder & LinkedIn Digest Bot

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_Workflow-FF6F00?style=flat-square)](https://github.com/langchain-ai/langgraph)
[![MongoDB Atlas](https://img.shields.io/badge/MongoDB-Atlas_Cloud-47A248?style=flat-square&logo=mongodb&logoColor=white)](https://cloud.mongodb.com)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automated_Cron-2088FF?style=flat-square&logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Hermes Agent** is an autonomous, AI-powered agentic workflow built with **Python**, **LangGraph**, **MongoDB Atlas**, **PyGithub**, and **Telegram Bot API**. 

It automatically discovers, scores, and delivers high-quality, fresh open-source **"Good First Issues"** directly to your phone via Telegram every morning, while generating curated weekly LinkedIn digests to build your developer portfolio.

---

## 🌟 Key Features & Capabilities

- 🎯 **100-Point Scoring Matrix**: Automatically ranks GitHub issues based on Tech Stack Match (40%), Issue Clarity (30%), Setup Accessibility (20%), and Maintainer Discussion Activity (10%).
- 📱 **Daily Telegram Mobile Alerts**: Receives today's Top 3 fresh open-source contribution opportunities directly on your phone every morning.
- 💾 **MongoDB Atlas NoSQL Storage**: Persists evaluated issues with atomic deduplication (`issue_id` upserts) and publication tracking.
- 🧠 **Dual Intelligence Architecture**: Uses Google Gemini 2.0 / OpenAI for AI scoring with a zero-latency 100-point heuristic rule fallback.
- 🔄 **Fresh Issue Search Engine**: Queries GitHub issues sorted by creation date descending (`sort="created", direction="desc"`) so you only receive active, recent tasks.
- 📝 **Weekly LinkedIn Post Generator**: Summarizes the Top 5 highest-scoring issues of the week into a formatted, ready-to-publish LinkedIn post draft.
- ☁️ **Serverless Automation**: Fully automated with zero server costs using GitHub Actions daily (`06:00 UTC`) and weekly (`12:00 UTC`) CRON schedules.

---

## 🏗️ System Architecture

```text
                       ┌───────────────────────────────┐
                       │   GitHub Actions (Daily Cron) │
                       └───────────────┬───────────────┘
                                       │
                                       ▼
                     ┌───────────────────────────────────┐
                     │     1. Scraper Node (PyGithub)    │
                     │  Fetches fresh Good First Issues  │
                     └─────────────────┬─────────────────┘
                                       │
                                       ▼
                     ┌───────────────────────────────────┐
                     │ 2. Evaluator Node (LLM/Heuristic) │
                     │  Scores issues on 1-100 Matrix    │
                     └─────────┬───────────────┬─────────┘
                               │               │
                               ▼               ▼
                ┌─────────────────────┐ ┌──────────────────────┐
                │ MongoDB Atlas Cloud │ │  Telegram Bot API    │
                │  Persists Scored DB │ │ Daily Top 3 Alerts   │
                └─────────────────────┘ └──────────────────────┘
                               │
                               ▼
                       ┌───────────────────────────────┐
                       │  GitHub Actions (Friday Cron) │
                       └───────────────┬───────────────┘
                                       │
                                       ▼
                     ┌───────────────────────────────────┐
                     │  3. Generator & Digest Node       │
                     │ Creates Weekly Top 5 LinkedIn Post│
                     └───────────────────────────────────┘
```

---

## 📊 100-Point Scoring Matrix Breakdown

| Criteria | Weight | Description |
| :--- | :---: | :--- |
| **Tech Stack Match** | **40%** | Exact keyword matching for `Python`, `React`, `FastAPI`, `Java`, `Spring Boot`, `TypeScript`, `Next.js`, `Tailwind`, `MySQL`. |
| **Issue Clarity** | **30%** | Text length $>300/600$ chars, structural indicators (`steps to reproduce`, `expected behavior`, code blocks). |
| **Setup Accessibility** | **20%** | Labels (`good first issue`, `easy`, `beginner friendly`) and setup keywords (`contributing`, `docker`, `setup`). |
| **Discussion Activity** | **10%** | Maintainer responsiveness and open comment count ($0 < \text{comments} \le 5$). |

---

## 🛠️ Technology Stack

- **Agentic Workflow Framework**: Python 3.11, LangGraph, LangChain
- **Cloud Database**: MongoDB Atlas (PyMongo SRV with TLS resilience)
- **Scraper & API**: PyGithub & GitHub REST API
- **AI Models**: Google Gemini 2.0 / Pro (`langchain-google-genai`), OpenAI (`langchain-openai`)
- **Notifications**: Telegram Bot API
- **CI/CD Cloud Engine**: GitHub Actions

---

## 📁 Repository Structure

```text
hermes-agent/
├── .github/
│   └── workflows/
│       ├── daily_scrape.yml      # Daily cron job (Runs at 06:00 UTC)
│       └── weekly_publish.yml    # Friday cron job (Runs at 12:00 UTC)
├── src/
│   ├── agents/
│   │   ├── graph.py              # LangGraph state machine execution graphs
│   │   ├── nodes.py              # Scraper, Evaluator, Generator nodes
│   │   └── state.py              # Pydantic Issue model & TypedDict AgentState
│   ├── database/
│   │   └── mongo_client.py       # MongoDB Atlas client manager with TLS resilience
│   └── utils/
│       ├── github_api.py         # GitHub API scraper client
│       └── telegram_api.py       # Telegram bot daily digest client
├── repos.json                    # Target repository configuration
├── requirements.txt              # Environment dependencies
├── .env.example                  # Environment variables template
└── main.py                       # CLI Runner Entrypoint
```

---

## ⚙️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/xlord101/open-source-contribution-agent.git
   cd open-source-contribution-agent
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and fill in your credentials:
   ```env
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/hermes_agent?retryWrites=true&w=majority
   GITHUB_TOKEN=your_github_token
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_CHAT_ID=your_telegram_chat_id
   GEMINI_API_KEY=your_gemini_api_key
   ```

---

## 🚀 Execution & Usage

### Running Locally

```bash
# Run full end-to-end pipeline
python main.py --full-pipeline

# Run daily scrape and score phase
python main.py --scrape-and-score

# Run weekly LinkedIn draft generation phase
python main.py --generate-and-publish
```

### GitHub Actions Automation

Configure the following secrets under **Settings ➔ Secrets and variables ➔ Actions**:
- `MONGODB_URI`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `GEMINI_API_KEY` (Optional)

Workflows will execute automatically on schedule:
- **Daily Scrape & Score**: Every day at `06:00 UTC`
- **Weekly Publish**: Every Friday at `12:00 UTC`

---

## ❓ Frequently Asked Questions (FAQ)

### What makes Hermes Agent different from standard issue bots?
Hermes Agent uses a **LangGraph state machine** to dynamically score and rank issues on a **100-Point Weighted Matrix** tailored specifically for developer portfolio building. It avoids stale issues by enforcing creation date descending sorting (`sort="created", direction="desc"`).

### How do I configure my own tech stack?
You can update target tech stacks and difficulty labels in `repos.json` or customize your environment variables.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
