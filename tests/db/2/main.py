import cProfile
from db import db
import ConfigParser
import base64

configreader = ConfigParser.ConfigParser()
configreader.read('config.ini')
#reading in file metadata
primkey = configreader.get('DEFAULT','id')
access = configreader.get('DEFAULT','access')
filename = configreader.get('DEFAULT','filename')
owner = configreader.get('DEFAULT','owner')
accesslist = configreader.get('DEFAULT','accesslist')
compression = configreader.get('DEFAULT','compression')

objectdata = base64.b64encode(open(filename,'r').read())

class DatabaseTest(object):
        def __init__(self,dbtype):
                self.currdb = db(dbtype)
                self.currdb.set_credentials('localhost', 'root', 101, 'cloudletX', 'files')
                self.currdb.connect()
        def test_insert(self,keys,data):
                cProfile.runctx('self.currdb.insert(keys,data)',globals(), locals())
        def test_get(self,key):
                cProfile.runctx('self.currdb.get(key)',globals(), locals())
        def test_update(self, key, keys, data):
                cProfile.runctx('self.currdb.update(self, key, keys, data)',globals(), locals())
        def test_delete(self,key):
                cProfile.runctx('self.currdb.delete(key)',globals(), locals())
        def test_getpublicfiles():
                cProfile.runctx('self.currdb.getpublicfiles()', globals(),locals())
        def test_getsharedfiles(self,requester):
                cProfile.runctx('self.getsharedfiles(requester)', globals(), locals())
        def test_cleandata(self):
                cProfile.runctx('self.cleandata()', globals(), locals())
if __name__=='__main__':
        databases = ['mysql','berkeleydb']
        for dbtype in databases:
                print('\t=={} tests=='.format(dbtype))
                dbX = DatabaseTest(dbtype)
                dbX.test_insert(('id', 'access', 'filename', 'owner', 'accesslist','compression'), (primkey, access, filename, owner, ':'.join(accesslist), compression))
                dbX.test_get({'id':primkey})
                dbX.test_update({'id':primkey}, ('id', 'access', 'filename', 'owner', 'accesslist','compression'), (primkey, access, filename, owner, ':'.join(accesslist), compression))
                dbX.test_delete(self, {'id':primkey})
                dbX.test_getpublicfiles()
                dbX.test_getsharedfiles(owner)
                dbX.test_cleandata()
                print('\n')
