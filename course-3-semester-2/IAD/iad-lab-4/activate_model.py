import torch
import torch.nn as nn
import cv2
import numpy as np
import albumentations as A
from albumentations.pytorch import ToTensorV2
import segmentation_models_pytorch as smp
import os
import glob
import matplotlib.pyplot as plt


class DoubleConv(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x): return self.double_conv(x)


class UNetScratch(nn.Module):
    def __init__(self, n_channels=3, n_classes=1):
        super(UNetScratch, self).__init__()
        self.inc = DoubleConv(n_channels, 64)
        self.down1 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(64, 128))
        self.down2 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(128, 256))
        self.down3 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(256, 512))
        self.down4 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(512, 1024))
        self.up1 = nn.ConvTranspose2d(1024, 512, kernel_size=2, stride=2)
        self.conv_up1 = DoubleConv(1024, 512)
        self.up2 = nn.ConvTranspose2d(512, 256, kernel_size=2, stride=2)
        self.conv_up2 = DoubleConv(512, 256)
        self.up3 = nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2)
        self.conv_up3 = DoubleConv(256, 128)
        self.up4 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
        self.conv_up4 = DoubleConv(128, 64)
        self.outc = nn.Conv2d(64, n_classes, kernel_size=1)

    def forward(self, x):
        x1 = self.inc(x);
        x2 = self.down1(x1);
        x3 = self.down2(x2);
        x4 = self.down3(x3);
        x5 = self.down4(x4)
        x = self.up1(x5);
        x = torch.cat([x, x4], dim=1);
        x = self.conv_up1(x)
        x = self.up2(x);
        x = torch.cat([x, x3], dim=1);
        x = self.conv_up2(x)
        x = self.up3(x);
        x = torch.cat([x, x2], dim=1);
        x = self.conv_up3(x)
        x = self.up4(x);
        x = torch.cat([x, x1], dim=1);
        x = self.conv_up4(x)
        return self.outc(x)


MODEL_TYPE = "scratch"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
DATA_DIR = os.path.join("sourse", "kaggle_3m")
IMG_SIZE = 256

MODEL_PATH = f"mri_model_{MODEL_TYPE}.pth"

if MODEL_TYPE == "scratch":
    model = UNetScratch(n_channels=3, n_classes=1).to(DEVICE)
else:
    model = smp.Unet(encoder_name="efficientnet-b3", encoder_weights=None, in_channels=3, classes=1).to(DEVICE)

if os.path.exists(MODEL_PATH):
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE, weights_only=True))
    model.eval()
    print(f"Модель {MODEL_TYPE} успешно загружена из {MODEL_PATH}")
else:
    print(f"Ошибка: Файл {MODEL_PATH} не найден!")
    exit()

all_files = glob.glob(os.path.join(DATA_DIR, "**", "*.tif"), recursive=True)
images = sorted([f for f in all_files if "_mask" not in f])
masks = [f.replace(".tif", "_mask.tif") for f in images]
valid_pairs = [(i, m) for i, m in zip(images, masks) if os.path.exists(m)]

transform = A.Compose([
    A.Resize(IMG_SIZE, IMG_SIZE),
    A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
    ToTensorV2()
])

all_ious = []
example_results = []
smooth = 1e-6

print(f"Запуск тестирования на {len(valid_pairs)} снимках...")

with torch.no_grad():
    for i, (img_path, mask_path) in enumerate(valid_pairs):
        img = cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_BGR2RGB)
        gt_mask = (cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE) > 0).astype(np.float32)
        gt_mask_res = cv2.resize(gt_mask, (IMG_SIZE, IMG_SIZE), interpolation=cv2.INTER_NEAREST)

        input_tensor = transform(image=img)["image"].unsqueeze(0).to(DEVICE)
        output = model(input_tensor)
        pred_mask = (torch.sigmoid(output) > 0.5).float().cpu().numpy()[0][0]

        intersection = np.sum(pred_mask * gt_mask_res)
        union = np.sum(np.maximum(pred_mask, gt_mask_res))
        iou = (intersection + smooth) / (union + smooth)
        all_ious.append(iou)

        if i % (max(1, len(valid_pairs) // 8)) == 0 and len(example_results) < 8:
            mask_res = cv2.resize(pred_mask, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_NEAREST)
            overlay = img.copy()
            overlay[mask_res > 0.5] = [255, 0, 0]

            res_img = cv2.addWeighted(img, 0.7, overlay, 0.3, 0)
            example_results.append(res_img)

print(f"\nИТОГОВЫЙ mIoU ({MODEL_TYPE}): {np.mean(all_ious):.4f}")

plt.figure(figsize=(10, 5))
plt.hist(all_ious, bins=50, color='skyblue', edgecolor='black')
plt.title(f'Распределение IoU для {MODEL_TYPE}')
plt.xlabel('IoU Score')
plt.ylabel('Количество снимков')
plt.grid(axis='y', alpha=0.3)
plt.savefig(f'iou_dist_{MODEL_TYPE}.png')

plt.figure(figsize=(16, 8))
for idx, res in enumerate(example_results):
    plt.subplot(2, 4, idx + 1)
    plt.imshow(res)
    plt.title(f"Sample {idx + 1}")
    plt.axis('off')
plt.tight_layout()
plt.savefig(f'test_examples_{MODEL_TYPE}.png')

print(f"Графики сохранены: iou_dist_{MODEL_TYPE}.png и test_examples_{MODEL_TYPE}.png")