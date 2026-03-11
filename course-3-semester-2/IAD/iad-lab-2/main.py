import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

SEED = 42
torch.manual_seed(SEED)
np.random.seed(SEED)

device = torch.device("cpu")

df = pd.read_csv("archive/train-scene classification/train.csv")

le = LabelEncoder()
df["label"] = le.fit_transform(df["label"])
num_classes = len(le.classes_)

train_df, temp_df = train_test_split(
    df, test_size=0.2,
    random_state=SEED,
    stratify=df["label"]
)

val_df, test_df = train_test_split(
    temp_df, test_size=0.5,
    random_state=SEED,
    stratify=temp_df["label"]
)

print("Train:", len(train_df))
print("Val:", len(val_df))
print("Test:", len(test_df))

transform = transforms.Compose([
    transforms.Resize((64, 64)),
    transforms.ToTensor()
])

class SceneDataset(Dataset):
    def __init__(self, dataframe, img_dir):
        self.df = dataframe.reset_index(drop=True)
        self.img_dir = img_dir

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        img_name = self.df.loc[idx, "image_name"]
        label = self.df.loc[idx, "label"]

        img_path = os.path.join(
            "archive/train-scene classification/train",
            img_name
        )

        image = Image.open(img_path).convert("RGB")
        image = transform(image)

        return image, label


train_loader = DataLoader(
    SceneDataset(train_df, ""),
    batch_size=32,
    shuffle=True
)

val_loader = DataLoader(
    SceneDataset(val_df, ""),
    batch_size=32,
    shuffle=False
)

test_loader = DataLoader(
    SceneDataset(test_df, ""),
    batch_size=32,
    shuffle=False
)

class CNN(nn.Module):
    def __init__(self):
        super().__init__()

        self.conv = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Dropout2d(0.3)
        )

        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 16 * 16, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        x = self.conv(x)
        x = self.fc(x)
        return x


model = CNN().to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

EPOCHS = 15

train_losses = []
val_accuracies = []

for epoch in range(EPOCHS):

    model.train()
    total_loss = 0

    for images, labels in train_loader:
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    train_loss = total_loss / len(train_loader)
    train_losses.append(train_loss)

    model.eval()
    preds = []
    true = []

    with torch.no_grad():
        for images, labels in val_loader:
            outputs = model(images)
            predictions = torch.argmax(outputs, 1)

            preds.extend(predictions.numpy())
            true.extend(labels.numpy())

    val_acc = accuracy_score(true, preds)
    val_accuracies.append(val_acc)

    print(f"Epoch {epoch+1}: "
          f"Train Loss = {train_loss:.4f}, "
          f"Val Acc = {val_acc:.4f}")

model.eval()
preds = []
true = []

with torch.no_grad():
    for images, labels in test_loader:
        outputs = model(images)
        predictions = torch.argmax(outputs, 1)

        preds.extend(predictions.numpy())
        true.extend(labels.numpy())

test_acc = accuracy_score(true, preds)
print("\nTest Accuracy:", test_acc)

plt.figure()
plt.plot(train_losses)
plt.title("Train Loss")
plt.show()

plt.figure()
plt.plot(val_accuracies)
plt.title("Validation Accuracy")
plt.show()