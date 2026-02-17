import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)


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


def evaluate_classification(y_true, y_pred):
    accuracy = accuracy_score(y_true, y_pred)
    f1_weighted = f1_score(y_true, y_pred, average='weighted')
    return accuracy, f1_weighted


def train_and_evaluate(X_train, X_test, y_train, y_test):
    results = []

    dt = DecisionTreeClassifier(max_depth=10, random_state=42)
    dt.fit(X_train, y_train)
    y_pred = dt.predict(X_test)
    acc, f1_weighted = evaluate_classification(y_test, y_pred)
    results.append(['Decision Tree', acc, f1_weighted])

    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X_train, y_train)
    y_pred = knn.predict(X_test)
    acc, f1_weighted = evaluate_classification(y_test, y_pred)
    results.append(['KNN', acc, f1_weighted])

    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train, y_train)
    y_pred = lr.predict(X_test)
    acc, f1_weighted = evaluate_classification(y_test, y_pred)
    results.append(['Logistic Regression', acc, f1_weighted])

    nb = GaussianNB()
    nb.fit(X_train, y_train)
    y_pred = nb.predict(X_test)
    acc, f1_weighted = evaluate_classification(y_test, y_pred)
    results.append(['Naive Bayes', acc, f1_weighted])

    return pd.DataFrame(results, columns=['Algorithm', 'Accuracy', 'F1 Weighted'])


if __name__ == '__main__':
    df = pd.read_csv('../diabetes_dataset.csv')

    target_column = 'diabetes_stage'

    diabetes_mapping = {
        'No Diabetes': 0, 'Pre-Diabetes': 1,
        'Type 2': 2, 'Type 1': 3, 'Gestational': 4
    }

    y = df[target_column].map(diabetes_mapping)

    categorical_cols = ['gender', 'ethnicity', 'education_level',
                        'income_level', 'employment_status', 'smoking_status']

    df_features = df.drop(columns=[target_column])
    df_encoded = encode_categorical(df_features, categorical_cols)
    df_scaled = standardize_features(df_encoded)

    X = df_scaled

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    X_train_small, _, y_train_small, _ = train_test_split(
        X_train, y_train, train_size=15000, stratify=y_train, random_state=42
    )

    results_df = train_and_evaluate(X_train_small, X_test, y_train_small, y_test)

    print("\n" + "=" * 80)
    print("РЕЗУЛЬТАТЫ КЛАССИФИКАЦИИ")
    print("=" * 80)
    print(results_df.to_string(index=False))
    print("=" * 80)