import pandas as pd

# Load the data
print("Loading data...")
details_df = pd.read_csv('data/Details_Itapema.csv')
mesh_df = pd.read_csv('data/Mesh_Ids_Data_Itapema.csv')
price_df = pd.read_csv('data/Price_AV_Itapema.csv')
hosts_df = pd.read_csv('data/Hosts_ids_Itapema.csv')
vivareal_df = pd.read_csv('data/VivaReal_Itapema.csv')

# 1. Merge Details, Mesh, and Price on airbnb_listing_id
# Note: Details and Mesh both have latitude, longitude, and aquisition_date. We should specify suffixes.
print("Merging Airbnb data...")
merged_airbnb = details_df.merge(mesh_df, on='airbnb_listing_id', how='left', suffixes=('', '_mesh'))
merged_airbnb = merged_airbnb.merge(price_df, on='airbnb_listing_id', how='left', suffixes=('', '_price'))

# 2. Add Hosts on owner_id
merged_airbnb = merged_airbnb.merge(hosts_df, on='owner_id', how='left')

# 3. VivaReal is loaded separately

print("\n--- AirBnb Unified Dataset Columns ---")
for col in merged_airbnb.columns:
    print(col)

print("\n--- VivaReal Dataset Columns ---")
for col in vivareal_df.columns:
    print(col)
