from azure.appconfiguration.provider import load
from flask import Flask, jsonify, request, json
from flask_cors import CORS
from shapely.geometry import Polygon
import pandas as pd
from dotenv.main import load_dotenv
import math
import os

import modules.generalCalculus as gc
import modules.panelsCalculus as panelsCalculus
import modules.electrical_demand as electrical_demand
import modules.panels as panels

app = Flask(__name__)
CORS(app)

load_dotenv()
connection_string = os.environ["APP_CONFIG_CONNECTION_STRING"]

df_radiation = pd.read_csv('files/radiancia_mensual.csv')
df_temperature = pd.read_csv('files/temperatura_mensual.csv')


@app.route('/info', methods=['POST'])
def info():
    config = load(connection_string=connection_string)
    data = json.loads(request.data)['data']
    charges = data['demanda']

    map_temperature = float(data['T_amb_INFO'])
    map_radiation = float(data['rad_INFO'])
    power = float(data['pt'])

    panel_noct = float(config['panel:NOCT'])                    # 45 °C
    panel_power_stc = float(config['panel:P_STC'])              # 520 W
    panel_alpha = float(config['panel:alpha'])                  # -0.35 %/°C
    width = float(config['panel:width'])                        # 2.279 m
    height = float(config['panel:height'])                      # 1.134 m
    I_P_mod = float(config['panel:I_P_mod'])                    # 12.6 A
    I_SC_mod = float(config['panel:I_SC_mod'])                  # 13.55 A

    days_irrigation = float(config['demand:DRS'])               # 7 Días
    hours_irrigation = float(config['demand:hours'])            # 3 h
    days_low_rain = float(config['demand:MBP'])                 # 6 Semanas
    factor_fs = float(config['demand:fs'])                      # 1.15
    days_consuption = float(config['demand:consuption'])        # 5 Días

    # VARIABLES CONEXION DE MODULOS
    V_tacu = float(config['other:V_tacu'])                      # 48
    V_mod = float(config['other:V_mod'])                        # 12
    V_P_mod = float(config['other:V_P_mod'])                    # 520
    V_OC_mod = float(config['other:V_OC_mod'])                  # 48.92

    # Batería de Ni/Cd
    C = float(config['accumulation:C'])                         # 200 Ah [Amperios hora]
    I_max_charge = float(config['accumulation:I_max_charge'])   # 60 A   
    N_D = float(config['accumulation:N_D'])                     # 3 Días
    P_D_diaria = float(config['accumulation:P_D_diaria'])       # 1 Tanto por uno
    P_D_max = float(config['accumulation:P_D_max'])             # 1 Tanto por uno
    V_acu = float(config['accumulation:V_acu'])                 # 1.2 V
    V_T_acu = float(config['accumulation:V_T_acu'])             # 24 V

    P_inv = float(config['adaptation:P_inv'])                   # 5000
    P_P_inv = float(config['adaptation:P_P_inv'])               # 15000

    # Eléctrico: Dimensionamiento del subsitema de regulación
    N_paralel_max = float(config['regulation:N_paralel_max'])   # 20 N.A
    P_reg = float(config['regulation:P_reg'])                   # 2000 V

    # 6 Análisis Económico
    C_acu = float(config['economic:C_acu'])                     # 240 $/acumulador  13.2 
    C_e = float(config['economic:C_e'])                         # 0.15 $/kWh
    C_estructure = float(config['economic:C_estructure'])       # 10.041 $
    C_inv_u = float(config['economic:C_inv_u'])                 # 0.151 $           0.0435
    C_panel = float(config['economic:C_panel_u'])               # 136 $
    C_reg_u = float(config['economic:C_reg_u'])                 # 0.2145 $          0.0195
    
    f_eco2 = float(config['environmental:f_eco2'])              # 0.1917

    C_reg = P_reg * C_reg_u         # $/W
    C_inv = P_inv * C_inv_u
    panel_area = width * height
    energy_crop = electrical_demand.get_crop_demand(
        power, hours_irrigation, factor_fs)
    energy_crop_yearly = electrical_demand.get_crop_demand_yearly(
        energy_crop, days_irrigation, days_low_rain)
    total_energy_charges = electrical_demand.get_total_daily_energy(charges)

    energy_demand = electrical_demand.get_energy_demand(
        energy_crop, total_energy_charges)
    energy_demand_yearly = electrical_demand.get_energy_demand_yearly(
        energy_crop_yearly, total_energy_charges, days_consuption)

    cell_temperature = panels.get_cell_temperature(
        map_temperature, panel_noct, map_radiation)
    potence_out = panels.get_potence_out(
        cell_temperature, panel_alpha, panel_power_stc, map_radiation)

    E_panel = gc.E_panel_energy(potence_out)
    N_panels = gc.calculate_N_panels_theoretical(energy_demand, E_panel)
    Potencia_Nominal = gc.calculate_Nominal_Potence(
        N_panels, panel_power_stc, potence_out)
    Potencia_Nominal_Operacion = gc.calculate_Nominal_Potence_operating(
        N_panels, potence_out)
    Area_minimaINFO = gc.min_area_panels(panel_area, N_panels)

    E_elec_month = pd.Series([energy_demand] * 12, index=['enero', 'febrero', 'marzo', 'abril',
                             'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'])

    rad_mean = gc.obtain_rad_mean_last_years(df_radiation)      # W/m^2
    Hs_mean = gc.obtain_Hs_last_years(df_radiation)             # kWh/(m^2 dia)
    temp_mean = gc.obtain_temp_mean_last_years(df_temperature)  # °C

    Y_per_month = gc.Y(energy_demand, Hs_mean)                  # cociente
    Y_max = Y_per_month.max()
    Y_max_month = Y_per_month.index[Y_per_month == Y_max][0]

    worst_rad_mean = rad_mean[Y_max_month]
    worst_Hs_mean = Hs_mean[Y_max_month]

    # CALCULO CONEXION DE MODULOS
    N_serie = gc.calculate_N_serie(V_tacu, V_mod)
    N_paralel = gc.calculate_N_paralel(N_panels, N_serie)
    N_panels_final = gc.calculate_N_panels_final(N_serie, N_paralel)

    E_elec_max = energy_demand
    E = gc.calculate_E(C, V_acu)
    E_acu = gc.calculate_E_acumulation_system(
        N_D, P_D_max, E_elec_max, fs=1.15)
    C_T = gc.calculate_C_T(E_acu, V_T_acu, E_elec_max, P_D_diaria, N_D)
    I_max_inv = gc.calculate_inversor_max_intensity(P_inv, V_T_acu)

    # Eléctrico: Cálculo conexión de Baterías
    N_s_acu = math.ceil(gc.calculate_N_accumulators(V_T_acu, V_acu))
    N_p_acu = math.ceil(gc.calculate_N_paralel_branches(C_T, C))
    N_acu = math.ceil(gc.calculate_N_total_accumulators(N_s_acu, N_p_acu))

    V_reg = gc.calculate_nominal_voltage(V_T_acu)
    I_reg_gen_acu = gc.calculate_nominal_intensity_switch(
        N_paralel_max, I_SC_mod)
    I_acu_recep = gc.calculate_nominal_battery_coupling_switch(I_max_inv)
    N_reg = math.ceil(gc.calculate_count_regulators(
        N_panels_final, N_serie, N_paralel_max))

    # Eléctrico: Cálculos de sistema de adaptación del suministro eléctrico (inversor)
    N_inv = gc.calculate_count_inversors(power, P_inv)

    # Eléctrico: Cálculos de cableado
    S_cable = gc.calculate_cable_Tsection(N_paralel_max, I_P_mod, V_reg)

    # CÁLCULOS ELÉCTRICOS TOTALES DEL SUBSISTEMA DE CAPTACIÓN DE ENERGÍA
    P_gen = gc.calculate_peak_power(N_panels_final, panel_power_stc)
    I_P_gen = gc.calculate_peak_output_intensity(
        N_paralel, I_P_mod)
    I_SC_gen = gc.calculate_intensity_short_circuit(
        N_paralel, I_SC_mod)
    V_gen = gc.calculate_output_nominal_voltage(V_mod, N_serie)
    V_P_gen = gc.calculate_peak_output_volage(V_P_mod, N_serie)
    V_OC_gen = gc.calculate_voltage_open_circuit(
        V_OC_mod, N_serie)
    S_T_panels = gc.calculate_panels_area(
        N_panels_final, width, height)

    Ct_panels = gc.cost_panels(N_panels_final, C_panel)
    Ct_reg = gc.cost_regulator(N_reg, C_reg)
    Ct_acu = gc.cost_bateries(N_acu, C_acu)
    Ct_inv = gc.cost_inversor(N_inv, C_inv)
    Ct_estructure = gc.cost_panel_structure(
        N_panels, C_estructure)

    Ct_materiales = Ct_panels + Ct_reg + Ct_inv + Ct_acu + Ct_estructure

    Ct_instalation = Ct_materiales * 0.15
    Ct_total = Ct_materiales + Ct_instalation
    return_time = gc.calculate_return_time(
        Ct_total, C_e, energy_demand_yearly)
    emision = gc.calculate_CO2_emision(energy_demand, f_eco2)
    savings = gc.calculate_annual_savings(C_e, energy_demand_yearly)

    cIGD = ((C_panel/panel_power_stc) + (C_reg/P_reg) +
            (C_inv/P_inv) + (C_estructure/panel_power_stc)) * 1000

    IPGDmax = gc.calculate_IPGDMAX(power, charges)

    cIPAE = cIEA = gc.calculate_cIPAE(C_acu, V_T_acu, I_max_charge)

    resp = {
        "E_acu": E_acu,
        "anual_energy": energy_demand_yearly,
        "emission": float("{:.2f}".format(abs(emision))),
        "cIGD": cIGD,
        "IPGDmax": IPGDmax,
        "cIPAE": cIPAE,
        "cIEA": cIEA,
        "Pt": "{:.2f}".format(power),
        "E_elec": "{:.2f}".format(energy_demand/24),
        "E_elec_anual_M": "{:.2f}".format(energy_demand_yearly/1000),
        "worst_Hs_mean": "{:.2f}".format(worst_Hs_mean),
        "E_panel": "{:.2f}".format(E_panel),
        "S_T_panels": "{:.2f}".format(S_T_panels),
        "N_panels_final": math.ceil(N_panels_final),
        "N_serie": math.ceil(N_serie),
        "N_paralel": math.ceil(N_paralel),
        "P_gen": "{:.2f}".format(P_gen/1000),
        "N_D": "{:.2f}".format(N_D),
        "V_tacu": "{:.2f}".format(V_tacu),
        "N_acu": math.ceil(N_acu),
        "N_s_acu": math.ceil(N_s_acu),
        "N_p_acu": math.ceil(N_p_acu),
        "I_reg_gen_acu": "{:.2f}".format(I_reg_gen_acu),
        "P_reg": "{:.2f}".format(P_reg),
        "N_reg": math.ceil(N_reg),
        "P_inv": "{:.2f}".format(P_inv),
        "P_P_inv": "{:.2f}".format(P_P_inv),
        "N_inv": math.ceil(N_inv),
        "Ct_total": "{:.2f}".format(Ct_total),
        "Ct_instalation": "{:.2f}".format(Ct_instalation),
        "return_time": "{:.2f}".format(return_time),
        "savings": "{:.2f}".format(savings),
        "Ct_panels": "{:.2f}".format(Ct_panels),
        "Ct_reg": "{:.2f}".format(Ct_reg),
        "Ct_acu": "{:.2f}".format(Ct_acu),
        "Ct_inv": "{:.2f}".format(Ct_inv),
        "Ct_estructure": "{:.2f}".format(Ct_estructure),
    }
    return jsonify(resp)


