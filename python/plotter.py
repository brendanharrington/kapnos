# Measuring the Efficacy of RapidVac ULPA Filters
## Loading the CSV files (tab-delimited)
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

filename1 = '../logs/jan24.csv'
filename2 = '../logs/jan24_2.csv'

# Read both CSV files, skipping over hardware information in top two rows
data1 = pd.read_csv(filename1, encoding='latin_1', delimiter='\t', skiprows=2)
data2 = pd.read_csv(filename2, encoding='latin_1', delimiter='\t', skiprows=2)

# Convert time columns to datetime format and handle errors
data1['Time'] = pd.to_datetime(data1['Time'], errors='coerce')
data2['Time'] = pd.to_datetime(data2['Time'], errors='coerce')

# Drop rows with NaT (invalid timestamps)
data1.dropna(subset=['Time'], inplace=True)
data2.dropna(subset=['Time'], inplace=True)

# Merge and align the two datasets according to "Time" column (inner join to match timestamps)
merged_data = pd.merge(data1, data2, on='Time', how='inner')

# Extract inlet and outlet VOC concentrations
inlet_concentration = merged_data['Concentration A, PPM_x']
outlet_concentration = merged_data['Concentration A, PPM_y']

## Additional sensor data handling
# If additional sensors exist, extract them
if 'Concentration B, PPM_x' in merged_data.columns and 'Concentration B, PPM_y' in merged_data.columns:
    inlet_conc_b = merged_data['Concentration B, PPM_x']
    outlet_conc_b = merged_data['Concentration B, PPM_y']

## Compute Rolling Mean for Smoother Visualization
merged_data['Rolling Efficiency'] = (
    ((inlet_concentration - outlet_concentration) / inlet_concentration) * 100
).rolling(window=5, min_periods=1).mean()

## Plot the pre- and post- concentrations as a function of time
plt.figure(figsize=(10, 6))
plt.plot(merged_data['Time'], inlet_concentration, label='Pre-filter Concentration', color='red', alpha=0.7)
plt.plot(merged_data['Time'], outlet_concentration, label='Post-filter Concentration', color='blue', alpha=0.7)

plt.xlabel('Time')
plt.ylabel('Concentration (ppm)')
plt.title('Pre- and Post-filter VOC Concentrations Over Time')
plt.legend()
plt.grid(True)
plt.show()

## Compute and plot the efficiency of the filter as a percentage
efficiency = ((inlet_concentration - outlet_concentration) / inlet_concentration) * 100

plt.figure(figsize=(10, 6))
plt.plot(merged_data['Time'], efficiency, label='Filter Efficiency (%)', color='purple', alpha=0.7)
plt.plot(merged_data['Time'], merged_data['Rolling Efficiency'], label='Smoothed Efficiency', color='green', linestyle='dashed')

plt.xlabel('Time')
plt.ylabel('Filter Efficiency (%)')
plt.title('Filter Efficiency Over Time')
plt.legend()
plt.grid(True)
plt.show()

## Save the computed efficiency values to a CSV file
output_filename = "../logs/efficiency_results.csv"
merged_data[['Time', 'Rolling Efficiency']].to_csv(output_filename, index=False)
print(f"Efficiency data saved to {output_filename}")

print(f'Average filter efficiency: {np.mean(efficiency):.2f}%.')
