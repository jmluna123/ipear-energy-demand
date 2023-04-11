import numpy as np
import math

def calculate_E_elec_cultivo(Pt, hours=3, fs=1.15):
    return Pt * hours * fs


def calculate_E_elec_cultivo_anual(E_elec_cultivo, DRS=7, MBP=6):
    return DRS * MBP * 4 * E_elec_cultivo


def calculate_EDTC(cargas):
    EDTC = 0
    for carga in cargas:
        hor = carga['distribución']
        x = hor.split(':')
        total = int(x[0]) * 60 + int(x[1])
        daily_energy = calculate_daily_energy(
            int(carga['cantidad']), int(carga['potencia']), total)
        EDTC = EDTC + daily_energy
    return EDTC

def calculate_IPGDMAX(Pt, cargas):
    Pt = Pt
    for carga in cargas:
        hor = carga['horas']
        x = hor.split(':')
        daily_energy = calculate_sum_potence(
            int(carga['cantidad']), int(carga['potencia']))
        Pt = Pt + daily_energy
    return Pt

def calculate_daily_energy(cantidad, potencia, horas):
    return cantidad * (potencia / 1000) * (horas/60)

def calculate_sum_potence(amount, potence):
    return amount * (potence / 1000)

def calculate_E_elec(E_elec_cultivo, EDTC):
    return E_elec_cultivo + EDTC

def calculate_cIPAE(C_acu, V_T_acu, I_max_charge):
    return C_acu/(V_T_acu * I_max_charge)

def calculate_E_elec_anual(E_elec_cultivo_anual, EDTC, dias_consumo_semana):
    return E_elec_cultivo_anual + (EDTC * 52 * dias_consumo_semana)


def generate_hours_dist(cargas):
    horas = [0.0] * 24

    for carga in cargas:
        energia_diaria = carga['cantidad'] * carga['potencia']
        rangos = carga['distribución']
        for rango in rangos:
            rango1 = int(rango[0][:2])
            rango2 = int(rango[1][:2])

            i = 0
            while rango1 != rango2 + 1 and i < 24:
                horas[rango1] = energia_diaria + horas[rango1]
                rango1 = (rango1 + 1) % 24
                i = i+1
    return horas


def calculate_total_radiation(Gd):
    return Gd * 12 * 365


def calculate_T_cell(T_amb, G, NOCT):
    tmp = (NOCT - 20.0) / 800.0
    return T_amb + (tmp * G)


def calculate_P_out(T_cell, alpha, P_STC, G):
    tmpAlpha = (alpha / 100) * (T_cell - 25)
    return P_STC * ((G / 1000) * (1 + tmpAlpha))


def min_area_panels(A, N_panels):
    return N_panels * A


def calculate_Nominal_Potence(N_total, P_STC, P_out):
    return N_total * P_out


def calculate_Nominal_Potence_operating(N_panels, P_out):
    return N_panels * P_out


def calculate_Pt(Pw, Ha, factor=0.7457):
    return Pw * factor * Ha


def daily_mean_energy_req(Pt, hours=3, fs=1.15):
    return Pt * hours * fs


def Hs_daily_mean_radiation(G, daily_sun_hours=24):
    return G * daily_sun_hours


def obtain_rad_mean_last_years(df, daily_sun_hours=24, years=10):
    return df[-years:].drop(['fecha'], axis=1).mean()


def obtain_Hs_last_years(df, daily_sun_hours=24, years=10):
    # 1000 para conversión a kW
    return df[-years:].drop(['fecha'], axis=1).mean() * daily_sun_hours / 1000


def obtain_temp_mean_last_years(df, years=10):
    return df[-years:].drop(['fecha'], axis=1).mean()


def obtain_worst_rad_mean(rad_mean):
    return rad_mean.min()


def Y(E_elec, Hs):
    return E_elec / Hs


def E_panel_energy(P_out, daily_sun_hours=24, conv='kW'):
    if conv == 'kW':
        return P_out * daily_sun_hours / 1000
    return P_out * daily_sun_hours


def calculate_N_panels_theoretical(E_elec, E_panel, fsp=1.1):
    return math.ceil((E_elec / E_panel) * fsp)


# Cálculos de Conexión de Módulos
def calculate_N_serie(V_tacu, V_mod):
    return math.ceil(V_tacu / V_mod)


