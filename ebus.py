#!/usr/bin/env python3
"""AHP analysis for e-bus transition for three cities.

This script:
- normalizes the provided data (min-max, inverts cost criteria where lower is better)
- applies the given AHP weights to compute a score per city
- estimates net annual economic impact using simple amortization and battery-mileage scenarios
- saves two plots to the project folder and prints a summary table

Assumptions are documented in the script. Tweak the amortization_years and annual_miles_scenarios
if you have real fleet-mileage or preferred amortization.
"""
import numpy as np
import matplotlib.pyplot as plt
import os

out_dir = os.path.dirname(os.path.abspath(__file__))

# City names
cities = ["Phoenix", "Dallas", "Charlotte"]

# Raw data provided in the prompt
# C1: Maintenance Savings (annual, $) -- higher is better
# C2: Bus + Transition Cost ($, assume up-front, lower is better)
# C3: Battery Replacement ($/mi) -- lower is better
# C4: Pollution saved (metric tons CO2/year) -- higher is better
# C5: Job impacts "gained/lost" -> we convert to net jobs gained (higher better)
# C6: Climate/health benefits (annual $, higher is better)

data = {
    'C1_maintenance_savings': np.array([53_050_000, 34_600_000, 16_150_000], dtype=float),
    'C2_bus_transition_cost': np.array([350_000_000, 245_000_000, 105_000_000], dtype=float),
    'C3_battery_per_mile': np.array([20.0, 14.0, 6.0], dtype=float),
    'C4_pollution_tons_saved': np.array([8000.0, 5600.0, 2400.0], dtype=float),
    # job impacts are 'gained/lost' strings in prompt; convert to net gained
    'C5_net_jobs_gained': np.array([350 - 150, 245 - 105, 105 - 45], dtype=float),
    'C6_climate_health_benefits': np.array([163_400_000, 114_380_000, 49_020_000], dtype=float),
}

# AHP weights from your ranking (map to C1..C6 as described)
weights = {
    'C6_climate_health_benefits': 0.247,
    'C1_maintenance_savings': 0.243,
    'C4_pollution_tons_saved': 0.243,
    'C2_bus_transition_cost': 0.103,
    'C5_net_jobs_gained': 0.096,
    'C3_battery_per_mile': 0.068,
}

criteria_keys = [
    'C1_maintenance_savings',
    'C2_bus_transition_cost',
    'C3_battery_per_mile',
    'C4_pollution_tons_saved',
    'C5_net_jobs_gained',
    'C6_climate_health_benefits',
]

# Define whether higher values are better for each criterion
benefit_direction = {
    'C1_maintenance_savings': True,
    'C2_bus_transition_cost': False,  # cost: lower is better
    'C3_battery_per_mile': False,     # cost per mile: lower is better
    'C4_pollution_tons_saved': True,
    'C5_net_jobs_gained': True,
    'C6_climate_health_benefits': True,
}


def minmax_normalize(arr):
    mn = np.nanmin(arr)
    mx = np.nanmax(arr)
    if mx == mn:
        # all same -> return 0.5 neutral
        return np.full_like(arr, 0.5)
    return (arr - mn) / (mx - mn)


# Build normalized matrix (cities x criteria_in_weights_order)
norm_matrix = []
for key in ['C6_climate_health_benefits', 'C1_maintenance_savings', 'C4_pollution_tons_saved',
            'C2_bus_transition_cost', 'C5_net_jobs_gained', 'C3_battery_per_mile']:
    arr = data[key]
    norm = minmax_normalize(arr)
    if not benefit_direction.get(key, True):
        norm = 1.0 - norm  # invert so larger is always better
    norm_matrix.append(norm)

norm_matrix = np.vstack(norm_matrix).T  # shape (n_cities, n_criteria)

# Create weight vector in the same order
weight_vector = np.array([
    weights['C6_climate_health_benefits'],
    weights['C1_maintenance_savings'],
    weights['C4_pollution_tons_saved'],
    weights['C2_bus_transition_cost'],
    weights['C5_net_jobs_gained'],
    weights['C3_battery_per_mile'],
])

# Compute weighted AHP score (higher -> better candidate for transition)
scores = norm_matrix.dot(weight_vector)


def print_table():
    header = ['City'] + [
        'Climate/health (C6)', 'Maintenance (C1)', 'Pollution (C4)',
        'Cost (C2) [inverted]', 'Jobs (C5)', 'Battery $/mi (C3) [inverted]']
    print('\t'.join(header))
    for i, city in enumerate(cities):
        row = [city] + [f"{val:.3f}" for val in norm_matrix[i, :]]
        print('\t'.join(row))
    print('\nAHP weighted scores:')
    for city, sc in zip(cities, scores):
        print(f"- {city}: {sc:.4f}")


def plot_scores(outfile=os.path.join(out_dir, 'ahp_scores.png')):
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(cities, scores, color=['#1f77b4', '#2ca02c', '#ff7f0e'])
    ax.set_ylabel('AHP score (higher = more favorable)')
    ax.set_title('AHP ranking: e-bus transition')
    ax.grid(axis='y', linestyle='--', alpha=0.25)
    plt.tight_layout()
    fig.savefig(outfile)
    print(f'Saved AHP score plot to {outfile}')


def estimate_net_annual(amort_years=12, annual_miles=100_000_000):
    """Estimate a simple net annual economic impact:

    net_annual = maintenance_savings + climate_benefits - amortized_transition_cost - battery_annual_cost

    battery_annual_cost = battery_$per_mile * annual_miles

    Notes:
    - C2 is treated as an up-front cost amortized over amort_years (user-provided assumption)
    - annual_miles is a scenario parameter (total fleet miles per year). The prompt did not
      provide fleet miles, so we present a few scenarios below.
    """
    maint = data['C1_maintenance_savings']
    climate = data['C6_climate_health_benefits']
    transition = data['C2_bus_transition_cost'] / amort_years
    battery_cost = data['C3_battery_per_mile'] * annual_miles
    net = maint + climate - transition - battery_cost
    return net


if __name__ == '__main__':
    print('\n--- AHP analysis summary ---\n')
    print_table()

    # Create and save AHP plot
    plot_scores()

    # Show net annual under a few battery-mileage scenarios (low/medium/high)
    amort_years = 12
    scenarios = {
        'low_mileage': 50_000_000,
        'mid_mileage': 100_000_000,
        'high_mileage': 200_000_000,
    }
    print('\nEstimated net annual economic impact (assumptions below):')
    print(f'- amortization years for transition cost: {amort_years} (transition cost / years)')
    for name, miles in scenarios.items():
        net = estimate_net_annual(amort_years=amort_years, annual_miles=miles)
        print(f"{name:12s} (annual miles={miles:,}):")
        for city, val in zip(cities, net):
            print(f"  - {city:8s}: ${val:,.0f}")

    # Plot the mid-mileage net annual results
    mid_net = estimate_net_annual(amort_years=amort_years, annual_miles=scenarios['mid_mileage'])
    fig, ax = plt.subplots(figsize=(7, 4))
    colors = ['#2ca02c' if v >= 0 else '#d62728' for v in mid_net]
    ax.bar(cities, mid_net, color=colors)
    ax.set_ylabel('Estimated net annual ($)')
    ax.set_title(f'Estimated net annual (amortized over {amort_years} years, mid mileage)')
    ax.grid(axis='y', linestyle='--', alpha=0.25)
    plt.tight_layout()
    out_net = os.path.join(out_dir, 'ahp_net_annual_mid_mileage.png')
    fig.savefig(out_net)
    print(f'Saved net-annual plot to {out_net}')