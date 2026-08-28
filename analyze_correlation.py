import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ast
import os

print("Loading data...")
details_df = pd.read_csv('data/Details_Itapema.csv')
hosts_df = pd.read_csv('data/Hosts_ids_Itapema.csv')
price_df = pd.read_csv('data/Price_AV_Itapema.csv')

# Calculate annual revenue per listing
revenue_df = price_df.groupby('airbnb_listing_id')['price'].sum().reset_index()
revenue_df.rename(columns={'price': 'total_revenue'}, inplace=True)

# Merge datasets
merged = details_df[['airbnb_listing_id', 'owner_id', 'amenities', 'star_rating', 'number_of_reviews']].merge(
    revenue_df, on='airbnb_listing_id', how='inner'
)
merged = merged.merge(hosts_df[['owner_id', 'is_superhost']], on='owner_id', how='left')

# Convert is_superhost to 1/0
merged['is_superhost'] = merged['is_superhost'].apply(lambda x: 1 if str(x).lower() == 'true' else 0)

# Process amenities
print("Processing amenities...")
def safe_eval(val):
    if pd.isna(val):
        return []
    try:
        return ast.literal_eval(val)
    except:
        # If it fails, fallback to simple string checking later or return empty
        return []

merged['amenities_list'] = merged['amenities'].apply(safe_eval)

# Flatten and find top 10
all_amenities = []
for am_list in merged['amenities_list']:
    all_amenities.extend(am_list)

top_10_amenities = pd.Series(all_amenities).value_counts().head(10).index.tolist()

# Create dummy columns for top 10 amenities
for amenity in top_10_amenities:
    col_name = f"amenidade: {amenity}"
    merged[col_name] = merged['amenities_list'].apply(lambda x: 1 if amenity in x else 0)

# Features to correlate
features = ['star_rating', 'number_of_reviews', 'is_superhost'] + [f"amenidade: {am}" for am in top_10_amenities]
correlations = {}

print("Calculating correlations...")
for feature in features:
    # Ensure numeric type
    merged[feature] = pd.to_numeric(merged[feature], errors='coerce')
    valid_data = merged[[feature, 'total_revenue']].dropna()
    if len(valid_data) > 0:
        # Avoid zero division or nan if variance is 0
        if valid_data[feature].nunique() > 1:
            corr = valid_data[feature].corr(valid_data['total_revenue'])
            correlations[feature] = corr
        else:
            correlations[feature] = 0.0

# Create dataframe and sort
corr_df = pd.DataFrame(list(correlations.items()), columns=['Feature', 'Correlation'])
corr_df = corr_df.sort_values(by='Correlation', ascending=False)

print("\n--- Correlação de Pearson com a Receita Anual ---")
print(corr_df.to_string(index=False))

# Plot
plt.figure(figsize=(10, 8))
sns.set_theme(style="whitegrid")

sns.barplot(data=corr_df, x='Correlation', y='Feature', hue='Feature', legend=False, palette='coolwarm')
plt.title('Correlação (Pearson) de Fatores vs. Receita Anual', fontsize=15, pad=15)
plt.xlabel('Coeficiente de Correlação', fontsize=12)
plt.ylabel('Variáveis (Fatores)', fontsize=12)
plt.axvline(x=0, color='black', linewidth=1)
plt.tight_layout()

os.makedirs('graficos', exist_ok=True)
plt.savefig('graficos/correlacao_features.png', dpi=300)
plt.close()

print("\nGráfico salvo em 'graficos/correlacao_features.png'.")
