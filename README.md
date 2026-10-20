# LLUN

ASCII-видеоплеер в отдельном окне: видео преобразуется в цветную ASCII-анимацию и проигрывается в окне Pygame, без прокрутки обычной терминальной консоли.

## Что делает проект

- читает `video.mp4` через OpenCV;
- переводит кадры в ASCII-символы с сохранением RGB-цвета;
- поддерживает цветной вывод True Color;
- рисует анимацию в отдельном окне, а не в консоли;
- повторяет видео бесконечно до `Esc` или `Ctrl+C`;
- поддерживает Windows 10, Ubuntu, Arch Linux.

## Быстрый запуск

### Windows 10 (PowerShell)

```powershell
git clone https://github.com/lwspamov-gif/LLUN.git
cd LLUN
Set-ExecutionPolicy -Scope Process Bypass
.\run.ps1
```

### Ubuntu / Arch Linux (Bash)

```bash
git clone https://github.com/lwspamov-gif/LLUN.git
cd LLUN
chmod +x run.sh
./run.sh
```

## Требования

- Python 3.11+
- `numpy`
- `opencv-python`
- `pygame` / `pygame-ce`
- подключение к интернету при первой установке зависимостей

## Как подготовить проект вручную

1. Положи исходное видео в корень проекта как `video.mp4`.
2. Создай виртуальное окружение.
3. Установи зависимости.
4. Запусти `run.py`.

### Windows 10

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python .\run.py
```

### Ubuntu / Arch Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python run.py
```

## Запуск отдельного окна

Если нужно открыть самостоятельное чёрное окно вместо обычного терминала, используй:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\start-video.ps1
```

Окно будет развёрнуто на весь экран и будет запускать проект в отдельном PowerShell-процессе.

## Управление

- `Space` — пауза / продолжение
- `←` / `→` — предыдущий / следующий кадр
- `F11` — полноэкранный режим
- `Esc` — выход

## Важные замечания

- `output/animation.json.gz` — уже сгенерированная анимация. Если поменялись настройки кодирования, удаляй старый кэш и пересоздавай его.
- Плотная ASCII-кадровая графика очень тяжёлая для терминала и даже для окна. Если окно слишком узкое, строка переносится, поэтому ширину нужно уменьшить или развернуть окно.
- Для более плавного воспроизведения можно уменьшать `--width` в `encoder.py` или `run.py`.

## GitHub и публикация

```bash
git add .
git commit -m "Update LLUN README and launcher instructions"
git branch -M main
git push -u origin main
```

Если remote уже настроен:

```bash
git add README.md
git commit -m "Update LLUN README"
git push
```
