# Final quality review

## Programmatic evidence

The full pipeline executes the English notebook from a fresh kernel, regenerates the PDF, and verifies every required file is present and nonempty. Source sizes and SHA-256 are recomputed from bytes. Independent pandas calculations verify row/column counts, missingness, exact and natural-key duplicates, target identity and grouped n/mean/median/SD. Output execution counts are sequential; error outputs are prohibited. Embedded figures and saved PNGs are checked. The PDF is reopened and its text, page count and size checked. Canonical counts, weather means and leakage language are compared across the notebook, PDF, README and submission text. `results/qa_validation.json` is the machine-readable receipt.

## Codex visual and text review

The PDF was rendered using Poppler and all ten pages inspected in page contact sheets, with chart and lineage pages also inspected at readable resolution. First-pass chart footnotes were too close to axis labels; layout margins were adjusted and the updated figures/report rendered again. Tables stay within page margins, figures preserve aspect ratio, the lineage diagram is visible, source links and hashes are readable, and each page has a footer/page number. Matplotlib count axes start at zero; the two hourly series have distinct line styles and colors. Blank heatmap cells remain missing combinations.

The saved notebook was rendered in a read-only local HTML viewer of its actual markdown and saved outputs, then inspected in the in-app browser. Images and explanations are present and tables are horizontally scrollable. Full hashes and unabridged audit conditions are retained in notebook tables. The viewer is a QA aid; the executed IPYNB is the deliverable. A conventional nbconvert HTML export failed while loading this machine's Windows certificate store; this is documented in reproducibility.md. It did not affect fresh-kernel execution or PDF creation.

The initial sentinel heuristic incorrectly flagged the legitimate record index 9999. The rule was narrowed to textual and impossible negative codes after inspecting its meaning. No source row was changed. Zero humidity remains a flagged measurement concern and is retained in the main analysis, with a separate sensitivity table.

Claim-search matches were reviewed in context. The requested causal/generalization words appear in prohibited-claim explanations or negative scope statements, not affirmative universal or causal findings. No unverified special-event attribution, artificial zero counts, latent-demand measurements or optimized scheduling result is asserted. The 200/100 illustration is explicitly conceptual. After the user authorized public GitHub publication, the repository was created and verified through GitHub CLI. The submission summary now uses the actual URL from docs/repository.json; no unresolved repository address remains. Other unfinished markers are absent from deliverable prose.

## Limitations of verification

This is Codex review plus programmatic recomputation, not a second human or instructor review. Original transaction/weather feeds and historical holiday schedule were not independently reconstructed. Feature availability timestamps, timezone/DST handling, omitted-hour reasons and conflicting source labels remain unresolved. These limits are reported rather than converted into false passes. Student acceptance and course submission remain manual.
