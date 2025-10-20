# import numpy as np
# import pandas as pd
# from sklearn import preprocessing
# from sklearn.preprocessing import StandardScaler
# from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LinearRegression
# from sklearn.linear_model import Ridge
# from sklearn.linear_model import Lasso
# from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
# from sklearn.linear_model import ElasticNetCV
# from sklearn.preprocessing import PolynomialFeatures
# from sklearn.pipeline import Pipeline
# from sklearn.pipeline import make_pipeline
# from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
# from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
#
# pd.set_option('display.max_columns', None)
# pd.set_option('display.width', 1000)
# pd.set_option('display.max_colwidth', 20)
#
#
# def outlier_processing(df):
#     df_clean = df.copy()
#     numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
#
#     for col in numeric_cols:
#         Q1 = df_clean[col].quantile(0.25)
#         Q3 = df_clean[col].quantile(0.75)
#         IQR = Q3 - Q1
#         lower_bound = Q1 - 1.5 * IQR
#         upper_bound = Q3 + 1.5 * IQR
#         df_clean[col] = np.clip(df_clean[col], lower_bound, upper_bound)
#
#     return df_clean
#
#
# def standardize_features(df, target_column):
#     df_standardized = df.copy()
#     scaler = StandardScaler()
#
#     numeric_cols = df_standardized.select_dtypes(include=[np.number]).columns.tolist()
#     if target_column in numeric_cols:
#         numeric_cols.remove(target_column)
#     df_standardized[numeric_cols] = scaler.fit_transform(df_standardized[numeric_cols])
#
#     return df_standardized
#
#
# def split_dataset(df, target_column):
#     test_size = 0.2
#     random_state = 42
#     x = df.drop(columns=[target_column])
#     y = df[target_column]
#
#     x_train, x_test, y_train, y_test = train_test_split(
#         x, y,
#         test_size=test_size,
#         random_state=random_state,
#     )
#
#     return x_train, x_test, y_train, y_test
#
#
# def train_linear_regression(x_train, x_test, y_train):
#     model = LinearRegression()
#     model.fit(x_train, y_train)
#     y_pred = model.predict(x_test)
#     return {
#         'type': 'Linear Regression',
#         'result': y_pred
#     }
#
#
# def train_lasso_regression(x_train, x_test, y_train):
#     model = Lasso()
#     model.fit(x_train, y_train)
#     y_pred = model.predict(x_test)
#     return {
#         'type': 'Lasso Regression',
#         'result': y_pred
#     }
#
#
# def train_ridge_regression(x_train, x_test, y_train):
#     model = Ridge()
#     model.fit(x_train, y_train)
#     y_pred = model.predict(x_test)
#     return {
#         'type': 'Ridge Regression',
#         'result': y_pred
#     }
#
#
# def train_polynomial_regression(x_train, x_test, y_train):
#     model = Pipeline([
#         ('poly', PolynomialFeatures(degree=2)),
#         ('linear', LinearRegression())
#     ])
#     model.fit(x_train, y_train)
#     y_pred = model.predict(x_test)
#     return {
#         'type': 'Polynomial Regression',
#         'result': y_pred
#     }
#
#
# def train_elastic_regression(x_train, x_test, y_train):
#     model = make_pipeline(
#         StandardScaler(),
#         ElasticNetCV(
#             l1_ratio=[0.1, 0.5, 0.9],
#             alphas=[0.001, 0.01, 0.1, 1.0],
#             cv=5,
#             random_state=42
#         )
#     )
#     model.fit(x_train, y_train)
#     y_pred = model.predict(x_test)
#     return {
#         'type': 'Elastic Regression',
#         'result': y_pred
#     }
#
#
# def train_random_forest(X_train, X_test, y_train):
#     model = RandomForestRegressor(
#         n_estimators=100,
#         random_state=42,
#         n_jobs=-1
#     )
#
#     model.fit(X_train, y_train)
#     y_pred = model.predict(X_test)
#
#     return {
#         'type': 'Random Forest',
#         'result': y_pred
#     }
#
#
# def train_gradient_boosting(X_train, X_test, y_train):
#     model = GradientBoostingRegressor(
#         n_estimators=100,
#         learning_rate=0.1,
#         random_state=42
#     )
#
#     model.fit(X_train, y_train)
#     y_pred = model.predict(X_test)
#
#     return {
#         'type': 'Gradient Boosting',
#         'result': y_pred
#     }
#
#
# def evaluate_regression_models(models_results, y_true):
#     comparison_data = []
#
#     for model_result in models_results:
#         y_pred = model_result['result']
#
#         mae = mean_absolute_error(y_true, y_pred)
#         mse = mean_squared_error(y_true, y_pred)
#         rmse = np.sqrt(mse)
#         r2 = r2_score(y_true, y_pred)
#
#         comparison_data.append({
#             'Модель': model_result['type'],
#             'MAE': f"{mae:.4f}",
#             'MSE': f"{mse:.4f}",
#             'RMSE': f"{rmse:.4f}",
#             'R²': f"{r2:.4f}"
#         })
#
#     comparison_df = pd.DataFrame(comparison_data)
#
#     print("=" * 80)
#     print("СРАВНИТЕЛЬНАЯ ТАБЛИЦА МОДЕЛЕЙ РЕГРЕССИИ")
#     print("=" * 80)
#     print(comparison_df.to_string(index=False))
#
#
# if __name__ == '__main__':
#     df = pd.read_csv('heart_disease.csv')
#     print(df.dtypes)
#     target_column = 'Triglyceride Level'
#     df['Alcohol Consumption'] = df['Alcohol Consumption'].fillna('No')
#     df_cleaned = df.dropna()
#
#     mappings = {
#         'Gender': {'Male': 0, 'Female': 1},
#         'Smoking': {'No': 0, 'Yes': 1},
#         'Family Heart Disease': {'No': 0, 'Yes': 1},
#         'Diabetes': {'No': 0, 'Yes': 1},
#         'High Blood Pressure': {'No': 0, 'Yes': 1},
#         'Low HDL Cholesterol': {'No': 0, 'Yes': 1},
#         'High LDL Cholesterol': {'No': 0, 'Yes': 1},
#         'Heart Disease Status': {'No': 0, 'Yes': 1},
#         'Exercise Habits': {'Low': 0, 'Medium': 1, 'High': 2},
#         'Stress Level': {'Low': 0, 'Medium': 1, 'High': 2},
#         'Alcohol Consumption': {'No': 0, 'Low': 1, 'Medium': 2, 'High': 3},
#         'Sugar Consumption': {'Low': 0, 'Medium': 1, 'High': 2}
#     }
#
#     df_encoded = df_cleaned.copy()
#     df_outlier = outlier_processing(df_cleaned)
#     print(df_encoded.describe())
#     print(df_outlier.describe())
#     df_standart = standardize_features(df_outlier, target_column)
#     x_train, x_test, y_train, y_test = split_dataset(df_standart, target_column)
#     for col, mapping in mappings.items():
#         x_train[col] = x_train[col].map(mapping)
#         x_test[col] = x_test[col].map(mapping)
#     print(df_standart.describe())
#     print(x_train.describe())
#     print(x_train.shape)
#     print(x_test.shape)
#
#
#
#
#     models_results = []
#     lir_result = train_linear_regression(x_train, x_test, y_train)
#     models_results.append(lir_result)
#     lar_result = train_lasso_regression(x_train, x_test, y_train)
#     models_results.append(lar_result)
#     rir_result = train_ridge_regression(x_train, x_test, y_train)
#     models_results.append(rir_result)
#     pr_result = train_polynomial_regression(x_train, x_test, y_train)
#     models_results.append(pr_result)
#     er_result = train_elastic_regression(x_train, x_test, y_train)
#     models_results.append(er_result)
#     rar_result = train_random_forest(x_train, x_test, y_train)
#     models_results.append(rar_result)
#     gr_result = train_gradient_boosting(x_train, x_test, y_train)
#     models_results.append(gr_result)
#     evaluate_regression_models(models_results, y_test)

