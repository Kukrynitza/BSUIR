import os
import cv2
import glob
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
import albumentations as A
from albumentations.pytorch import ToTensorV2
import segmentation_models_pytorch as smp
from tqdm import tqdm

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
DATA_DIR = os.path.join("sourse", "kaggle_3m")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
IMG_SIZE = 256
BATCH_SIZE = 8
EPOCHS = 21
LR = 1e-4


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


all_files = glob.glob(os.path.join(DATA_DIR, "**", "*.tif"), recursive=True)
images = sorted([f for f in all_files if "_mask" not in f])
masks = [f.replace(".tif", "_mask.tif") for f in images]

valid_images, valid_masks = [], []
for i, m in zip(images, masks):
    if os.path.exists(m):
        valid_images.append(i);
        valid_masks.append(m)

X_train, X_val, y_train, y_val = train_test_split(valid_images, valid_masks, test_size=0.2, random_state=42)

train_transforms = A.Compose([
    A.Resize(IMG_SIZE, IMG_SIZE),
    A.HorizontalFlip(p=0.5),
    A.Affine(rotate=(-15, 15), scale=(0.95, 1.05), translate_percent=(-0.05, 0.05), p=0.5),
    A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
    ToTensorV2()
])

val_transforms = A.Compose([
    A.Resize(IMG_SIZE, IMG_SIZE),
    A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
    ToTensorV2()
])


class MRIDataset(Dataset):
    def __init__(self, img_paths, mask_paths, transform=None):
        self.img_paths, self.mask_paths, self.transform = img_paths, mask_paths, transform

    def __len__(self): return len(self.img_paths)

    def __getitem__(self, idx):
        img = cv2.cvtColor(cv2.imread(self.img_paths[idx]), cv2.COLOR_BGR2RGB)
        mask = (cv2.imread(self.mask_paths[idx], cv2.IMREAD_GRAYSCALE) > 0).astype(np.float32)
        if self.transform:
            augmented = self.transform(image=img, mask=mask)
            img, mask = augmented['image'], augmented['mask']
        return img, mask


def get_metrics(pred, target):
    smooth = 1e-6
    pred = (torch.sigmoid(pred) > 0.5).float()
    target = target.float().unsqueeze(1)
    intersection = (pred * target).sum()
    union = (pred + target).clamp(0, 1).sum()
    iou = (intersection + smooth) / (union + smooth)
    dice = (2. * intersection + smooth) / (pred.sum() + target.sum() + smooth)
    return iou, dice


def main(model_type="scratch"):
    print(f"--- Starting: {model_type} on {DEVICE} ---")

    train_loader = DataLoader(MRIDataset(X_train, y_train, train_transforms), batch_size=BATCH_SIZE, shuffle=True,
                              num_workers=0)
    val_loader = DataLoader(MRIDataset(X_val, y_val, val_transforms), batch_size=BATCH_SIZE, num_workers=0)

    if model_type == "scratch":
        model = UNetScratch().to(DEVICE)
    else:
        model = smp.Unet(encoder_name="efficientnet-b3", encoder_weights="imagenet", in_channels=3, classes=1).to(
            DEVICE)

    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=3)
    criterion_bce = nn.BCEWithLogitsLoss()
    criterion_dice_loss = smp.losses.DiceLoss(mode='binary', from_logits=True)

    for epoch in range(EPOCHS):
        model.train()
        train_loss = 0
        pbar = tqdm(train_loader, desc=f"Epoch {epoch + 1}/{EPOCHS}")

        for imgs, msks in pbar:
            imgs, msks = imgs.to(DEVICE), msks.to(DEVICE)
            optimizer.zero_grad()
            output = model(imgs)
            loss = criterion_bce(output.squeeze(1), msks.float()) + criterion_dice_loss(output, msks.unsqueeze(1))
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
            pbar.set_postfix(loss=loss.item())

        model.eval()
        v_iou, v_dice = 0, 0
        with torch.no_grad():
            for imgs, msks in val_loader:
                imgs, msks = imgs.to(DEVICE), msks.to(DEVICE)
                output = model(imgs)
                iou, dice = get_metrics(output, msks)
                v_iou += iou.item()
                v_dice += dice.item()

        avg_iou = v_iou / len(val_loader)
        avg_dice = v_dice / len(val_loader)
        avg_loss = train_loss / len(train_loader)
        scheduler.step(avg_iou)

        print(
            f"\n[Epoch {epoch + 1}] Avg Loss: {avg_loss:.4f} | mIoU: {avg_iou:.4f} | Dice: {avg_dice:.4f} | LR: {optimizer.param_groups[0]['lr']}")

    torch.save(model.state_dict(), f"mri_model_{model_type}.pth")
    print(f"--- Training Finished. Model saved. ---")


if __name__ == "__main__":
    main(model_type="imagenet")