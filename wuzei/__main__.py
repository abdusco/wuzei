import sys
from pathlib import Path
import keyboard
from .core.manager import WallpaperManager
from threading import Thread
from time import sleep
from multiprocessing.connection import Listener, Client

ADDRESS = ('127.0.0.1', 9090)
SECRET = bytes('secret', encoding='utf-8')


def run_server(source, callback: callable = None):
    wuzei = WallpaperManager(paths=[source])

    actions = dict(
        next=wuzei.next_wallpaper,
        prev=wuzei.prev_wallpaper,
        shuffle=wuzei.toggle_shuffle,
        blur=wuzei.blur,
        unblur=wuzei.unblur,
        toggle_blur=wuzei.toggle_blur
    )

    with Listener(ADDRESS, authkey=SECRET) as listener:
        if callback:
            callback()
        with listener.accept() as conn:
            print('connection accepted from', listener.last_accepted)
            while True:
                msg = conn.recv()
                if msg == 'close':
                    print('bye')
                    conn.close()
                    break
                try:
                    print('RECEIVED:', msg)
                    actions[msg]()
                except KeyError:
                    pass


def setup_client():
    print('setting up client')
    client = Client(ADDRESS, authkey=SECRET)
    keyboard.add_hotkey('alt+shift+left',
                        # callback=client.prev,
                        # args=[client],
                        callback=client.send,
                        args=['prev'],
                        suppress=True,
                        trigger_on_release=True)
    keyboard.add_hotkey('alt+shift+right',
                        # callback=client.prev,
                        # args=[client],
                        callback=client.send,
                        args=['next'],
                        suppress=True,
                        trigger_on_release=True)
    keyboard.add_hotkey('alt+\\',
                        # callback=client.prev,
                        # args=[client],
                        callback=client.send,
                        args=['close'],
                        suppress=True,
                        trigger_on_release=True)
    keyboard.add_hotkey('alt+shift+s',
                        # callback=client.prev,
                        # args=[client],
                        callback=client.send,
                        args=['shuffle'],
                        suppress=True,
                        trigger_on_release=True)
    keyboard.add_hotkey('alt+shift+/',
                        # callback=client.prev,
                        # args=[client],
                        callback=client.send,
                        args=['toggle_blur'],
                        suppress=True,
                        trigger_on_release=True)


def main():
    if not sys.argv[1]:
        raise ValueError
    source = Path(sys.argv[1])
    if not source.exists() or not source.is_dir():
        print(f'Not a directory. {source}')
        raise ValueError

    def cb():
        t = Thread(target=setup_client)
        t.start()

    run_server(source=str(source),
               callback=cb)


main()
