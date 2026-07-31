import os
import requests
from typing import Dict, Any, Optional

class LinkedInClient:
    """Utility class to publish curated posts to LinkedIn via LinkedIn API."""

    def __init__(self, access_token: Optional[str] = None, author_urn: Optional[str] = None):
        self.access_token = access_token or os.getenv("LINKEDIN_ACCESS_TOKEN")
        self.author_urn = author_urn or os.getenv("LINKEDIN_AUTHOR_URN")

    def publish_post(self, content: str) -> Dict[str, Any]:
        """
        Publish a post to LinkedIn.
        If credentials are absent, run in simulation mode and print the post content.
        """
        if not self.access_token or not self.author_urn:
            print("[Simulated LinkedIn Post]")
            print("=" * 60)
            try:
                print(content)
            except UnicodeEncodeError:
                print(content.encode('utf-8', errors='replace').decode('ascii', errors='replace'))
            print("=" * 60)
            print("[Info] Set LINKEDIN_ACCESS_TOKEN and LINKEDIN_AUTHOR_URN in environment to publish live.")
            return {"status": "simulated", "content": content}

        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }

        payload = {
            "author": self.author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": content},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            if response.status_code in (200, 201):
                res_json = response.json()
                print(f"Successfully published post to LinkedIn: {res_json.get('id')}")
                return {"status": "success", "id": res_json.get("id")}
            else:
                print(f"Failed to publish to LinkedIn ({response.status_code}): {response.text}")
                return {"status": "error", "code": response.status_code, "error": response.text}
        except Exception as e:
            print(f"Exception while posting to LinkedIn: {e}")
            return {"status": "exception", "error": str(e)}
