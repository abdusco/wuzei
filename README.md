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
hook_refresh_interval = 60

[hotkeys]
# Reference
# https://github.com/boppreh/keyboard#keyboardall_modifiers
# Leave a hotkey empty or remove it to disable
prev = alt+shift+[
next = alt+shift+]
prev_source = ctrl+alt+shift+[
next_source = ctrl+alt+shift+]
toggle_shuffle = alt+shift+s
toggle_blur = alt+shift+b
blur = alt+shift+/
exit = alt+shift+\
pause = alt+shift+p
view = alt+shift+v

[sources]
nature = d:\wallpapers\nature
abstract = d:\wallpapers\abstract
```