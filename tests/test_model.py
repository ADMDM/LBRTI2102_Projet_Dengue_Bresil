"""Run with: python -m unittest discover -s tests -v"""
import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import numpy as np
from dengue_rio.model import SEIRParameters,simulate_weekly

class SEIRTests(unittest.TestCase):
    def test_conservation(self):
        p=SEIRParameters(10000,.2,.15,.5)
        x,reports,beta=simulate_weekly(p,[8995,3,2,1000,0],.5,np.zeros(10),np.zeros(10))
        np.testing.assert_allclose(x[:,:4].sum(axis=1),p.N,atol=1e-5)
        self.assertTrue(np.all(reports>=0))
        np.testing.assert_allclose(reports,p.rho*np.diff(x[:,4]))
    def test_baseline_nesting(self):
        p=SEIRParameters(10000,.2,.15)
        t=np.linspace(-1,1,8)
        a=simulate_weekly(p,[9990,5,5,0,0],.3,t,t)
        b=simulate_weekly(p,[9990,5,5,0,0],.3,t,t,0,0)
        np.testing.assert_allclose(a[0],b[0])
        np.testing.assert_allclose(a[2],.3)
if __name__=="__main__":
    unittest.main()
