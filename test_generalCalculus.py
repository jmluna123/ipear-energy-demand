import pytest
import math
import numpy as np
import pandas as pd
from modules.generalCalculus import *

def test_calculate_E_elec_cultivo():
    # Caso de prueba 1
    assert calculate_E_elec_cultivo(5, 3, 1.15) == 17.25
    
    # Caso de prueba 2
    assert calculate_E_elec_cultivo(10, 4, 1.10) == 44.0
    
    # Caso de prueba 3
    assert calculate_E_elec_cultivo(2.5, 2, 1.05) == 5.25


def test_calculate_E_elec_cultivo_anual():
    # Caso de prueba 1
    assert calculate_E_elec_cultivo_anual(17.25, 7, 6) == pytest.approx(2898)
    
    # Caso de prueba 2
    assert calculate_E_elec_cultivo_anual(44.0, 5, 4) == pytest.approx(3520)
    

def test_calculate_EDTC():
    cargas = [{'distribución': '01:30', 'cantidad': 2, 'potencia': 100}, 
              {'distribución': '02:45', 'cantidad': 3, 'potencia': 200}]
    assert calculate_EDTC(cargas) == pytest.approx(1.95)

def test_calculate_IPGDMAX():
    Pt = 500
    cargas = [{'horas': '2:30', 'cantidad': 3, 'potencia': 100}]
    resultado = calculate_IPGDMAX(Pt, cargas)
    assert resultado == pytest.approx(500.3)

def test_calculate_daily_energy():
    # Datos de prueba
    cantidad = 3
    potencia = 100
    horas = 150

    # Llamamos a la función
    resultado = calculate_daily_energy(cantidad, potencia, horas)

    # Verificamos el resultado esperado
    assert resultado == pytest.approx(0.75)  # El resultado esperado debe ser 12.5

# Pruebas unitarias para calculate_sum_potence
def test_calculate_sum_potence():
    # Datos de prueba
    amount = 5
    potence = 200

    # Llamamos a la función
    resultado = calculate_sum_potence(amount, potence)

    # Verificamos el resultado esperado
    assert resultado == 1  # El resultado esperado debe ser 1.0

# Pruebas unitarias para calculate_E_elec
def test_calculate_E_elec():
    # Datos de prueba
    E_elec_cultivo = 150
    EDTC = 50

    # Llamamos a la función
    resultado = calculate_E_elec(E_elec_cultivo, EDTC)

    # Verificamos el resultado esperado
    assert resultado == 200

# Pruebas unitarias para calculate_cIPAE
def test_calculate_cIPAE():
    # Datos de prueba
    C_acu = 100
    V_T_acu = 12
    I_max_charge = 0.5

    # Llamamos a la función
    resultado = calculate_cIPAE(C_acu, V_T_acu, I_max_charge)

    # Verificamos el resultado esperado
    assert resultado == pytest.approx(16.6666666667) 

def test_calculate_E_elec_anual():
    # Datos de prueba
    E_elec_cultivo_anual = 1000
    EDTC = 5
    dias_consumo_semana = 3

    # Llamamos a la función
    resultado = calculate_E_elec_anual(E_elec_cultivo_anual, EDTC, dias_consumo_semana)

    # Calculamos el resultado esperado
    resultado_esperado = E_elec_cultivo_anual + (EDTC * 52 * dias_consumo_semana)

    # Verificamos el resultado esperado
    assert resultado == resultado_esperado

def test_generate_hours_dist():
    # Datos de prueba
    cargas = [
        {'cantidad': 2, 'potencia': 100, 'distribución': [('08:00', '10:00'), ('18:00', '20:00')]},
        {'cantidad': 3, 'potencia': 50, 'distribución': [('09:00', '12:00'), ('15:00', '18:00')]},
    ]

    # Llamamos a la función
    resultado = generate_hours_dist(cargas)

    # Verificamos que la suma de las energías diarias sea correcta
    assert resultado[8] == 200  # Energía diaria para las 08:00

def test_calculate_total_radiation():
    # Datos de prueba
    Gd = 5

    # Llamamos a la función
    resultado = calculate_total_radiation(Gd)

    # Verificamos que el resultado sea correcto
    assert resultado == (Gd * 12 * 365)

