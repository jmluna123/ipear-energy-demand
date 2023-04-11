
def get_crop_demand(power, days_irrigation, factor_fs):
    return power * days_irrigation * factor_fs


def get_crop_demand_yearly(energy_crop, days_irrigation, days_low_rain):
    return days_irrigation * days_low_rain * 4 * energy_crop


def get_total_daily_energy(charges):
    EDTC = 0
    for charge in charges:
        hor = charge['horas']
        x = hor.split(':')
        total = int(x[0]) * 60 + int(x[1])
        daily_energy = __calculate_daily_energy(
            int(charge['cantidad']), int(charge['potencia']), total)
        EDTC = EDTC + daily_energy
    return EDTC


def __calculate_daily_energy(count, potence, hours):
    return count * (potence / 1000) * (hours/60)


def get_energy_demand(energy_crop, total_energy_charges):
    return energy_crop + total_energy_charges


def get_energy_demand_yearly(energy_crop_yearly, total_energy_charges, days_consuption):
    return energy_crop_yearly + (total_energy_charges * 52 * days_consuption)
