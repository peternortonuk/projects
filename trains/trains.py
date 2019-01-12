from nredarwin.webservice import DarwinLdbSession
from credentials import open_ldbws_account_details

wsdl = "https://lite.realtime.nationalrail.co.uk/OpenLDBWS/wsdl.aspx"
api_key = open_ldbws_account_details['token']

crs_london_waterloo = 'WAT'
crs_godalming = 'GOD'
report_properties = ['destination_text', 'destinations', 'estimated_arrival', 'estimated_departure', 'eta', 'etd', 'operator_code', 'operator_name', 'origin_text', 'origins', 'platform', 'scheduled_arrival', 'scheduled_departure', 'service_id', 'sta', 'std']


darwin_sesh = DarwinLdbSession(wsdl=wsdl, api_key=api_key)
board = darwin_sesh.get_station_board(crs=crs_godalming, destination_crs=crs_london_waterloo)

services = board.train_services
for service in services:
    print('==============')
    for property in report_properties:
        try:
            message = getattr(service, property)
            print(property, ': ', message)
        except NotImplementedError:
            print(property, ': not implemented')