def test_calculate_T_cell():
    # Datos de prueba
    T_amb = 30.0
    G = 800.0
    NOCT = 45.0

    # Llamamos a la función
    resultado = calculate_T_cell(T_amb, G, NOCT)

    # Verificamos que el resultado sea correcto
    assert resultado == (T_amb + ((NOCT - 20.0) / 800.0) * G)


def test_calculate_P_out():
    # Datos de prueba
    T_cell = 35.0
    alpha = 0.4
    P_STC = 1000.0
    G = 900.0

    # Llamamos a la función
    resultado = calculate_P_out(T_cell, alpha, P_STC, G)

    # Verificamos que el resultado sea correcto
    assert resultado == (P_STC * ((G / 1000) * (1 + (alpha / 100) * (T_cell - 25))))


def test_min_area_panels():
    # Datos de prueba
    A = 1.5
    N_panels = 10

    # Llamamos a la función
    resultado = min_area_panels(A, N_panels)

    # Verificamos que el resultado sea correcto
    assert resultado == (A * N_panels)


def test_calculate_Nominal_Potence():
    # Datos de prueba
    N_total = 5
    P_STC = 1000.0
    P_out = 900.0

    # Llamamos a la función
    resultado = calculate_Nominal_Potence(N_total, P_STC, P_out)

    # Verificamos que el resultado sea correcto
    assert resultado == (N_total * P_out)


def test_calculate_Nominal_Potence_operating():
    # Datos de prueba
    N_panels = 10
    P_out = 900.0

    # Llamamos a la función
    resultado = calculate_Nominal_Potence_operating(N_panels, P_out)

    # Verificamos que el resultado sea correcto
    assert resultado == (N_panels * P_out)


def test_calculate_Pt():
    # Datos de prueba
    Pw = 100.0
    Ha = 5.0
    factor = 0.7457

    # Llamamos a la función
    resultado = calculate_Pt(Pw, Ha, factor)

    # Verificamos que el resultado sea correcto
    assert resultado == (Pw * factor * Ha)


def test_daily_mean_energy_req():
    # Datos de prueba
    Pt = 500.0
    hours = 6
    fs = 1.2

    # Llamamos a la función
    resultado = daily_mean_energy_req(Pt, hours, fs)

    # Verificamos que el resultado sea correcto
    assert resultado == (Pt * hours * fs)


def test_Hs_daily_mean_radiation():
    # Datos de prueba
    G = 1000.0
    daily_sun_hours = 8

    # Llamamos a la función
    resultado = Hs_daily_mean_radiation(G, daily_sun_hours)

    # Verificamos que el resultado sea correcto
    assert resultado == (G * daily_sun_hours)

def test_obtain_rad_mean_last_years():
    # Datos de prueba
    df = pd.DataFrame({'fecha': ['2010-01-01', '2010-01-02', '2010-01-03'],
                       'radiacion': [5.0, 7.0, 6.0]})
    daily_sun_hours = 24
    years = 2

    # Llamamos a la función
    resultado = obtain_rad_mean_last_years(df, daily_sun_hours, years)

    # Verificamos que el resultado sea correcto
    assert resultado.equals(pd.Series({'radiacion': 6.5}))

def test_obtain_worst_rad_mean():
    # Datos de prueba
    rad_mean = pd.Series({'radiacion1': 5.0, 'radiacion2': 7.0, 'radiacion3': 6.0})

    # Llamamos a la función
    resultado = obtain_worst_rad_mean(rad_mean)

    # Verificamos que el resultado sea correcto
    assert resultado == pytest.approx(5.0)

def test_Y():
    # Datos de prueba
    E_elec = 1000
    Hs = 8.0

    # Llamamos a la función
    resultado = Y(E_elec, Hs)

    # Verificamos que el resultado sea correcto
    assert resultado == pytest.approx(125.0)

def test_E_panel_energy():
    # Datos de prueba
    P_out = 300
    daily_sun_hours = 6
    conv_kW = 'kW'
    conv_W = 'W'

    # Llamamos a la función con conversión a kW
    resultado_kW = E_panel_energy(P_out, daily_sun_hours, conv_kW)

    # Llamamos a la función con conversión a W
    resultado_W = E_panel_energy(P_out, daily_sun_hours, conv_W)

    # Verificamos que los resultados sean correctos
    assert resultado_kW == pytest.approx(1.8)
    assert resultado_W == pytest.approx(1800)

