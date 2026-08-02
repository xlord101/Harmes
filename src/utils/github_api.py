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
        self, target_repos: Optional[List[str]] = None, limit: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Fetch recent 'good first issue' or beginner-friendly issues from target repositories
        or global search if target_repos is empty or yields fewer than limit issues.
        Sorted by creation date descending.
        """
        issues_data = []
        seen_ids = set()

        if target_repos:
            for repo_name in target_repos:
                if len(issues_data) >= limit:
                    break
                try:
                    repo_issues = self._fetch_issues_for_repo(repo_name, limit_per_repo=5)
                    for issue in repo_issues:
                        if issue["id"] not in seen_ids:
                            seen_ids.add(issue["id"])
                            issues_data.append(issue)
                except Exception as e:
                    print(f"Error fetching issues for repo {repo_name}: {e}")

        # If target repos yielded fewer issues than limit, supplement with fresh issues from global search
        if len(issues_data) < limit:
            needed = limit - len(issues_data)
            print(f"[Info] Target repos yielded {len(issues_data)} issues. Supplementing with fresh issues from global search...")
            global_issues = self._search_issues_global(limit=needed * 2)
            for issue in global_issues:
                if len(issues_data) >= limit:
                    break
                if issue["id"] not in seen_ids:
                    seen_ids.add(issue["id"])
                    issues_data.append(issue)

        return issues_data

    def _fetch_issues_for_repo(self, repo_name: str, limit_per_repo: int = 5) -> List[Dict[str, Any]]:
        issues_data = []
        target_labels = {"good first issue", "good-first-issue", "help wanted", "easy", "beginner", "starter", "first-timers-only"}
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
                    if not issue_labels.intersection(target_labels):
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

    def _search_issues_global(self, limit: int = 15) -> List[Dict[str, Any]]:
        issues_data = []
        headers = {"Accept": "application/vnd.github+json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        url = "https://api.github.com/search/issues"
        params = {
            "q": 'is:issue state:open label:"good first issue" no:assignee',
            "sort": "created",
            "order": "desc",
            "per_page": min(100, limit * 2)
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
