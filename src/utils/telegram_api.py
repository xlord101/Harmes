import os
import requests
from typing import List, Dict, Any, Optional
from src.agents.state import Issue

class TelegramClient:
    """Utility class to send daily issue notifications to a Telegram chat."""

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")

    def send_daily_digest(self, issues: List[Issue], limit: int = 3) -> Dict[str, Any]:
        """Format and send the top N daily issues to Telegram."""
        if not self.bot_token or not self.chat_id:
            print("[Info] Telegram Bot credentials not configured. Skipping Telegram notification.")
            return {"status": "skipped"}

        clean_token = self.bot_token.strip()
        if clean_token.lower().startswith("bot"):
            clean_token = clean_token[3:]
        clean_chat_id = self.chat_id.strip()

        top_issues = issues[:limit]
        if not top_issues:
            return {"status": "empty"}

        lines = [
            "📬 <b>Today's Top Good First Issues for CS Students</b>\n",
            "Here are fresh, beginner-friendly open-source issues to contribute to today:\n"
        ]

        for i, issue in enumerate(top_issues, 1):
            title = issue.title.replace("<", "&lt;").replace(">", "&gt;")
            url = issue.url
            repo = issue.repository or "GitHub"
            stack = ", ".join(issue.tech_stack) if issue.tech_stack else "General Tech"
            score = issue.score

            lines.append(f"<b>{i}. 📌 {title}</b>")
            lines.append(f"🏢 <b>Repo:</b> {repo}")
            lines.append(f"💻 <b>Tech Stack:</b> {stack} | <b>Score:</b> {score}/100")
            lines.append(f"🔗 <a href='{url}'>Tackle this issue on GitHub</a>\n")

        lines.append("💡 <i>Tip: Comment on the issue asking maintainers to assign it to you before writing code!</i>")
        message_text = "\n".join(lines)

        telegram_url = f"https://api.telegram.org/bot{clean_token}/sendMessage"
        payload = {
            "chat_id": clean_chat_id,
            "text": message_text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }

        try:
            response = requests.post(telegram_url, json=payload, timeout=10)
            if response.status_code == 200:
                print("Successfully sent daily issue digest to Telegram!")
                return {"status": "success"}
            else:
                print(f"Telegram API Error ({response.status_code}): {response.text}")
                print(f"[Debug Tip] Verify TELEGRAM_BOT_TOKEN in GitHub Secrets (e.g., 7123456789:AAFg...) and TELEGRAM_CHAT_ID.")
                return {"status": "error", "error": response.text}
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")
            return {"status": "exception", "error": str(e)}
