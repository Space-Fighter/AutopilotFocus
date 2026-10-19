"""Step 0 accuracy test: run the pipeline over labelled (page, goal) pairs and report results.

Run from ai-service/:  uv run python eval/run_eval.py            (normal mode)
                       uv run python eval/run_eval.py --basic    (basic mode, no LLM: spec §5.9)
Add rows to eval/dataset.jsonl. Aim for 50-100 real pages, half "allow" and half "block".
"""

import json
import sys
import time
from collections import Counter
from pathlib import Path

from ai_service.config import get_settings, load_providers
from ai_service.embedder import Embedder
from ai_service.llm import ProviderChain
from ai_service.pipeline import classify
from ai_service.schemas import Goal, PageData

DATASET = Path(__file__).parent / "dataset.jsonl"


def main() -> int:
    use_llm = "--basic" not in sys.argv
    settings = get_settings()
    embedder = Embedder(settings.embedding_model)
    llm = ProviderChain(load_providers(settings.providers_file), settings.llm_timeout_s)

    rows = [json.loads(line) for line in DATASET.read_text(encoding="utf-8").splitlines() if line.strip()]
    correct = 0
    by_source: Counter[str] = Counter()
    latencies: list[float] = []

    for row in rows:
        page = PageData(**row["page"])
        goal = Goal(text=row["goal"], profile=row.get("profile", ""))
        start = time.perf_counter()
        verdict = classify(page, goal, llm, embedder, settings, use_llm=use_llm)
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
    print(f"mode          {'normal' if use_llm else 'basic (no LLM)'}")
    print(f"accuracy      {correct}/{n} = {correct / n:.0%}")
    print(f"decided by    {dict(by_source)}  (llm = cases that cost an LLM judge call)")
    print(f"latency       avg {sum(latencies) / n:.2f}s, max {max(latencies):.2f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