def test_calculate_N_panels_theoretical():
    # Datos de prueba
    E_elec = 1000
    E_panel = 200
    fsp = 1.1

    # Llamamos a la función
    resultado = calculate_N_panels_theoretical(E_elec, E_panel, fsp)

    # Verificamos que el resultado sea correcto
    assert resultado == 6


def test_calculate_N_serie():
    # Datos de prueba
    V_tacu = 24
    V_mod = 6

    # Llamamos a la función
    resultado = calculate_N_serie(V_tacu, V_mod)

    # Verificamos que el resultado sea correcto
    assert resultado == 4


def test_calculate_N_paralel():
    # Datos de prueba
    N_panels = 8
    N_serie = 2

    # Llamamos a la función
    resultado = calculate_N_paralel(N_panels, N_serie)

    # Verificamos que el resultado sea correcto
    assert resultado == 4


def test_calculate_N_panels_final():
    # Datos de prueba
    N_serie = 3
    N_paralel = 5

    # Llamamos a la función
    resultado = calculate_N_panels_final(N_serie, N_paralel)

    # Verificamos que el resultado sea correcto
    assert resultado == 15

def test_calculate_peak_power():
    # Datos de prueba
    N_panels = 5
    P_STC = 250

    # Llamamos a la función
    resultado = calculate_peak_power(N_panels, P_STC)

    # Verificamos que el resultado sea correcto
    assert resultado == 1250


def test_calculate_peak_output_intensity():
    # Datos de prueba
    N_paralel = 4
    I_P_mod = 5

    # Llamamos a la función
    resultado = calculate_peak_output_intensity(N_paralel, I_P_mod)

    # Verificamos que el resultado sea correcto
    assert resultado == 20


def test_calculate_intensity_short_circuit():
    # Datos de prueba
    N_paralel = 3
    I_SC_mod = 8

    # Llamamos a la función
    resultado = calculate_intensity_short_circuit(N_paralel, I_SC_mod)

    # Verificamos que el resultado sea correcto
    assert resultado == 24


def test_calculate_output_nominal_voltage():
    # Datos de prueba
    V_mod = 20
    N_serie = 6

    # Llamamos a la función
    resultado = calculate_output_nominal_voltage(V_mod, N_serie)

    # Verificamos que el resultado sea correcto
    assert resultado == 120


def test_calculate_peak_output_volage():
    # Datos de prueba
    V_P_mod = 18
    N_serie = 5

    # Llamamos a la función
    resultado = calculate_peak_output_volage(V_P_mod, N_serie)

    # Verificamos que el resultado sea correcto
    assert resultado == 90


def test_calculate_voltage_open_circuit():
    # Datos de prueba
    V_OC_mod = 22
    N_serie = 4

    # Llamamos a la función
    resultado = calculate_voltage_open_circuit(V_OC_mod, N_serie)

    # Verificamos que el resultado sea correcto
    assert resultado == 88


def test_calculate_panels_area():
    # Datos de prueba
    N_panels = 6
    width = 1.2
    height = 1.6

    # Llamamos a la función
    resultado = calculate_panels_area(N_panels, width, height)

    # Verificamos que el resultado sea correcto
    assert resultado == 11.52

# def test_coords_centroid():
#     # Datos de prueba
#     arr = np.array([[0, 0, 0, 0],
#                     [0, 1, 0, 0],
#                     [0, 0, 0, 0],
#                     [0, 0, 0, 0]])

#     # Llamamos a la función
#     resultado = coords_centroid(arr)

#     # Verificamos que el resultado sea correcto
#     assert resultado == (2, 1)


# def test_calculate_distances_charge():
#     # Datos de prueba
#     P = (2, 2)
#     charges = [(1, 1), (3, 3), (0, 0)]
#     resolution = 5

#     # Llamamos a la función
#     resultado = calculate_distances_charge(P, charges, resolution)

#     # Verificamos que el resultado sea correcto
#     assert resultado == [1.4142135623730951, 1.4142135623730951, 3.16227766016838]


# def test_calculate_distances_charge_with_default_resolution():
#     # Datos de prueba
#     P = (2, 2)
#     charges = [(1, 1), (3, 3), (0, 0)]

#     # Llamamos a la función sin especificar la resolución
#     resultado = calculate_distances_charge(P, charges)

