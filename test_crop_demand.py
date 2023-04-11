import modules.electrical_demand as electrical_demand

power = 74.57
days_irrigation = 3
factor_fs = 1.15
days_low_rain = 6

energy_crop = electrical_demand.get_crop_demand(
    power, days_irrigation, factor_fs)
energy_crop_yearly = electrical_demand.get_crop_demand_yearly(
    energy_crop, days_irrigation, days_low_rain)

print("E_elec_cultivo", energy_crop)
print("E_elec_anual_cultivo", energy_crop_yearly)


charges = [{'nombre': 'Bomba de extracción',
            'cantidad': 4,
            'potencia': 500,
            'horas diarias': 4,
            'horas': [('10:00', '13:00')]
            },
           {'nombre': 'Iluminación',
            'cantidad': 30,
            'potencia': 20,
            'horas diarias': 12,
            'horas': [('18:00', '05:00')]
            },
           {'nombre': 'cerco eléctrico',
            'cantidad': 5,
            'potencia': 80,
            'horas diarias': 24,
            'horas': [('00:00', '23:00')]
            },
           {'nombre': 'lavadora',
            'cantidad': 2,
            'potencia': 200,
            'horas diarias': 5,
            'horas': [('14:00', '18:00')]
            }]

total_energy_charges = electrical_demand.get_total_daily_energy(charges)
print("EDTC", total_energy_charges)

#print("", )
