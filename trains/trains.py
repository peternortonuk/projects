from nredarwin.webservice import DarwinLdbSession
from credentials import open_ldbws_account_details

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
for service in services:
    # print all the standard details
    print_properties(service, service_properties)

    # for each service print the extra disruption details
    service_id = service.service_id
    service_item = session.get_service_details(service_id)
    print_properties(service_item, service_detail_properties)

pass

