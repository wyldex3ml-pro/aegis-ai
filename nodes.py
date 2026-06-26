"""
aegis-ai / nodes.py
====================
The Three AI Agent Nodes for AegisAI.

- TriageAgent   : Reads the error, fetches RAG context
- CoderAgent    : Writes a code fix using the LLM
- TesterAgent   : Runs the fix in a local sandbox
"""

import os
import logging
import subprocess
import tempfile
from groq import Groq
from dotenv import load_dotenv
from state import AegisState
from rag_storage import RagStorage

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("aegis.nodes")

# ---------------------------------------------------------------------------
# Shared clients (created once, reused across all agent calls)
# ---------------------------------------------------------------------------
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
rag = RagStorage()
rag.seed_with_examples()


# ---------------------------------------------------------------------------
# Helper: call the LLM
# ---------------------------------------------------------------------------
def call_llm(system_prompt: str, user_prompt: str) -> str:
    """Calls Groq's Llama 3.3 70B and returns the response text."""
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=1024,
        )
        raw = response.choices[0].message.content.strip()
        # Strip markdown code fences the LLM sometimes wraps code in
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        return raw.strip()
    except Exception as e:
        logger.error("LLM call failed: %s", e)
        return f"LLM_ERROR: {e}"


# ---------------------------------------------------------------------------
# Helper: run code safely in a local subprocess sandbox
# ---------------------------------------------------------------------------
def run_code_in_sandbox(code: str) -> str:
    """
    Writes code to a temp file and runs it in a subprocess.
    Returns stdout + stderr combined.
    Kills the process after 15 seconds (safety timeout).
    """
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        result = subprocess.run(
            ["python", tmp_path],
            capture_output=True,
            text=True,
            timeout=15,
        )
        output = result.stdout + result.stderr
        exit_code = result.returncode
        return f"EXIT_CODE: {exit_code}\n{output}" if output else f"EXIT_CODE: {exit_code}\n(no output)"

    except subprocess.TimeoutExpired:
        return "EXIT_CODE: 1\nERROR: Code execution timed out after 15 seconds."
    except Exception as e:
        return f"EXIT_CODE: 1\nERROR: Sandbox failed: {e}"


# ---------------------------------------------------------------------------
# AGENT 1: Triage Agent
# ---------------------------------------------------------------------------
def triage_agent(state: AegisState) -> AegisState:
    """
    Reads the incoming error log and fetches similar past incidents
    from the RAG database to build historical context.
    """
    logger.info("🔍 Triage Agent started.")

    context = rag.retrieve_similar(error_log=state["error_log"], top_k=2)
    logger.info("RAG context retrieved.")

    return {
        **state,
        "historical_context": context,
        "status": "analyzing",
    }


# ---------------------------------------------------------------------------
# AGENT 2: Coder Agent
# ---------------------------------------------------------------------------
def coder_agent(state: AegisState) -> AegisState:
    """
    Uses the LLM to generate a Python code fix based on:
    - The error log
    - Historical context from the Triage Agent
    - Previous failed patches (if this is a retry)
    """
    logger.info("💻 Coder Agent started. Retry #%d", state["retry_count"])

    system_prompt = """You are an expert Python engineer.
Your job is to fix broken Python code.
Reply with ONLY the fixed Python code — no explanations, no markdown, no backticks.
The code must be complete and runnable on its own."""

    retry_context = ""
    if state["patch_history"]:
        retry_context = "\n\nPREVIOUS FAILED ATTEMPTS:\n"
        for i, old_patch in enumerate(state["patch_history"], 1):
            retry_context += f"\nAttempt {i}:\n{old_patch}\n"
        retry_context += "\nThose attempts failed. Write a different fix.\n"

    user_prompt = f"""ERROR LOG:
{state["error_log"]}

HISTORICAL CONTEXT FROM SIMILAR PAST INCIDENTS:
{state["historical_context"]}
{retry_context}
Write the complete fixed Python code now:"""

    patch = call_llm(system_prompt, user_prompt)
    logger.info("Patch generated (%d chars).", len(patch))

    return {
        **state,
        "current_patch": patch,
        "patch_history": [patch],
        "status": "patching",
    }


# ---------------------------------------------------------------------------
# AGENT 3: Tester Agent
# ---------------------------------------------------------------------------
def tester_agent(state: AegisState) -> AegisState:
    """
    Runs the generated patch in a local sandbox subprocess.
    Records the result and increments the retry counter.
    """
    logger.info("🧪 Tester Agent started.")

    test_results = run_code_in_sandbox(state["current_patch"])
    logger.info("Sandbox result: %s", test_results[:80])

    passed = "EXIT_CODE: 0" in test_results

    new_status = "fixed" if passed else "patching"
    new_retry = state["retry_count"] + (0 if passed else 1)

    logger.info(
        "Test %s | retry_count now %d",
        "PASSED ✅" if passed else "FAILED ❌",
        new_retry,
    )

    return {
        **state,
        "test_results": test_results,
        "retry_count": new_retry,
        "status": new_status,
    }


# ---------------------------------------------------------------------------
# Smoke Test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from state import create_initial_state

    print("\n" + "=" * 55)
    print("  AegisAI — Phase 3 Nodes Validation")
    print("=" * 55)

    state = create_initial_state(
        repo_url="https://github.com/demo-org/payment-service",
        error_log=(
            "AttributeError: 'NoneType' object has no attribute 'total'\n"
            "  File 'payment/processor.py', line 42, in process_payment\n"
            "    result = cart.total()"
        ),
    )

    print("\n[1/3] Running Triage Agent...")
    state = triage_agent(state)
    print(f"  ✅ historical_context length: {len(state['historical_context'])} chars")

    print("\n[2/3] Running Coder Agent...")
    state = coder_agent(state)
    print(f"  ✅ patch generated:\n")
    print(state["current_patch"])

    print("\n[3/3] Running Tester Agent...")
    state = tester_agent(state)
    print(f"  ✅ test_results:\n{state['test_results']}")
    print(f"  ✅ status: {state['status']}")
    print(f"  ✅ retry_count: {state['retry_count']}")

    print("\n✅ Phase 3 complete. All three agents working.\n")