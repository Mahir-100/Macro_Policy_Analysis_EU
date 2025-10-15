import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os # <-- NEW: Needed for robust pathing

# Set plotting style
plt.style.use('ggplot')

# --- DEFINITIVE PATH FIX ---
# Get the directory of the current script (src/)
# This ensures the code finds the data files even when run from the 'src' folder.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the data folder (../data)
DATA_PATH = os.path.join(SCRIPT_DIR, '..', 'data')

# Construct the full path to each CSV file
FILE_IRELAND_EA = os.path.join(DATA_PATH, "ireland_ea.csv")
FILE_INF = os.path.join(DATA_PATH, "inf.csv")
FILE_GOV = os.path.join(DATA_PATH, "gov.csv")
# ---------------------------

# --- Common Encoding Fix ---
ENCODING_FIX = 'latin-1'


# ==============================================================================
# 1. The Irish Case: GDP and Consumption Indices
# ==============================================================================

# Load Ireland/Euro Area GDP and Consumption Indices
df_ireland_ea = pd.read_csv(
    FILE_IRELAND_EA,
    header=0,
    encoding=ENCODING_FIX
)

# Clean and set index
# Columns are: [0: Quarter], [1: Ireland GDP], [2: Euro Area GDP], [3: Ireland Cons], [4: Euro Area Cons]
df_ireland_ea = df_ireland_ea.rename(columns={df_ireland_ea.columns[0]: 'Quarter'})
df_ireland_ea = df_ireland_ea.set_index('Quarter')
df_ireland_ea = df_ireland_ea.dropna(axis=1, how='all')

# Rename columns explicitly for clarity in plots
df_ireland_ea.columns = [
    'Ireland GDP Index (2008Q1=100)', 
    'Euro Area GDP Index (2008Q1=100)', 
    'Ireland Consumption Index (2008Q1=100)', 
    'Euro Area Consumption Index (2008Q1=100)'
]

# Convert relevant columns to numeric
for col in df_ireland_ea.columns:
    df_ireland_ea[col] = pd.to_numeric(df_ireland_ea[col], errors='coerce')


# --- Plot 1: GDP Index (2008-Q1=100) ---
plt.figure(figsize=(12, 6))
df_ireland_ea.iloc[:, 0].plot(label='Ireland GDP Index (2008Q1=100)')
df_ireland_ea.iloc[:, 1].plot(label='Euro Area GDP Index (2008Q1=100)')
plt.title('GDP Index: Ireland vs. Euro Area (2008Q1=100)', fontsize=16)
plt.xlabel('Quarter', fontsize=12)
plt.ylabel('Index (2008Q1=100)', fontsize=12)
plt.legend()
plt.xticks(rotation=45, ha='right')
plt.grid(True)
plt.tight_layout()
plt.savefig('GDP_Index_Plot.png')
plt.close()


# --- Plot 2: Consumption Index (2008-Q1=100) ---
plt.figure(figsize=(12, 6))
df_ireland_ea.iloc[:, 2].plot(label='Ireland Consumption Index (2008Q1=100)')
df_ireland_ea.iloc[:, 3].plot(label='Euro Area Consumption Index (2008Q1=100)')
plt.title('Consumption Index: Ireland vs. Euro Area (2008Q1=100)', fontsize=16)
plt.xlabel('Quarter', fontsize=12)
plt.ylabel('Index (2008Q1=100)', fontsize=12)
plt.legend()
plt.xticks(rotation=45, ha='right')
plt.grid(True)
plt.tight_layout()
plt.savefig('Consumption_Index_Plot.png')
plt.close()


# ==============================================================================
# 2. Scatter Plot: Core Inflation vs. Cumulative Government Spending Growth
# ==============================================================================

# Load Inflation Data
df_inf = pd.read_csv(FILE_INF, header=0, encoding=ENCODING_FIX)

# Load Government Spending Data
df_gov = pd.read_csv(FILE_GOV, header=0, encoding=ENCODING_FIX)


# --- Data Cleaning and Merging ---

# 1. Government Spending Data (gov.csv)
df_gov = df_gov.rename(columns={df_gov.columns[0]: 'Country'})
# Filter for countries, excluding aggregates (which are the first 7 rows)
df_gov = df_gov.iloc[7:].copy()
# Extract the cumulative growth rate (4th column, index 3)
df_gov['G_EXP_Growth'] = pd.to_numeric(df_gov.iloc[:, 3], errors='coerce')
df_gov = df_gov[['Country', 'G_EXP_Growth']].dropna()


# 2. Inflation Data (inf.csv)
df_inf = df_inf.rename(columns={df_inf.columns[0]: 'Country'})
# The relevant cumulative growth is in the 6th column (index 5)
df_inf['INF_Growth'] = pd.to_numeric(df_inf.iloc[:, 5], errors='coerce')
df_inf = df_inf[['Country', 'INF_Growth']].dropna()


# 3. Merge the two datasets
df_combined = pd.merge(df_gov, df_inf, on='Country', how='inner')

# Extract final data arrays
countries = df_combined['Country'].values
gov = df_combined['G_EXP_Growth'].values
inf = df_combined['INF_Growth'].values


# --- Perform Linear Regression (Using numpy) ---
fit = np.polyfit(gov, inf, 1)
slope = fit[0]
intercept = fit[1]
fit_fn = np.poly1d(fit)
x_range = np.linspace(min(gov), max(gov), 100)
y_range = fit_fn(x_range)


# --- Create Scatter Plot ---
plt.figure(figsize=(12, 8))
plt.scatter(gov, inf, s=100, alpha=0.7, edgecolors='k', zorder=2)

# Add the regression line
plt.plot(
    x_range, y_range,
    color='red',
    linestyle='--',
    linewidth=2,
    zorder=1,
    label=f'Trendline (y = {slope:.2f}x + {intercept:.2f})'
)

# Add country labels for specific points
labeled_countries = ['Ireland', 'Germany', 'Spain', 'Bulgaria', 'Czechia', 'Greece', 'Estonia']
for i, country in enumerate(countries):
    if country in labeled_countries:
        plt.annotate(
            country,
            (gov[i], inf[i]),
            textcoords="offset points",
            xytext=(5,-5),
            ha='left',
            fontsize=9
        )

# Add labels and title
plt.title('Cumulative Government Spending Growth vs. Core Inflation (2019 Q4 - 2022 Q4)', fontsize=14)
plt.xlabel('Cumulative Government Spending Growth (%)', fontsize=12)
plt.ylabel('Cumulative Core Inflation Growth (%)', fontsize=12)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('Scatter_Plot.png')
plt.close()

# --- Print Regression Results (previously missing) ---
print("\n--- Final Regression Results (INF vs. G_EXP) ---")
print(f"Slope (Impact of G_EXP): {slope:.3f}")
print(f"Intercept: {intercept:.3f}")

# Final success message
print("\nPlots generated successfully: GDP_Index_Plot.png, Consumption_Index_Plot.png, Scatter_Plot.png")