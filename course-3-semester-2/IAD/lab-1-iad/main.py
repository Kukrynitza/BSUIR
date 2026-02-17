import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

class NeuralNet(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(NeuralNet, self).__init__()

        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        return out


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

if __name__ == '__main__':
    df = pd.read_csv('diabetes_dataset.csv')
    print(df.info())
    print(df.head())
    print(df.describe())

    target_column = 'diabetes_stage'

    print(f"Пропущенные значения:")
    print(df.isnull().sum())

    df_cleaned = df.dropna()
    df_cleaned = df_cleaned.sample(n=45000, random_state=42)
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
        if col != target_column:
            x_train[col] = x_train[col].map(mapping)
            x_test[col] = x_test[col].map(mapping)

    y_train = y_train.map(mappings[target_column])
    y_test = y_test.map(mappings[target_column])

    print(df_standart.describe())
    print(x_train.describe())
    print(x_train.shape)
    print(x_test.shape)

    print('================================================')

    X_train = x_train.values
    X_test = x_test.values
    y_train = y_train.values
    y_test = y_test.values

    X_train = torch.tensor(X_train, dtype=torch.float32)
    X_test = torch.tensor(X_test, dtype=torch.float32)

    y_train = torch.tensor(y_train, dtype=torch.long)
    y_test = torch.tensor(y_test, dtype=torch.long)
    print(f'X_train.shape[1]: {X_train.shape[1]}')
    print(len(torch.unique(y_train)))
    print(torch.unique(y_train))
    input_size = X_train.shape[1]
    hidden_size = 64
    num_classes = len(torch.unique(y_train))

    model = NeuralNet(input_size, hidden_size, num_classes)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)


    train_losses = []
    test_losses = []
    train_accuracies = []
    test_accuracies = []
    train_f1s = []
    test_f1s = []

    for epoch in range(50):
        model.train()
        optimizer.zero_grad()
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        loss.backward()
        optimizer.step()

        train_losses.append(loss.item())

        _, predicted = torch.max(outputs, 1)
        train_accuracy = (predicted == y_train).float().mean().item()
        train_accuracies.append(train_accuracy)
        train_f1 = f1_score(y_train.numpy(), predicted.numpy(), average='weighted')
        train_f1s.append(train_f1)

        model.eval()
        with torch.no_grad():
            test_outputs = model(X_test)
            test_loss = criterion(test_outputs, y_test)
            test_losses.append(test_loss.item())

            _, test_predicted = torch.max(test_outputs, 1)
            test_accuracy = (test_predicted == y_test).float().mean().item()
            test_accuracies.append(test_accuracy)
            test_f1 = f1_score(y_test.numpy(), test_predicted.numpy(), average='weighted')
            test_f1s.append(test_f1)

        print(f"Epoch [{epoch + 1}/50] "
              f"Train Loss: {loss.item():.4f} "
              f"Test Loss: {test_loss.item():.4f} "
              f"Train Acc: {train_accuracy:.4f} "
              f"Test Acc: {test_accuracy:.4f} "
              f"Train F1: {train_f1:.4f} "
              f"Test F1: {test_f1:.4f}")






    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot(train_losses, label='Train Loss')
    plt.plot(test_losses, label='Test Loss')
    plt.title('Loss per Epoch')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(train_accuracies, label='Train Accuracy')
    plt.plot(test_accuracies, label='Test Accuracy')
    plt.title('Accuracy per Epoch')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()

    plt.show()