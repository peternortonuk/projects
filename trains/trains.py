from nredarwin.webservice import DarwinLdbSession
from pprint import pprint as pp
from credentials import open_ldbws_account_details

from projects.trains.dao_mongo import save_observation
from projects.trains.models import Train

wsdl = "https://lite.realtime.nationalrail.co.uk/OpenLDBWS/wsdl.aspx"
api_key = open_ldbws_account_details['token']

crs_london_waterloo = 'WAT'
crs_godalming = 'GOD'
service_properties = ['destination_text', 'destinations', 'estimated_arrival', 'estimated_departure', 'eta', 'etd', 'operator_code', 'operator_name', 'origin_text', 'origins', 'platform', 'scheduled_arrival', 'scheduled_departure', 'service_id', 'sta', 'std']
service_detail_properties = ['disruption_reason', 'is_cancelled', 'overdue_message']

session = DarwinLdbSession(wsdl=wsdl, api_key=api_key)
board = session.get_station_board(crs=crs_godalming, destination_crs=crs_london_waterloo)
services = board.train_services

for service in services:
    # get the extra disruption details
    service_id = service.service_id
    service_item = session.get_service_details(service_id)

    # prepare data
    service_dict = vars(service)
    service_dict_key = service_dict.pop('_service_id')
    service_detail_dict = vars(service_item)

    # print details
    print('=============')
    pp(service_dict)
    pp(service_detail_dict)

    # butchery to remove nredarwin objects
    service_remove_items = ['_destinations', '_origins']
    details_remove_items = ['_previous_calling_point_lists', '_subsequent_calling_point_lists']
    for k in service_remove_items:
        service_dict.pop(k)
    for k in details_remove_items:
        service_detail_dict.pop(k)

    # create instance of Train data class
    train = Train(
        service_id=service_id,
        service=service_dict,
        details=service_detail_dict
    )
    print(train)

    # call function in mongo DAO
    save_observation(train)

pass

