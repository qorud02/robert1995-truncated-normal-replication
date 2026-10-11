"""Independent numerical integration and saved-output audit.
Integration kernels are written independently of the production closed forms.
"""
import csv,json,math,unittest
from pathlib import Path
from scipy.integrate import quad
from scipy.optimize import brentq
import replicate as production
BASE=Path(__file__).resolve().parent
QUADRATURE_RECORDS=[]
ROOT_RECORDS=[]

def integral_targets(a,b):
    kernel=lambda z:math.exp(-0.5*(z*z-a*a))
    i0=quad(kernel,a,b,epsabs=2e-13,epsrel=2e-13)[0]
    i1=quad(lambda z:z*kernel(z),a,b,epsabs=2e-13,epsrel=2e-13)[0]
    i2=quad(lambda z:z*z*kernel(z),a,b,epsabs=2e-13,epsrel=2e-13)[0]
    al=(a+math.sqrt(a*a+4))/2
    exp_rate=al*math.exp(-0.5*(a-al)**2)*i0
    uniform=None if math.isinf(b) else i0/(b-a)
    return exp_rate,uniform,i1/i0,i2/i0

class IndependentAudit(unittest.TestCase):
    def test_table_formulas_against_quadrature(self):
        for a in [0,.5,1,1.5,2,2.5,3,8,12]:
            for width in [.1,.5,1,2,math.inf]:
                b=a+width
                er,ur,mu,m2=integral_targets(a,b)
                rates=production.probabilities(a,b)
                QUADRATURE_RECORDS.append(dict(a=a,b=None if math.isinf(b) else b,exponential_integral=er,exponential_closed=rates['exponential'],uniform_integral=ur,mean_integral=mu,second_integral=m2,probability_abs_error=abs(er-rates['exponential'])))
                self.assertAlmostEqual(er,rates['exponential'],delta=2e-12)
                if ur is not None:self.assertAlmostEqual(ur,rates['uniform'],delta=2e-12)
                pmu,pm2,_=production.moment_targets(a,b)
                self.assertAlmostEqual(mu,pmu,delta=1e-10)
                self.assertAlmostEqual(m2,pm2,delta=1e-9)
    def test_switch_boundary_by_numerical_root(self):
        for a in [0,.1,.5,1,2,3,4,8,12]:
            def gap(width):
                er,ur,_,_=integral_targets(a,a+width)
                return er-ur
            width=brentq(gap,1e-4,5,xtol=1e-13)
            ROOT_RECORDS.append(dict(a=a,numerical_upper_endpoint=a+width,formula_upper_endpoint=production.boundary_original(a),absolute_error=abs(a+width-production.boundary_original(a))))
            self.assertAlmostEqual(a+width,production.boundary_original(a),delta=1e-10)
    def test_printed_anchors_and_saved_mc(self):
        allrows=[]
        for name in ['table21.csv','table22.csv']:
            allrows += list(csv.DictReader((BASE/name).open()))
        self.assertEqual(len(allrows),27)
        for r in allrows:
            self.assertEqual(r['matches']=='True', abs(float(r['calculated'])-float(r['original_printed']))<=.00050000001)
        mc=list(csv.DictReader((BASE/'monte_carlo.csv').open()))
        self.assertEqual(len(mc),47)
        self.assertEqual(sum(int(r['proposals']) for r in mc),23500000)
        max_error=0.0
        for r in mc:
            a=float(r['a']);b=math.inf if not r['b'] else float(r['b'])
            er,ur,mu,m2=integral_targets(a,b)
            expected=er if r['method']=='exponential' else ur
            max_error=max(max_error,abs(expected-float(r['theoretical_probability'])))
            self.assertAlmostEqual(expected,float(r['theoretical_probability']),delta=2e-12)
            self.assertAlmostEqual(mu,float(r['target_mean']),delta=1e-11)
            self.assertAlmostEqual(m2,float(r['target_second_moment']),delta=1e-10)
            n=int(r['proposals']);k=int(r['accepted'])
            self.assertAlmostEqual(k/n,float(r['empirical_probability']),delta=1e-15)
            self.assertTrue(r['support_pass']=='True')
            self.assertLessEqual(float(r['ks_distance']),float(r['dkw_familywise_99_bound']))
        self.assertLess(max_error,2e-12)
    def test_exponential_optimization_and_rate_order(self):
        for a in [0,.5,1,2,3,8,12]:
            al=production.alpha_star(a)
            def rate(x):
                if x>=a:
                    return x*math.exp(x*a-x*x/2)*math.sqrt(2*math.pi)*production.survival(a)
                return x*math.exp(a*a/2)*math.sqrt(2*math.pi)*production.survival(a)
            optimal=production.probabilities(a)['exponential']
            for candidate in [al*.5,al*.9,al*1.1,al*2]:
                self.assertLessEqual(rate(candidate),optimal+2e-14)
            self.assertGreater(optimal,production.survival(a))

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(IndependentAudit)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    record=dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),passed=result.wasSuccessful(),
                checks='Independent quadrature:45intervals;9switchingroots;27printedanchors;47MonteCarlo summaries;optimality perturbations at7points',
                limitations='Does not infer journal acceptance, original timing, or multivariate Gibbs convergence.')
    record['max_probability_quad_abs_error']=max(r['probability_abs_error'] for r in QUADRATURE_RECORDS)
    record['max_switch_root_abs_error']=max(r['absolute_error'] for r in ROOT_RECORDS)
    production.save_csv(BASE/'quadrature.csv',QUADRATURE_RECORDS)
    production.save_csv(BASE/'switch-root.csv',ROOT_RECORDS)
    (BASE/'verification.json').write_text(json.dumps(record,indent=2))
    raise SystemExit(0 if result.wasSuccessful() else 1)
