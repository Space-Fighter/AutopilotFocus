# Parked: basic mode (judging without an LLM)

Built on 2026-10-19, removed from the code for the MVP on 2026-11-01. The MVP assumes an LLM
is available; if every provider fails, the page is allowed and rechecked later.

- **Design:** main spec §5.9, `.plans/goals-and-basic-mode-nearest-case-spec.md`, full board frame 15.
- **Code:** `code-basic-mode.patch` re-adds `extracted_facts()`, `basic_classify()`, the `use_llm`
  flag (pipeline + API), basic thresholds, the `extracted` / `nearest` sources and `--basic` in the eval.

Bring it back from the repo root:

```bash
git apply .plans/architecture/future/basic-mode/code-basic-mode.patch
```

If the files changed a lot since, apply it by hand using the patch as a guide.
