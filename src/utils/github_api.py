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
        or global search if target_repos is empty.
        """
        issues_data = []

        if target_repos:
            for repo_name in target_repos:
                try:
                    repo_issues = self._fetch_issues_for_repo(repo_name, limit_per_repo=5)
                    issues_data.extend(repo_issues)
                except Exception as e:
                    print(f"Error fetching issues for repo {repo_name}: {e}")
        else:
            # General search across open source projects
            issues_data = self._search_issues_global(limit=limit)

        return issues_data

    def _fetch_issues_for_repo(self, repo_name: str, limit_per_repo: int = 5) -> List[Dict[str, Any]]:
        issues_data = []

        if self._github:
            repo = self._github.get_repo(repo_name)
            open_issues = repo.get_issues(state="open", labels=["good first issue"])
            count = 0
            for issue in open_issues:
                if issue.pull_request:
                    continue
                issues_data.append({
                    "id": str(issue.id),
                    "title": issue.title,
                    "url": issue.html_url,
                    "description": issue.body or "",
                    "repository": repo_name,
                    "labels": [label.name for label in issue.labels],
                    "created_at": issue.created_at.isoformat(),
                    "comments_count": issue.comments,
                })
                count += 1
                if count >= limit_per_repo:
                    break
        else:
            # Fallback to REST API
            headers = {"Accept": "application/vnd.github+json"}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"

            url = f"https://api.github.com/repos/{repo_name}/issues?state=open&labels=good%20first%20issue&per_page={limit_per_repo}"
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                for item in response.json():
                    if "pull_request" in item:
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
            else:
                print(f"GitHub API REST error for {repo_name}: {response.status_code} {response.text}")

        return issues_data

    def _search_issues_global(self, limit: int = 15) -> List[Dict[str, Any]]:
        issues_data = []
        headers = {"Accept": "application/vnd.github+json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        query = 'label:"good first issue" state:open is:issue'
        url = f"https://api.github.com/search/issues?q={requests.utils.quote(query)}&sort=created&order=desc&per_page={limit}"

        try:
            response = requests.get(url, headers=headers, timeout=10)
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
