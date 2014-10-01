import cProfile
from db import db
import ConfigParser
import base64
import pstats
import os

configreader = ConfigParser.ConfigParser()
configreader.read('config.ini')
#reading in file metadata
primkey = configreader.get('DEFAULT','id')
access = configreader.get('DEFAULT','access')
filename = configreader.get('DEFAULT','filename')
owner = configreader.get('DEFAULT','owner')
accesslist = configreader.get('DEFAULT','accesslist')
compression = configreader.get('DEFAULT','compression')
numtimes = int(configreader.get('DEFAULT','numberoftimes'))

objectdata = base64.b64encode(open(filename,'r').read())

class DatabaseTest(object):
        def __init__(self,dbtype):
                self.currdb = db(dbtype)
                self.currdb.set_credentials('localhost', 'root', 101, 'cloudletX', 'files')
                self.currdb.connect()
        def test_insert(self,keys,data):
                fileobs = None
                for i in range(numtimes):
                        _file = 'insert{}.results'.format(i)
                        cProfile.runctx('self.currdb.insert(keys,data)',globals(), locals(), _file)
                        if (i==0):
                                fileobs = pstats.Stats(_file)
                        else:
                                fileobs.add(_file)
                        os.remove(_file)
                print('{0:20}\t\t  {1}'.format(fileobs.total_tt, (fileobs.total_tt/float(numtimes))))
        def test_get(self,key):
                fileobs = None
                for i in range(numtimes):
                        _file = 'insert{}.results'.format(i)
                        cProfile.runctx('self.currdb.get(key)',globals(), locals(), _file)
                        if (i==0):
                                fileobs = pstats.Stats(_file)
                        else:
                                fileobs.add(_file)
                        os.remove(_file)
                print('{0:20}\t\t  {1}'.format(fileobs.total_tt, (fileobs.total_tt/float(numtimes))))
        def test_update(self, key, keys, data):
                fileobs = None
                for i in range(numtimes):
                        _file = 'insert{}.results'.format(i)
                        cProfile.runctx('self.currdb.update(key, keys, data)',globals(), locals(), _file)
                        if (i==0):
                                fileobs = pstats.Stats(_file)
                        else:
                                fileobs.add(_file)
                        os.remove(_file)
                print('{0:20}\t\t  {1}'.format(fileobs.total_tt, (fileobs.total_tt/float(numtimes))))
        def test_delete(self,key):
                fileobs = None
                for i in range(numtimes):
                        _file = 'insert{}.results'.format(i)
                        cProfile.runctx('self.currdb.delete(key)',globals(), locals(), _file)
                        if (i==0):
                                fileobs = pstats.Stats(_file)
                        else:
                                fileobs.add(_file)
                        os.remove(_file)
                print('{0:20}\t\t  {1}'.format(fileobs.total_tt, (fileobs.total_tt/float(numtimes))))
        def test_getpublicfiles(self):
                fileobs = None
                for i in range(numtimes):
                        _file = 'insert{}.results'.format(i)
                        cProfile.runctx('self.currdb.getpublicfiles()', globals(),locals(), _file)
                        if (i==0):
                                fileobs = pstats.Stats(_file)
                        else:
                                fileobs.add(_file)
                        os.remove(_file)
                print('{0:20}\t\t  {1}'.format(fileobs.total_tt, (fileobs.total_tt/float(numtimes))))
        def test_getsharedfiles(self,requester):
                fileobs = None
                for i in range(numtimes):
                        _file = 'insert{}.results'.format(i)
                        cProfile.runctx('self.currdb.getsharedfiles(requester)', globals(), locals(), _file)
                        if (i==0):
                                fileobs = pstats.Stats(_file)
                        else:
                                fileobs.add(_file)
                        os.remove(_file)
                print('{0:20}\t\t  {1}'.format(fileobs.total_tt, (fileobs.total_tt/float(numtimes))))
        def test_cleandata(self):
                fileobs = None
                for i in range(numtimes):
                        _file = 'insert{}.results'.format(i)
                        cProfile.runctx('self.currdb.cleandata()', globals(), locals(), _file)
                        if (i==0):
                                fileobs = pstats.Stats(_file)
                        else:
                                fileobs.add(_file)
                        os.remove(_file)
                print('{0:20}\t\t  {1}'.format(fileobs.total_tt, (fileobs.total_tt/float(numtimes))))
if __name__=='__main__':
        databases = ['mysql','berkeleydb']
        for dbtype in databases:
                print('\t=={} tests=='.format(dbtype))
                print('insert, get, update, delete, getpublicfiles, sharedfiles, cleandata')
                print('cumulativ time(seconds)\t\t| average (seconds)')
                dbX = DatabaseTest(dbtype)
                dbX.test_insert(('id', 'access', 'filename', 'owner', 'accesslist','compression'), (primkey, access, filename, owner, ':'.join(accesslist), compression))
                dbX.test_get({'id':primkey})
                if accesslist=='None':
                        accesslist = []
                dbX.test_update({'id':primkey}, ('id', 'access', 'filename', 'owner', 'accesslist','compression'), (primkey, access, filename, owner, ':'.join(accesslist), compression))
                dbX.test_delete({'id':primkey})
                dbX.test_getpublicfiles()
                dbX.test_getsharedfiles(owner)
                dbX.test_cleandata()
                print('\n')
