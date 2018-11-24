from FileSystemWatcher import FileSystemWatcher, NotifyFilters, RenamedEventArgs, FileSystemEventArgs

__all__ = ['DirectoryWatcher']


class DirectoryWatcher:
    def __init__(self,
                 path: str,
                 on_created: callable = None,
                 on_deleted: callable = None,
                 on_renamed: callable = None,
                 filter: str = '*.*'):
        self._path = path
        self._filter = filter

        if not any([on_created, on_deleted, on_renamed]):
            raise ValueError('Specify at least one listener')

        self._created_callback = on_created
        self._renamed_callback = on_renamed
        self._deleted_callback = on_deleted

        self._watcher = self._make_watcher()
        self._watcher.EnableRaisingEvents = True

    def _make_watcher(self):
        watcher = FileSystemWatcher(self._path, filter=self._filter)
        watcher.NotifyFilter = NotifyFilters.FileName
        if self._created_callback:
            watcher.Created += self._on_created
        if self._renamed_callback:
            watcher.Renamed += self._on_renamed
        if self._deleted_callback:
            watcher.Deleted += self._on_deleted
        return watcher

    def _on_renamed(self, update: RenamedEventArgs):
        self._renamed_callback(update.OldFullPath, update.FullPath)

    def _on_created(self, update: FileSystemEventArgs):
        self._created_callback(update.FullPath)

    def _on_deleted(self, update: FileSystemEventArgs):
        self._deleted_callback(update.FullPath)
