import os
import pathlib

from common.runtime import get_runtime_path


class TmpDir(object):
    """A temporary directory that is deleted when the object is destroyed."""

    tmpFilePath = pathlib.Path(get_runtime_path("tmp"))

    def __init__(self):
        pathExists = os.path.exists(self.tmpFilePath)
        if not pathExists:
            os.makedirs(self.tmpFilePath)

    def path(self):
        return str(self.tmpFilePath) + "/"
