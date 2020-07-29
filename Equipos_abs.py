import abc
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd

class Equipo(ABC):
    def __init__(self,_coste_ref = 0,_capacity = 0, _capacity_ref = 0, n = 0, _installed = True):
        self.capacity = _capacity
        self.capacity_ref = _capacity_ref
        self.coste_ref = _coste_ref
        self.n = n
        self.installed = _installed
        data_factors = np.array([[0.3, 0.5, 0.6],
                         [0.8, 0.6, 0.2],
                         [0.3, 0.3, 0.2],
                         [0.2, 0.2, 0.15],
                         [0.3, 0.3, 0.2],
                         [0.2, 0.2, 0.1],
                         [0.1, 0.1, 0.05],
                         [0.3, 0.4, 0.4],
                         [0.35, 0.25, 0.2],
                         [0.1, 0.1, 0.1]])

        self.Capital_factors = pd.DataFrame(data_factors,    
                               index=["fer", "fp", "fi", "fel", "fc", "fs", "fl", "OS", "D&E", "X"], 
                               columns=["Fluids", "Fluids-Solids", "Solids"])
    
    @abstractmethod
    def lang(self, fm = 1):
        pass
        
    def lang_true(self,C,fm = 1):
        C *= ((1+self.Capital_factors.loc["fp"]["Fluids"])*fm+(self.Capital_factors.loc["fer"]["Fluids"] + self.Capital_factors.loc["fel"]["Fluids"]
                                                        + self.Capital_factors.loc["fi"]["Fluids"] + self.Capital_factors.loc["fc"]["Fluids"]
                                                        + self.Capital_factors.loc["fs"]["Fluids"] + self.Capital_factors.loc["fl"]["Fluids"]))
        return C

    def william(self):
        C = self.coste_ref * (self.capacity / self.capacity_ref) ** self.n
        return C

    
class Boiler(Equipo):
    def __init__(self, _q, _p, _capacity = 0, _capacity_ref = 0, _coste_ref = 0, n = 0, _installed = True):
        super().__init__(_capacity,_capacity_ref,_coste_ref,n, _installed)
        self.q = _q
        self.p = _p
    
    def own_lang(self):
        """Return boiler cost. Inputs:
        Vapor production (kg/h): 5000 < Q < 800000
        Pressure (bar): 			   10 < p < 70
        fm = material factor"""

        assert type(self.installed) == bool

        if self.q < 5000 or self.q > 800000:
            print(f"    - WARNING: boiler vapor production out of method bounds, 5000 < Q < 800000. Results may not be accurate.")

        if self.p < 10 or self.p > 70:
            print(f"    - WARNING: boiler pressure out of method bounds, 10 < p < 70. Results may not be accurate.")

        if self.q < 20000:
            C = 106000 + 8.7*self.q
        elif self.q < 200000:
            if self.p < 15:
                C = 110000 + 4.5*self.q**0.9
            elif self.p < 40:
                C = 106000 + 8.7*self.q
            else:
                C = 110000 + 4.5*self.q**0.9
        else:
            C = 110000 + 4.5*self.q**0.9

        return C

    def lang(self, fm = 1):
        if self.n == 0:
            C = self.own_lang()
           
            if self.installed == True:
                C = self.lang_true(C,fm)
        else:
            C = self.william()
        return C


class Pump(Equipo):
    def __init__(self, _q, _capacity = 0, _capacity_ref = 0, _coste_ref = 0, n = 0, _installed = True):
        super().__init__(_capacity,_capacity_ref,_coste_ref,n, _installed)
        self.q = _q
    
    def lang(self, fm = 1):
        if self.n == 0:
            
            if self.q < 0.2 or self.q > 126:
                print(f"    - WARNING: pump caudal out of method bounds, 0.2 < Q (L/s) < 126. Results may not be accurate.")
    
            C = 6900 + 206*self.q**0.9
            if self.installed == True:
                C = self.lang_true(C,fm)
        else:
            C = self.william()
        return C


class Turbine(Equipo):
    def __init__(self, _kw, _capacity = 0, _capacity_ref = 0, _coste_ref = 0, n = 0, _installed = True):
        super().__init__(_capacity,_capacity_ref,_coste_ref,n, _installed)
        self.kw = _kw
    
    def lang(self, fm = 1):
        if self.n == 0:
            
            if self.kw < 100 or self.kw > 20000:
                print(f"    - WARNING: steam turbine power out of method bounds, 100 < kW < 20000. Results may not be accurate.")
    
            C = -12000 + 1630*self.kw**0.75
            if self.installed == True:
                C = self.lang_true(C,fm)
        else:
            C = self.william()
        return C


class Condenser(Equipo):
    def __init__(self, _capacity = 0, _capacity_ref = 0, _coste_ref = 0, n = 0, _installed = True):
        super().__init__(_capacity,_capacity_ref,_coste_ref,n, _installed)

    
    def lang(self, fm = 1):
        if self.n == 0:
            if self.installed == True:
                C = self.lang_true(C,fm)
                
        else:
            C = self.william()
        return C


    
