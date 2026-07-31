from langgraph.graph import StateGraph, END
from src.agents.state import AgentState
from src.agents.nodes import (
    scrape_github_issues,
    evaluate_and_score_issues,
    generate_linkedin_post,
)

def create_daily_scrape_graph():
    """Create state machine graph for daily scraping and scoring phase."""
    workflow = StateGraph(AgentState)

    workflow.add_node("scrape_github_issues", scrape_github_issues)
    workflow.add_node("evaluate_and_score_issues", evaluate_and_score_issues)

    workflow.set_entry_point("scrape_github_issues")
    workflow.add_edge("scrape_github_issues", "evaluate_and_score_issues")
    workflow.add_edge("evaluate_and_score_issues", END)

    return workflow.compile()


def create_weekly_publish_graph():
    """Create state machine graph for weekly draft generation phase."""
    workflow = StateGraph(AgentState)

    workflow.add_node("generate_linkedin_post", generate_linkedin_post)

    workflow.set_entry_point("generate_linkedin_post")
    workflow.add_edge("generate_linkedin_post", END)

    return workflow.compile()


def create_hermes_graph():
    """Construct full end-to-end sequential workflow."""
    workflow = StateGraph(AgentState)

    workflow.add_node("scrape_github_issues", scrape_github_issues)
    workflow.add_node("evaluate_and_score_issues", evaluate_and_score_issues)
    workflow.add_node("generate_linkedin_post", generate_linkedin_post)

    workflow.set_entry_point("scrape_github_issues")
    workflow.add_edge("scrape_github_issues", "evaluate_and_score_issues")
    workflow.add_edge("evaluate_and_score_issues", "generate_linkedin_post")
    workflow.add_edge("generate_linkedin_post", END)

    return workflow.compile()
