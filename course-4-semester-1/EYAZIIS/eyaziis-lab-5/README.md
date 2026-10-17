# Лабораторная работа. Фонетические, просодические и компиляционные закономерности речевого сигнала

Часть 1: изучение фонетических закономерностей речевого сигнала.

## Структура проекта

```
eyaziis-lab-5/
├── README.md
├── audio/lab1/              записи *.wav
│   ├── rate_depth/          варианты частоты дискретизации и разрядности
│   ├── sample1.wav          гласные [а о у э ы и]
│   ├── sample1b.wav         гласные буквы «я ё ю е»
│   ├── sample2.wav          шипящие [ф с ш х]
│   ├── sample3.wav          слоги «фа са ша ха»
│   ├── sample4.wav          [б д м н]
│   └── sample5.wav          слоги «ба да ма на»
├── scripts/                 Python-анализ и генерация рисунков
└── eyazis-report-5/         LaTeX-отчёт
    ├── sections/*.tex
    └── png/                 рисунки для отчёта
```

## Программное обеспечение

- Audacity 4.0 (`C:\Program Files\Audacity 4\bin\Audacity4.exe`) — запись и прослушивание
- Python 3.14: numpy, scipy, soundfile, matplotlib — анализ и графики
- MiKTeX + latexmk — сборка отчёта

## Настройка проекта в Audacity

1. Внизу окна задайте частоту проекта (Project Rate): **16000 Гц**
2. Микрофон: моно (1 channel), 16-битное ПКМ (Signed 16-bit PCM)
3. Красная кнопка Record (R) — запись, пробел — стоп
4. Файл → Экспорт → Экспорт как WAV → `audio/lab1/...`

## Сборка отчёта

```powershell
cd eyazis-report-5
latexmk -pdf course_report.tex
```