import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
from sklearn.linear_model import Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import ElasticNetCV
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
def outlier_processing(df):
    df_clean = df.copy()
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:
        Q1 = df_clean[col].quantile(0.25)
        Q3 = df_clean[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df_clean[col] = np.clip(df_clean[col], lower_bound, upper_bound)

    return df_clean


pd.set_option('display.max_colwidth', 20)


def standardize_features(df, target_column):
    df_standardized = df.copy()
    scaler = StandardScaler()

    numeric_cols = df_standardized.select_dtypes(include=[np.number]).columns.tolist()
    if target_column in numeric_cols:
        numeric_cols.remove(target_column)
    df_standardized[numeric_cols] = scaler.fit_transform(df_standardized[numeric_cols])

    return df_standardized


def split_dataset(df, target_column):
    test_size = 0.2
    random_state = 42
    x = df.drop(columns=[target_column])
    y = df[target_column]

    x_train, x_test, y_train, y_test = train_test_split(
        x, y,
        test_size=test_size,
        random_state=random_state,
    )

    return x_train, x_test, y_train, y_test


def train_linear_regression(x_train, x_test, y_train):
    model = LinearRegression()
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    return {
        'type': 'Linear Regression',
        'result': y_pred
    }


def train_lasso_regression(x_train, x_test, y_train):
    model = Lasso()
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    return {
        'type': 'Lasso Regression',
        'result': y_pred
    }


def train_ridge_regression(x_train, x_test, y_train):
    model = Ridge()
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    return {
        'type': 'Ridge Regression',
        'result': y_pred
    }


def train_polynomial_regression(x_train, x_test, y_train):
    model = Pipeline([
        ('poly', PolynomialFeatures(degree=2)),
        ('linear', LinearRegression())
    ])
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    return {
        'type': 'Polynomial Regression',
        'result': y_pred
    }


def train_elastic_regression(x_train, x_test, y_train):
    model = make_pipeline(
        StandardScaler(),
        ElasticNetCV(
            l1_ratio=[0.1, 0.5, 0.9],
            alphas=[0.001, 0.01, 0.1, 1.0],
            cv=5,
            random_state=42
        )
    )
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    return {
        'type': 'Elastic Regression',
        'result': y_pred
    }


def train_random_forest(X_train, X_test, y_train):
    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    return {
        'type': 'Random Forest',
        'result': y_pred
    }


def train_gradient_boosting(X_train, X_test, y_train):
    model = GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.1,
        random_state=42
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    return {
        'type': 'Gradient Boosting',
        'result': y_pred,
        'model': model
    }


def simple_feature_importance(model, feature_names):
    importance = model.feature_importances_
    indices = np.argsort(importance)[::-1]
    top_features = indices[:10]

    plt.figure(figsize=(10, 6))
    plt.barh(range(10), importance[top_features][::-1])
    plt.yticks(range(10), [feature_names[i] for i in top_features][::-1])
    plt.xlabel('Важность признака')
    plt.title('Топ-10 самых важных признаков')
    plt.tight_layout()
    plt.show()



def simple_prediction_plot(y_true, y_pred, model_name):
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.scatter(y_true, y_pred, alpha=0.5)
    plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--')
    plt.xlabel('Реальные значения')
    plt.ylabel('Предсказанные значения')
    plt.title(f'{model_name}\nПредсказания vs Реальные значения')

    plt.subplot(1, 2, 2)
    errors = y_pred - y_true
    plt.hist(errors, bins=30, alpha=0.7)
    plt.axvline(x=0, color='red', linestyle='--')
    plt.xlabel('Ошибка предсказания')
    plt.ylabel('Количество')
    plt.title('Распределение ошибок')

    plt.tight_layout()
    plt.show()
def evaluate_regression_models(models_results, y_true):
    comparison_data = []

    for model_result in models_results:
        y_pred = model_result['result']

        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_true, y_pred)

        comparison_data.append({
            'Модель': model_result['type'],
            'MAE': f"{mae:.4f}",
            'MSE': f"{mse:.4f}",
            'RMSE': f"{rmse:.4f}",
            'R²': f"{r2:.4f}"
        })

    comparison_df = pd.DataFrame(comparison_data)

    print("=" * 80)
    print("СРАВНИТЕЛЬНАЯ ТАБЛИЦА МОДЕЛЕЙ РЕГРЕССИИ")
    print("=" * 80)
    print(comparison_df.to_string(index=False))
    simple_feature_importance(models_results[-1]['model'], x_train.columns.tolist())
    simple_prediction_plot(y_true, models_results[-1]['result'], models_results[-1]['type'])

