import os
import json
from typing import Dict, Any, List
from src.agents.state import AgentState, Issue
from src.utils.github_api import GitHubClient
from src.database.mongo_client import MongoDBClient
from src.utils.linkedin_api import LinkedInClient

# Import LangChain LLM wrappers
from langchain_core.prompts import PromptTemplate

def get_llm():
    """Helper to initialize available LLM based on environment variables (Gemini, OpenAI, Anthropic)."""
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if gemini_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=gemini_key,
                temperature=0.2
            )
        except Exception as e:
            print(f"[Warning] Could not initialize ChatGoogleGenerativeAI: {e}")

    if os.getenv("OPENAI_API_KEY"):
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    elif os.getenv("ANTHROPIC_API_KEY"):
        try:
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(model="claude-3-haiku-20240307", temperature=0.2)
        except ImportError:
            pass
    return None


def _extract_tech_stack_heuristics(item: dict) -> List[str]:
    """Extract technology stack keywords from issue title/description."""
    text = (item.get("title", "") + " " + (item.get("description") or "")).lower()
    known = [
        ("React", "react"),
        ("Python", "python"),
        ("FastAPI", "fastapi"),
        ("Java", "java"),
        ("Spring Boot", "spring"),
        ("Tailwind CSS", "tailwind"),
        ("Vite", "vite"),
        ("MySQL", "mysql"),
        ("TypeScript", "typescript"),
        ("Node.js", "node"),
        ("Next.js", "next")
    ]
    found = [display_name for display_name, kw in known if kw in text]
    return found if found else ["General Tech"]


def _fallback_heuristic_score(item: dict) -> int:
    """Rule-based heuristic scoring matrix (1-100 scale)."""
    text = (item.get("title", "") + " " + (item.get("description") or "")).lower()
    labels = [l.lower() for l in item.get("labels", [])]

    tech_score = 0
    core_techs = ["react", "vite", "tailwind", "java", "spring", "fastapi", "mysql", "python", "typescript", "next", "node"]
    matched_techs = [tech for tech in core_techs if tech in text]
    if matched_techs:
        tech_score = min(40, len(matched_techs) * 15 + 10)

    clarity_score = 10
    desc_len = len(item.get("description") or "")
    if desc_len > 300:
        clarity_score += 10
    if desc_len > 600:
        clarity_score += 5

    setup_score = 5
    if any(l in labels for l in ["good first issue", "easy", "beginner", "help wanted"]):
        setup_score += 10

    activity_score = 5
    comments = item.get("comments_count", 0)
    if 0 < comments <= 5:
        activity_score += 5

    total_score = tech_score + clarity_score + setup_score + activity_score
    return min(100, max(1, total_score))


def _template_linkedin_post(issues: List[dict]) -> str:
    """Generate structured fallback LinkedIn post draft."""
    lines = [
        "🌟 Top Open-Source 'Good First Issues' for CS Students & Developers! 🌟\n",
        "Looking to build real-world experience and level up your GitHub profile? Here are curated, high-scoring issues ready for contributions:\n"
    ]
    for i, issue in enumerate(issues, 1):
        title = issue.get("title", "Issue")
        url = issue.get("url", "#")
        repo = issue.get("repository", "")
        stack_list = issue.get("tech_stack", ["General Tech"])
        stack = ", ".join(stack_list) if isinstance(stack_list, list) else str(stack_list)
        score = issue.get("evaluation_score", issue.get("score", "N/A"))

        lines.append(f"{i}. 📌 {title}")
        if repo:
            lines.append(f"   🏢 Repo: {repo}")
        lines.append(f"   💻 Tech Stack: {stack} | Score: {score}/100")
        lines.append(f"   🔗 Tackle this issue: {url}\n")

    lines.append("💡 Tip: Comment on the issue asking to be assigned before starting work!\n")
    lines.append("#OpenSource #GoodFirstIssue #SoftwareEngineering #CSStudents #GitHub #Coding #WebDev")
    return "\n".join(lines)


def scrape_github_issues(state: AgentState) -> dict:
    """Scrape raw issues from target GitHub repositories."""
    print("--- [Scraper Node] Fetching issues from GitHub ---")
    target_repos = state.get("target_repos", [])
    client = GitHubClient()
    raw_issues = client.fetch_good_first_issues(target_repos=target_repos, limit=15)
    print(f"Scraped {len(raw_issues)} raw issues.")
    return {"raw_issues": raw_issues}


