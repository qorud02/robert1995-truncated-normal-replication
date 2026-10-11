"""Independent replication of Robert's (1995) univariate numerical results.
No original implementation is imported or copied. See SOURCE_TRACE.md.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math, platform, sys, time
from pathlib import Path
import numpy as np

BASE = Path(__file__).resolve().parent
SQRT2 = math.sqrt(2.0)
SQRT2PI = math.sqrt(2.0 * math.pi)

def alpha_star(a):
    return (a + math.hypot(a, 2.0)) / 2.0

def survival(x):
    return 0.5 * math.erfc(x / SQRT2)

def mass(a, b):
    return survival(a) if math.isinf(b) else survival(a) - survival(b)

def probabilities(a, b=math.inf):
    al = alpha_star(a)
    lm = math.log(mass(a, b))
    exponential = math.exp(math.log(al) + al*a - al*al/2 + math.log(SQRT2PI) + lm)
    if math.isinf(b):
        return {'exponential': exponential}
    closest = min(max(0.0, a), b)
    uniform = math.exp(closest*closest/2 + math.log(SQRT2PI) + lm - math.log(b-a))
    return {'exponential': exponential, 'uniform': uniform}

def boundary_original(a):
    r = math.sqrt(a*a + 4)
    return a + 2*math.sqrt(math.e)/(a+r) * math.exp((a*a-a*r)/4)

def boundary_reduced(a):
    al = alpha_star(a)
    return a + math.exp(1/(2*al*al))/al

def moment_targets(a, b):
    m = mass(a, b)
    pa = math.exp(-a*a/2)/SQRT2PI
    pb = 0.0 if math.isinf(b) else math.exp(-b*b/2)/SQRT2PI
    mu = (pa-pb)/m
    second = 1 + (a*pa-(0 if math.isinf(b) else b*pb))/m
    return mu, second, second-mu*mu

def wilson(k, n):
    z = 1.959963984540054
    p = k/n
    den = 1+z*z/n
    center = (p+z*z/(2*n))/den
    half = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return center-half, center+half

def run_cell(a,b,method,n,seed, family_size=47):
    rng = np.random.Generator(np.random.PCG64DXSM(seed))
    if method == 'exponential':
        al = alpha_star(a)
        proposal = a+rng.exponential(1/al, n)
        probability = np.exp(-0.5*(proposal-al)**2)
        keep = (proposal <= b) & (rng.random(n) <= probability)
    else:
        proposal = rng.uniform(a,b,n)
        closest = min(max(0.0,a),b)
        keep = rng.random(n) <= np.exp(0.5*(closest*closest-proposal*proposal))
    values = proposal[keep]
    k = len(values)
    target = probabilities(a,b)[method]
    lo,hi = wilson(k,n)
    true_mean, true_second, true_var = moment_targets(a,b)
    empirical_mean = float(np.mean(values))
    se_mean = float(np.std(values,ddof=1)/math.sqrt(k))
    sorted_x = np.sort(values)
    sa, norm_mass = survival(a), mass(a,b)
    cdf = np.fromiter(((sa-survival(float(x)))/norm_mass for x in sorted_x),dtype=float,count=k)
    upper = np.arange(1,k+1)/k
    lower = np.arange(k)/k
    ks = float(max(np.max(upper-cdf),np.max(cdf-lower)))
    dkw = math.sqrt(math.log(2*family_size/0.01)/(2*k))
    return dict(a=a,b=None if math.isinf(b) else b,method=method,proposals=n,accepted=k,
                empirical_probability=k/n,theoretical_probability=target,wilson95_low=lo,wilson95_high=hi,
                probability_z=(k/n-target)/math.sqrt(target*(1-target)/n),
                sample_mean=empirical_mean,target_mean=true_mean,mean_mcse=se_mean,
                mean_z=(empirical_mean-true_mean)/se_mean,
                sample_second_moment=float(np.mean(values*values)),target_second_moment=true_second,
                sample_variance=float(np.var(values,ddof=1)),target_variance=true_var,
                ks_distance=ks,dkw_familywise_99_bound=dkw,dkw_within_bound=ks<=dkw,
                support_pass=bool(np.all(values>=a) and np.all(values<=b)),
                seed_entropy=seed.entropy,seed_spawn_key=list(seed.spawn_key))

def save_csv(path, rows):
    with path.open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader();w.writerows(rows)

def plots(rows21,rows22,boundaries):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(6,4))
    ax.plot([r['a'] for r in boundaries],[r['b_original'] for r in boundaries],color='#173d56',lw=2)
    ax.set(xlabel='Lower truncation a',ylabel='Switching upper truncation b*',xlim=(0,4))
    ax.grid(alpha=.2); fig.tight_layout()
    fig.savefig(BASE/'figure21_replication.pdf');fig.savefig(BASE/'figure21_replication.png',dpi=300);plt.close(fig)
    fig,ax=plt.subplots(figsize=(6,4))
    ax.plot([r['a'] for r in rows21],[r['calculated'] for r in rows21],marker='o',label='Optimized exponential')
    ax.plot([r['a'] for r in rows21],[survival(r['a']) for r in rows21],marker='s',label='Repeated normal')
    ax.set(xlabel='Lower truncation a',ylabel='Acceptance per proposal',ylim=(0,1.02));ax.legend();ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(BASE/'acceptance_comparison.pdf');fig.savefig(BASE/'acceptance_comparison.png',dpi=300);plt.close(fig)

def main():
    p=argparse.ArgumentParser();p.add_argument('--skip-plots',action='store_true');args=p.parse_args()
    start=time.perf_counter()
    anchors=json.loads((BASE/'anchors.json').read_text(encoding='utf8'))
    protocol=json.loads((BASE/'protocol.json').read_text(encoding='utf8'))
    n=protocol['proposals_per_method_and_setting']
    rows21=[]
    for a,original in zip(anchors['table21']['a'],anchors['table21']['printed']):
        calc=probabilities(a)['exponential']
        rows21.append(dict(a=a,original_printed=original,calculated=calc,rounded=f'{calc:.3f}',matches=abs(calc-original)<=.00050000001,difference=calc-original))
    rows22=[]
    for width,printed_row in zip(anchors['table22']['width'],anchors['table22']['printed']):
        for a,original in zip(anchors['table22']['a'],printed_row):
            probs=probabilities(a,a+width)
            method=max(probs,key=probs.get);calc=probs[method]
            rows22.append(dict(a=a,width=width,original_printed=original,calculated=calc,rounded=f'{calc:.3f}',matches=abs(calc-original)<=.00050000001,selected_method=method,uniform_probability=probs['uniform'],exponential_probability=probs['exponential'],difference=calc-original))
    boundaries=[]
    for a in np.linspace(0,4,401):
        a=float(a);original=boundary_original(a);reduced=boundary_reduced(a)
        probs=probabilities(a,original)
        boundaries.append(dict(a=a,b_original=original,b_reduced=reduced,formula_abs_difference=abs(original-reduced),rate_abs_difference=abs(probs['uniform']-probs['exponential'])))
    cells=[(r['a'],math.inf,'exponential') for r in rows21]
    cells += [(r['a'],r['a']+r['width'],method) for r in rows22 for method in ['uniform','exponential']]
    children=np.random.SeedSequence(protocol['base_seed']).spawn(len(cells))
    mc=[]
    for i,((a,b,method),seed) in enumerate(zip(cells,children)):
        mc.append(run_cell(a,b,method,n,seed,len(cells)))
        print(f'cell {i+1}/{len(cells)} {method} a={a} b={b}',flush=True)
    save_csv(BASE/'table21.csv',rows21);save_csv(BASE/'table22.csv',rows22);save_csv(BASE/'boundary.csv',boundaries);save_csv(BASE/'monte_carlo.csv',mc)
    summary=dict(anchor_cells=27,anchor_matches=sum(r['matches'] for r in rows21+rows22),
                 table21_matches=sum(r['matches'] for r in rows21),table22_matches=sum(r['matches'] for r in rows22),
                 max_anchor_abs_difference=max(abs(r['difference']) for r in rows21+rows22),
                 boundary_points=len(boundaries),max_boundary_formula_difference=max(r['formula_abs_difference'] for r in boundaries),
                 max_boundary_rate_difference=max(r['rate_abs_difference'] for r in boundaries),
                 mc_cells=len(mc),mc_proposals=n*len(mc),wilson95_containing_rate=sum(r['wilson95_low']<=r['theoretical_probability']<=r['wilson95_high'] for r in mc),
                 max_abs_probability_z=max(abs(r['probability_z']) for r in mc),max_abs_mean_z=max(abs(r['mean_z']) for r in mc),
                 all_support_pass=all(r['support_pass'] for r in mc),all_dkw_familywise99_pass=all(r['dkw_within_bound'] for r in mc),
                 elapsed_seconds=time.perf_counter()-start,python=sys.version,numpy=np.__version__,platform=platform.platform(),
                 protocol_sha256=hashlib.sha256((BASE/'protocol.json').read_bytes()).hexdigest(),
                 script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (BASE/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
    if not args.skip_plots: plots(rows21,rows22,boundaries)
    print(json.dumps(summary,indent=2))
    assert len(rows21)+len(rows22)==27
    assert all(0 < float(r['calculated']) <= 1 for r in rows21+rows22)
    assert summary['max_boundary_rate_difference']<2e-12
    assert summary['all_support_pass'] and summary['all_dkw_familywise99_pass']
if __name__=='__main__':main()