def calculate_N_paralel(N_panels, N_serie):
    return math.ceil(N_panels / N_serie)


def calculate_N_panels_final(N_serie, N_paralel):
    return N_serie * N_paralel


# Cálculos del subsistema de captación de energía
def calculate_peak_power(N_panels, P_STC):
    return N_panels * P_STC


def calculate_peak_output_intensity(N_paralel, I_P_mod):
    return N_paralel * I_P_mod


def calculate_intensity_short_circuit(N_paralel, I_SC_mod):
    return N_paralel * I_SC_mod


def calculate_output_nominal_voltage(V_mod, N_serie):
    return V_mod * N_serie


def calculate_peak_output_volage(V_P_mod, N_serie):
    return V_P_mod * N_serie


def calculate_voltage_open_circuit(V_OC_mod, N_serie):
    return V_OC_mod * N_serie


def calculate_panels_area(N_panels, width, height):
    return N_panels * width * height


# Cálculos de Localización de Planta
def coords_centroid(arr):
    y, x = np.argwhere(arr == 1).mean(0)[1:]
    return (math.ceil(x), math.ceil(y))


def calculate_distances_charge(P, charges, resolution=10):
    distances = []
    p_x, p_y = P
    for charge in charges:
        c_x, c_y = charge
        d = math.sqrt(math.pow((p_x - c_x) * resolution, 2) +
                      math.pow((p_y - c_y) * resolution, 2))
        distances.append(d)
    return distances


# Cálculos de sistema de acumulación de energía
def calculate_E(C, V_acu):
    return C * V_acu


def calculate_E_acumulation_system(N_D, P_D_max, E_elec_max, fs=1.15):
    return (N_D / P_D_max) * E_elec_max * fs


def calculate_C_T(E_acu, V_T_acu, E_elec_max, P_D_diaria, N_D, fs=1.1):
    C_T = E_acu / (V_T_acu * 1000)
    C_min = (E_elec_max) / (P_D_diaria * V_T_acu)

    if C_min > C_T:
        C_T = (N_D / (P_D_diaria * V_T_acu)) * E_elec_max * fs
    return C_T


# Cálculos de Conexión de Baterías
def calculate_N_accumulators(V_T_acu, V_acu):
    return V_T_acu / V_acu


def calculate_N_paralel_branches(C_T, C):
    return C_T / C


def calculate_N_total_accumulators(N_s_acu, N_p_acu):
    return N_s_acu * N_p_acu


# Cálculos de sistema de regulación de energía
def calculate_nominal_voltage(V_T_acu):
    return 1.25 * V_T_acu


def calculate_nominal_intensity_switch(N_paralel_max, I_SC_mod):
    return 1.25 * N_paralel_max * I_SC_mod


def calculate_nominal_battery_coupling_switch(I_max_inv):
    return 1.25 * I_max_inv


def calculate_count_regulators(N_panels, N_serie, N_paralel_max):
    return (N_panels) / (N_serie * N_paralel_max)


def calculate_inversor_max_intensity(P_inv, V_T_acu):
    return 1.25 * (P_inv / V_T_acu)


# Cálculos de sistema de adaptación del suministro eléctrico (inversor)
def calculate_count_inversors(Pt, P_inv):
    return math.ceil((Pt * 1000) / P_inv)


# Cálculos de cableado
def calculate_cable_Tsection(N_paralel_max, I_P_mod, V_reg):
    return (2 * 8 * N_paralel_max * I_P_mod) / ((1.7 / 100) * V_reg * 56)


# Análisis Económico
def cost_panels(N_panels, C_panel):
    return N_panels * C_panel


def cost_regulator(N_reg, C_reg):
    return N_reg * C_reg


def cost_inversor(N_inv, C_inv):
    return N_inv * C_inv


def cost_bateries(N_acu, C_acu):
    return N_acu * C_acu


def cost_panel_structure(N_panels, C_estructure):
    return N_panels * C_estructure


def calculate_return_time(Ct_total, C_e, E_elec):
    return Ct_total / (C_e * E_elec)


def calculate_annual_savings(C_e, E_elect_anual):
    return (C_e * E_elect_anual)


def calculate_CO2_emision(E_elec, f_eco2):
    return (E_elec * 265 / 1000) * f_eco2
