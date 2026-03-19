import os
import time
import numpy as np
import pandas as pd
from PIL import Image

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

SEED = 42
torch.manual_seed(SEED)
np.random.seed(SEED)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

df = pd.read_csv("../archive/train-scene classification/train.csv")
le = LabelEncoder()
df["label"] = le.fit_transform(df["label"])
num_classes = len(le.classes_)

train_df, temp_df = train_test_split(df, test_size=0.2, random_state=SEED, stratify=df["label"])
val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=SEED, stratify=temp_df["label"])

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.Lambda(lambda img: img.convert("RGB")),
    transforms.ToTensor(),
    # transforms.Normalize(([0.485, 0.456, 0.406]), ([0.229, 0.224, 0.225]))
])

class SceneDataset(Dataset):
    def __init__(self, dataframe, base_path):
        self.df = dataframe.reset_index(drop=True)
        self.base_path = base_path

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        img_path = os.path.join(self.base_path, self.df.loc[idx, "image_name"])
        image = transform(Image.open(img_path))
        return image, self.df.loc[idx, "label"]

img_dir = "../archive/train-scene classification/train"
test_loader = DataLoader(
    SceneDataset(test_df, img_dir),
    batch_size=64,
    shuffle=False,
    num_workers=4,
    pin_memory=True
)
train_loader = DataLoader(SceneDataset(train_df, img_dir), batch_size=64, shuffle=True, num_workers=4, pin_memory=True)
val_loader = DataLoader(SceneDataset(val_df, img_dir), batch_size=64, shuffle=False, num_workers=4, pin_memory=True)

class ModelA(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2),
            nn.Dropout2d(0.3)
        )
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 56 * 56, 128), nn.ReLU(), nn.Dropout(0.5),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        return self.fc(self.conv(x))

def get_model(mode="A"):
    if mode == "A":
        return ModelA(num_classes)

    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model.fc = nn.Linear(model.fc.in_features, num_classes)

    if mode == "B":
        for name, param in model.named_parameters():
            if "fc" not in name:
                param.requires_grad = False
    return model

def train_and_save(mode="A", epochs=10):
    model = get_model(mode).to(device)
    os.makedirs("models", exist_ok=True)

    if mode == "A":
        optimizer = optim.Adam(model.parameters(), lr=0.01)
    elif mode == "B":
        optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=0.001)
    elif mode == "C":
        optimizer = optim.Adam([
            {'params': [p for n, p in model.named_parameters() if "fc" not in n], 'lr': 1e-4},
            {'params': model.fc.parameters(), 'lr': 1e-3}
        ])

    criterion = nn.CrossEntropyLoss()
    print(f"\n___ Запуск Модели {mode} ___")

    for epoch in range(epochs):
        start_time = time.time()
        model.train()
        for imgs, labels in train_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            optimizer.zero_grad()
            criterion(model(imgs), labels).backward()
            optimizer.step()

        model.eval()
        all_preds, all_true = [], []
        with torch.no_grad():
            for imgs, labels in val_loader:
                outputs = model(imgs.to(device))
                all_preds.extend(torch.argmax(outputs, 1).cpu().numpy())
                all_true.extend(labels.numpy())

        acc = accuracy_score(all_true, all_preds)
        print(f"Эпоха {epoch + 1}: Val Acc = {acc:.4f}, Время = {time.time() - start_time:.1f}s")

    torch.save(model.state_dict(), f"models/model_{mode}.pth")
    print(f"Модель {mode} успешно сохранена в папку models.")


if __name__ == '__main__':
    train_and_save(mode="A", epochs=15)