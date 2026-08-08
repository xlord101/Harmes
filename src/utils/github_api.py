import os
import requests
from typing import List, Dict, Any, Optional

try:
    from github import Github, Auth
    PYGITHUB_AVAILABLE = True
except ImportError:
    PYGITHUB_AVAILABLE = False


class GitHubClient:
    """Utility class to scrape issues and repository data from GitHub API."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self._github = None
        if PYGITHUB_AVAILABLE and self.token:
            auth = Auth.Token(self.token)
            self._github = Github(auth=auth)

    def fetch_good_first_issues(
        self,
        target_repos: Optional[List[str]] = None,
        limit: int = 25,
        difficulty_levels: Optional[List[str]] = None,
        global_search_first: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Fetch recent beginner-friendly issues based on difficulty labels.
        Can fetch from specific/all target repositories, global GitHub search, or both.
        Sorted by creation date descending.
        """
        issues_data = []
        seen_ids = set()

        labels = [l.lower() for l in difficulty_levels] if difficulty_levels else [
            "good first issue", "good-first-issue", "help wanted", "easy", "beginner", "starter", "first-timers-only"
        ]

        if global_search_first:
            print(f"[Info] Running primary global GitHub search for labels: {labels[:3]}...")
            global_issues = self._search_issues_global(limit=limit, labels=labels)
            for issue in global_issues:
                if issue["id"] not in seen_ids:
                    seen_ids.add(issue["id"])
                    issues_data.append(issue)

        if target_repos and len(issues_data) < limit:
            limit_per_repo = max(2, min(10, (limit - len(issues_data)) // max(1, len(target_repos)) + 1))
            for repo_name in target_repos:
                if len(issues_data) >= limit:
                    break
                try:
                    repo_issues = self._fetch_issues_for_repo(
                        repo_name, limit_per_repo=limit_per_repo, difficulty_levels=labels
                    )
                    for issue in repo_issues:
                        if issue["id"] not in seen_ids:
                            seen_ids.add(issue["id"])
                            issues_data.append(issue)
                except Exception as e:
                    print(f"Error fetching issues for repo {repo_name}: {e}")

        # If we still haven't met the limit, run global search to backfill
        if len(issues_data) < limit and not global_search_first:
            needed = limit - len(issues_data)
            print(f"[Info] Scraped {len(issues_data)} issues from repos. Backfilling from global search...")
            global_issues = self._search_issues_global(limit=needed * 2, labels=labels)
            for issue in global_issues:
                if len(issues_data) >= limit:
                    break
                if issue["id"] not in seen_ids:
                    seen_ids.add(issue["id"])
                    issues_data.append(issue)

        return issues_data[:limit]

    def _fetch_issues_for_repo(
        self, repo_name: str, limit_per_repo: int = 5, difficulty_levels: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        issues_data = []
        target_labels = set(difficulty_levels) if difficulty_levels else {
            "good first issue", "good-first-issue", "help wanted", "easy", "beginner", "starter", "first-timers-only"
        }
        headers = {"Accept": "application/vnd.github+json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        try:
            url = f"https://api.github.com/repos/{repo_name}/issues?state=open&sort=created&direction=desc&per_page=30"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                count = 0
                for item in response.json():
                    if "pull_request" in item:
                        continue
                    issue_labels = {l["name"].lower() for l in item.get("labels", [])}
                    if target_labels and not issue_labels.intersection(target_labels):
                        continue
                    issues_data.append({
                        "id": str(item["id"]),
                        "title": item["title"],
                        "url": item["html_url"],
                        "description": item.get("body") or "",
                        "repository": repo_name,
                        "labels": [l["name"] for l in item.get("labels", [])],
                        "created_at": item.get("created_at"),
                        "comments_count": item.get("comments", 0),
                    })
                    count += 1
                    if count >= limit_per_repo:
                        break
            else:
                print(f"GitHub API REST warning for {repo_name}: {response.status_code}")
        except Exception as e:
            print(f"Error fetching issues for {repo_name}: {e}")

        return issues_data

    def _search_issues_global(
        self, limit: int = 15, labels: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        issues_data = []
        headers = {"Accept": "application/vnd.github+json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        primary_label = labels[0] if labels else "good first issue"
        url = "https://api.github.com/search/issues"
        params = {
            "q": f'is:issue state:open label:"{primary_label}" no:assignee',
            "sort": "created",
            "order": "desc",
            "per_page": min(100, max(15, limit * 2))
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                items = response.json().get("items", [])
                for item in items:
                    repo_url = item.get("repository_url", "")
                    repo_name = repo_url.replace("https://api.github.com/repos/", "")
                    issues_data.append({
                        "id": str(item["id"]),
                        "title": item["title"],
                        "url": item["html_url"],
                        "description": item.get("body") or "",
                        "repository": repo_name,
                        "labels": [l["name"] for l in item.get("labels", [])],
                        "created_at": item.get("created_at"),
                        "comments_count": item.get("comments", 0),
                    })
            else:
                print(f"GitHub Search API Error: {response.status_code}")
        except Exception as e:
            print(f"Failed to fetch global GitHub search issues: {e}")

        return issues_data

