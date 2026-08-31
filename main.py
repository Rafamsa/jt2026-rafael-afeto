import ast
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def load_data():
    print("\n[1/5] Carregando bases de dados (Airbnb e VivaReal)...")
    data = {
        "details": pd.read_csv("data/Details_Itapema.csv"),
        "mesh": pd.read_csv("data/Mesh_Ids_Data_Itapema.csv"),
        "price": pd.read_csv("data/Price_AV_Itapema.csv"),
        "hosts": pd.read_csv("data/Hosts_ids_Itapema.csv"),
        "vivareal": pd.read_csv("data/VivaReal_Itapema.csv"),
    }

    revenue_df = data["price"].groupby("airbnb_listing_id")["price"].sum().reset_index()
    revenue_df.rename(columns={"price": "total_revenue"}, inplace=True)
    data["revenue"] = revenue_df

    return data


def analyze_revenue_profile(details_df, revenue_df):
    print("\n[2/5] Calculando faturamento por perfil de imóvel...")
    merged_profile = details_df[
        [
            "airbnb_listing_id",
            "number_of_bedrooms",
            "number_of_bathrooms",
            "listing_type",
        ]
    ].merge(revenue_df, on="airbnb_listing_id", how="inner")

    grouped_profile = (
        merged_profile.groupby(
            ["listing_type", "number_of_bedrooms", "number_of_bathrooms"]
        )
        .agg(
            faturamento_total=("total_revenue", "sum"),
            receita_media_anual=("total_revenue", "mean"),
            tamanho_da_amostra=("airbnb_listing_id", "count"),
        )
        .reset_index()
    )

    filtered_profile = grouped_profile[
        grouped_profile["tamanho_da_amostra"] > 10
    ].copy()
    sorted_profile = filtered_profile.sort_values(
        by="receita_media_anual", ascending=False
    )

    print("      -> Gerando gráficos de perfis...")
    sns.set_theme(style="whitegrid")
    sorted_profile["perfil"] = (
        sorted_profile["listing_type"].str.capitalize()
        + " | "
        + sorted_profile["number_of_bedrooms"].astype(str)
        + "Q | "
        + sorted_profile["number_of_bathrooms"].astype(str)
        + "B"
    )

    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=sorted_profile,
        x="receita_media_anual",
        y="perfil",
        hue="perfil",
        legend=False,
        palette="viridis",
    )
    plt.title("Receita Média Anual por Perfil de Imóvel", fontsize=14)
    plt.tight_layout()
    plt.savefig("graficos/receita_media_anual.png", dpi=300)
    plt.close()

    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=sorted_profile,
        x="tamanho_da_amostra",
        y="perfil",
        hue="perfil",
        legend=False,
        palette="magma",
    )
    plt.title("Quantidade de Anúncios por Perfil", fontsize=14)
    plt.tight_layout()
    plt.savefig("graficos/tamanho_amostra.png", dpi=300)
    plt.close()


def analyze_spatial_revenue(mesh_df, revenue_df):
    print("\n[3/5] Analisando faturamento por bairros...")
    merged_bairros = mesh_df[
        ["airbnb_listing_id", "suburb", "latitude", "longitude"]
    ].merge(revenue_df, on="airbnb_listing_id", how="inner")

    suburb_group = (
        merged_bairros.groupby("suburb")
        .agg(faturamento_total=("total_revenue", "sum"))
        .reset_index()
        .sort_values(by="faturamento_total", ascending=False)
    )

    print("      -> Top 3 bairros (receita bruta):")
    for i, row in suburb_group.head(3).iterrows():
        print(f"         - {row['suburb']}: R$ {row['faturamento_total']:,.0f}")

    print("      -> Gerando mapa de calor espacial...")
    plt.figure(figsize=(10, 8))
    sns.scatterplot(
        data=merged_bairros,
        x="longitude",
        y="latitude",
        hue="suburb",
        size="total_revenue",
        sizes=(20, 800),
        alpha=0.6,
        palette="Set1",
    )
    plt.title("Mapa Espacial de Receita por Imóvel", fontsize=15)
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig("graficos/mapa_receita_bairros.png", dpi=300)
    plt.close()


def safe_eval(val):
    if pd.isna(val):
        return []
    try:
        return ast.literal_eval(val)
    except Exception:
        return []


