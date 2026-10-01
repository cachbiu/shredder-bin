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

Ярлык **Shredder Bin** на рабочем столе запускает виджет через `run.py` и `pythonw` (без консоли).

Анимация: `assets/shredder.gif` (кот со шредером). Если файла нет, удаление в корзину всё равно работает.

## Управление

- Drag-and-drop файла или папки — в Recycle Bin + GIF
- Клик по виджету — открыть системную корзину
- Перетаскивание окна — за иконку
- ПКМ: открыть корзину, поверх окон, выход
