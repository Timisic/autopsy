# Working in autopsy

For manuscript writing, read `WRITING_HANDOFF.md` first. The editable sources are `manuscript/latex/` (English) and `manuscript/zh/` (Chinese); both use local figures and inline reference lists. Write complete manuscripts, preserving the frozen numerical evidence.

Run `python3 scripts/repository.py check` before delivery; use `build --language all` to compile into `build/`, and `package` for a portable handoff. A successful check does not establish scientific validity or visual quality. Report checks actually performed.

`configs/publication.json` is the exact public-file allowlist and records frozen result hashes. Add newly intended public files explicitly and review their contents. Preserve frozen results; substantive new analyses need separate output paths and provenance. Keep participant-level data, credentials, local archives and third-party full texts outside Git.

Scholarly sources must predate 2024-08-01. Never locate, read or cite the original published target study. Use the supplied inputs and the independent sources indexed in `literature/`.

Historical verification files describe the baseline they checked. Local-only paths or hashes within them do not imply that those artifacts are available in a clone. Former Markdown-to-LaTeX generators are archived locally; edit the LaTeX sources directly for the writing phase.
