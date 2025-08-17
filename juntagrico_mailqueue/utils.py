import base64
import datetime
import json
import logging
from pathlib import Path


logger = logging.getLogger(__name__)


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
    def __init__(self, file, expiration=5):
        self._file = file
        self.expiration = expiration

    def __enter__(self):
        try:
            logger.debug(f'Acquiring Lock {self._file}')
            open(self._file, 'x').close()
        except FileExistsError:
            # check if lock file is old and
            lock_time = datetime.datetime.fromtimestamp(Path(self._file).stat().st_mtime)
            if lock_time + datetime.timedelta(minutes=self.expiration) < datetime.datetime.now():
                self.renew()
            else:
                raise RuntimeError('sendmails command is already running.')

    def renew(self):
        # touch lock file to renew the timestamp
        Path(self._file).touch()

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug(f'Releasing Lock {self._file}')
        Path(self._file).unlink()
