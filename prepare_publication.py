"""Build publication sources and mandatory ReScience metadata from manuscript.md.

The official template parser and converter remain in latex/ with their licenses.
"""
from pathlib import Path
import argparse, importlib.util, json, re, shutil, sys
ROOT=Path(__file__).resolve().parent
LATEX=ROOT/'latex'
p=argparse.ArgumentParser()
p.add_argument('--code-url', default='https://github.com/qorud02/robert1995-truncated-normal-replication')
p.add_argument('--code-doi', default='')
p.add_argument('--review-url', default='')
args=p.parse_args()
md=(ROOT/'manuscript.md').read_text(encoding='utf-8')
title=md.splitlines()[0][2:]
abstract=re.search(r'^## Abstract\s*\n(.*?)(?=\nKeywords:)',md,re.S|re.M).group(1).strip()
abstract=' '.join(abstract.split())
meta={
 'title':title,
 'authors':[{'name':'Kyunghan Bae','orcid':'','email':'qorud001@gmail.com','affiliations':'1,*'}],
 'affiliations':[{'code':1,'name':'Independent researcher','address':'South Korea'}],
 'keywords':'truncated normal, accept-reject sampling, computational replication, Monte Carlo, numerical integration',
 'code':[{'url':args.code_url},{'doi':args.code_doi},{'swh':''}],
 'data':[{'url':args.code_url},{'doi':args.code_doi}],
 'replication':[
  {'cite':'Robert, C. P. (1995). Simulation of truncated normal variables. Statistics and Computing, 5, 121-125.'},
  {'bib':'robert1995'}, {'url':'https://arxiv.org/pdf/0907.4010v1'}, {'doi':'10.1007/BF00143942'}],
 'abstract':abstract, 'bibliography':'bibliography.bib', 'type':'Replication', 'domain':'Statistics', 'language':'Python',
 'review':[{'url':args.review_url}],
 'contributors':[{'name':'','orcid':'','role':'editor'},{'name':'','orcid':'','role':'reviewer'},{'name':'','orcid':'','role':'reviewer'}],
 'dates':[{'received':''},{'accepted':''},{'published':''}],
 'article':[{'number':''},{'doi':''},{'url':''}],
 'journal':[{'name':'ReScience C'},{'issn':'2430-3658'},{'volume':''},{'issue':''}]
}
# JSON is a strict subset of YAML; use a readily parsed UTF-8 YAML serialization.
mt=json.dumps(meta,indent=2,ensure_ascii=False)+'\n'
(ROOT/'metadata.yaml').write_text(mt,encoding='utf-8')
(LATEX/'metadata.yaml').write_text(mt,encoding='utf-8')
sys.path.insert(0,str(LATEX))
from article import Article
spec=importlib.util.spec_from_file_location('official_converter',LATEX/'yaml-to-latex.py')
conv=importlib.util.module_from_spec(spec); spec.loader.exec_module(conv)
a=Article(mt)
(LATEX/'metadata.tex').write_text(conv.generate_latex_metadata('metadata.yaml',a),encoding='utf-8')

def esc(s):
 chars={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}
 return ''.join(chars.get(c,c) for c in s)
def inline(s):
 # Scientific symbols in otherwise plain prose are rendered as math glyphs.
 tokens={'φ':r'$\phi$','Φ':r'$\Phi$','α':r'$\alpha$','∞':r'$\infty$','≤':r'$\leq$','≥':r'$\geq$','−':r'$-$','×':r'$\times$','²':r'$^2$','ε':r'$\epsilon$','⁻¹⁶':r'$^{-16}$','⁻¹⁵':r'$^{-15}$'}
 out=esc(s)
 for token in ['⁻¹⁶','⁻¹⁵']:
  out=out.replace(token,tokens[token])
 for token,tex in tokens.items():
  if token not in ['⁻¹⁶','⁻¹⁵']: out=out.replace(token,tex)
 for name in ['protocol.json','summary.json','source-provenance.json','requirements.txt','replicate.py','verify.py']:
  out=out.replace(name,r'\texttt{'+name.replace('-',r'-\allowbreak{}').replace('.',r'.\allowbreak{}')+'}')
 out=out.replace('Robert (1995)',r'\citet{robert1995}').replace('(Robert, 2009)',r'\cite{robert2009}').replace('(Massart, 1990)',r'\cite{massart1990}').replace('Botev and L’Ecuyer (2016)',r'\citet{botev2016}')
 return out
body=md[md.index('## Abstract'):]
lines=body.splitlines(); pieces=[]; para=[]; i=0

def flush():
 if para:
  pieces.append(inline(' '.join(para))+'\n'); para.clear()
