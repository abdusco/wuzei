# Wuzei
Wallpaper manager for Windows. Like Muzei on Android but more primitive.

## Usage
Install dependencies and run.
```commandline
pipenv install
python -m wuzei config.ini
```

## Configuration
```ini
[config]
cache_dir = d:\wallpapers\.cache
interval = 20
start_blurred = yes
start_shuffled = yes
start_paused = no

[sources]
nature = d:\wallpapers\nature
```