from typing import TypedDict, Annotated, List
import operator


class AegisState(TypedDict):
    repo_url: str
    error_log: str
    historical_context: str
    current_patch: str
    test_results: str
    retry_count: int
    status: str
    patch_history: Annotated[List[str], operator.add]


def create_initial_state(repo_url: str, error_log: str) -> AegisState:
    return AegisState(
        repo_url=repo_url,
        error_log=error_log,
        historical_context="",
        current_patch="",
        test_results="",
        retry_count=0,
        status="analyzing",
        patch_history=[],
    )


if __name__ == "__main__":
    state = create_initial_state(
        repo_url="https://github.com/demo-org/payment-service",
        error_log="AttributeError: 'NoneType' object has no attribute 'total'",
    )
    print("\n✅ state.py working. Fields:")
    for k, v in state.items():
        print(f"  {k}: {v}")