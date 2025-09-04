import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('motorcycle-dataset.csv')
# Преобразование категориальных переменных
df.seller_type = df.seller_type.astype('category')
df.owner = df.owner.astype('category')
# print(df.dtypes)
# Основная информация о датасете
# print(df.info())
# print(df.describe())
# print(df.head(3))
# print(df.tail(3))
# print(f"Размер датасета: {df.shape}")


# # Поиск пропусков
# print(df.isnull().sum())
# print(df.isnull().sum() / len(df) * 100) # в процентах
df_cleaned = df.dropna() # удаление строк с пропусками
# print(df_cleaned.isnull().sum())

# Обработка дубликатов:
# print(f"Количество дубликатов: {df_cleaned.duplicated().sum()}")
df_unique = df_cleaned.drop_duplicates()
# print(f"Количество дубликатов: {df_unique.duplicated().sum()}")

# # Метод межквартильного размаха (IQR)
Q1 = df_unique['selling_price'].quantile(0.25)
Q3 = df_unique['selling_price'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
# Фильтрация выбросов
df_filtered = df[(df['selling_price'] >= lower_bound) & (df['selling_price'] <= upper_bound)]

# Кодирование категориальных переменных
# df_encoded = pd.get_dummies(df, columns=['seller_type'])

# print(df_filtered.info())

# 1. Какова разница в цене между мотоциклами с одним владельцем и двумя?
# first_owner_prices = df_filtered[df_filtered.owner == '1st owner'].selling_price
# # print(first_owner_prices.median())
# second_owner_prices = df_filtered[df_filtered.owner == '2nd owner'].selling_price
# # print(second_owner_prices.median())
# print(f'Мотоциклы принадлежавшие только одному хозяину в среднем дороже на {first_owner_prices.median() - second_owner_prices.median()}')

# 2. Какова в среднем зависимость между годом выпуска мотоцикла и его цены?
# yearly_stats = df_filtered.groupby('year')['selling_price'].agg(['mean',  'count']).reset_index()
# print("Статистика по годам:")
# print(yearly_stats.tail(20).sort_values('year', ascending=False))
# correlation = df_filtered['year'].corr(df_filtered['selling_price'])
# print(f"Коэффициент корреляции: {correlation:.3f}")

# 3. Как можно вычислить цену мотоцикла по году и пробегу?
# X = df_filtered[['year', 'km_driven']].values
# y = df_filtered['selling_price'].values
#
# X_with_intercept = np.column_stack([np.ones(len(X)), X])
#
# coefficients = np.linalg.inv(X_with_intercept.T @ X_with_intercept) @ X_with_intercept.T @ y
#
# print(f"Цена = ({coefficients[1]:.2f} × Год) + ({coefficients[2]:.2f} × Пробег) + ({coefficients[0]:.2f})")

# 4. Какая средняя стоимость мотоцикла без налогов из салона у каждого бренда?
# df_brand = df_filtered.copy()
# df_brand.name = df_brand.name.str.split().str[0]
# brand_stats = df_brand.groupby('name')['selling_price'].agg(['mean',  'count'])
# print("Статистика по брендам:")
# print(brand_stats.tail(20).sort_values('count', ascending=False))

# 5. Какая зависимость между количеством владельцев и пробегом?
# owner_km_driven_stats = df_filtered.groupby('owner', observed=False)['km_driven'].agg(['mean', 'count'])
# print("Статистика по владельцам:")
# print(owner_km_driven_stats.head().sort_values('count', ascending=False))

# 6. Какие есть ценовые сегменты и их характеристик?
# df_analysis = df_filtered.copy()
# price_75 = df_analysis['selling_price'].quantile(0.75)
# price_25 = df_analysis['selling_price'].quantile(0.25)
#
# df_analysis.loc[:, 'price_segment'] = pd.cut(df_analysis['selling_price'],
#                                             bins=[0, price_25, price_75, float('inf')],
#                                             labels=['бюджетные', 'средние', 'премиум'])
#
# current_year = 2023
# df_analysis.loc[:, 'age'] = current_year - df_analysis['year']
# df_analysis.loc[:, 'km_per_year'] = df_analysis['km_driven'] / df_analysis['age']
#
# segment_analysis = df_analysis.groupby('price_segment', observed=False).agg({
#     'selling_price': ['mean', 'count'],
#     'year': 'mean',
#     'km_driven': 'mean',
#     'age': 'mean',
#     'km_per_year': 'mean',
#     'ex_showroom_price': 'mean'
# }).round(2)
#
# print("Анализ по ценовым сегментам:")
# print(segment_analysis)
#
# owner_segment_dist = pd.crosstab(df_analysis['owner'], df_analysis['price_segment'],
#                                 normalize='index') * 100
# print("\nРаспределение типов владельцев по ценовым сегментам (%):")
# print(owner_segment_dist.round(2))

# 7. Какая зависимость цены от типа владельца?
# seller_stats = df_filtered.groupby('seller_type', observed=False)['selling_price'].agg(['mean', 'count', 'median']).round(2)
# print("Статистика цен по типам продавцов:")
# print(seller_stats.sort_values('mean', ascending=False))
# seller_km_stats = df_filtered.groupby('seller_type' , observed=False)['km_driven'].mean().round(2)
# print("\nСредний пробег по типам продавцов:")
# print(seller_km_stats)

# 8. Топ мотоциклов с лучшим соотношением цена/пробег?
# Цена за километр пробега
# df_filtered['price_per_km'] = df_filtered['selling_price'] / df_filtered['km_driven'].replace(0, 1)
#
# # Топ мотоциклов с лучшим соотношением цена/пробег
# best_value = df_filtered[df_filtered['km_driven'] > 1000].nlargest(10, 'price_per_km')
# print("Топ-10 мотоциклов с лучшим соотношением цена/пробег:")
# print(best_value[['name', 'selling_price', 'km_driven', 'price_per_km']].round(2))
#
# # Худшее соотношение
# worst_value = df_filtered[df_filtered['km_driven'] > 1000].nsmallest(10, 'price_per_km')
# print("\nТоп-10 мотоциклов с худшим соотношением цена/пробег:")
# print(worst_value[['name', 'selling_price', 'km_driven', 'price_per_km']].round(2))

# 9. Какая зависимость пробега от типа владельца?
# owner_km_driven_stats = df_filtered.groupby('seller_type', observed=False)['km_driven'].agg(['mean', 'count'])
# print("Статистика:")
# print(owner_km_driven_stats.head().sort_values('count', ascending=False))

# 10.
# Разница между новыми и старыми мотоциклами?
# current_year = 2023
# df_old_new = df_filtered.copy()
# df_old_new['age_category'] = pd.cut(current_year - df_old_new['year'],
#                            bins=[0, 3, 7, 15, 50],
#                            labels=['новые (0-3 года)', 'средние (4-7 лет)', 'старые (8-15 лет)', 'антиквариат (15+ лет)'])
#
# age_stats = df_old_new.groupby('age_category', observed=False).agg({
#     'selling_price': ['mean', 'count'],
#     'km_driven': 'mean',
#     'year': 'mean'
# }).round(2)
#
# print("Сравнение новых и старых мотоциклов:")
# print(age_stats)

# # Первая гистограмма: Распределение цен продажи
# plt.figure(figsize=(10, 6))
# plt.hist(df['selling_price'], bins=30, alpha=0.7, edgecolor='black', color='skyblue')
# plt.title('Распределение цен на мотоциклы')
# plt.xlabel('Цена продажи (рубли)')
# plt.ylabel('Частота')
# plt.grid(True, alpha=0.3)
# plt.show()
#
# # Вторая гистограмма: Распределение пробега
# plt.figure(figsize=(10, 6))
# plt.hist(df['km_driven'], bins=30, alpha=0.7, edgecolor='black', color='lightgreen')
# plt.title('Распределение пробега мотоциклов')
# plt.xlabel('Пробег (км)')
# plt.ylabel('Частота')
# plt.grid(True, alpha=0.3)
# plt.show()

# # Первая коробчатая диаграмма: Цены продажи
# plt.figure(figsize=(8, 6))
# plt.boxplot(df['selling_price'])
# plt.title('Коробчатая диаграмма цен на мотоциклы')
# plt.ylabel('Цена продажи (рубли)')
# plt.grid(True, alpha=0.3)
# plt.show()
#
# # Вторая коробчатая диаграмма: Пробег
# plt.figure(figsize=(8, 6))
# plt.boxplot(df['km_driven'])
# plt.title('Коробчатая диаграмма пробега мотоциклов')
# plt.ylabel('Пробег (км)')
# plt.grid(True, alpha=0.3)
# plt.show()

# # Первая диаграмма: Распределение по типам владельцев
# plt.figure(figsize=(10, 6))
# df['owner'].value_counts().plot(kind='bar', color='lightblue', edgecolor='black')
# plt.title('Распределение мотоциклов по типам владельцев')
# plt.xlabel('Тип владельца')
# plt.ylabel('Количество мотоциклов')
# plt.xticks(rotation=45)
# plt.grid(True, alpha=0.3)
# plt.show()
#
# # Вторая диаграмма: Распределение по типам продавцов
# plt.figure(figsize=(10, 6))
# df['seller_type'].value_counts().plot(kind='bar', color='lightgreen', edgecolor='black')
# plt.title('Распределение по типам продавцов')
# plt.xlabel('Тип продавца')
# plt.ylabel('Количество мотоциклов')
# plt.xticks(rotation=45)
# plt.grid(True, alpha=0.3)
# plt.show()

# Correlation matrix
# Вычисляем матрицу корреляций только для числовых столбцов
# numeric_columns = df.select_dtypes(include=[np.number]).columns
# corr_matrix = df[numeric_columns].corr()
# plt.figure(figsize=(10, 8))
# heatmap = plt.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1, aspect='auto')
# for i in range(len(corr_matrix)):
#     for j in range(len(corr_matrix)):
#         plt.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
#                  ha='center', va='center', fontsize=10,
#                  bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
# plt.xticks(range(len(corr_matrix)), corr_matrix.columns, rotation=45, ha='right')
# plt.yticks(range(len(corr_matrix)), corr_matrix.columns)
# plt.title('Матрица корреляций количественных переменных')
# plt.colorbar(heatmap, label='Коэффициент корреляции')
#
# plt.tight_layout()
# plt.show()

# # Первый scatter plot: Зависимость цены от года выпуска
# plt.figure(figsize=(10, 6))
# plt.scatter(df['year'], df['selling_price'], alpha=0.6, color='blue')
# plt.xlabel('Год выпуска')
# plt.ylabel('Цена продажи (рубли)')
# plt.title('Зависимость цены от года выпуска мотоциклов')
# plt.grid(True, alpha=0.3)
# plt.show()
#
# # Второй scatter plot: Зависимость цены от пробега
# plt.figure(figsize=(10, 6))
# plt.scatter(df['km_driven'], df['selling_price'], alpha=0.6, color='red')
# plt.xlabel('Пробег (км)')
# plt.ylabel('Цена продажи (рубли)')
# plt.title('Зависимость цены от пробега мотоциклов')
# plt.grid(True, alpha=0.3)
# plt.show()

# Contingency table
# Создаем таблицу сопряженности между типом владельца и типом продавца
contingency_table = pd.crosstab(df['owner'], df['seller_type'])
print("Таблица сопряженности: Владелец vs Продавец")
print(contingency_table)

# Таблица с процентами по строкам
contingency_percent = pd.crosstab(df['owner'], df['seller_type'], normalize='index') * 100
print("\nТаблица сопряженности (% по владельцам):")
print(contingency_percent.round(1))

# Создаем комплексную визуализацию в одном окне
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# 1. Тепловая карта таблицы сопряженности (без seaborn)
im = axes[0, 0].imshow(contingency_table.values, cmap='Blues', aspect='auto')
for i in range(len(contingency_table)):
    for j in range(len(contingency_table.columns)):
        axes[0, 0].text(j, i, f'{contingency_table.iloc[i, j]}',
                       ha='center', va='center', fontsize=12,
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
axes[0, 0].set_xticks(range(len(contingency_table.columns)))
axes[0, 0].set_xticklabels(contingency_table.columns)
axes[0, 0].set_yticks(range(len(contingency_table)))
axes[0, 0].set_yticklabels(contingency_table.index)
axes[0, 0].set_title('Тепловая карта: Владелец vs Продавец')
axes[0, 0].set_xlabel('Тип продавца')
axes[0, 0].set_ylabel('Тип владельца')
plt.colorbar(im, ax=axes[0, 0], label='Количество')

# 2. Столбчатая диаграмма с накоплением
contingency_table.plot(kind='bar', stacked=True, colormap='Set2', ax=axes[0, 1])
axes[0, 1].set_title('Столбчатая диаграмма с накоплением')
axes[0, 1].set_xlabel('Тип владельца')
axes[0, 1].set_ylabel('Количество')
axes[0, 1].legend(title='Тип продавца', bbox_to_anchor=(1.05, 1), loc='upper left')
axes[0, 1].grid(True, alpha=0.3)

# 3. Групповая столбчатая диаграмма
contingency_table.plot(kind='bar', colormap='tab10', ax=axes[1, 0])
axes[1, 0].set_title('Групповая столбчатая диаграмма')
axes[1, 0].set_xlabel('Тип владельца')
axes[1, 0].set_ylabel('Количество')
axes[1, 0].legend(title='Тип продавца')
axes[1, 0].grid(True, alpha=0.3)
axes[1, 0].tick_params(axis='x', rotation=45)

# 4. Нормализованная столбчатая диаграмма (%)
contingency_percent.plot(kind='bar', stacked=True, colormap='Set3', ax=axes[1, 1])
axes[1, 1].set_title('Нормализованная диаграмма (%)')
axes[1, 1].set_xlabel('Тип владельца')
axes[1, 1].set_ylabel('Процент (%)')
axes[1, 1].legend(title='Тип продавца', bbox_to_anchor=(1.05, 1), loc='upper left')
axes[1, 1].grid(True, alpha=0.3)
axes[1, 1].set_ylim(0, 100)

plt.tight_layout()
plt.show()