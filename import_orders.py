from app import initialize_app, db
from app.models.load import Load
from app.models.comodity import Commodity
from mcleod import get_order
from deltatms import create_load, get_delta_vehicle_type_id_for_mc_leod_mode,\
    get_delta_status_id_for_mcleod_order_status, get_customer_by_external_id, create_customer
from utils import get_delta_state_id_for_mcleod_state, get_delta_work_hours_for_delivery


def get_new_loads(is_test: bool):
    with initialize_app().app_context():
        order = None
        last_inserted_load = Load.get_last_inserted_load_by_order_id()
        if last_inserted_load:
            print("last_inserted_load is: ", last_inserted_load.__repr__())
            order_id = last_inserted_load.order_id
            next_order_id = f"0{int(order_id) + 1}"
            print(f"next_order_id is: {next_order_id}")
            order = get_order(is_test, next_order_id)
        else:
            order_id = "0100000"
            order = get_order(is_test, order_id)

        if order:
            print(f"order is: {order}")
            pickups = []
            deliveries = []
            commodity = Commodity.get_commodity_by_commodity_id(order['commodity_id'])
            product_type_id = commodity.id if commodity else 5
            for stop in order['stops']:
                address_object = {
                    "addresS_ID": 0,
                    "addresS_LINE_1": stop['address'],
                    "city": stop['city_name'],
                    "statE_ID": get_delta_state_id_for_mcleod_state(stop['state']),
                    "ziP_CODE": stop['zip_code'],
                    "longitude": stop['longitude'],
                    "latitude": stop['latitude']
                }
                if stop['stop_type'] == 'PU':
                    pickup_object = {
                        "loaD_PICKUP_ID": 0,
                        "addresS_ID": 0,
                        "loaD_WEIGHT_UNIT_ID": 2,
                        "loaD_WEIGHT": 0,
                        "packagE_TYPE_ID": 1,
                        "packagE_COUNT": 0,
                        "producT_TYPE_ID": product_type_id,
                        "stackable": False,
                        "pickuP_TIME_TYPE_ID": 1,
                        "address": address_object
                    }
                    pickups.append(pickup_object)
                elif stop['stop_type'] == 'SO':
                    work_hours_from, work_hours_to = get_delta_work_hours_for_delivery(stop['sched_arrive_early'])
                    delivery_object = {
                        "loaD_DELIVERY_ID": 0,
                        "addresS_ID": 0,
                        "deliverY_WORK_HOURS_FROM": work_hours_from,
                        "deliverY_WORK_HOURS_TO": work_hours_to,
                        "address": address_object
                    }
                    deliveries.append(delivery_object)
            customer = get_customer_by_external_id(order['customer_id'])
            if not customer:
                new_customer_address = {
                    "address_1": order['customer']['address1'],
                    "address_2": "",
                    "city": order['customer']['city'],
                    "state": order['customer']['state_id'],
                    "zip_code": order['customer']['zip_code']
                }
                new_customer_object = {
                    "name": order['customer']['name'],
                    "phone": '',
                    "contact_person": '',
                    "externaL_id": order['customer_id'],
                }
                _, customer = create_customer(new_customer_object, new_customer_address)
            customer_id = customer['customeR_ID']
            load_line_object = {
                "loaD_LINE_ID": 0,
                "customeR_ID": customer_id
            }
            load_request_object = {
                "loaD_ID": 0,
                "externaL_ID": order['id'],
                "loaD_LINE_ID": 0,
                "mode": get_delta_vehicle_type_id_for_mc_leod_mode(order['equipment_type_id']),
                "entereD_BY": 65,
                "approved": False if get_delta_status_id_for_mcleod_order_status(order['status']) == 1 else True,
                "loaD_STATUS_ID": get_delta_status_id_for_mcleod_order_status(order['status']),
                "repeatable": False,
                "awarD_TO_CHEAPEST": False,
                "loadPickup": pickups,
                "loadDelivery": deliveries,
                "loaD_LINE": load_line_object
            }

            success, load = create_load(load_request_object)
            if success:
                load = Load(
                    order_id=order['id'],
                    order_mcleod_status=order['status'],
                    delta_load_id=load['loaD_ID']
                )
                db.session.add(load)
                db.session.commit()


if __name__ == '__main__':
    get_new_loads(False)
