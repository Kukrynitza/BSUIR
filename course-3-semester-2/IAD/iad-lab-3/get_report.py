import torch
import pandas as pd
from main import get_model, val_loader, test_loader, device, accuracy_score


def build_report():
    modes = ["A", "B", "C"]
    results = []

    for mode in modes:
        path = f"models/model_{mode}.pth"
        if not torch.os.path.exists(path):
            print(f"Пропуск: файл {path} не найден.")
            continue

        model = get_model(mode).to(device)
        model.load_state_dict(torch.load(path, map_location=device, weights_only=True))
        model.eval()

        trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)

        def evaluate(loader):
            preds, true = [], []
            with torch.no_grad():
                for imgs, labels in loader:
                    out = model(imgs.to(device))
                    preds.extend(torch.argmax(out, 1).cpu().numpy())
                    true.extend(labels.numpy())
            return accuracy_score(true, preds)

        print(f"Модель {mode} вычисляется точность")
        val_acc = evaluate(val_loader)
        test_acc = evaluate(test_loader)

        results.append({
            "Модель": mode,
            "Режим": "С нуля" if mode == "A" else ("Заморозка" if mode == "B" else "Fine-tuning"),
            "Обучаемых парам.": f"{trainable:,}",
            "Val Accuracy": f"{val_acc:.4f}",
            "Test Accuracy": f"{test_acc:.4f}"
        })

    df_res = pd.DataFrame(results)
    print("\n" + "=" * 80)
    print(df_res.to_string(index=False))
    print("=" * 80)


if __name__ == '__main__':
    build_report()