def analyze_correlations(details_df, hosts_df, revenue_df):
    print("\n[4/5] Processando comodidades e correlação (Pearson)...")
    merged_corr = details_df[
        [
            "airbnb_listing_id",
            "owner_id",
            "amenities",
            "star_rating",
            "number_of_reviews",
        ]
    ].merge(revenue_df, on="airbnb_listing_id", how="inner")

    merged_corr = merged_corr.merge(
        hosts_df[["owner_id", "is_superhost"]], on="owner_id", how="left"
    )

    merged_corr["is_superhost"] = merged_corr["is_superhost"].apply(
        lambda x: 1 if str(x).lower() == "true" else 0
    )

    merged_corr["amenities_list"] = merged_corr["amenities"].apply(safe_eval)

    all_amenities = []
    for am_list in merged_corr["amenities_list"]:
        all_amenities.extend(am_list)

    top_10 = pd.Series(all_amenities).value_counts().head(10).index.tolist()

    for am in top_10:
        merged_corr[f"am:{am}"] = merged_corr["amenities_list"].apply(
            lambda x: 1 if am in x else 0
        )

    features = ["star_rating", "number_of_reviews", "is_superhost"] + [
        f"am:{am}" for am in top_10
    ]
    correlations = {}

    for f in features:
        merged_corr[f] = pd.to_numeric(merged_corr[f], errors="coerce")
        valid = merged_corr[[f, "total_revenue"]].dropna()
        if len(valid) > 0 and valid[f].nunique() > 1:
            correlations[f] = valid[f].corr(valid["total_revenue"])

    corr_df = pd.DataFrame(
        list(correlations.items()), columns=["Feature", "Correlation"]
    )
    corr_df = corr_df.sort_values(by="Correlation", ascending=False)

    print("      -> Gerando gráfico de correlação...")
    plt.figure(figsize=(10, 8))
    sns.barplot(
        data=corr_df,
        x="Correlation",
        y="Feature",
        hue="Feature",
        legend=False,
        palette="coolwarm",
    )
    plt.title("Correlação (Pearson) vs. Receita Anual", fontsize=15)
    plt.axvline(x=0, color="black", linewidth=1)
    plt.tight_layout()
    plt.savefig("graficos/correlacao_features.png", dpi=300)
    plt.close()


def analyze_roi_hypothesis(details_df, mesh_df, revenue_df, vivareal_df):
    print("\n[5/5] Calculando ROI Imobiliário (VivaReal vs Airbnb)...")
    airbnb_roi = (
        details_df[["airbnb_listing_id", "number_of_bedrooms"]]
        .merge(
            mesh_df[["airbnb_listing_id", "suburb"]],
            on="airbnb_listing_id",
            how="inner",
        )
        .merge(revenue_df, on="airbnb_listing_id", how="inner")
    )

    airbnb_roi = airbnb_roi[
        (airbnb_roi["number_of_bedrooms"] >= 1)
        & (airbnb_roi["number_of_bedrooms"] <= 6)
    ]
    airbnb_grp = (
        airbnb_roi.groupby(["suburb", "number_of_bedrooms"])
        .agg(
            mean_rev=("total_revenue", "mean"),
            count_abnb=("airbnb_listing_id", "count"),
        )
        .reset_index()
        .rename(columns={"number_of_bedrooms": "bedrooms"})
    )

    viva_valid = vivareal_df.dropna(subset=["sale_price", "suburb", "bedrooms"]).copy()
    viva_valid["sale_price"] = pd.to_numeric(viva_valid["sale_price"], errors="coerce")
    viva_valid = viva_valid.dropna(subset=["sale_price"])
    viva_valid = viva_valid[
        (viva_valid["bedrooms"] >= 1) & (viva_valid["bedrooms"] <= 6)
    ]

    viva_grp = (
        viva_valid.groupby(["suburb", "bedrooms"])
        .agg(mean_price=("sale_price", "mean"), count_viva=("listing_id", "count"))
        .reset_index()
    )

    roi_df = pd.merge(airbnb_grp, viva_grp, on=["suburb", "bedrooms"], how="inner")
    roi_df["roi_pct"] = (roi_df["mean_rev"] / roi_df["mean_price"]) * 100

    c1 = roi_df[(roi_df["suburb"] == "Centro") & (roi_df["bedrooms"] == 1)].iloc[0]
    c2 = roi_df[(roi_df["suburb"] == "Centro") & (roi_df["bedrooms"] == 2)].iloc[0]

    print("\n      [Conclusão: Teste de Hipótese (Centro 1Q vs 2Q)]")
    print(
        f"      - ROI Centro 1Q: {c1['roi_pct']:.2f}% | ROI Centro 2Q: {c2['roi_pct']:.2f}%"
    )
    print(
        f"      - Custo Extra para o 2o Quarto: R$ {c2['mean_price'] - c1['mean_price']:,.0f}"
    )
    print(
        f"      - Retorno Extra Anual Gerado: R$ {c2['mean_rev'] - c1['mean_rev']:,.0f}"
    )


def main():
    print("=" * 60)
    print(" Iniciando Análise de Dados Imobiliários - Itapema")
    print("=" * 60)

    os.makedirs("graficos", exist_ok=True)

    data = load_data()

    analyze_revenue_profile(data["details"], data["revenue"])
    analyze_spatial_revenue(data["mesh"], data["revenue"])
    analyze_correlations(data["details"], data["hosts"], data["revenue"])
    analyze_roi_hypothesis(
        data["details"], data["mesh"], data["revenue"], data["vivareal"]
    )

    print("\n" + "=" * 60)
    print(" Análise concluída! Todos os gráficos foram atualizados.")
    print("=" * 60)


if __name__ == "__main__":
    main()
