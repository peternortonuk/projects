from nredarwin.webservice import DarwinLdbSession
from credentials import open_ldbws_account_details
from pprint import pprint as pp

wsdl = "https://lite.realtime.nationalrail.co.uk/OpenLDBWS/wsdl.aspx"
api_key = open_ldbws_account_details['token']

crs_london_waterloo = 'WAT'
crs_godalming = 'GOD'
service_properties = ['destination_text', 'destinations', 'estimated_arrival', 'estimated_departure', 'eta', 'etd', 'operator_code', 'operator_name', 'origin_text', 'origins', 'platform', 'scheduled_arrival', 'scheduled_departure', 'service_id', 'sta', 'std']
service_detail_properties = ['disruption_reason', 'is_cancelled', 'overdue_message']


def print_properties(item, properties):
    print('==============')
    for property in properties:
        try:
            message = getattr(item, property, None)
            print(property, ': ', message)
        except NotImplementedError:
            print(property, ': not implemented')


session = DarwinLdbSession(wsdl=wsdl, api_key=api_key)
board = session.get_station_board(crs=crs_godalming, destination_crs=crs_london_waterloo)
services = board.train_services

insert_dict = {}
for service in services:
    # get the extra disruption details
    service_id = service.service_id
    service_item = session.get_service_details(service_id)

    # prepare data to insert into db
    service_dict = vars(service)
    service_dict_key = service_dict.pop('_service_id')
    service_detail_dict = vars(service_item)
    insert_dict[service_dict_key] = {'service': service_dict, 'details': service_detail_dict}

    # print details
    print('=============')
    pp(service_dict)
    pp(service_detail_dict)
pass

