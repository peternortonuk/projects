from mongoengine import *
connect(db='trains', host='localhost', port=27017)

'''
ensure mongodb server is running with
C:\Program Files\MongoDB\Server\4.0\bin\mongod.exe
'''

class Train(Document):
    service_id = StringField(required=True)
    service = DictField()
    details = DictField()

pass