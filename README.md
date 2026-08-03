# 🚀 Hermes Agent: Open-Source Issue Evaluator & Weekly Digest Generator

**Hermes Agent** is a fully automated, AI-powered agentic pipeline designed to aggregate, score, and deliver high-quality open-source *"Good First Issues"* for developers and CS students. 

Built with **Python**, **LangGraph**, **MongoDB Atlas**, **PyGithub**, and **Telegram Bot API**, it automates daily issue discovery directly to your phone and generates curated weekly LinkedIn post digests ready for publishing.

---

## ✨ Features

- 🎯 **100-Point Scoring Matrix**: Evaluates GitHub issues based on Tech Stack Match (40%), Issue Clarity (30%), Setup Difficulty (20%), and Repository Activity (10%).
- 📱 **Daily Mobile Telegram Alerts**: Delivers today's Top 3 fresh open-source issues directly to your phone every morning.
- 💾 **MongoDB Atlas Persistence**: Automatically upserts and tracks evaluated issues with deduplication and publication status flags.
- 🧠 **Dual Intelligence Engine**: Powered by Google Gemini 2.0 / Pro with a built-in zero-latency rule-based heuristic fallback.
- 🔄 **Fresh Issue Discovery**: Queries GitHub issues sorted by creation date descending (`sort="created", direction="desc"`) to ensure you always get active, recent tasks.
- 📝 **Weekly LinkedIn Digest Generator**: Aggregates the top 5 highest-scoring issues of the week into a formatted, ready-to-publish LinkedIn post draft.
- ☁️ **Zero-Cost Automation**: Automated via GitHub Actions daily and weekly cron jobs.

---

## 🏗️ System Architecture

```
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

## 🛠️ Technology Stack

- **Core Framework**: Python 3.11, LangGraph, LangChain
- **Database**: MongoDB Atlas (PyMongo)
- **Scraper**: PyGithub & GitHub REST API
- **AI Models**: Google Gemini 2.0 / Pro (`langchain-google-genai`), OpenAI (`langchain-openai`)
- **Notifications**: Telegram Bot API
- **CI/CD**: GitHub Actions

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
│   │   ├── graph.py              # LangGraph pipeline construction
│   │   ├── nodes.py              # Scraper, Evaluator, Generator nodes
│   │   └── state.py              # Pydantic Issue model & TypedDict AgentState
│   ├── database/
│   │   └── mongo_client.py       # MongoDB Atlas client manager
│   └── utils/
│       ├── github_api.py         # GitHub API scraper client
│       └── telegram_api.py       # Telegram bot daily digest client
├── repos.json                    # Curated list of target GitHub repositories
├── requirements.txt              # Environment dependencies
├── .env.example                  # Environment variables template
└── main.py                       # CLI Entrypoint
```

---

## ⚙️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/xlord101/Harmes.git
   cd Harmes
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

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