if __name__ == '__main__':
    df = pd.read_csv('diabetes_dataset.csv')
    print(df.info())
    print(df.head())
    print(df.describe())

    target_column = 'diabetes_risk_score'

    print(f"Пропущенные значения:")
    print(df.isnull().sum())

    df_cleaned = df.dropna()

    mappings = {
        'gender': {'Male': 0, 'Female': 1, 'Other': 2},
        'ethnicity': {'White': 0, 'Black': 1, 'Hispanic': 2, 'Asian': 3, 'Other': 4},
        'education_level': {
            'No formal': 0, 'Highschool': 1, 'Graduate': 2,
            'Postgraduate': 3
        },
        'income_level': {
            'Low': 0, 'Lower-Middle': 1, 'Middle': 2,
            'Upper-Middle': 3, 'High': 4
        },
        'employment_status': {
            'Employed': 0, 'Unemployed': 1, 'Retired': 2,
            'Student': 3
        },
        'smoking_status': {'Never': 0, 'Former': 1, 'Current': 2},
        'diabetes_stage': {
            'No Diabetes': 0, 'Pre-Diabetes': 1,
            'Type 2': 2, 'Type 1': 3, 'Gestational': 4
        }
    }

    df_encoded = df_cleaned.copy()
    df_outlier = outlier_processing(df_encoded)
    print(df_encoded.describe())
    print(df_outlier.describe())
    df_standart = standardize_features(df_outlier, target_column)
    x_train, x_test, y_train, y_test = split_dataset(df_standart, target_column)
    for col, mapping in mappings.items():
        x_train[col] = x_train[col].map(mapping)
        x_test[col] = x_test[col].map(mapping)
    print(df_standart.describe())
    print(x_train.describe())
    print(x_train.shape)
    print(x_test.shape)

    models_results = []
    print("Вот анекдот на время обучения: Попадают три кота в кошачий приют. Первый — кот священника, второй — архитектора, третий — дизайнера. Дают им каждому по миске с «Китекэтом». Кот священника вываливает миску на пол, раскладывает корм крестом, молится, съедает корм и тихонько ложится спать довольный. Кот архитектора также высыпает корм, раскладывает из него архитектурный план, долго что-то двигает, думает, меняет детали местами, наконец удовлетворенно съедает всё и чинно ложится спать. Кот дизайнера высыпает еду на пол, напряженно смотрит на нее, начинает неистово долбить корм миской, раздалбывает его в пыль, раскладывает из этой пыли три дорожки, вынюхивает их, трахает первых двух котов, падает на спину и колошматя лапами по полу в истерике орет: «Суки! Сволочи! Я не могу работать в таких условиях!!!»")

    print("\nАнекдот про охотников: «Два охотника выходят из лесной чащи, когда один из них внезапно падает. Его глаза остекленели и кажется, что он уже не дышит. Другой охотник хватает телефон и набирает номер экстренной службы: «Мой друг умер, что делать?» Оператор отвечает: «Успокойтесь. Для начала, давайте убедимся, что он действительно мертв». Слышится тишина, а затем выстрел. Охотник снова снимает трубку: «Убедился. Что теперь?»»")

    print("\nАнекдот про Штирлица: «Штирлиц шел по лесу. Вдруг он увидел на ветке табличку: «Здесь был Штирлиц». Штирлиц удивился. Спустя время, он снова вышел к тому же месту и увидел новую табличку: «Штирлиц, а ты вернулся?»»")
    lir_result = train_linear_regression(x_train, x_test, y_train)
    models_results.append(lir_result)
    lar_result = train_lasso_regression(x_train, x_test, y_train)
    models_results.append(lar_result)
    rir_result = train_ridge_regression(x_train, x_test, y_train)
    models_results.append(rir_result)
    pr_result = train_polynomial_regression(x_train, x_test, y_train)
    models_results.append(pr_result)
    er_result = train_elastic_regression(x_train, x_test, y_train)
    models_results.append(er_result)
    rar_result = train_random_forest(x_train, x_test, y_train)
    models_results.append(rar_result)
    gr_result = train_gradient_boosting(x_train, x_test, y_train)
    models_results.append(gr_result)

    evaluate_regression_models(models_results, y_test)