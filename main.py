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
    parser.add_argument(
        "--all-categories",
        action="store_true",
        help="Scrape all repositories across all categories in repos.json instead of just default target repos",
    )
    parser.add_argument(
        "--global-search",
        action="store_true",
        help="Run global GitHub search for beginner issues across all open source projects",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=25,
        help="Maximum number of raw issues to scrape (default: 25)",
    )
    parser.add_argument(
        "--difficulty",
        type=str,
        default="",
        help="Comma-separated list of target difficulty labels (e.g. 'good first issue,help wanted,easy')",
    )

    args = parser.parse_args()
    target_repos = [r.strip() for r in args.repos.split(",") if r.strip()]
    difficulty_levels = [d.strip() for d in args.difficulty.split(",") if d.strip()]

    if not target_repos:
        try:
            import json
            with open("repos.json", "r", encoding="utf-8") as f:
                repos_data = json.load(f)
                if args.all_categories:
                    all_repos = set()
                    for cat_name, repos in repos_data.get("categories", {}).items():
                        all_repos.update(repos)
                    target_repos = list(all_repos)
                    print(f"[Config] Loaded {len(target_repos)} repositories across ALL categories from repos.json.")
                else:
                    target_repos = repos_data.get("default_target_repos", [])
                    print(f"[Config] Loaded default target repositories from repos.json: {target_repos}")

                if not difficulty_levels:
                    difficulty_levels = repos_data.get("difficulty_levels", [])
        except Exception as e:
            print(f"[Warning] Could not load repos.json: {e}")

    initial_state = {
        "target_repos": target_repos,
        "limit": args.limit,
        "difficulty_levels": difficulty_levels,
        "global_search_first": args.global_search,
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
