#
#
# Copyright 2014 Zola Mahlaza
# This the class that handles all
# access to the database.
#
# "If a book about failures doesn't sell, is it a success?"
# - Jerry Seinfeld
#
class storage(object):
    def __init__(self):
        print('hello')
    def connect(self):
        print('connect')
    def isconnected(self):
        print('isconnected')
    def upload(self,someobject):
        print('upload')
    def download(self,someobject):
        print('download')
    def object_exists(self,someobject):
        print('object exists')