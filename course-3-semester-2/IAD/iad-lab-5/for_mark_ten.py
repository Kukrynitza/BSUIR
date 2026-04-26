import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import transforms, datasets, utils
from torch.utils.data import DataLoader, Subset
from torch.nn.utils import spectral_norm
from torchmetrics.image.fid import FrechetInceptionDistance
import matplotlib.pyplot as plt
import numpy as np

MAX_TRAIN_SAMPLES = 5000


class Generator(nn.Module):
    def __init__(self, latent_dim=100):
        super().__init__()
        self.net = nn.Sequential(
            nn.ConvTranspose2d(latent_dim, 512, 4, 1, 0, bias=False),
            nn.BatchNorm2d(512),
            nn.ReLU(True),

            nn.ConvTranspose2d(512, 256, 4, 2, 1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(True),

            nn.ConvTranspose2d(256, 128, 4, 2, 1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(True),

            nn.ConvTranspose2d(128, 64, 4, 2, 1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(True),

            nn.ConvTranspose2d(64, 3, 4, 2, 1, bias=False),
            nn.Tanh()
        )

    def forward(self, z):
        return self.net(z)


class Discriminator(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            spectral_norm(nn.Conv2d(3, 64, 4, 2, 1, bias=False)),
            nn.LeakyReLU(0.2, inplace=True),

            spectral_norm(nn.Conv2d(64, 128, 4, 2, 1, bias=False)),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2, inplace=True),

            spectral_norm(nn.Conv2d(128, 256, 4, 2, 1, bias=False)),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2, inplace=True),

            spectral_norm(nn.Conv2d(256, 512, 4, 2, 1, bias=False)),
            nn.BatchNorm2d(512),
            nn.LeakyReLU(0.2, inplace=True),

            spectral_norm(nn.Conv2d(512, 1, 4, 1, 0, bias=False))
        )

    def forward(self, img):
        return self.net(img).view(-1)



def weights_init(m):
    if isinstance(m, (nn.Conv2d, nn.ConvTranspose2d)):
        nn.init.normal_(m.weight, 0.0, 0.02)
    elif isinstance(m, nn.BatchNorm2d):
        nn.init.normal_(m.weight, 1.0, 0.02)
        nn.init.zeros_(m.bias)


def denorm(x):
    return (x * 0.5 + 0.5).clamp(0, 1)


def prep_fid(img):
    img = denorm(img)
    img = F.interpolate(img, size=(75, 75))
    return (img * 255).byte()



if __name__ == '__main__':
    torch.manual_seed(42)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print("Device:", device)

    latent_dim = 100
    batch_size = 128
    num_epochs = 90
    lr = 2e-4

    transform = transforms.Compose([
        transforms.Resize(64),
        transforms.CenterCrop(64),
        transforms.ToTensor(),
        transforms.Normalize([0.5]*3, [0.5]*3)
    ])

    dataset_full = datasets.ImageFolder('sourse/images', transform=transform)

    if MAX_TRAIN_SAMPLES is not None:
        indices = torch.randperm(len(dataset_full))[:MAX_TRAIN_SAMPLES]
        dataset = Subset(dataset_full, indices)
    else:
        dataset = dataset_full
    print("Используем изображений:", len(dataset))
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    print("Dataset size:", len(dataset_full))

    gen = Generator(latent_dim).to(device)
    disc = Discriminator().to(device)

    gen.apply(weights_init)
    disc.apply(weights_init)

    criterion = nn.BCEWithLogitsLoss()

    opt_G = optim.Adam(gen.parameters(), lr=lr, betas=(0.5, 0.999))
    opt_D = optim.Adam(disc.parameters(), lr=lr, betas=(0.5, 0.999))

    fixed_noise = torch.randn(16, latent_dim, 1, 1, device=device)

    history = {'loss_D': [], 'loss_G': [], 'D_x': [], 'D_G_z': []}

    os.makedirs("results-5000", exist_ok=True)


    for epoch in range(num_epochs):
        lossD_sum = lossG_sum = Dx_sum = DGz_sum = 0

        for real, _ in dataloader:
            real = real.to(device)
            b = real.size(0)

            opt_D.zero_grad()

            real_labels = torch.full((b,), 0.9, device=device)
            fake_labels = torch.zeros(b, device=device)

            out_real = disc(real)
            loss_real = criterion(out_real, real_labels)

            z = torch.randn(b, latent_dim, 1, 1, device=device)
            fake = gen(z)
            out_fake = disc(fake.detach())
            loss_fake = criterion(out_fake, fake_labels)

            loss_D = loss_real + loss_fake
            loss_D.backward()
            opt_D.step()

            opt_G.zero_grad()

            z = torch.randn(b, latent_dim, 1, 1, device=device)
            fake = gen(z)
            out = disc(fake)

            loss_G = criterion(out, torch.ones(b, device=device))
            loss_G.backward()
            opt_G.step()

            lossD_sum += loss_D.item()
            lossG_sum += loss_G.item()
            Dx_sum += torch.sigmoid(out_real).mean().item()
            DGz_sum += torch.sigmoid(out).mean().item()

        n = len(dataloader)
        history['loss_D'].append(lossD_sum / n)
        history['loss_G'].append(lossG_sum / n)
        history['D_x'].append(Dx_sum / n)
        history['D_G_z'].append(DGz_sum / n)

        print(f"[{epoch+1}/{num_epochs}] "
              f"LossD={history['loss_D'][-1]:.3f} "
              f"LossG={history['loss_G'][-1]:.3f}")

        if (epoch+1) % 5 == 0:
            gen.eval()
            with torch.no_grad():
                fake = gen(fixed_noise)
                grid = utils.make_grid(denorm(fake), nrow=4)
                plt.imshow(np.transpose(grid.cpu(), (1,2,0)))
                plt.axis('off')
                plt.savefig(f"results-5000/epoch_{epoch+1}.png")
                plt.close()
            gen.train()

    plt.plot(history['loss_D'], label='Loss D')
    plt.plot(history['loss_G'], label='Loss G')
    plt.legend()
    plt.savefig("results-5000/loss.png")
    plt.close()

    plt.plot(history['D_x'], label='D(x)')
    plt.plot(history['D_G_z'], label='D(G(z))')
    plt.legend()
    plt.savefig("results-5000/D_metrics.png")
    plt.close()

    print("Calculating FID...")
    fid = FrechetInceptionDistance(feature=2048).to(device)

    NUM = 10000

    s = 0
    for real, _ in dataloader:
        real = real.to(device)
        fid.update(prep_fid(real), real=True)
        s += real.size(0)
        if s >= NUM:
            break

    gen.eval()
    s = 0
    with torch.no_grad():
        while s < NUM:
            z = torch.randn(batch_size, latent_dim, 1, 1, device=device)
            fake = gen(z)
            fid.update(prep_fid(fake), real=False)
            s += batch_size

    print("FID:", fid.compute().item())


    torch.save(gen.state_dict(), "results-5000/generator.pth")
    torch.save(disc.state_dict(), "results-5000/discriminator.pth")

    print("DONE")

    z1 = torch.randn(1, latent_dim, 1, 1, device=device)
    z2 = torch.randn(1, latent_dim, 1, 1, device=device)

    alphas = torch.linspace(0, 1, steps=10)

    gen.eval()
    with torch.no_grad():
        images = [gen((1 - a) * z1 + a * z2) for a in alphas]

    grid = utils.make_grid(denorm(torch.cat(images)), nrow=10)
    plt.imshow(np.transpose(grid.cpu(), (1, 2, 0)))
    plt.axis('off')
    plt.savefig("results-5000/interpolation.png")
    plt.close()