@app.route('/panels', methods=['POST'])
def paneles():
    data = json.loads(request.data)['data']
    charges = data['cargas']
    crops = data['propiedades']
    n_panels = data['n_panels']
    coords_prop = data['coords_prop']

    # coordenates required
    coords_charges = panelsCalculus.obtain_coords_charges(charges)
    coords_crops = panelsCalculus.obtain_coords_crops(crops)

    # coords_terrain = Polygon([(-80.32, -0.490), (-80.29, -0.490),
    #                           (-80.29, -0.517), (-80.32, -0.517), (-80.32, -0.491)])
    coords_terrain = Polygon(coords_prop)
    coords_terrain_available = panelsCalculus.obtain_terrain_available(
        coords_terrain, coords_crops)

    # Obtain centroid
    charges_centroid = panelsCalculus.obtain_geometric_center(
        coords_crops, coords_charges)

    terrain_centroid = (coords_terrain_available.centroid.x,
                        coords_terrain_available.centroid.y)

    # location = obtain_location(terrain_centroid[0], terrain_centroid[1],
    #                            charges_centroid[0], charges_centroid[1], coords_terrain_available)
    location = panelsCalculus.obtain_location(
        terrain_centroid, charges_centroid, coords_crops, coords_terrain_available)

    # panels = obtain_panels_coord(n_panels, location, coords_terrain_available)

    # panel_polygons = panelsCalculus.obtain_panels_polygon(
    #     n_panels, location, coords_terrain_available)
    return [location.x, location.y]


host1 = 'localhost'
port1 = 5000

if __name__ == '__main__':
    app.run(host=host1, port=port1)
