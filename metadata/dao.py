from mongoengine import *
from collections import namedtuple

# config settings
connection_details = namedtuple('connection_details', 'host, port, ssl, username, password')

local = connection_details(
    r'mongodb://localhost',
    27017,
    False,
    None,
    None,
)

# select connection
selected_connection = local

# define database name
db = 'metadata'

# create connection
connect(db=db, host=selected_connection.host,
        port=selected_connection.port,
        username=selected_connection.username,
        password=selected_connection.password,
        ssl=selected_connection.ssl)


# define the data object
class Metadata(Document):
    curve_id = IntField(required=True)
    attributes = ListField(StringField(max_length=30))




