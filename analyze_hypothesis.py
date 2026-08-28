import pandas as pd

# Load data
vivareal = pd.read_csv('data/VivaReal_Itapema.csv')
details = pd.read_csv('data/Details_Itapema.csv')
mesh = pd.read_csv('data/Mesh_Ids_Data_Itapema.csv')
price = pd.read_csv('data/Price_AV_Itapema.csv')

# 1. Airbnb Annual Revenue
revenue = price.groupby('airbnb_listing_id')['price'].sum().reset_index()
revenue.rename(columns={'price': 'annual_revenue'}, inplace=True)

# Merge Airbnb
airbnb_merged = details[['airbnb_listing_id', 'number_of_bedrooms']].merge(
    mesh[['airbnb_listing_id', 'suburb']], on='airbnb_listing_id', how='inner'
).merge(revenue, on='airbnb_listing_id', how='inner')

# Group Airbnb by suburb and bedrooms
airbnb_grouped = airbnb_merged.groupby(['suburb', 'number_of_bedrooms']).agg(
    mean_annual_revenue=('annual_revenue', 'mean'),
    airbnb_sample_size=('airbnb_listing_id', 'count')
).reset_index()

airbnb_grouped.rename(columns={'number_of_bedrooms': 'bedrooms'}, inplace=True)

# 2. VivaReal Purchase Price
vivareal_valid = vivareal.dropna(subset=['sale_price', 'suburb', 'bedrooms']).copy()
vivareal_valid['sale_price'] = pd.to_numeric(vivareal_valid['sale_price'], errors='coerce')
vivareal_valid = vivareal_valid.dropna(subset=['sale_price'])

vivareal_grouped = vivareal_valid.groupby(['suburb', 'bedrooms']).agg(
    mean_sale_price=('sale_price', 'mean'),
    vivareal_sample_size=('listing_id', 'count')
).reset_index()

# 3. Merge both datasets
roi_df = pd.merge(airbnb_grouped, vivareal_grouped, on=['suburb', 'bedrooms'], how='inner')

# 4. Calculate ROI
roi_df['rentabilidade_anual_pct'] = (roi_df['mean_annual_revenue'] / roi_df['mean_sale_price']) * 100

# 5. Filter for the specific hypothesis
conditions = [
    (roi_df['suburb'] == 'Centro') & (roi_df['bedrooms'] == 1),
    (roi_df['suburb'] == 'Centro') & (roi_df['bedrooms'] == 2),
    (roi_df['suburb'] == 'Morretes') & (roi_df['bedrooms'].isin([2, 3]))
]

final_mask = pd.concat([cond for cond in conditions], axis=1).any(axis=1)
comparison_df = roi_df[final_mask].copy()

# Sort by ROI
comparison_df = comparison_df.sort_values(by='rentabilidade_anual_pct', ascending=False)

# Format
comparison_df['mean_sale_price'] = comparison_df['mean_sale_price'].apply(lambda x: f"R$ {x:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
comparison_df['mean_annual_revenue'] = comparison_df['mean_annual_revenue'].apply(lambda x: f"R$ {x:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
comparison_df['rentabilidade_anual_pct'] = comparison_df['rentabilidade_anual_pct'].apply(lambda x: f"{x:.2f}%")

display_df = comparison_df[['suburb', 'bedrooms', 'mean_sale_price', 'mean_annual_revenue', 'rentabilidade_anual_pct']]
display_df.columns = ['Bairro', 'Quartos', 'Preço Médio Compra', 'Receita Média Airbnb', 'Rentabilidade (ROI a.a)']

print("\n--- Comparativo da Hipótese: Compactos no Centro vs Alternativas ---")
print(display_df.to_string(index=False))

# Calculo de diferença entre 1q e 2q no Centro
centro_1q_price = roi_df[(roi_df['suburb'] == 'Centro') & (roi_df['bedrooms'] == 1)]['mean_sale_price'].values[0]
centro_2q_price = roi_df[(roi_df['suburb'] == 'Centro') & (roi_df['bedrooms'] == 2)]['mean_sale_price'].values[0]
diff_price = centro_2q_price - centro_1q_price

centro_1q_rev = roi_df[(roi_df['suburb'] == 'Centro') & (roi_df['bedrooms'] == 1)]['mean_annual_revenue'].values[0]
centro_2q_rev = roi_df[(roi_df['suburb'] == 'Centro') & (roi_df['bedrooms'] == 2)]['mean_annual_revenue'].values[0]
diff_rev = centro_2q_rev - centro_1q_rev

print(f"\nDiferença de Custo Adicional (Centro 2Q vs 1Q): R$ {diff_price:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
print(f"Ganho de Receita Adicional (Centro 2Q vs 1Q): R$ {diff_rev:,.0f} a mais por ano".replace(',', 'X').replace('.', ',').replace('X', '.'))

