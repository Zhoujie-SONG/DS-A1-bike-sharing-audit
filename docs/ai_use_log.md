# AI-use disclosure

## AI tool
OpenAI Codex / ChatGPT-assisted workflow.

## Tasks assisted by AI
The user supplied a detailed assignment specification. Codex performed project scaffolding, official-source retrieval, Python audit and bootstrap implementation, notebook construction and execution, figure generation, documentation drafting, PDF creation, Git preparation and programmatic QA.

## Accepted suggestions
The implemented design follows the supplied research question and data source, immutable SHA-256 pinning, date-hour duplicate checks, deterministic target-leakage identification and the conceptual supply-constraint counterexample. These were task instructions, not fabricated user interactions.

## Rejected / modified suggestions
No human acceptance or rejection beyond the initial request is documented. During implementation Codex modified the suggested bootstrap approach to use seven-day blocks instead of independent hourly resampling, withheld intervals in sparsely supported cells, avoided selecting one of the conflicting temperature normalizations, and treated weekday mapping as empirically verified rather than documented. A broad sentinel scan initially flagged legitimate instant=9999; contextual inspection rejected that flag and removed positive 9999 from the candidate list without changing raw data. These are Codex implementation decisions, not claimed human judgments. Network package installation attempts were interrupted after prolonged delays. Existing analysis packages and a workspace-only copy of bundled ReportLab were used for this run; no successful installation is asserted.

## Independent verification
Here independent means results recomputed or checked against source bytes/documentation, not a second human reviewer. Code verifies official UCI DOI/license and raw SHA-256, date/calendar consistency, cnt identity and daily/hourly totals; fresh-kernel notebook reruns and artifact validation are performed by run_all.py. The accompanying results/qa_validation.json and docs/qa_review.md distinguish programmatic checks from Codex visual/text review. No unperformed manual or instructor review is asserted. The student must inspect and accept the submitted work under their course policy.
