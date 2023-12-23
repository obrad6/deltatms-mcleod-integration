import requests
from requests.auth import HTTPBasicAuth
from app.models.comodity import Commodity
from utils import get_state_abbreviation, convert_kgs_to_lb, format_date_time_for_mcleod,\
    get_mcleod_equipment_type_id, is_team_required_based_on_the_equipment



def get_new_location_object(is_test) -> dict:
    """"""
    test_url = "https://dgld.loadtracking.com:5790/ws/locations/new"
    prod_url = "https://dgld.loadtracking.com/ws/locations/new"
    headers = {'Accept': 'application/json'}

    print("Getting new location object")
    if is_test:
        response = requests.get(test_url, auth=HTTPBasicAuth("apiuser", "dgldapiuser"),
                                headers=headers)
        print(f"Response is: {response.text}")
        if response:
            return response.json()
    else:
        response = requests.get(prod_url, auth=HTTPBasicAuth("apiuser", "dgldapiuser"),
                                headers=headers)
        if response:
            return response.json()


def get_location(is_test, address1: str = None, city: str = None, state: str = None, zip_code: str = None) -> list:
    """"""
    url = ""
    print(f"Get location for address: {address1}, city: {city}, state: {state}, zip: {zip_code}")
    test_url = "https://dgld.loadtracking.com:5790/ws/locations/search?"
    prod_url = "https://dgld.loadtracking.com/ws/locations/search?"

    if is_test:
        url = test_url
    else:
        url = prod_url

    headers = {'Accept': 'application/json'}
    if not address1 and not city and not state and not zip_code:
        return url[:-1]
    if address1:
        url += f"address1={address1}"
    if city:
        if not address1:
            url += f"city_name={city}"
        else:
            url += f"&city_name={city}"
    if zip_code:
        if url[-1] == '?':
            url += f"zip_code={zip_code}"
        else:
            url += f"&zip_code={zip_code}"
    if state:
        st = ""
        if len(state) > 2:
            st = get_state_abbreviation(state)
        else:
            st = state
        if url[-1] == '?':
            url += f"state={state}"
        else:
            url += f"&state={state}"

    print(f"Searching for address: {url}")
    response = requests.get(url, auth=HTTPBasicAuth("apiuser", "dgldapiuser"),
                            headers=headers)

    print(f"response for location search is: {response.text}")
    if response:
        return response.json()


def save_new_location(is_test, location):
    """"""
    print(f"Received location: {location}")
    test_url = "https://dgld.loadtracking.com:5790/ws/locations/create"
    prod_url = "https://dgld.loadtracking.com/ws/locations/create"
    headers = {'Accept': 'application/json'}
    if is_test:
        response = requests.put(test_url, auth=HTTPBasicAuth("apiuser", "dgldapiuser"),
                                headers=headers, json=location)
        print(response.text)
    else:
        response = requests.put(prod_url, auth=HTTPBasicAuth("apiuser", "dgldapiuser"),
                                headers=headers, json=location)
    print(f"Returning location: {response.json()}")
    return response.json()


def get_mcleod_pickup_objects_list(pickup_list: list, is_test: bool) -> list:
    """Iterate over pickup list and create pickup objects list for McLeod API."""
    list_of_pickups = []
    for pickup in pickup_list:
        pickup_location_id = None
        pickup_city_id = None
        pickup_location = get_location(is_test, pickup['pickup_address'], pickup['pickup_city'],
                                       pickup['pickup_state'], pickup['pickup_zip_code'])
        print(f"pickup is: {pickup_location}")
        if pickup_location:
            pickup_location_id = pickup_location[0]['id']
            pickup_city_id = pickup_location[0]['city_id']
            pickup_location_name = pickup_location[0]['name']
        else:
            st = ""
            if len(pickup['pickup_state']) > 2:
                st = get_state_abbreviation(pickup['pickup_state'])
            else:
                st = pickup['pickup_state']
            new_location = {'__type': 'location', 'name': f"{pickup['pickup_address']} {pickup['pickup_city']}",
                            'city_name': pickup['pickup_city'], 'state': st,
                            'address1': pickup['pickup_address'], 'zip_code': pickup['pickup_zip_code']}

            print(f"Saving pickup location: {new_location}")
            pickup_location = save_new_location(is_test, new_location)
            print("Saved pickup location")
            pickup_location_id = pickup_location['id']
            pickup_city_id = pickup_location['city_id']
            pickup_location_name = pickup_location['name']

        sched_arrive_early_pu = format_date_time_for_mcleod(pickup['pickup_est_dt'])
        pickup_object = {
                            "__type": "stop",
                            "location_name": pickup_location_name,
                            "company_id": "TMS",
                            "address": pickup['pickup_address'],
                            "location_id": pickup_location_id,
                            "sched_arrive_early": sched_arrive_early_pu,
                            "weight": pickup['weight'],
                            "cases": pickup['package_count'],
                            "stop_type": "PU"
                        }
        list_of_pickups.append(pickup_object)
    return list_of_pickups