#     # Verificamos que el resultado sea correcto
#     assert resultado == [1.0, 1.0, 2.8284271247461903]

def test_calculate_E():
    # Datos de prueba
    C = 10
    V_acu = 5

    # Llamamos a la función
    resultado = calculate_E(C, V_acu)

    # Verificamos que el resultado sea correcto
    assert resultado == 50


def test_calculate_E_acumulation_system():
    # Datos de prueba
    N_D = 8
    P_D_max = 100
    E_elec_max = 1000
    fs = 1.15

    # Llamamos a la función
    resultado = calculate_E_acumulation_system(N_D, P_D_max, E_elec_max, fs)

    # Verificamos que el resultado sea correcto
    assert resultado == 92


def test_calculate_C_T():
    # Datos de prueba
    E_acu = 500
    V_T_acu = 10
    E_elec_max = 1000
    P_D_diaria = 50
    N_D = 10
    fs = 1.1

    # Llamamos a la función
    resultado = calculate_C_T(E_acu, V_T_acu, E_elec_max, P_D_diaria, N_D, fs)

    # Verificamos que el resultado sea correcto
    assert resultado == pytest.approx(50)


def test_calculate_C_T_with_C_min_greater_than_C_T():
    # Datos de prueba
    E_acu = 500
    V_T_acu = 10
    E_elec_max = 1000
    P_D_diaria = 150
    N_D = 10
    fs = 1.1

    # Llamamos a la función
    resultado = calculate_C_T(E_acu, V_T_acu, E_elec_max, P_D_diaria, N_D, fs)

    # Verificamos que el resultado sea correcto
    assert resultado == 50

def test_calculate_N_accumulators():
    # Datos de prueba
    V_T_acu = 100
    V_acu = 10

    # Llamamos a la función
    resultado = calculate_N_accumulators(V_T_acu, V_acu)

    # Verificamos que el resultado sea correcto
    assert resultado == 10


def test_calculate_N_paralel_branches():
    # Datos de prueba
    C_T = 100
    C = 10

    # Llamamos a la función
    resultado = calculate_N_paralel_branches(C_T, C)

    # Verificamos que el resultado sea correcto
    assert resultado == 10


def test_calculate_N_total_accumulators():
    # Datos de prueba
    N_s_acu = 5
    N_p_acu = 8

    # Llamamos a la función
    resultado = calculate_N_total_accumulators(N_s_acu, N_p_acu)

    # Verificamos que el resultado sea correcto
    assert resultado == 40

def test_calculate_nominal_voltage():
    # Datos de prueba
    V_T_acu = 100

    # Llamamos a la función
    resultado = calculate_nominal_voltage(V_T_acu)

    # Verificamos que el resultado sea correcto
    assert resultado == 125


def test_calculate_nominal_intensity_switch():
    # Datos de prueba
    N_paralel_max = 10
    I_SC_mod = 2

    # Llamamos a la función
    resultado = calculate_nominal_intensity_switch(N_paralel_max, I_SC_mod)

    # Verificamos que el resultado sea correcto
    assert resultado == 25


def test_calculate_nominal_battery_coupling_switch():
    # Datos de prueba
    I_max_inv = 5

    # Llamamos a la función
    resultado = calculate_nominal_battery_coupling_switch(I_max_inv)

    # Verificamos que el resultado sea correcto
    assert resultado == 6.25


def test_calculate_count_regulators():
    # Datos de prueba
    N_panels = 20
    N_serie = 2
    N_paralel_max = 5

    # Llamamos a la función
    resultado = calculate_count_regulators(N_panels, N_serie, N_paralel_max)

    # Verificamos que el resultado sea correcto
    assert resultado == 2


def test_calculate_inversor_max_intensity():
    # Datos de prueba
    P_inv = 1000
    V_T_acu = 400

    # Llamamos a la función
    resultado = calculate_inversor_max_intensity(P_inv, V_T_acu)

    # Verificamos que el resultado sea correcto
    assert resultado == 3.125

def test_calculate_count_inversors():
    # Datos de prueba
    Pt = 5
    P_inv = 1

    # Llamamos a la función
    resultado = calculate_count_inversors(Pt, P_inv)

    # Verificamos que el resultado sea correcto
    assert resultado == 5000


