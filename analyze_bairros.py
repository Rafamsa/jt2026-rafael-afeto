import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

print("Loading data...")
mesh_df = pd.read_csv('data/Mesh_Ids_Data_Itapema.csv')
price_df = pd.read_csv('data/Price_AV_Itapema.csv')

# Calculate annual revenue per listing
revenue_df = price_df.groupby('airbnb_listing_id')['price'].sum().reset_index()
revenue_df.rename(columns={'price': 'total_revenue'}, inplace=True)

# Merge mesh (which contains suburb, lat, long) and revenue
merged_df = mesh_df[['airbnb_listing_id', 'suburb', 'latitude', 'longitude']].merge(
    revenue_df, on='airbnb_listing_id', how='inner'
)

# 1. Group by suburb
suburb_group = merged_df.groupby('suburb').agg(
    faturamento_total=('total_revenue', 'sum'),
    receita_media_anual=('total_revenue', 'mean'),
    quantidade_imoveis=('airbnb_listing_id', 'count')
).reset_index()

# 2. Sort by faturamento_total descending
sorted_suburb = suburb_group.sort_values(by='faturamento_total', ascending=False)

print("\n--- Desempenho por Bairro ---")
# Format numbers for better readability
sorted_suburb['faturamento_total_fmt'] = sorted_suburb['faturamento_total'].apply(lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
sorted_suburb['receita_media_anual_fmt'] = sorted_suburb['receita_media_anual'].apply(lambda x: f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

display_df = sorted_suburb[['suburb', 'faturamento_total_fmt', 'receita_media_anual_fmt', 'quantidade_imoveis']]
display_df.columns = ['Bairro', 'Faturamento Total', 'Receita Média Anual', 'Qtd. Imóveis']
print(display_df.to_string(index=False))

# 3. Spatial visualization (Scatter plot mapping)
plt.figure(figsize=(10, 8))
sns.set_theme(style="whitegrid")

# Create the scatter plot
scatter = sns.scatterplot(
    data=merged_df,
    x='longitude',
    y='latitude',
    hue='suburb',
    size='total_revenue',
    sizes=(20, 800), # Size range of the bubbles
    alpha=0.6,
    palette='Set1',
    edgecolor='w',
    linewidth=0.5
)

plt.title('Mapa Espacial de Receita por Imóvel e Bairro (Itapema)', fontsize=15, pad=15)
plt.xlabel('Longitude', fontsize=12)
plt.ylabel('Latitude', fontsize=12)

# Move the legend outside the plot
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0., title="Bairros & Faturamento")
plt.tight_layout()

os.makedirs('graficos', exist_ok=True)
plt.savefig('graficos/mapa_receita_bairros.png', dpi=300)
plt.close()

print("\nGráfico espacial gerado e salvo em 'graficos/mapa_receita_bairros.png'.")
