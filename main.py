"""
aegis-ai / main.py
====================
LangGraph Assembly & Self-Healing Loop.

Wires all three agents into a stateful graph with:
- Sequential flow: Triage → Coder → Tester
- Conditional retry loop: up to 3 attempts
- Terminal states: fixed ✅ or failed ❌
"""

import logging
from langgraph.graph import StateGraph, END
from state import AegisState, create_initial_state
from nodes import triage_agent, coder_agent, tester_agent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("aegis.main")

MAX_RETRIES = 3


# ---------------------------------------------------------------------------
# Conditional Router — decides what happens after the Tester Agent
# ---------------------------------------------------------------------------
def route_after_tester(state: AegisState) -> str:
    """
    Called by LangGraph after every Tester Agent run.
    Returns the name of the next node to go to.

    Logic:
        - If test passed (status == "fixed")  → go to END
        - If retries exhausted (>= MAX_RETRIES) → go to END
        - Otherwise → go back to Coder Agent for another attempt
    """
    if state["status"] == "fixed":
        logger.info("✅ Incident resolved. Routing to END.")
        return "end_fixed"

    if state["retry_count"] >= MAX_RETRIES:
        logger.warning("❌ Max retries (%d) reached. Routing to END.", MAX_RETRIES)
        return "end_failed"

    logger.info("🔁 Test failed. Retrying... (attempt %d/%d)",
                state["retry_count"], MAX_RETRIES)
    return "retry"


# ---------------------------------------------------------------------------
# Build the LangGraph
# ---------------------------------------------------------------------------
def build_graph() -> StateGraph:
    """
    Assembles all agent nodes into a LangGraph workflow.

    Graph structure:
        START → triage → coder → tester → [router]
                                              ↓ retry
                                           coder → tester → [router]
                                              ↓ end_fixed / end_failed
                                            END
    """
    graph = StateGraph(AegisState)

    # Register all agent nodes
    graph.add_node("triage", triage_agent)
    graph.add_node("coder",  coder_agent)
    graph.add_node("tester", tester_agent)

    # Define the entry point
    graph.set_entry_point("triage")

    # Fixed edges (always happen)
    graph.add_edge("triage", "coder")
    graph.add_edge("coder",  "tester")

    # Conditional edge after tester (this is the self-healing loop)
    graph.add_conditional_edges(
        "tester",
        route_after_tester,
        {
            "retry":      "coder",  # loop back for another fix attempt
            "end_fixed":  END,      # success — stop the graph
            "end_failed": END,      # exhausted retries — stop the graph
        },
    )

    return graph.compile()


# ---------------------------------------------------------------------------
# Main Runner
# ---------------------------------------------------------------------------
def run_aegis(repo_url: str, error_log: str) -> dict:
    """
    Entry point for running AegisAI on a new incident.

    Args:
        repo_url  : GitHub URL of the affected repository
        error_log : The raw error / stack trace

    Returns:
        dict with final state including status, patch, and test results
    """
    logger.info("=" * 55)
    logger.info("  AegisAI Incident Commander — Starting Run")
    logger.info("=" * 55)
    logger.info("Repo     : %s", repo_url)
    logger.info("Error    : %s", error_log[:80])
    logger.info("-" * 55)

    # Build the graph
    app = build_graph()

    # Create the initial state
    initial_state = create_initial_state(
        repo_url=repo_url,
        error_log=error_log,
    )

    # Run the graph — LangGraph handles passing state between nodes
    final_state = app.invoke(initial_state)

    # Print final report
    logger.info("-" * 55)
    logger.info("  FINAL REPORT")
    logger.info("-" * 55)
    logger.info("Status       : %s", final_state["status"].upper())
    logger.info("Retries used : %d / %d", final_state["retry_count"], MAX_RETRIES)
    logger.info("Patches tried: %d", len(final_state["patch_history"]))

    if final_state["status"] == "fixed":
        logger.info("✅ INCIDENT RESOLVED AUTOMATICALLY")
    else:
        logger.warning("❌ INCIDENT NEEDS HUMAN REVIEW")

    return final_state


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  AegisAI — Phase 4 Full System Test")
    print("=" * 55 + "\n")

    # Test incident 1 — NoneType error (should fix on first try)
    result = run_aegis(
        repo_url="https://github.com/demo-org/payment-service",
        error_log=(
            "AttributeError: 'NoneType' object has no attribute 'total'\n"
            "  File 'payment/processor.py', line 42, in process_payment\n"
            "    result = cart.total()"
        ),
    )

    print("\n" + "=" * 55)
    print("  FINAL PATCH APPLIED:")
    print("=" * 55)
    print(result["current_patch"])
    print("\n" + "=" * 55)
    print("  SANDBOX OUTPUT:")
    print("=" * 55)
    print(result["test_results"])
    print("\n✅ Phase 4 complete. AegisAI is fully operational.\n")