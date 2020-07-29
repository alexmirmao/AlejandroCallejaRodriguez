from Equipos_abs import Equipo
import numpy as np
import pandas as pd
import abc
from numpy_financial import pmt, ipmt, ppmt, npv, irr
class Procesos():
    def __init__(self, _name, _equipos, _salaries,_waters, _years, _sales):
        self.name = _name
        self.equipos = _equipos
        self.salaries = _salaries
        self.waters = _waters
        self.years = _years
        self.sales = _sales
    
    def capex(self):
        sum = 0
        for equipo in self.equipos:
            sum += equipo.lang()
        
        return sum

    def loan(self,prestamo, interest, years):
        """Compute annual payment of a loan. Inputs:
        quantity [monetary units] == investment which will be funded
        interest [as fraction of unity] == annual interest
        years == number of yeras to return the loan."""
        quantity = prestamo * self.capex()
        assert quantity > 0
        assert interest >= 0 and interest <= 1
        assert years > 1

        loan_payment   = pmt(interest, years, quantity)
        loan_interest  = ipmt(interest, np.arange(years) + 1, years, quantity)
        loan_principal = ppmt(interest, np.arange(years) + 1, years, quantity)

        return loan_payment, loan_interest, loan_principal


    def depreciation(self,annual_percent, residual_value=0):
        """Compute annual depreciation of investment. Inputs:
        annual_percent [as fraction of unity] == annual percent of depreciation.
        capex [monetary units] == capital expenditure
        residual_value[monetary units] == plant value at the end of its life."""

        assert annual_percent >= 0 and annual_percent <= 1

        annual_depreciation = []
        prev = 1

        while True:
            if prev < annual_percent:
                annual_depreciation.append(prev)
                break
            annual_depreciation.append(annual_percent)
            prev = prev - annual_percent

        depreciation_array = -1 * np.array(annual_depreciation) * (self.capex() - residual_value)

        return depreciation_array


    def financial_model(self,interest, principal, dep_array):
        capex = self.capex()
        investment    = np.array([-capex*0.4] + [0 for i in range(self.years-1)])
        depreciation  = np.hstack(([0], dep_array, [0 for i in range(self.years-1-len(dep_array))]))
        loan_prin     = np.hstack(([0], principal, [0 for i in range(self.years-1-len(principal))]))
        loan_int      = np.hstack(([0], interest, [0 for i in range(self.years-1-len(interest))]))

        sales_array    = np.zeros(self.years)
        water_array    = np.zeros(self.years)
        salaries_array = np.zeros(self.years)   

        for i in range(self.years):
            if i == 0:
                sales_array[i]    = 0
                water_array[i]    = 0
                salaries_array[i] = 0
            elif i == 1:
                sales_array[i]    = self.sales
                water_array[i]    = -1*self.waters
                salaries_array[i] = -1*self.salaries
            else:
                sales_array[i]    = sales_array[i-1]*1.03
                water_array[i]    = water_array[i-1]*1.03
                salaries_array[i] = salaries_array[i-1]*1.02

        ebt   = np.vstack((investment, depreciation, loan_int, sales_array, water_array, salaries_array)).sum(axis=0)
        taxes = ebt * -0.3
        for i in range(len(taxes)):
            if taxes[i] > 0:
                taxes[i] = 0
        eat = ebt - taxes
        cash_flow = eat - depreciation + loan_prin
        cumulative_cash_flow = np.cumsum(cash_flow)

        data = np.vstack((investment, sales_array, depreciation, loan_prin, loan_int, salaries_array, water_array, ebt, 
                        taxes, eat, cash_flow, cumulative_cash_flow))
        self.df   = pd.DataFrame(data,
                            index=['Investment', 'Sales', 'Depreciation', 'Loan principal', 'Loan interest', 'Salaries',
                                'Water', 'EBT', 'Taxes', 'EAT', 'Cash Flow', 'Cumulative Cash Flow'],
                            columns=[i for i in range(self.years)])
        
    def financial_metrics(self,discount_rate):
        return irr(self.df.loc['Cash Flow']),npv(discount_rate, self.df.loc['Cash Flow'])

    def results(self,discount_rate):
        irr,npv = self.financial_metrics(discount_rate)
        print(self.df)
        print(f"The project has a net present value of {'{:,.2f}'.format(npv)}€ and an internal rate of return of {round(irr*100, 2)}%")
        
    def payback(self):
        new_df = self.df.loc['Cumulative Cash Flow']
        r_init = new_df[0]
        i = 2
        sum = new_df[1]
        acumulado = sum + r_init
        
        while acumulado < 0 and i < self.years:
            print("HOLAAAAAAA",new_df[i])
            print("acumuladooo", acumulado)
            sum += new_df[i]
            i += 1
            acumulado = sum + r_init
        if i >= self.years:
            return "No hay periodo de recuperacion suficiente"
        anio = i - 2#anio anterior al que se sobrepasa la deuda
        acumulado_anio_anterior= np.sum(self.df.loc['Cumulative Cash Flow'][1:anio+1])
        falta = -(acumulado_anio_anterior + r_init)
        decimales = falta / self.df.loc['Cumulative Cash Flow'][anio+1]
        #divisor = acumulado + r_init
        
        return anio + decimales