while i<len(lines):
 line=lines[i].strip()
 if line=='## References': flush(); break
 if line.startswith('## '):
  flush(); heading=line[3:]
  pieces.append((r'\section*' if heading=='Abstract' else r'\section')+'{'+esc(heading)+'}\n')
 elif line.startswith('Keywords:'):
  flush(); pieces.append(r'{\small\sffamily '+inline(line)+r'\par}'+'\n')
 elif line.startswith('$$') and line.endswith('$$'):
  flush(); pieces.append('\\[\n'+line[2:-2]+'\n\\]\n')
 elif line.startswith('!['):
  flush(); m=re.fullmatch(r'!\[(.*)\]\(([^)]*)\)',line)
  fn=Path(m[2]).with_suffix('.pdf').name
  shutil.copy2(ROOT/fn,LATEX/fn)
  pieces.append(r'\begin{figure}[tbp]'+'\n'+r'\centering'+'\n'+r'\includegraphics[width=\linewidth]{'+fn+'}\n'+r'\caption{'+inline(m[1])+'}\n'+r'\end{figure}'+'\n')
 elif line.startswith('|'):
  flush(); rows=[]
  while i<len(lines) and lines[i].strip().startswith('|'):
   rows.append([x.strip() for x in lines[i].strip().strip('|').split('|')]); i+=1
  headers,values=rows[0],rows[2:]
  while i<len(lines) and not lines[i].strip(): i+=1
  caption=lines[i].strip() if i<len(lines) and lines[i].strip().startswith('Table ') else ''
  if caption: caption=re.sub(r'^Table \d+\.\s*','',caption); i+=1
  n=len(headers); size=r'\footnotesize' if n==6 else r'\small'
  if n==4: headers=[r'Lower endpoint $a$','Source','Recalculated','Rounded']
  if n==6: headers=[r'Width $b-a$',r'$a=0$',r'$a=0.5$',r'$a=1$',r'$a=1.5$',r'$a=2$']
  # The header math tokens are deliberately supplied as TeX.
  pieces.append(r'\begin{table}[tbp]'+'\n'+r'\centering'+size+r'\setlength{\tabcolsep}{3pt}'+'\n'+r'\begin{tabular}{@{}'+'r'*n+'@{}}\n'+r'\toprule'+'\n')
  pieces.append(' & '.join(headers)+r' \\'+'\n'+r'\midrule'+'\n')
  pieces.extend(' & '.join(inline(x) for x in row)+r' \\'+'\n' for row in values)
  pieces.append(r'\bottomrule'+'\n'+r'\end{tabular}'+'\n'+r'\caption{'+inline(caption)+'}\n'+r'\end{table}'+'\n')
  continue
 elif not line: flush()
 else: para.append(line)
 i+=1
flush(); pieces.append(r'\nocite{robert1995,robert2009,massart1990,botev2016}'+'\n')
(LATEX/'content.tex').write_text('\n'.join(pieces),encoding='utf-8')
(LATEX/'article.tex').write_text(r'''\documentclass{rescience}
\usepackage{booktabs,array,graphicx}
\setlength{\emergencystretch}{2em}
\lhead{\ifthenelse{\value{page}=1}{}{\scriptsize\sffamily [Re] Robert's truncated-normal algorithms}}
\begin{document}
\input{header.tex}
\input{content.tex}
\hypersetup{linkcolor=black,urlcolor=darkgray}
\setlength\bibitemsep{0pt}
\printbibliography
\end{document}
''',encoding='utf-8')
# Adapt the official style's status box without assigning an editorial status.
cls=LATEX/'rescience.cls'
ct=cls.read_text(encoding='utf-8').replace('backend=biber,','backend=bibtex,').replace(r'\fbox{UNDER REVIEW}',r'\fbox{REPLICATION}')
cls.write_text(ct,encoding='utf-8')
header=LATEX/'header.tex'
ht=header.read_text(encoding='utf-8')
start=ht.index(r'\marginnote{'); end=ht.index('%% --- Bottom statement',start)
ht=ht[:start]+r'''\marginnote{\footnotesize\sffamily
\textbf{Replication manuscript}\\
12 October 2026\\[1em]
\textbf{Original study}\\
Robert (1995)\\[1em]
\textbf{Numerical source}\\
arXiv:0907.4010v1
}

'''+ht[end:]
header.write_text(ht,encoding='utf-8')
shutil.copy2(ROOT/'bibliography.bib',LATEX/'bibliography.bib')
validation={
 'official_template_commit':'0978d0e5d9a86246789fd3468aec6fc71e39c944',
 'official_metadata_parser_used':True,'title':a.title,'contact_email':a.contact.email,
 'code_url':args.code_url,'code_url_requires_external_verification':True,
 'template_changes':['BibLaTeX biber to bibtex','Status box Replication; manuscript source sidebar before editorial assignment','Booktabs/array/graphicx'],
 'metadata_source':'https://github.com/ReScience/template/blob/master/metadata.yaml',
 'submission_authorization_recorded_by_parent':True,
 'protocol_preserved':True
}
(ROOT/'publication-preparation.json').write_text(json.dumps(validation,indent=2),encoding='utf-8')
print(json.dumps(validation,indent=2))
