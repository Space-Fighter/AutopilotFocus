"""Step 0 accuracy test: run the pipeline over labelled (page, goal) pairs and report results.

Run from ai-service/:  uv run python eval/run_eval.py
Add rows to eval/dataset.jsonl. Aim for 50-100 real pages, half "allow" and half "block".
"""

import json
import sys
import time
from collections import Counter
from pathlib import Path

from ai_service.pipeline import classify
from ai_service.schemas import Goal, PageData
from ai_service.services import build_services

DATASET = Path(__file__).parent / "dataset.jsonl"


def main() -> int:
    services = build_services()  # needs Postgres running (repo-root docker-compose.yml)

    rows = [json.loads(line) for line in DATASET.read_text(encoding="utf-8").splitlines() if line.strip()]
    correct = 0
    by_source: Counter[str] = Counter()
    latencies: list[float] = []

    for row in rows:
        page = PageData(**row["page"])
        goal = Goal(text=row["goal"], profile=row.get("profile", ""))
        start = time.perf_counter()
        verdict = classify(page, goal, services)
        latencies.append(time.perf_counter() - start)

        ok = verdict.decision == row["expected"]
        correct += ok
        by_source[verdict.source] += 1
        mark = "OK  " if ok else "MISS"
        sim = "  –  " if verdict.similarity is None else f"{verdict.similarity:.3f}"
        print(
            f"{mark} {row['id']:<34} expected={row['expected']:<5} got={verdict.decision:<5} "
            f"sim={sim} via={verdict.source:<9} {verdict.reason}"
        )

    n = len(rows)
    print()
    print(f"accuracy      {correct}/{n} = {correct / n:.0%}")
    print(f"decided by    {dict(by_source)}  (llm = cases that cost an LLM judge call)")
    print(f"latency       avg {sum(latencies) / n:.2f}s, max {max(latencies):.2f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
