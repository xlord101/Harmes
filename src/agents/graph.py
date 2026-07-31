from langgraph.graph import StateGraph, END
from src.agents.state import AgentState
from src.agents.nodes import (
    scrape_github_issues,
    evaluate_and_score_issues,
    generate_linkedin_post,
)

def create_hermes_graph():
    """Construct the LangGraph StateGraph for Hermes Agent sequential workflow."""
    workflow = StateGraph(AgentState)

    # Add core nodes
    workflow.add_node("scrape_github_issues", scrape_github_issues)
    workflow.add_node("evaluate_and_score_issues", evaluate_and_score_issues)
    workflow.add_node("generate_linkedin_post", generate_linkedin_post)

    # Define sequential control flow
    workflow.set_entry_point("scrape_github_issues")
    workflow.add_edge("scrape_github_issues", "evaluate_and_score_issues")
    workflow.add_edge("evaluate_and_score_issues", "generate_linkedin_post")
    workflow.add_edge("generate_linkedin_post", END)

    return workflow.compile()
