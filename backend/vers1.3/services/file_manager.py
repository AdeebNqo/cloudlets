#
# Managing destination of files
#
import os
import hashlib

class file_manager(object):
        def __init__(self, direc):
                self.dir = os.getcwd()+os.sep+direc
                if not os.path.exists(os.path.dirname(self.dir)):
                        os.makedirs(os.path.dirname(self.dir))
        def place(self, _file, filename):
                path = _file.name
                vals = path.split(os.sep)
                name = vals[len(vals)-1]
                finalpath = "{0}{1}".format(self.dir,filename)
                print('path is {}'.format(finalpath))
                return (hashlib.sha224(finalpath).hexdigest(), finalpath)
