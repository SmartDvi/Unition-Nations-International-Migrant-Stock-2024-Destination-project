import pandas as pd

# File path
path = "C:\\Users\\Moritus Peters\\Documents\\United\\undesa_pd_2024_ims_stock_by_sex_and_destination.xlsx"
xls = pd.ExcelFile(path)

def standardize_country_name(name):
    name_mapping = {
        "Côte d'Ivoire": "Ivory Coast",
        "United Republic of Tanzania": "Tanzania",
        "Dem. People's Republic of Korea": "North Korea",
        "Republic of Korea": "South Korea",
        "China, Hong Kong SAR": "Hong Kong",
        "China, Macao SAR": "Macao",
        "China, Taiwan Province of China": "Taiwan",
        "Iran (Islamic Republic of)": "Iran",
        "Lao People's Democratic Republic": "Laos",
        "Syrian Arab Republic": "Syria",
        "Türkiye": "Turkey",
        "Bolivia (Plurinational State of)": "Bolivia",
        "Venezuela (Bolivarian Republic of)": "Venezuela",
        "Russian Federation": "Russia",
        "Republic of Moldova": "Moldova",
        "Cabo Verde": "Cape Verde",
        "Timor-Leste": "East Timor"
    }
    return name_mapping.get(name, name)

def get_continent(country_name):
    try:
        country_alpha2 = pc.country_name_to_country_alpha2(country_name)
        continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
        return pc.convert_continent_code_to_continent_name(continent_code)
    except:
        return None

def assign_category(row, state):
    name = row["Region, development group, country or area"]
    
# List of continents, regions, and development groups
continents = [
    'AFRICA', 'ASIA', 'EUROPE', 'LATIN AMERICA AND THE CARIBBEAN',
    'NORTHERN AMERICA', 'OCEANIA'
]
regions = [
    'Eastern Africa', 'Middle Africa', 'Northern Africa', 'Southern Africa', 'Western Africa',
    'Central Asia', 'Eastern Asia', 'Southern Asia', 'South-Eastern Asia', 'Western Asia',
    'Eastern Europe', 'Northern Europe', 'Southern Europe', 'Western Europe',
    'Caribbean', 'Central America', 'South America',
    'Australia/New Zealand', 'Melanesia', 'Micronesia', 'Polynesia*'
]
development_groups = [
    'Small Island Developing States (SIDS)', 'High-and-upper-middle-income countries',
    'Low-and-Lower-middle-income countries', 'High-income countries', 'Low-and-middle-income countries',
    'Middle-income countries', 'Upper-middle-income countries', 'Lower-middle-income countries',
    'Low-income countries', 'No income group available'
]
def assign_category(row, state):
    name = row["Region, development group, country or area"]
    if name in continents:
        state["continent"] = name
        return pd.Series([name, None, None, None])
    elif name in regions:
        state["region"] = name
        return pd.Series([None, name, None, None])
    elif name in development_groups:
        state["development_group"] = name
        return pd.Series([None, None, name, None])
    else:
        return pd.Series([state.get("continent"), state.get("region"), state.get("development_group"), name])

def process_sheet(sheet_name, skip_header_rows, id_vars, prefix):
    headers = pd.read_excel(xls, sheet_name=sheet_name, skiprows=10, nrows=1).columns.tolist()
    df = pd.read_excel(xls, sheet_name=sheet_name, skiprows=skip_header_rows, header=None, names=headers)

    years = [1990, 1995, 2000, 2005, 2010, 2015, 2020, 2024]
    male_cols = [f"{y}.1" for y in years]
    female_cols = [f"{y}.2" for y in years]

    # Melt
    df_melted = pd.melt(df, id_vars=id_vars, value_vars=years, var_name='Year', value_name=f"{prefix}_both")
    df_melted[f"{prefix}_male"] = pd.melt(df, id_vars=id_vars, value_vars=male_cols)['value']
    df_melted[f"{prefix}_female"] = pd.melt(df, id_vars=id_vars, value_vars=female_cols)['value']
    df_melted['Year'] = df_melted['Year'].astype(str).str.replace('.1|.2', '', regex=True)

    # Assign categories properly
    state = {}
    categories = df[['Region, development group, country or area']].apply(lambda row: assign_category(row, state), axis=1)
    df[['continent', 'region', 'development_group', 'country']] = categories
    df_melted = df_melted.merge(df[['Unnamed: 0', 'continent', 'region', 'development_group', 'country']], on='Unnamed: 0', how='left')
    return df_melted[df_melted['country'].notna()].reset_index(drop=True)

# ID Vars
migration_id_vars = ["Unnamed: 0", "Region, development group, country or area", "Coverage", "Data type", "Location code"]
population_id_vars = ["Unnamed: 0", "Region, development group, country or area", "Population notes", "Location code"]

# Process both sheets
migration_df = process_sheet("Table 1", 26, migration_id_vars, "migration")
population_df = process_sheet("Table 2", 26, population_id_vars, "population")

# Convert to int for merging
migration_df["Unnamed: 0"] = migration_df["Unnamed: 0"].astype(int)
population_df["Unnamed: 0"] = population_df["Unnamed: 0"].astype(int)

# Merge
final_df = pd.merge(migration_df, population_df, on=["Unnamed: 0", "Year"], how="left", suffixes=("", "_pop"))

final_df['Year'] = final_df['Year'].replace({
    '20': '2020',
    '25': '2025',
    '24': '2024'
})


# Optional: Drop duplicate columns from population
cols_to_keep = [col for col in final_df.columns if not col.endswith('_pop') or col in ['population_both', 'population_male', 'population_female']]
final_df = final_df[cols_to_keep]

# Final data
final_df.head()
print()