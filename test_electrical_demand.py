import pytest
from modules.electrical_demand import get_crop_demand, get_crop_demand_yearly, get_total_daily_energy, __calculate_daily_energy, get_energy_demand, get_energy_demand_yearly

def test_get_crop_demand():
    assert get_crop_demand(2, 5, 0.8) == 8

def test_get_crop_demand_yearly():
    assert get_crop_demand_yearly(3, 10, 7) == 840

def test_get_total_daily_energy():
    charges = [{'horas': '01:30', 'cantidad': 2, 'potencia': 100}, {'horas': '02:45', 'cantidad': 3, 'potencia': 200}]
    assert get_total_daily_energy(charges) == pytest.approx(1.95)

def test_calculate_daily_energy():
    assert __calculate_daily_energy(2, 100, 90) == pytest.approx(0.3)

def test_get_energy_demand():
    assert get_energy_demand(5, 20) == 25

def test_get_energy_demand_yearly():
    assert get_energy_demand_yearly(40, 100, 5) == 26040