import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.metrics import (
    silhouette_score, davies_bouldin_score, calinski_harabasz_score,
    adjusted_rand_score, normalized_mutual_info_score
)
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 20)


def encode_categorical(df, categorical_cols):
    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')

    encoded = encoder.fit_transform(df[categorical_cols])
    encoded_df = pd.DataFrame(encoded, columns=encoder.get_feature_names_out(categorical_cols))

    df = df.drop(columns=categorical_cols)
    df = pd.concat([df.reset_index(drop=True), encoded_df.reset_index(drop=True)], axis=1)
    return df


def standardize_features(df):
    df_scaled = df.copy()
    scaler = StandardScaler()

    numeric_cols = df_scaled.select_dtypes(include=[np.number]).columns
    df_scaled[numeric_cols] = scaler.fit_transform(df_scaled[numeric_cols])

    return df_scaled


def evaluate_clustering(X, labels, y_true=None):

    if len(set(labels)) <= 1:
        return {
            "silhouette": None,
            "db_index": None,
            "calinski": None,
            "ari": None,
            "nmi": None
        }

    silhouette = silhouette_score(X, labels)
    db_index = davies_bouldin_score(X, labels)
    calinski = calinski_harabasz_score(X, labels)

    ari = adjusted_rand_score(y_true, labels) if y_true is not None else None
    nmi = normalized_mutual_info_score(y_true, labels) if y_true is not None else None

    return {
        "silhouette": silhouette,
        "db_index": db_index,
        "calinski": calinski,
        "ari": ari,
        "nmi": nmi
    }


def cluster_kmeans(X, y_true=None, n_clusters=5):
    model = KMeans(n_clusters=n_clusters, random_state=42)
    labels = model.fit_predict(X)

    metrics = evaluate_clustering(X, labels, y_true)

    return {
        "algorithm": "KMeans",
        "labels": labels,
        "n_clusters": len(np.unique(labels)),
        "n_outliers": 0,
        "metrics": metrics
    }


def cluster_agglomerative(X, y_true=None, n_clusters=5):
    model = AgglomerativeClustering(n_clusters=n_clusters)
    labels = model.fit_predict(X)

    metrics = evaluate_clustering(X, labels, y_true)

    return {
        "algorithm": "Agglomerative",
        "labels": labels,
        "n_clusters": len(np.unique(labels)),
        "n_outliers": 0,
        "metrics": metrics
    }


def cluster_dbscan(X, y_true=None, eps=0.7, min_samples=10):
    model = DBSCAN(eps=eps, min_samples=min_samples)
    labels = model.fit_predict(X)

    mask = labels != -1
    n_outliers = np.sum(labels == -1)

    if np.sum(mask) > 1:
        metrics = evaluate_clustering(X[mask], labels[mask], y_true[mask] if y_true is not None else None)
    else:
        metrics = {
            "silhouette": None,
            "db_index": None,
            "calinski": None,
            "ari": None,
            "nmi": None
        }

    return {
        "algorithm": "DBSCAN",
        "labels": labels,
        "n_clusters": len(np.unique(labels)) - (1 if -1 in labels else 0),
        "n_outliers": n_outliers,
        "metrics": metrics
    }


def plot_clusters_2d(X, labels, title):
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)

    plt.figure(figsize=(7, 5))
    sns.scatterplot(x=X_pca[:, 0], y=X_pca[:, 1], hue=labels, palette='tab10', s=20)
    plt.title(title)
    plt.show()


def plot_cluster_sizes(labels, title):
    unique, counts = np.unique(labels, return_counts=True)
    plt.figure(figsize=(7, 4))
    sns.barplot(x=unique, y=counts)
    plt.title(title)
    plt.xlabel("Cluster label")
    plt.ylabel("Count")
    plt.show()


def plot_boxplots_by_cluster(df, labels, feature):
    df_tmp = df.copy()
    df_tmp["cluster"] = labels

    plt.figure(figsize=(8, 5))
    sns.boxplot(data=df_tmp, x="cluster", y=feature)
    plt.title(f"{feature} distribution per cluster")
    plt.show()


def print_results_table(results):
    table = []

    for r in results:
        m = r["metrics"]
        table.append([
            r["algorithm"],
            r["n_clusters"],
            m["silhouette"],
            m["db_index"],
            m["calinski"],
            m["ari"],
            m["nmi"],
            r["n_outliers"]
        ])

    columns = [
        "Algorithm", "Clusters", "Silhouette", "DB Index",
        "Calinski-Harabasz", "ARI", "NMI", "Outliers"
    ]

    df_results = pd.DataFrame(table, columns=columns)
    print(df_results)
    return df_results


if __name__ == '__main__':
    df = pd.read_csv('diabetes_dataset.csv')
    print(df.info())
    print(df.head())
    print(df.describe())

    target_column = 'diabetes_stage'

    print("Пропущенные значения:")
    print(df.isnull().sum())

    df_cleaned = df.dropna()

    categorical_cols = [
        'gender',
        'ethnicity',
        'education_level',
        'income_level',
        'employment_status',
        'smoking_status'
    ]

    diabetes_mapping = {
        'No Diabetes': 0, 'Pre-Diabetes': 1,
        'Type 2': 2, 'Type 1': 3, 'Gestational': 4
    }

    y = df_cleaned[target_column].map(diabetes_mapping).astype(int)

    df_features = df_cleaned.drop(columns=[target_column])

    df_encoded = encode_categorical(df_features, categorical_cols)

    df_scaled = standardize_features(df_encoded)

    X = df_scaled

    N = 15000
    X_sample, _, y_sample, _ = train_test_split(
        X, y,
        train_size=N,
        stratify=y,
        random_state=42
    )

    X = X_sample.reset_index(drop=True)
    y = y_sample.reset_index(drop=True)

    pca = PCA(n_components=10, random_state=42)
    X_pca = pca.fit_transform(X)

    print("\nГотовые данные для кластеризации:")
    print(X.head())
    print("\nФорма X:", X.shape)
    print("Форма y:", y.shape)

    results = []

    r1 = cluster_kmeans(X_pca, y, n_clusters=5)
    results.append(r1)

    r2 = cluster_agglomerative(X_pca, y, n_clusters=5)
    results.append(r2)

    r3 = cluster_dbscan(X_pca, y, eps=2.0, min_samples=8)
    results.append(r3)

    print_results_table(results)
    df_sample = df_encoded.loc[X_sample.index].reset_index(drop=True)

    for r in [r1, r2, r3]:
        plot_clusters_2d(X_pca, r['labels'], title=f"{r['algorithm']} clusters")
        plot_cluster_sizes(r['labels'], title=f"{r['algorithm']} cluster sizes")
        for feature in ['bmi', 'age', 'glucose_fasting']:
            plot_boxplots_by_cluster(df_sample, r['labels'], feature=feature)

