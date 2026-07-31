import sys
import argparse
from dotenv import load_dotenv

# Reconfigure stdout/stderr encoding for UTF-8 compatibility
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Load environment variables
load_dotenv()

from src.agents.graph import (
    create_daily_scrape_graph,
    create_weekly_publish_graph,
    create_hermes_graph,
)


def main():
    parser = argparse.ArgumentParser(description="Hermes Agent CLI - GitHub Issue Evaluator & Publisher")
    parser.add_argument(
        "--scrape-and-score",
        action="store_true",
        help="Run daily scrape and score workflow (Phases 1 & 2)",
    )
    parser.add_argument(
        "--generate-and-publish",
        action="store_true",
        help="Run weekly post generation workflow (Phase 3)",
    )
    parser.add_argument(
        "--full-pipeline",
        action="store_true",
        help="Run full pipeline from scraping to post generation",
    )
    parser.add_argument(
        "--repos",
        type=str,
        default="",
        help="Comma-separated list of target GitHub repositories (e.g., 'facebook/react,fastapi/fastapi')",
    )

    args = parser.parse_args()
    target_repos = [r.strip() for r in args.repos.split(",") if r.strip()]

    if not target_repos:
        try:
            import json
            with open("repos.json", "r", encoding="utf-8") as f:
                repos_data = json.load(f)
                target_repos = repos_data.get("default_target_repos", [])
                print(f"[Config] Loaded default target repositories from repos.json: {target_repos}")
        except Exception as e:
            print(f"[Warning] Could not load repos.json: {e}")

    initial_state = {
        "target_repos": target_repos,
        "raw_issues": [],
        "evaluated_issues": [],
        "post_draft": "",
    }

    if args.scrape_and_score:
        print("=== Running Daily Scrape & Score Workflow ===")
        graph = create_daily_scrape_graph()
        result = graph.invoke(initial_state)
        print(f"Successfully scraped & evaluated {len(result.get('evaluated_issues', []))} issues.")

    elif args.generate_and_publish:
        print("=== Running Weekly Post Generation Workflow ===")
        graph = create_weekly_publish_graph()
        result = graph.invoke(initial_state)
        print("\nGenerated LinkedIn Post Draft:")
        print("--------------------------------------------------")
        print(result.get("post_draft", ""))
        print("--------------------------------------------------")

    else:
        print("=== Executing Hermes Agent Full Pipeline ===")
        graph = create_hermes_graph()
        result = graph.invoke(initial_state)

        print("\nPipeline Finished Successfully!")
        print(f"Total issues evaluated: {len(result.get('evaluated_issues', []))}")
        print("\nGenerated LinkedIn Post Draft:")
        print("--------------------------------------------------")
        print(result.get("post_draft", ""))
        print("--------------------------------------------------")


if __name__ == "__main__":
    main()
