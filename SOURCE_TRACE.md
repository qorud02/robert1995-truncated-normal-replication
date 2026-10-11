# Primary source and replication scope

Original journal article: Christian P. Robert (1995), Simulation of truncated normal variables, Statistics and Computing 5, 121–125. DOI https://doi.org/10.1007/BF00143942 .

The numerical targets are transcribed from the author's publicly archived reprint, arXiv:0907.4010v1, https://arxiv.org/pdf/0907.4010v1 . The author identifies this upload as a reprint of the original version at https://xianblog.wordpress.com/2009/07/24/simulation-of-truncated-normal-variables-reprint/ . The archived ten-page manuscript retains March 1992 on its final page; this is not the five-page typeset journal file. The result reported here concerns this identified reprint. No claim is made that the discrepant digit has been checked against the typeset publisher PDF or that it has never been noticed elsewhere.

- Table 2.1: printed page 4, seven lower endpoints 0, 0.5, 1, 1.5, 2, 2.5, 3; original probabilities in anchors.json.
- Table 2.2: printed page 7, columns lower endpoint 0, 0.5, 1, 1.5, 2; rows interval width 2, 1, 0.5, 0.1; twenty original probabilities in anchors.json. We reconstruct the better of the uniform and capped exponential proposals defined immediately before the table.
- Figure 2.1: printed page 6, the switching upper endpoint as a function of the lower endpoint on [0,4]. The source supplies equation (2.1), but no source numerical coordinate array. We recompute that equation and independently verify equality of the two acceptance rates.

These are all numerical tables and the single numerical figure in Section 2. Section 3 gives a multivariate Gibbs construction and symbolic bivariate ball example without a reported numerical experiment. This study replicates the complete univariate numerical section; it does not test Gibbs-chain mixing or validate every theorem in Section 3.

No original source code was used. replicate.py and verify.py were written independently from the mathematical definitions. The original article PDF is not redistributed as part of the project; source-provenance.json records the exact retrieved PDF hash and version. Its private _source cache is excluded from the release.

After the first calculation, the a=0.5 one-sided cell differed from its printed anchor. Both the original anchor and the calculated value are retained. The reporting assertion was changed to permit an actual replication discrepancy; neither the sampler, formulas, settings nor seeds were adjusted in response to the result. The first run used the system NumPy 2.5.3; the final recorded run uses the isolated pinned environment in requirements.txt. Initial diagnostic metadata is retained privately in _source/initial-run-summary.json.