def test_calculate_cable_Tsection():
    # Datos de prueba
    N_paralel_max = 10
    I_P_mod = 5
    V_reg = 10

    # Llamamos a la función
    resultado = calculate_cable_Tsection(N_paralel_max, I_P_mod, V_reg)

    # Verificamos que el resultado sea correcto
    assert resultado == pytest.approx(84.0336134454)


def test_cost_panels():
    # Datos de prueba
    N_panels = 20
    C_panel = 200

    # Llamamos a la función
    resultado = cost_panels(N_panels, C_panel)

    # Verificamos que el resultado sea correcto
    assert resultado == 4000


def test_cost_regulator():
    # Datos de prueba
    N_reg = 5
    C_reg = 100

    # Llamamos a la función
    resultado = cost_regulator(N_reg, C_reg)

    # Verificamos que el resultado sea correcto
    assert resultado == 500


def test_cost_inversor():
    # Datos de prueba
    N_inv = 3
    C_inv = 1000

    # Llamamos a la función
    resultado = cost_inversor(N_inv, C_inv)

    # Verificamos que el resultado sea correcto
    assert resultado == 3000


def test_cost_bateries():
    # Datos de prueba
    N_acu = 4
    C_acu = 200

    # Llamamos a la función
    resultado = cost_bateries(N_acu, C_acu)

    # Verificamos que el resultado sea correcto
    assert resultado == 800

def test_cost_panel_structure():
    # Datos de prueba
    N_panels = 10
    C_estructure = 100

    # Llamamos a la función
    resultado = cost_panel_structure(N_panels, C_estructure)

    # Verificamos que el resultado sea correcto
    assert resultado == 1000


def test_calculate_return_time():
    # Datos de prueba
    Ct_total = 5000
    C_e = 100
    E_elec = 1000

    # Llamamos a la función
    resultado = calculate_return_time(Ct_total, C_e, E_elec)

    # Verificamos que el resultado sea correcto
    assert resultado == 0.05


def test_calculate_annual_savings():
    # Datos de prueba
    C_e = 100
    E_elect_anual = 5000

    # Llamamos a la función
    resultado = calculate_annual_savings(C_e, E_elect_anual)

    # Verificamos que el resultado sea correcto
    assert resultado == 500000

def test_calculate_annual_savings_optimized():
    # Datos de prueba
    C_e = 100
    E_elect_anual = 5000
    cost_disel_year = 2000

    # Llamamos a la función
    resultado = calculate_annual_savings_optimized(C_e, E_elect_anual, cost_disel_year)

    # Verificamos que el resultado sea correcto
    assert resultado == 502000


def test_calculate_CO2_emision():
    # Datos de prueba
    E_elec = 1000
    f_eco2 = 0.5

    # Llamamos a la función
    resultado = calculate_CO2_emision(E_elec, f_eco2)

    # Verificamos que el resultado sea correcto
    assert resultado == 132.5


def test_calculate_CO2_emision_disel():
    # Datos de prueba
    disel_consuption = 500
    emision_disel = 2.5

    # Llamamos a la función
    resultado = calculate_CO2_emision_disel(disel_consuption, emision_disel)

    # Verificamos que el resultado sea correcto
    assert resultado == 1.25

def test_disel_consuption():
    # Datos de prueba
    E_elect_anual = 5000
    R_D = 10

    # Llamamos a la función
    resultado = disel_consuption(E_elect_anual, R_D)

    # Verificamos que el resultado sea correcto
    assert resultado == 500


def test_gasoline_consuption():
    # Datos de prueba
    E_elect_anual = 5000
    G_D = 5

    # Llamamos a la función
    resultado = gasoline_consuption(E_elect_anual, G_D)

    # Verificamos que el resultado sea correcto
    assert resultado == 1000


def test_cost_disel_yearly():
    # Datos de prueba
    disel_consuption = 500
    C_D = 2

    # Llamamos a la función
    resultado = cost_disel_yearly(disel_consuption, C_D)

    # Verificamos que el resultado sea correcto
    assert resultado == 1000


def test_cost_gasoline_yearly():
    # Datos de prueba
    gasoline_consuption = 1000
    C_G = 1.5

    # Llamamos a la función
    resultado = cost_gasoline_yearly(gasoline_consuption, C_G)

    # Verificamos que el resultado sea correcto
    assert resultado == 1500
    