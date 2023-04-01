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
import modules.crop_demand as crop_demand

app = Flask(__name__)
CORS(app)

load_dotenv()
connection_string = os.environ["AZURE_APPCONFIG_CONNECTION_STRING"]

df_radiation = pd.read_csv('files/radiancia_mensual.csv')
df_temperature = pd.read_csv('files/temperatura_mensual.csv')


@app.route('/info', methods=['POST'])
def info():
    data = json.loads(request.data)['data']
    demanda = data['demanda']

    config = load(connection_string=connection_string)

    panel_noct = config['panel:NOCT']
    P_STC = config['panel:P_STC']
    panel_alpha = config['panel:alpha']
    panel_area = config['panel:area']
    I_P_mod = config['panel:I_P_mod']
    I_SC_mod = config['panel:I_SC_mod']

    map_temperature = float(data['T_amb_INFO'])
    map_radiation = float(data['rad_INFO'])

    #
    Pt = float(data['pt'])
    E_elec_cultivo = gc.calculate_E_elec_cultivo(Pt)  # kWh/dia
    E_elec_cultivo_anual = gc.calculate_E_elec_cultivo_anual(E_elec_cultivo)

    # Ingresado por el usuario
    dias_consumo_semana = 5

    EDTC = gc.calculate_EDTC(demanda)

    E_elec = gc.calculate_E_elec(E_elec_cultivo, EDTC)  # kWh/dia
    E_elec_anual = gc.calculate_E_elec_anual(
        E_elec_cultivo_anual, EDTC, dias_consumo_semana)

    T_cell = gc.calculate_T_cell(map_temperature, map_radiation, panel_noct)
    P_out = gc.calculate_P_out(
        T_cell, panel_alpha, P_STC, map_radiation)
    E_panel = gc.E_panel_energy(P_out)
    N_panels = gc.calculate_N_panels_theoretical(
        E_elec, E_panel)
    Potencia_Nominal = gc.calculate_Nominal_Potence(
        N_panels, P_STC, P_out)
    Potencia_Nominal_Operacion = gc.calculate_Nominal_Potence_operating(
        N_panels, P_out)
    Area_minimaINFO = gc.min_area_panels(panel_area, N_panels)

    # 3.2
    E_elec_month = pd.Series([E_elec] * 12,
                             index=['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
                                    'septiembre',
                                    'octubre', 'noviembre', 'diciembre'])

    rad_mean = gc.obtain_rad_mean_last_years(df_radiation)  # W/m^2
    Hs_mean = gc.obtain_Hs_last_years(df_radiation)  # kWh/(m^2 dia)
    temp_mean = gc.obtain_temp_mean_last_years(df_temperature)  # °C

    Y_per_month = gc.Y(E_elec, Hs_mean)  # cociente
    Y_max = Y_per_month.max()
    Y_max_month = Y_per_month.index[Y_per_month ==
                                    Y_max][0]

    worst_rad_mean = rad_mean[Y_max_month]
    worst_Hs_mean = Hs_mean[Y_max_month]

    # 4-1. VARIABLES CONEXION DE MODULOS
    V_tacu = 48
    V_mod = 12
    V_P_mod = 520
    V_OC_mod = 48.92
    width, height = 2.279, 1.134

    # 4-2. CALCULO CONEXION DE MODULOS
    N_serie = gc.calculate_N_serie(V_tacu, V_mod)
    N_paralel = gc.calculate_N_paralel(N_panels, N_serie)
    N_panels_final = gc.calculate_N_panels_final(
        N_serie, N_paralel)

    # 4.3 Batería de Ni/Cd
    P_D_max = 1  # Tanto por uno
    P_D_diaria = 1  # Tanto por uno
    V_acu = 1.2  # V

    P_inv = 5000
    P_P_inv = 15000

    V_T_acu = 24  # V
    N_D = 3  # días
    C = 200  # Ah [Amperios hora]
    E_elec_max = E_elec

    E = gc.calculate_E(C, V_acu)
    E_acu = gc.calculate_E_acumulation_system(
        N_D, P_D_max, E_elec_max, fs=1.15)
    C_T = gc.calculate_C_T(E_acu, V_T_acu,
                           E_elec_max, P_D_diaria, N_D)
    I_max_inv = gc.calculate_inversor_max_intensity(
        P_inv, V_T_acu)

    # 4.4 Eléctrico: Cálculo conexión de Baterías
    N_s_acu = math.ceil(
        gc.calculate_N_accumulators(V_T_acu, V_acu))
    N_p_acu = math.ceil(gc.calculate_N_paralel_branches(C_T, C))
    N_acu = math.ceil(
        gc.calculate_N_total_accumulators(N_s_acu, N_p_acu))

    # Eléctrico: Dimensionamiento del subsitema de regulación
    P_reg = 2000  # V
    N_paralel_max = 20

    V_reg = gc.calculate_nominal_voltage(V_T_acu)
    I_reg_gen_acu = gc.calculate_nominal_intensity_switch(
        N_paralel_max, I_SC_mod)
    I_acu_recep = gc.calculate_nominal_battery_coupling_switch(
        I_max_inv)
    N_reg = math.ceil(gc.calculate_count_regulators(
        N_panels_final, N_serie, N_paralel_max))

    # Eléctrico: Cálculos de sistema de adaptación del suministro eléctrico (inversor)
    N_inv = gc.calculate_count_inversors(Pt, P_inv)

    # Eléctrico: Cálculos de cableado
    S_cable = gc.calculate_cable_Tsection(
        N_paralel_max, I_P_mod, V_reg)

    # 5. CÁLCULOS ELÉCTRICOS TOTALES DEL SUBSISTEMA DE CAPTACIÓN DE ENERGÍA
    P_gen = gc.calculate_peak_power(N_panels_final, P_STC)
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

    # 6 Análisis Económico
    C_panel = 136  # $
    C_reg = P_reg * 0.0195  # $/W
    C_inv = P_inv * 0.0435
    C_acu = 13.2
    C_estructure = 10.041
    C_e = 0.15  # $/kWh

    Ct_panels = gc.cost_panels(N_panels_final, C_panel)
    Ct_reg = gc.cost_regulator(N_reg, C_reg)
    Ct_acu = gc.cost_bateries(N_acu, C_acu)
    Ct_inv = gc.cost_inversor(N_inv, C_inv)
    Ct_estructure = gc.cost_panel_structure(
        N_panels, C_estructure)

    Ct_materiales = Ct_panels + Ct_reg + \
        Ct_inv + Ct_acu + Ct_estructure

    Ct_instalation = Ct_materiales * 0.15
    Ct_total = Ct_materiales + Ct_instalation
    return_time = gc.calculate_return_time(
        Ct_total, C_e, E_elec_anual)
    emision = gc.calculate_CO2_emision(E_elec)
    savings = gc.calculate_annual_savings(C_e, E_elec_anual)

    cIGD = ((C_panel/P_STC) + (C_reg/P_reg) +
            (C_inv/P_inv) + (C_estructure/P_STC)) * 1000

    resp = {
        "E_acu": E_acu,
        "anual_energy": E_elec_anual,
        "emission": float("{:.2f}".format(abs(emision))),
        "cIGD": cIGD,
        "Pt": "{:.2f}".format(Pt),
        "E_elec": "{:.2f}".format(E_elec/24),
        "E_elec_anual_M": "{:.2f}".format(E_elec_anual/1000),
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
    print(resp)
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
