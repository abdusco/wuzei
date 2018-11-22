# Wuzei
Wallpaper manager for Windows. Like Muzei on Android but more primitive.

## Usage
Install dependencies and run. The app defaults to `./config.ini`, 
gives error if it doesn't exists and not specified as argument.

```commandline
pipenv install
python -m wuzei config.ini
```

## Configuration
```ini
[config]
cache_dir = d:\wallpapers\.cache
interval = 20
blurred = yes
shuffled = yes
paused = no

[sources]
nature = d:\wallpapers\nature
```