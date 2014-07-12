#
# Managing destination of files
#
import os
import hashlib

class file_manager(object):
        def __init__(self, direc):
                self.dir = direc
                if not os.path.exists(os.path.dirname(self.dir)):
                        os.makedirs(os.path.dirname(self.dir))
        def place(self, _file):
                path = _file.name
                vals = path.split(os.sep)
                name = vals[len(vals)-1]
                finalpath = self.dir+os.sep
                return (hashlib.sha224(finalpath).hexdigest(), finalpath)
