# Shredder Bin

Виджет корзины для Windows: перетащите файлы из Explorer — они попадут в системную Recycle Bin, поверх иконки проиграется GIF шреддера.

Список файлов в приложении не ведётся. Восстановление и очистка — в стандартной корзине Windows.

## Запуск

Нужен Python 3.11+.

```powershell
cd C:\Users\DLarichev\Projects\shredder-bin
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
.\.venv\Scripts\python -m shredder_bin
```

Ярлык **Shredder Bin** на рабочем столе запускает виджет через `run.py` и `pythonw` (без консоли). Замороженный `.exe` сам создаёт такой ярлык при запуске.

Анимация: `assets/shredder.gif` (кот со шредером). Если файла нет, удаление в корзину всё равно работает.

## Сборка exe для раздачи

На Windows, в этой папке:

```powershell
.\.venv\Scripts\python -m pip install -r requirements-build.txt
.\.venv\Scripts\python -m PyInstaller --noconfirm --clean ShredderBin.spec
```

Готовый файл: `dist\ShredderBin.exe`. Его можно скопировать кому угодно: Python на чужом ПК не нужен. Первый запуск положит ярлык на рабочий стол. Антивирус может ругаться на неподписанный PyInstaller — это обычная история для самосборных exe.

## Управление

- Drag-and-drop файла или папки — в Recycle Bin + GIF
- Клик по виджету — открыть системную корзину
- Перетаскивание окна — за иконку
- ПКМ: открыть корзину, поверх окон, выход
