import os
import datetime
from typing import List, Dict, Any, Optional
from pymongo import MongoClient, UpdateOne
import certifi
from src.agents.state import Issue

class MongoDBClient:
    """MongoDB Atlas Client helper for storing and retrieving Hermes Agent issues."""

    def __init__(self, connection_uri: Optional[str] = None, db_name: Optional[str] = None):
        self.uri = connection_uri or os.getenv("MONGODB_URI")
        
        raw_db = (db_name or os.getenv("MONGODB_DB_NAME") or "").strip()
        self.db_name = raw_db if raw_db else "hermes_agent"
        
        raw_coll = (os.getenv("MONGODB_COLLECTION_NAME") or "").strip()
        self.collection_name = raw_coll if raw_coll else "issues"
        
        self._client = None
        self._db = None

    @property
    def collection(self):
        if not self.uri:
            print("[Warning] MONGODB_URI not configured. Database operations will be skipped or simulated.")
            return None
        if self._client is None:
            try:
                # Primary: certifi CA bundle
                self._client = MongoClient(
                    self.uri,
                    tlsCAFile=certifi.where(),
                    serverSelectionTimeoutMS=10000
                )
                self._db = self._client[self.db_name]
            except Exception as e:
                print(f"[Warning] PyMongo connection with certifi failed: {e}. Trying TLS fallback...")
                try:
                    self._client = MongoClient(
                        self.uri,
                        tls=True,
                        tlsAllowInvalidCertificates=True,
                        serverSelectionTimeoutMS=10000
                    )
                    self._db = self._client[self.db_name]
                except Exception as ex:
                    print(f"[Error] Failed to connect to MongoDB: {ex}")
                    return None
        return self._db[self.collection_name]

    def insert_or_update_issues(self, issues: List[Issue]) -> int:
        """Upsert evaluated issues into MongoDB Atlas based on issue_id."""
        try:
            coll = self.collection
            if coll is None:
                print(f"[Simulated] Would upsert {len(issues)} issues to MongoDB.")
                return len(issues)

            operations = []
            now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
            
            for issue in issues:
                doc = {
                    "issue_id": str(issue.id),
                    "title": issue.title,
                    "url": issue.url,
                    "description": issue.description,
                    "repository": issue.repository,
                    "tech_stack": issue.tech_stack,
                    "evaluation_score": issue.score,
                    "labels": issue.labels,
                    "is_published": issue.is_published,
                    "scraped_at": now_str,
                }
                operations.append(
                    UpdateOne(
                        {"issue_id": str(issue.id)},
                        {"$set": doc},
                        upsert=True
                    )
                )

            if operations:
                result = coll.bulk_write(operations)
                modified_count = result.upserted_count + result.modified_count
                print(f"Successfully upserted {modified_count} issues in MongoDB Atlas.")
                return modified_count
        except Exception as e:
            print(f"[Warning] MongoDB operations failed: {e}. Skipping DB insert.")
            return len(issues)
        return 0

    def get_top_unpublished_issues(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve top scoring unpublished issues."""
        try:
            coll = self.collection
            if coll is None:
                print("[Simulated] Returning empty/mock list of unpublished issues.")
                return []

            cursor = coll.find({"is_published": False}).sort("evaluation_score", -1).limit(limit)
            return list(cursor)
        except Exception as e:
            print(f"[Warning] MongoDB fetch failed: {e}. Returning empty list.")
            return []

    def mark_as_published(self, issue_ids: List[str]) -> int:
        """Mark specified issues as published."""
        try:
            coll = self.collection
            if coll is None:
                print(f"[Simulated] Marked issues {issue_ids} as published.")
                return len(issue_ids)

            result = coll.update_many(
                {"issue_id": {"$in": [str(i) for i in issue_ids]}},
                {"$set": {"is_published": True}}
            )
            print(f"Marked {result.modified_count} issues as published in MongoDB.")
            return result.modified_count
        except Exception as e:
            print(f"[Warning] MongoDB mark as published failed: {e}.")
            return 0
