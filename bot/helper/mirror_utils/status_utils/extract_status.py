from time import time

from bot import DOWNLOAD_DIR, LOGGER
from bot.helper.ext_utils.bot_utils import (MirrorStatus,
                                            get_readable_file_size,
                                            get_readable_time)
from bot.helper.ext_utils.fs_utils import get_path_size


class ExtractStatus:
    def __init__(self, name, size, gid, listener):
        self.__name = name
        self.__size = size
        self.__gid = gid
        self.__listener = listener
        self.__uid = self.__listener.uid
        self.__start_time = time()
        self.message = self.__listener.message
        self.source = self.__source()
        self.engine = '7z'

    def gid(self):
        return self.__gid

    def speed_raw(self):
        return self.processed_bytes() / (time() - self.__start_time)

    def progress_raw(self):
        try:
            return self.processed_bytes() / self.__size * 100
        except:
            return 0

    def progress(self):
        return f'{round(self.progress_raw(), 2)}%'

    def speed(self):
        return f'{get_readable_file_size(self.speed_raw())}/s'

    def name(self):
        return self.__name

    def size_raw(self):
        return self.__size

    def size(self):
        return get_readable_file_size(self.__size)

    def eta(self):
        try:
            seconds = (self.size_raw() - self.processed_bytes()) / self.speed_raw()
            return f'{get_readable_time(seconds)}'
        except:
            return '-'

    def status(self):
        return MirrorStatus.STATUS_EXTRACTING

    def processed_bytes(self):
        if self.__listener.newDir:
            return get_path_size(f"{DOWNLOAD_DIR}{self.__uid}10000")
        else:
            return get_path_size(f"{DOWNLOAD_DIR}{self.__uid}") - self.__size

    def download(self):
        return self

    def cancel_download(self):
        LOGGER.info(f'Cancelling Extract: {self.__name}')
        if self.__listener.suproc:
            self.__listener.suproc.kill()
        self.__listener.onUploadError('extracting stopped by user!')

    def __source(self):
        reply_to = self.message.reply_to_message
        return reply_to.from_user.username or reply_to.from_user.id if reply_to and \
            not reply_to.from_user.is_bot else self.message.from_user.username \
                or self.message.from_user.id

    def mode(self):
        return self.__listener.mode