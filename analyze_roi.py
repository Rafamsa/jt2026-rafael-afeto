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

# Filter for reasonable bedrooms to avoid edge cases (e.g., 0 or >10)
airbnb_merged = airbnb_merged[(airbnb_merged['number_of_bedrooms'] >= 1) & (airbnb_merged['number_of_bedrooms'] <= 6)]

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
vivareal_valid = vivareal_valid[(vivareal_valid['bedrooms'] >= 1) & (vivareal_valid['bedrooms'] <= 6)]

vivareal_grouped = vivareal_valid.groupby(['suburb', 'bedrooms']).agg(
    mean_sale_price=('sale_price', 'mean'),
    vivareal_sample_size=('listing_id', 'count')
).reset_index()

# 3. Merge both datasets
roi_df = pd.merge(airbnb_grouped, vivareal_grouped, on=['suburb', 'bedrooms'], how='inner')

# 4. Calculate ROI
roi_df['rentabilidade_anual_pct'] = (roi_df['mean_annual_revenue'] / roi_df['mean_sale_price']) * 100

# Filter for minimum sample size to avoid extreme outliers distorting the insight
roi_df = roi_df[(roi_df['airbnb_sample_size'] >= 3) & (roi_df['vivareal_sample_size'] >= 5)]

# Sort by profitability
roi_df_sorted = roi_df.sort_values(by='rentabilidade_anual_pct', ascending=False)

# Format for printing
roi_df_sorted['mean_sale_price_fmt'] = roi_df_sorted['mean_sale_price'].apply(lambda x: f"R$ {x:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
roi_df_sorted['mean_annual_revenue_fmt'] = roi_df_sorted['mean_annual_revenue'].apply(lambda x: f"R$ {x:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
roi_df_sorted['rentabilidade_anual_pct_fmt'] = roi_df_sorted['rentabilidade_anual_pct'].apply(lambda x: f"{x:.2f}%")

display_df = roi_df_sorted[['suburb', 'bedrooms', 'mean_sale_price_fmt', 'mean_annual_revenue_fmt', 'rentabilidade_anual_pct_fmt', 'airbnb_sample_size', 'vivareal_sample_size']]
display_df.columns = ['Bairro', 'Quartos', 'Preço Médio Compra', 'Receita Média Airbnb', 'Rentabilidade (ROI a.a)', 'Amostra (Airbnb)', 'Amostra (VivaReal)']

print("\n--- Ranking de Rentabilidade (ROI Bruto) por Bairro e Quartos ---")
print(display_df.to_string(index=False))
