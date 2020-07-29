from Equipos_abs import Equipo,Boiler,Turbine,Condenser,Pump
from Procesos import Procesos
boiler    = Boiler(10000, 70)
turbine   = Turbine(1500)
condenser = Condenser(400000,10000,15000,0.8)
pump      = Pump(2.84)
equipos = []
equipos.append(boiler)
equipos.append(turbine)
equipos.append(condenser)
equipos.append(pump)

capacity_factor = 0.9
water       = 1.29 * 10 * 8760 * capacity_factor
salaries    = 4 * 3 * 30000
years = 20
sales = 1500 * 0.05 * 8760 * capacity_factor
annual_percent = 0.07
proceso = Procesos("Proceso1",equipos,salaries,water,years,sales)
_, interest, principal = proceso.loan(0.6, 0.04, 10)
dep_array = proceso.depreciation(annual_percent)
proceso.financial_model(interest, principal, dep_array)
proceso.results(0.053)
print(proceso.payback())
