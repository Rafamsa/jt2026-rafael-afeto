import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Create graficos/ folder
os.makedirs('graficos', exist_ok=True)

# 1. Load data
print("Loading data...")
details_df = pd.read_csv('data/Details_Itapema.csv')
price_df = pd.read_csv('data/Price_AV_Itapema.csv')

# Calculate annual revenue per listing
revenue_df = price_df.groupby('airbnb_listing_id')['price'].sum().reset_index()
revenue_df.rename(columns={'price': 'total_revenue'}, inplace=True)

# 2. Merge with characteristics
merged_df = details_df[['airbnb_listing_id', 'number_of_bedrooms', 'number_of_bathrooms', 'listing_type']].merge(
    revenue_df, on='airbnb_listing_id', how='inner'
)

# 3. Group by characteristics
grouped = merged_df.groupby(['listing_type', 'number_of_bedrooms', 'number_of_bathrooms']).agg(
    faturamento_total=('total_revenue', 'sum'),
    receita_media_anual=('total_revenue', 'mean'),
    tamanho_da_amostra=('airbnb_listing_id', 'count')
).reset_index()

# 4. Filter sample size > 10 and sort by mean revenue
filtered = grouped[grouped['tamanho_da_amostra'] > 10]
sorted_result = filtered.sort_values(by='receita_media_anual', ascending=False)

print("\n--- Top Perfis de Imóveis (Amostra > 10) ---")
print(sorted_result.to_string(index=False))

# 5. Create charts
sns.set_theme(style="whitegrid")

# Formatting output for charts
# Convert floats to ints if possible for cleaner labels
sorted_result['perfil'] = sorted_result['listing_type'].str.capitalize() + ' | ' + \
                          sorted_result['number_of_bedrooms'].astype(str) + ' Quartos | ' + \
                          sorted_result['number_of_bathrooms'].astype(str) + ' Banh.'

# Chart 1
plt.figure(figsize=(10, 6))
sns.barplot(data=sorted_result, x='receita_media_anual', y='perfil', hue='perfil', legend=False, palette='viridis')
plt.title('Receita Média Anual por Perfil de Imóvel (Itapema)', fontsize=14, pad=15)
plt.xlabel('Receita Média Anual (R$)', fontsize=12)
plt.ylabel('Perfil (Tipo | Quartos | Banheiros)', fontsize=12)
plt.tight_layout()
plt.savefig('graficos/receita_media_anual.png', dpi=300)
plt.close()

# Chart 2
plt.figure(figsize=(10, 6))
sns.barplot(data=sorted_result, x='tamanho_da_amostra', y='perfil', hue='perfil', legend=False, palette='magma')
plt.title('Quantidade de Anúncios por Perfil de Imóvel (Concorrência)', fontsize=14, pad=15)
plt.xlabel('Número de Anúncios Ativos', fontsize=12)
plt.ylabel('Perfil (Tipo | Quartos | Banheiros)', fontsize=12)
plt.tight_layout()
plt.savefig('graficos/tamanho_amostra.png', dpi=300)
plt.close()

print("\nCharts generated and saved in 'graficos/' folder.")
