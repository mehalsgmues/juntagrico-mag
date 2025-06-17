import base64
import json
from pathlib import Path


class AttachmentEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return {'AttachmentBytes': base64.b64encode(obj).decode('ascii')}
        return super().default(obj)


class AttachmentDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dictionary):
        if 'AttachmentBytes' in dictionary:
            return base64.b64decode(dictionary['AttachmentBytes'].encode('ascii'))
        return dictionary


class Lock:
    def __init__(self, file):
        self._file = file
        self._lock = None

    def __enter__(self):
        try:
            self._lock = open(self._file, 'x')
        except FileExistsError:
            raise RuntimeError('sendmails command is already running.')

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._lock:
            self._lock.close()
        Path(self._file).unlink()