def evaluate_and_score_issues(state: AgentState) -> dict:
    """Evaluate raw issues using LLM or rule-based scoring (1-100 scale)."""
    print("--- [Evaluator Node] Scoring issues ---")
    raw_issues = state.get("raw_issues", [])
    evaluated_issues: List[Issue] = []
    llm = get_llm()

    scoring_prompt = PromptTemplate(
        template="""You are an expert tech recruiter and open-source evaluator.
Evaluate the following GitHub issue for beginner/contributor suitability.

Scoring Criteria (Total 100 points):
1. Tech Stack Match (40 pts): Strict alignment with core technologies (e.g. React, Vite, Tailwind CSS, Java, Spring Boot, FastAPI, MySQL, Python, Node.js).
2. Issue Clarity (30 pts): Presence of clear description, reproducible steps, clear acceptance criteria.
3. Setup Difficulty (20 pts): Simple environment setup and clear contributing guidelines.
4. Repository Activity (10 pts): Active maintainers and active issue thread.

Issue Details:
Title: {title}
Repository: {repository}
Labels: {labels}
Description: {description}

Return your response strictly as JSON with this schema:
{{
  "score": <int 1 to 100>,
  "reasoning": "<string>"
}}
""",
        input_variables=["title", "repository", "labels", "description"]
    )

    for item in raw_issues:
        score = 50

        if llm:
            try:
                formatted_prompt = scoring_prompt.format(
                    title=item.get("title", ""),
                    repository=item.get("repository", ""),
                    labels=", ".join(item.get("labels", [])),
                    description=(item.get("description", "") or "")[:1000]
                )
                res = llm.invoke(formatted_prompt)
                content = res.content if hasattr(res, "content") else str(res)
                clean_json = content.strip().strip("```json").strip("```")
                data = json.loads(clean_json)
                score = int(data.get("score", 50))
            except Exception as e:
                print(f"LLM scoring fallback for issue {item.get('id')}: {e}")
                score = _fallback_heuristic_score(item)
        else:
            score = _fallback_heuristic_score(item)

        issue_obj = Issue(
            id=str(item.get("id")),
            title=item.get("title", ""),
            url=item.get("url", ""),
            description=(item.get("description") or "")[:500],
            repository=item.get("repository", ""),
            labels=item.get("labels", []),
            tech_stack=_extract_tech_stack_heuristics(item),
            score=score,
            is_published=False
        )
        evaluated_issues.append(issue_obj)

    evaluated_issues.sort(key=lambda x: x.score, reverse=True)
    print(f"Evaluated {len(evaluated_issues)} issues.")

    # Save to MongoDB
    db_client = MongoDBClient()
    db_client.insert_or_update_issues(evaluated_issues)

    # Send daily top 3 issues digest to Telegram
    try:
        from src.utils.telegram_api import TelegramClient
        telegram = TelegramClient()
        telegram.send_daily_digest(evaluated_issues, limit=3)
    except Exception as e:
        print(f"[Warning] Could not send Telegram notification: {e}")

    return {"evaluated_issues": evaluated_issues}


def generate_linkedin_post(state: AgentState) -> dict:
    """Generate structured LinkedIn post draft for the top evaluated issues."""
    print("--- [Generator Node] Generating LinkedIn post draft ---")
    db_client = MongoDBClient()
    top_issues_docs = db_client.get_top_unpublished_issues(limit=5)

    if not top_issues_docs:
        eval_issues = state.get("evaluated_issues", [])
        top_issues_docs = [issue.model_dump() for issue in eval_issues[:5]]

    if not top_issues_docs:
        draft = "🚀 Weekly Good First Issues Digest: No new issues available this week! Stay tuned!"
        return {"post_draft": draft}

    llm = get_llm()

    if llm:
        prompt_text = f"""You are a professional tech career coach and LinkedIn content creator.
Draft a highly engaging, structured LinkedIn post highlighting the top 5 GitHub 'Good First Issues' for software developers looking to contribute to open source.

Issues Data:
{json.dumps(top_issues_docs, indent=2, default=str)}

Guidelines:
- Include an eye-catching hook intro.
- List each of the issues with title, score, and link URL.
- Add relevant call to action and hashtags (#OpenSource #GoodFirstIssue #SoftwareEngineering #Python #React).
- Keep formatting clean with emojis and line breaks suitable for LinkedIn.
"""
        try:
            res = llm.invoke(prompt_text)
            draft = res.content if hasattr(res, "content") else str(res)
        except Exception as e:
            print(f"LLM draft generation error: {e}")
            draft = _template_linkedin_post(top_issues_docs)
    else:
        draft = _template_linkedin_post(top_issues_docs)

    print("Draft generated successfully.")
    return {"post_draft": draft}
