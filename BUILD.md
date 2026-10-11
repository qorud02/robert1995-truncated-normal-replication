# Build the research manuscript

The code and experiment run with requirements.txt. PDF generation additionally uses PyYAML (requirements-build.txt) and Tectonic 0.17.0, or a standard XeLaTeX/BibTeX installation.

    python -m pip install -r requirements-build.txt
    python prepare_publication.py --code-url ACTUAL_PUBLIC_CODE_URL
    cd latex
    tectonic -X compile --keep-logs article.tex

Copy latex/article.pdf to article.pdf after a successful build. The metadata.yaml in both directories is synchronized by prepare_publication.py; the official parser and converter generate latex/metadata.tex. An optional --code-doi or --review-url must be supplied only after the corresponding record exists.

The provided official ReScience style and fonts come from ReScience/template commit 0978d0e5d9a86246789fd3468aec6fc71e39c944. Their licenses remain in latex/COPYING and the font directories. Local adaptations use the BibTeX backend and show a replication-manuscript sidebar until editorial metadata exists. The manuscript's code, figure and source-version information comes from this study; no original article images are included.
