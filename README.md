# [Re] Acceptance probabilities in Robert's truncated-normal simulation algorithms

Kyunghan Bae · 12 October 2026

Independent reproduction of all 27 printed acceptance probabilities and the algorithm-switching figure in Section 2 of Robert (1995), using the author's arXiv:0907.4010v1 reprint.

## Reproduce

Use Python 3.12 in a fresh environment:

    python -m venv .venv
    .venv\Scripts\python -m pip install -r requirements.txt
    .venv\Scripts\python replicate.py
    .venv\Scripts\python verify.py

On Unix use .venv/bin/python. The fixed experiment uses 500,000 proposals in each of 47 method-setting pairs (23.5 million proposals), typically taking a few minutes in one process. It records the actual measured duration and software versions in summary.json. Original targets, seeds, proposal counts and pointwise Wilson settings were recorded in protocol.json before calculation. The familywise DKW diagnostic is an additional descriptive check absent from the recorded protocol. Exact repeatability requires the recorded NumPy version.

For an isolated --target installation, add that directory to PYTHONPATH before running. The local .deps directory is not part of the project or release.

## Files

- manuscript.md and article.pdf: research report in readable and publication formats.
- metadata.yaml: mandatory ReScience metadata in the official template schema.
- latex/: official-style publication sources and separately licensed template/fonts.
- prepare_publication.py and BUILD.md: synchronized metadata and PDF build instructions.
- anchors.json and SOURCE_TRACE.md: the original numerical targets, exact source version and scope.
- protocol.json: pre-computation targets, proposal counts, seeds and pointwise acceptance-interval settings.
- replicate.py: independently written closed forms, accept-reject samplers, Monte Carlo diagnostics and plotting.
- verify.py: independently written quadrature, switching-root and saved-output checks.
- table21.csv / table22.csv: every printed anchor, recalculated value, selected proposal and rounding comparison.
- boundary.csv and figure21_replication.png/.pdf: recomputed Figure 2.1, with 401 numerical checkpoints.
- monte_carlo.csv: all 47 proposal-acceptance estimates, pointwise Wilson intervals, accepted-sample moments, support checks and distribution diagnostics.
- acceptance_comparison.png/.pdf: newly calculated contrast with repeated-normal acceptance.
- summary.json and verification.json: execution and independent numerical audit.
- quadrature.csv and switch-root.csv: all 45 independent integrals and nine numerical boundary roots.
- source-provenance.json: retrieval timestamp, URL and SHA-256 of the primary PDF.

The numerical comparison reproduces 26 of 27 printed cells to three decimal places. The reprint's Table 2.1 gives 0.826 at lower endpoint 0.5; the stated optimized algorithm gives approximately 0.8275277271, which rounds to 0.828. This localized difference is preserved for inspection. The other six one-sided and all twenty two-sided cells agree at the printed precision. Acceptance probabilities measure proposals, rather than elapsed runtime.

The multivariate algorithm in Section 3 is outside this numerical replication. The original paper, figures and implementation are not bundled. See SOURCE_TRACE.md for source pagination and the distinction between the author reprint and the typeset journal article.

New code: MIT. New manuscript, figures and result files: CC BY 4.0. OpenAI Codex agents assisted with the design, implementation, execution, numerical checks and manuscript preparation, as recorded in the manuscript.
