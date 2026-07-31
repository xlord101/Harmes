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

from src.agents.graph import create_hermes_graph


def main():
    parser = argparse.ArgumentParser(description="Hermes Agent CLI - GitHub Issue Evaluator & LinkedIn Publisher")
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

    print("=== Executing Hermes Agent LangGraph Pipeline ===")
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
