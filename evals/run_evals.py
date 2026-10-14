"""Golden evals: ask the agent known questions and check its answers (PLAN.md §12).

    uv run python -m evals.run_evals                          # every case
    uv run python -m evals.run_evals --case flutter-init      # selected cases (repeatable)
    uv run python -m evals.run_evals --model gemini-3.8-flash # override MAIN_MODEL

Each run calls the real model, so it spends API quota. Results are saved to evals/results/.
"""

import argparse
import asyncio
import json
import os
import sys
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

EVALS_DIR = Path(__file__).parent
DEFAULT_PROFILE = {
    "company": "Eval Co",
    "modules": ["core", "push", "gamification"],
    "environment": "uat",
    "region": "IN",
    "customer_id_type": "mobile",
}
JUDGE_PROMPT = """You are grading an AI assistant's answer to a client's question.

Client's question:
<question>{question}</question>

Assistant's answer:
<answer>{answer}</answer>

Grading question: {check}

Reply with exactly one word: yes or no."""


@dataclass
class Result:
    id: str
    passed: bool
    failures: list[str] = field(default_factory=list)
    answer: str = ""
    seconds: float = 0.0


def load_cases(selected: list[str]) -> list[dict]:
    cases = yaml.safe_load((EVALS_DIR / "golden.yaml").read_text(encoding="utf-8"))
    if selected:
        unknown = set(selected) - {c["id"] for c in cases}
        if unknown:
            sys.exit(f"Unknown case id(s): {', '.join(sorted(unknown))}")
        cases = [c for c in cases if c["id"] in selected]
    return cases


def profile_for(shorthand: str):
    from app.graph.state import IntegrationProfile

    platform, mode = shorthand.split("/")
    return IntegrationProfile.model_validate(
        {**DEFAULT_PROFILE, "platforms": [{"platform": platform, "config_mode": mode}]}
    )


async def with_retries(make_call, attempts: int = 3):
    """Retry transient provider errors (e.g. 503 "high demand") with backoff."""
    for attempt in range(attempts):
        try:
            return await make_call()
        except Exception:
            if attempt == attempts - 1:
                raise
            await asyncio.sleep(10 * (attempt + 1))


async def ask(graph, case: dict) -> str:
    from app.api.setup import initial_state
    from app.graph.messages import message_text

    inputs = {
        **initial_state(profile_for(case["profile"])),
        "messages": [HumanMessage(case["question"])],
    }
    config = {"configurable": {"thread_id": f"eval-{case['id']}-{uuid.uuid4()}"}}
    state = await with_retries(lambda: graph.ainvoke(inputs, config))
    replies = [m for m in state["messages"] if isinstance(m, AIMessage)]
    return "\n\n".join(t for m in replies if (t := message_text(m.content)))


async def judge(model, case: dict, answer: str, check: str) -> str:
    from app.graph.messages import message_text

    prompt = JUDGE_PROMPT.format(question=case["question"], answer=answer, check=check)
    reply = await with_retries(lambda: model.ainvoke(prompt))
    return "yes" if message_text(reply.content).strip().lower().startswith("yes") else "no"


async def run_case(graph, judge_model, case: dict) -> Result:
    started = time.monotonic()
    try:
        answer = await ask(graph, case)
    except Exception as error:  # a crash is a failure, not the end of the run
        return Result(case["id"], False, [f"agent error: {error}"], seconds=time.monotonic() - started)

    expect = case.get("expect", {})
    lowered = answer.lower()
    failures = [f"missing: {s!r}" for s in expect.get("contains", []) if s.lower() not in lowered]
    failures += [f"should not contain: {s!r}" for s in expect.get("not_contains", []) if s.lower() in lowered]
    for check in expect.get("judge", []):
        verdict = await judge(judge_model, case, answer, check["q"])
        if verdict != check["want"]:
            failures.append(f"judge said {verdict!r} (want {check['want']!r}): {check['q']}")
    return Result(case["id"], not failures, failures, answer, time.monotonic() - started)


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--case", action="append", default=[], help="run only this case id (repeatable)")
    parser.add_argument("--model", help="override MAIN_MODEL for this run")
    parser.add_argument("--delay", type=float, default=4.0, help="seconds between cases (free-tier rate limits)")
    parser.add_argument("--min-pass", type=float, default=0.9, help="exit non-zero below this pass rate")
    args = parser.parse_args()

    if args.model:
        os.environ["MAIN_MODEL"] = args.model
    from app.config import get_settings
    from app.graph.builder import build_graph
    from app.llm import DEFAULT_MODELS, fallback_models, main_model

    get_settings.cache_clear()
    settings = get_settings()
    model_name = settings.main_model or DEFAULT_MODELS[settings.llm_provider][0]
    graph = build_graph(checkpointer=InMemorySaver())
    judge_model = main_model().with_fallbacks(fallback_models())

    cases = load_cases(args.case)
    print(f"Running {len(cases)} case(s) on {settings.llm_provider}:{model_name}\n")
    results = []
    for index, case in enumerate(cases):
        if index:
            await asyncio.sleep(args.delay)
        result = await run_case(graph, judge_model, case)
        results.append(result)
        print(f"{'PASS' if result.passed else 'FAIL'}  {result.id}  ({result.seconds:.0f}s)")
        for failure in result.failures:
            print(f"      - {failure}")

    passed = sum(r.passed for r in results)
    rate = passed / len(results) if results else 0.0
    print(f"\n{passed}/{len(results)} passed ({rate:.0%})")

    out_dir = EVALS_DIR / "results"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"{time.strftime('%Y%m%d-%H%M%S')}-{model_name}.json"
    out.write_text(
        json.dumps(
            {"model": model_name, "passed": passed, "total": len(results), "results": [asdict(r) for r in results]},
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Saved {out.relative_to(EVALS_DIR.parent)}")
    return 0 if rate >= args.min_pass else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