def get_mcleod_delivery_objects_list(delivery_list: list, is_test: bool) -> list:
    """Iterate over delivery list and create delivery objects list for McLeod API."""
    list_of_deliveries = []
    for delivery in delivery_list:
        delivery_city_id = None
        delivery_location_id = None
        delivery_location = get_location(is_test, delivery['delivery_address'], delivery['delivery_city'],
                                         delivery['delivery_state'], delivery['delivery_zip_code'])
        print(f"delivery is: {delivery_location}")
        if delivery_location:
            delivery_city_id = delivery_location[0]['city_id']
            delivery_location_id = delivery_location[0]['id']
            delivery_location_name = delivery_location[0]['name']
        else:
            st = ""
            if len(delivery['delivery_state']) > 2:
                st = get_state_abbreviation(delivery['delivery_state'])
            else:
                st = delivery['delivery_state']
            new_location = {'__type': 'location', 'name': f"{delivery['delivery_address']} {delivery['delivery_city']}",
                            'city_name': delivery['delivery_city'], 'state': st,
                            'address1': delivery['delivery_address'], 'zip_code': delivery['delivery_zip_code']}
            print(f"Saving delivery: {new_location}")
            delivery_location = save_new_location(is_test, new_location)
            print(f"delivery location is: {delivery_location}")
            delivery_city_id = delivery_location['city_id']
            delivery_location_id = delivery_location['id']
            delivery_location_name = delivery_location['name']

        sched_arrive_early_del = format_date_time_for_mcleod(delivery['delivery_est_dt'])
        delivery_object = {
                                "__type": "stop",
                                "location_name": delivery_location_name,
                                "company_id": "TMS",
                                "address": delivery['delivery_address'],
                                "city_name": delivery['delivery_city'],
                                "city_id": delivery_city_id,
                                "location_id": delivery_location_id,
                                "state": delivery['delivery_state'],
                                "zip_code": delivery['delivery_zip_code'],
                                "sched_arrive_early": sched_arrive_early_del,
                                "stop_type": "SO"
                            }
        print(f"Adding delivery object to stops: {delivery_object}")
        list_of_deliveries.append(delivery_object)
        return list_of_deliveries


def get_mcleod_commodity_id_and_description(pickup_list: list) -> tuple:
    """Get McLeod commodity id and description for a given pickup list."""
    commodity_id = None
    commodity_description = None
    if len(pickup_list) == 1:
        if 'product_type' in pickup_list[0]:
            commodity = Commodity.get_commodity_by_product_type(pickup_list[0]['product_type'])
            if commodity:
                commodity_id = commodity['commodity_id']
                commodity_description = commodity['commodity_description']
    else:
        commodity_id = "MISCFF"
        commodity_descriptions = []
        for pickup in pickup_list:
            if 'product_type' in pickup:
                commodity = Commodity.get_commodity_by_product_type(pickup['product_type'])
                if commodity:
                    commodity_descriptions.append(commodity['commodity_description'])
        commodity_description = ", ".join(commodity_descriptions)

    return commodity_id, commodity_description


