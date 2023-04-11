
def get_cell_temperature(map_temperature, panel_noct, map_radiation):
    tmp = (panel_noct - 20.0) / 800.0
    return map_temperature + (tmp * map_radiation)


def get_potence_out(cell_temperature, panel_alpha, panel_power_stc, map_radiation):
    tmpAlpha = (panel_alpha / 100) * (cell_temperature - 25)
    return panel_power_stc * ((map_radiation / 1000) * (1 + tmpAlpha))
