# ASCII-Video

ASCII-Video — это простой проект для превращения обычного видео в цветную ASCII-анимацию, которая проигрывается прямо в терминале.

## Что делает проект

- читает `video.mp4` через OpenCV;
- уменьшает кадры до ширины терминала;
- сохраняет пропорции видео;
- переводит яркость и RGB-цвета в символы ASCII;
- поддерживает цветной вывод в ANSI True Color;
- проигрывает анимацию по кругу до `Ctrl+C`;
- работает на Windows 10, Ubuntu и Arch Linux.

## Быстрый запуск

### Windows 10 (PowerShell)

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\run.ps1
```

### Ubuntu / Arch Linux (Bash)

```bash
chmod +x run.sh
./run.sh
```

## Требования

- Python 3
- терминал с поддержкой ANSI True Color (желательно)
- подключение к интернету при первой установке зависимостей

## Как подготовить проект

1. Помести исходное видео в корень проекта как `video.mp4`.
2. Убедись, что в папке есть файлы:
   - `run.py`
   - `run.sh`
   - `run.ps1`
   - `requirements.txt`
3. Запусти:

### Windows 10

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
.\run.ps1
```

### Ubuntu / Arch Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
chmod +x run.sh
./run.sh
```

## Команды запуска для GitHub

### Ubuntu / Arch Linux

```bash
git clone https://github.com/lwspamov-gif/LLUN.git
cd LLUN
chmod +x run.sh
./run.sh
```

### Windows 10

```powershell
git clone https://github.com/lwspamov-gif/LLUN.git
cd LLUN
.\run.ps1
```

## Важные замечания

- `60 FPS` — целевая частота, а не жёсткая гарантия. При медленном терминале кадры могут пропускаться, чтобы не накапливалась задержка.
- Ширина 300 символов подходит только для достаточно широкого окна терминала.
- Если терминал не поддерживает ANSI True Color, программа может перейти в более простой режим вывода, но при этом будет продолжать работать.
- Для остановки нажмите `Ctrl+C`.

## GitHub и публикация

После фиксации обновлений можно опубликовать проект в GitHub командой:

```bash
git add .
git commit -m "Fix README encoding and terminal playback instructions"
git branch -M main
git remote add origin https://github.com/lwspamov-gif/LLUN.git
git push -u origin main
```

Если remote уже существует, используйте:

```bash
git remote set-url origin https://github.com/lwspamov-gif/LLUN.git
git push --force-with-lease origin main
```

## Что важно для корректного отображения на GitHub

Файл README должен быть сохранён в UTF-8. В старых редакторах иногда сохраняли файл в неправильной кодировке, из-за чего GitHub показывал символы в виде "ромбиков" или вопросительных знаков. В репозитории добавлен файл `.gitattributes`, который помогает Git правильно трактовать текстовые файлы и сохраняет их в корректной кодировке.