def save_order(pickup_list, delivery_list, is_test, order=None):
    test_url = "https://dgld.loadtracking.com:5790/ws/orders/create"
    prod_url = "https://dgld.loadtracking.com/ws/orders/create"

    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    stops = []

    total_weight = 0
    total_pieces_count = 0
    # Get pickup stops
    pickups = get_mcleod_pickup_objects_list(pickup_list, is_test)
    commodity_id, commodity_description = get_mcleod_commodity_id_and_description(pickup_list)
    for pickup in pickups:
        total_weight += pickup['weight']
        total_pieces_count += pickup['cases']
        stops.append(pickup)

    # Get delivery stops
    deliveries = get_mcleod_delivery_objects_list(delivery_list, is_test)
    for delivery in deliveries:
        stops.append(delivery)

    equipment_type_id = get_mcleod_equipment_type_id(order['mode'])
    teams_required = 'Y' if is_team_required_based_on_the_equipment(equipment_type_id) else 'N'

    request_object = {
        "__type": "orders",
        "company_id": "TMS",
        "collection_method": "T",
        "customer_id": order['external_customer_id'],
        "revenue_code_id": "NORM",
        "teams_required": teams_required,
        "equipment_type_id": equipment_type_id,
        "commodity_id": commodity_id,
        "commodity_description": commodity_description,
        "order_type_id": "SPOT",
        "stops": stops,
        "entered_user_id": "apiuser",
        "consignee_refno": order['billing_number'],
        "weight": convert_kgs_to_lb(total_weight),
        "pieces": total_pieces_count
    }
    response = None
    if is_test:
        print(f"Sending order request object: {request_object} in test: {is_test}")
        response = requests.put(test_url, auth=HTTPBasicAuth("apiuser", "dgldapiuser"),
                                headers=headers, json=request_object)
        print(f"Response for save order is: {response.text} in test: {is_test}")
    else:
        print(f"Sending order request object: {request_object} in test: {is_test}")
        response = requests.put(prod_url, auth=HTTPBasicAuth("apiuser", "dgldapiuser"),
                                headers=headers, json=request_object)
        print(f"Response for save order is: {response.text} in test: {is_test}")
    return response.json()


def save_delivery_notes(response, stop_comments, is_test):

    test_url = "https://dgld.loadtracking.com:5790/ws/stop_note/create"
    prod_url = "https://dgld.loadtracking.com/ws/stop_note/create"

    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    for stp in response.json()['stops']:
        if stp['stop_type'] == "SO":
            key_stop = f"{stp['city_id']}{stp['location_id']}"
            if key_stop in stop_comments:
                request_object = {
                    "__type": "stop_note",
                    "company_id": "TMS",
                    "comment_type": "OC",
                    "comments": stop_comments[key_stop],
                    "sequence": 1,
                    "stop_id": stp['id'],
                    "system_added": False
                }
                if is_test:
                    requests.put(test_url, auth=HTTPBasicAuth("apiuser", "dgldapiuser"),
                                 headers=headers, json=request_object)
                    print(f"Saved delivery note: {request_object}")

                else:
                    requests.put(prod_url, auth=HTTPBasicAuth("apiuser", "dgldapiuser"),
                                 headers=headers, json=request_object)
                    print(f"Saved delivery note: {request_object}")


def get_order(is_test, order_id):
    headers = {'Accept': 'application/json'}
    order = None
    url = None
    if is_test:
        url = f"https://dgld.loadtracking.com:5790/ws/orders/{order_id}"
        order = requests.get(url, auth=HTTPBasicAuth("apiuser", "dgldapiuser"),
                                 headers=headers)
    else:
        url = f"https://dgld.loadtracking.com/ws/orders/{order_id}"
        order = requests.get(url, auth=HTTPBasicAuth("apiuser", "dgldapiuser"),
                             headers=headers)
    return order.json()


def get_orders_by_status(is_test, status):
    headers = {'Accept': 'application/json'}
    url = None
    if is_test:
        url = f"https://dgld.loadtracking.com:5790/ws/orders/search?orders.status={status}"
    else:
        url = f"https://dgld.loadtracking.com/ws/orders/search?orders.status={status}"

    print(f"{url}")
    orders = requests.get(url, auth=HTTPBasicAuth("apiuser", "dgldapiuser"),
                          headers=headers)
    return orders.json()


def get_edi_partner_code(is_test, reference_number):
    headers = {'Accept': 'application/json'}
    url = None
    test_url = "https://dgld.loadtracking.com:5790/ws/edi_partner_code/search?"
    prod_url = "https://dgld.loadtracking.com/ws/edi_partner_code/search?"

    if not reference_number:
        return ""

    reference_number_code = reference_number[0:2].upper()
    if is_test:
        url = test_url
    else:
        url = prod_url

    url += f"standard_code={reference_number_code}"

    print(f"Searching for edi partner code: {url}")
    response = requests.get(url, auth=HTTPBasicAuth("apiuser", "dgldapiuser"),
                            headers=headers)

    print(f"Edi partner code response is: {response.json()}")
    return response.json()


def save_reference_number(response, reference_numbers, stop_weights, stop_pieces, is_test):
    test_url = "https://dgld.loadtracking.com:5790/ws/reference_number/create"
    prod_url = "https://dgld.loadtracking.com/ws/reference_number/create"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    for stp in response.json()['stops']:
        # if stp['stop_type'] == "SO":
        key_stop = f"{stp['city_id']}{stp['location_id']}"

        reference_number = None
        if key_stop in reference_numbers:
            reference_number = reference_numbers[key_stop]

        edi_partner_code = get_edi_partner_code(is_test, reference_number)
        if edi_partner_code and len(edi_partner_code) > 0:
            element_id = edi_partner_code[0]['element_id']
            version = edi_partner_code[0]['version']
            ref_qual_description = edi_partner_code[0]['description']
            request_object = {
                "__type": "reference_number",
                "company_id": "TMS",
                "element_id": element_id,
                "partner_id": "TMS",
                "reference_number": reference_number,
                "reference_qual": reference_number[0:2].upper(),
                "send_to_driver": False,
                "stop_id": stp['id'],
                "version": version,
                "__referenceQualDescr": ref_qual_description
            }

            if key_stop in stop_weights:
                weight = stop_weights[key_stop]
                request_object['weight'] = weight

            if key_stop in stop_pieces:
                pieces = stop_pieces[key_stop]
                request_object['pieces'] = pieces

            if is_test:
                requests.put(test_url, auth=HTTPBasicAuth("apiuser", "dgldapiuser"),
                             headers=headers, json=request_object)
                print(f"Saved reference number: {request_object}")

            else:
                requests.put(prod_url, auth=HTTPBasicAuth("apiuser", "dgldapiuser"),
                             headers=headers, json=request_object)
                print(f"Saved reference number: {request_object}")


def get_customer_by_name(is_test: bool, name: str):
    """"""
    url = None
    test_url = "https://dgld.loadtracking.com:5790/ws/customers/search?"
    prod_url = "https://dgld.loadtracking.com/ws/customers/search?"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    if is_test:
        url = f"{test_url}name={name}"

    else:
        url = f"{prod_url}name={name}"

    print(f"Searching for customer: {url}")
    response = requests.get(url, auth=HTTPBasicAuth("apiuser", "dgldapiuser"),
                            headers=headers)

    print(f"Customer response is: {response.json()}")
    return response.json()


def get_customers_by_query_string(is_test: bool, query_string: str = '') -> list:
    url = None
    test_url = "https://dgld.loadtracking.com:5790/ws/customers?q"
    prod_url = "https://dgld.loadtracking.com/ws/customers?q"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    if is_test:
        url = f"{test_url}={query_string}"

    else:
        url = f"{prod_url}={query_string}"

    if not query_string:
        url = url[:-4]

    print(f"Searching for customers: {url}")
    response = requests.get(url, auth=HTTPBasicAuth("apiuser", "dgldapiuser"),
                            headers=headers)

    print(f"Customers response is: {response.json()}")
    return response.json()


def save_customer(is_test: bool, name: str):
    """"""
    test_url = "https://dgld.loadtracking.com:5790/ws/customers/create"
    prod_url = "https://dgld.loadtracking.com/ws/customers/create"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    request_object = {
        "__type": "customer",
        "company_id": "TMS",
        "name": name
    }

    if is_test:
        response = requests.put(test_url, auth=HTTPBasicAuth("apiuser", "dgldapiuser"),
                                headers=headers, json=request_object)

    else:
        response = requests.put(prod_url, auth=HTTPBasicAuth("apiuser", "dgldapiuser"),
                                headers=headers, json=request_object)

    print(f"Saved customer: {response.json()}")
    return response.json()


def get_users_by_query_string(is_test: bool, query_string: str) -> list:
    url = None
    test_url = "https://dgld.loadtracking.com:5790/ws/users/search?"
    prod_url = "https://dgld.loadtracking.com/ws/users/search?"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    if is_test:
        url = f"{test_url}{query_string}"

    else:
        url = f"{prod_url}{query_string}"

    print(f"Searching for users: {url}")
    response = requests.get(url, auth=HTTPBasicAuth("apiuser", "dgldapiuser"),
                            headers=headers)

    print(f"Users response is: {response.status_code}")
    return response.json()


if __name__ == "__main__":
    # print(get_customer_by_name(True, "apex logistics international jfk"))
    # print(save_customer(True, "DGLTms Integration Test Customer"))
    print(get_users_by_query_string(False,"users.is_active=Y&orderBy=users.name+DESC"))
