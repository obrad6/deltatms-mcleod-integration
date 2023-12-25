import requests
import json
import string

from mcleod import get_customers_by_query_string, get_orders_by_status
from utils import get_delta_status_id_for_mcleod_order_status, get_delta_vehicle_type_id_for_mc_leod_mode
from app.models.load import Load


def get_users() -> list:
    """Get all users from Delta TMS."""
    url = "https://dgltmsapi.azurewebsites.net/api/v1/GetUsers"
    try:
        response = requests.get(url, auth=('Misko', 'VoziM1$k0'))
        if response.status_code != 200:
            print(f"When trying to return users from Delta TMS, received status code: {str(response.status_code)}")
            return []
        return json.loads(response.text)
    except Exception as e:
        print(f"Failed to retrieve users from Delta TMS. Error: {str(e)}")
        return []


def get_states() -> list:
    """"""
    url = "https://dgltmsapi.azurewebsites.net/api/v1/GetStates"
    try:
        response = requests.get(url, auth=('Misko', 'VoziM1$k0'))

        if response.status_code != 200:
            print(f"When trying to return states from Delta TMS, received status code: {str(response.status_code)}")
            return []
        return json.loads(response.text)
    except Exception as e:
        print(f"Failed to retrieve states from Delta TMS. Error: {str(e)}")
        return []


def get_load_statuses() -> list:
    """Get all load statuses from Delta TMS."""
    url = "https://dgltmsapi.azurewebsites.net/api/v1/GetLoadStatuses"
    try:
        response = requests.get(url, auth=('Misko', 'VoziM1$k0'))

        if response.status_code != 200:
            print(f"When trying to return load statuses from Delta TMS, received status code: "
                  f"{str(response.status_code)}")
            return []
        return json.loads(response.text)
    except Exception as e:
        print(f"Failed to retrieve load statuses from Delta TMS. Error: {str(e)}")
        return []


def get_load_weight_units() -> list:
    """"""
    url = "https://dgltmsapi.azurewebsites.net/api/v1/GetLoadWeightUnits"
    try:
        response = requests.get(url, auth=('Misko', 'VoziM1$k0'))

        if response.status_code != 200:
            print(f"When trying to return weight units from Delta TMS, received status code: "
                  f"{str(response.status_code)}")
            return []
        return json.loads(response.text)
    except Exception as e:
        print(f"Failed to retrieve weight units from Delta TMS. Error: {str(e)}")
        return []


def get_package_types() -> list:
    """"""
    url = "https://dgltmsapi.azurewebsites.net/api/v1/GetPackageTypes"
    try:
        response = requests.get(url, auth=('Misko', 'VoziM1$k0'))

        if response.status_code != 200:
            print(f"When trying to return package types from Delta TMS, received status code: "
                  f"{str(response.status_code)}")
            return []
        return json.loads(response.text)
    except Exception as e:
        print(f"Failed to retrieve package types from Delta TMS. Error: {str(e)}")
        return []


def get_product_types() -> list:
    """"""
    url = "https://dgltmsapi.azurewebsites.net/api/v1/GetProductTypes"
    try:
        response = requests.get(url, auth=('Misko', 'VoziM1$k0'))

        if response.status_code != 200:
            print(f"When trying to return product types from Delta TMS, received status code: "
                  f"{str(response.status_code)}")
            return []
        return json.loads(response.text)
    except Exception as e:
        print(f"Failed to retrieve product types from Delta TMS. Error: {str(e)}")
        return []


def get_pickup_time_types() -> list:
    """"""
    url = "https://dgltmsapi.azurewebsites.net/api/v1/GetPickupTimeTypes"
    try:
        response = requests.get(url, auth=('Misko', 'VoziM1$k0'))

        if response.status_code != 200:
            print(f"When trying to return pickup time types from Delta TMS, received status code: "
                  f"{str(response.status_code)}")
            return []
        return json.loads(response.text)
    except Exception as e:
        print(f"Failed to retrieve pickup time types from Delta TMS. Error: {str(e)}")
        return []


def get_vehicle_types() -> list:
    """"""
    url = "https://dgltmsapi.azurewebsites.net/api/v1/GetVehicleTypes"
    try:
        response = requests.get(url, auth=('Misko', 'VoziM1$k0'))

        if response.status_code != 200:
            print(f"When trying to return vehicle types from Delta TMS, received status code: "
                  f"{str(response.status_code)}")
            return []
        return json.loads(response.text)
    except Exception as e:
        print(f"Failed to retrieve vehicle types from Delta TMS. Error: {str(e)}")
        return []


def get_customer_by_external_id(external_id: str) -> dict:
    """"""
    url = f"https://dgltmsapi.azurewebsites.net/api/v1/GetCustomer?externalID={external_id}"
    try:
        response = requests.get(url, auth=('Misko', 'VoziM1$k0'))
        if not response.text:
            return {}
        return json.loads(response.text)
    except Exception as e:
        print(f"Error: {str(e)} retrieving customer by id: {external_id}")
        return {}


def create_customer(customer: dict, address: dict) -> tuple:
    """"""
    url = f"https://dgltmsapi.azurewebsites.net/api/v1/CreateCustomer"
    headers = {'Content-Type': 'application/json'}
    if not customer or not address:
        print("Customer and Address objects must be provided.")
        return False, None
    try:
        states = get_states()
        address_object = {'addresS_LINE_1': address['address_1'], 'addresS_LINE_2': address['address_2'],
                          'city': address['city'], 'ziP_CODE': address['zip_code']}
        for state in states:
            if state['addresS_STATE_ABBREVIATION'] == address['state']:
                address_object['statE_ID'] = state['addresS_STATE_ID']
                break

        request_object = {'customeR_NAME': customer['name'], 'phone': customer['phone'],
                          'contacT_PERSON': customer['contact_person'], 'externaL_ID': customer['externaL_id'],
                          'address': address_object}
        if 'tier' in customer:
            request_object['tier'] = customer['tier']
        if not get_customer_by_external_id(customer['externaL_id']):
            print(f"Sending request: {request_object}")
            response = requests.post(url, data=json.dumps(request_object), headers=headers, auth=('Misko', 'VoziM1$k0'))
            print(f"Response of create_customer is: {response.text}")
            if response.status_code != 200:
                print(f"Failed to create new customer. Response: {response.text}")
                return False, None
            return True, json.loads(response.text)
    except Exception as e:
        print(f"Failed to create new customer. Error: {str(e)}")
        return False, None


def insert_all_existing_customers_in_dgltms():
    """Insert all existing customers in Delta TMS"""
    customers_list = []
    for letter in string.ascii_lowercase:
        customers = get_customers_by_query_string(False, letter)
        for customer in customers:
            customers_list.append(customer)
            # print(f"Trying insert for customer: {customer}")
            # phone = customer['main_phone'] if 'main_phone' in customer and customer['main_phone'] else ''
            # contact = customer['primary_contact'] if 'primary_contact' in customer \
            #                                          and customer['primary_contact'] else ''
            # customer_object = {'name': customer['name'], 'phone': phone,
            #                    'contact_person': contact, 'externaL_id': customer['id']}
            #
            # address_1 = customer['address1'] if 'address1' in customer and customer['address1'] else ''
            # address_2 = customer['address2'] if 'address2' in customer and customer['address2'] else ''
            # city = customer['city'] if 'city' in customer and customer['city'] else ''
            # state = customer['state_id'] if 'state_id' in customer and customer['state_id'] else ''
            # zip_code = customer['zip_code'] if 'zip_code' in customer and customer['zip_code'] else ''
            # address_object = {'address_1': address_1, 'address_2': address_2,
            #                   'city': city, 'state': state, 'zip_code': zip_code}
            # if not create_customer(customer_object, address_object):
            #     print(f"Failed for customer: {customer_object} and address: {address_object}")

    for cust in customers_list:
        with open('customers.json', 'a') as f:
            json.dump(cust, f)
            f.write('\n')


def insert_customers_from_json(file_name: str):

    customer_objects = []
    with open(file_name, 'r') as f:
        for line in f:
            if line.strip():
                customer_objects.append(json.loads(line))

    for customer in customer_objects:
        print(f"Trying insert for customer: {customer}")
        phone = customer['main_phone'] if 'main_phone' in customer and customer['main_phone'] else ''
        contact = customer['primary_contact'] if 'primary_contact' in customer \
                                                 and customer['primary_contact'] else ''
        customer_object = {'name': customer['name'], 'phone': phone,
                           'contact_person': contact, 'externaL_id': customer['id']}
        address_1 = customer['address1'] if 'address1' in customer and customer['address1'] else ''
        address_2 = customer['address2'] if 'address2' in customer and customer['address2'] else ''
        city = customer['city'] if 'city' in customer and customer['city'] else ''
        state = customer['state_id'] if 'state_id' in customer and customer['state_id'] else ''
        zip_code = customer['zip_code'] if 'zip_code' in customer and customer['zip_code'] else ''
        address_object = {'address_1': address_1, 'address_2': address_2,
                          'city': city, 'state': state, 'zip_code': zip_code}
        print(f"customer object is: {customer_object} and address object is: {address_object}")
        create_customer_response = create_customer(customer_object, address_object)
        print(f"create_customer_response is: {create_customer_response}")


def create_load(load_request: dict) -> tuple:
    """"""
    url = f"https://dgltmsapi.azurewebsites.net/api/v1/CreateLoad"
    headers = {'Content-Type': 'application/json'}
    if not load_request:
        print("Load object must be provided.")
        return False, None
    try:
        response = requests.post(url, data=json.dumps(load_request), headers=headers, auth=('Misko', 'VoziM1$k0'))
        print(f"Response of create_load is: {response.text}")
        if response.status_code != 200:
            print(f"Failed to create new load. Response: {response.text}")
            return False, None
        saved_load = json.loads(response.text)
        return True, saved_load
    except Exception as e:
        print(f"Failed to create new load. Error: {str(e)}")
        return False, None


def insert_existing_loads(is_test):
    """"""
    statuses = ['C', 'V', 'P', 'A', 'D']
    for letter in statuses:
        orders = get_orders_by_status(is_test, letter)
        if orders and letter == 'A':
            print(f"Number of orders for status {letter} is: {len(orders)}")
            for order in orders:
                load = {
                    'mC_LOUD_LOAD_ID': order['id'],
                    'loaD_STATUS_ID': get_delta_status_id_for_mcleod_order_status(order['status']),
                    'mode': get_delta_vehicle_type_id_for_mc_leod_mode(order['equipment_type_id']),
                    'entereD_BY': order['id']
                }
                print(f"Trying insert for order: {order}")

            # print(f"Trying insert for order: {order}")
            # pickup_address = {'addresS_LINE_1': '', 'addresS_LINE_2': '', 'city': '', 'statE_ID': 1, 'ziP_CODE': ''}
            # pickup_object = {'loaD_WEIGHT_UNIT_ID': 2, 'loaD_WEIGHT': 12.33, 'packagE_TYPE_ID': 1, 'packagE_COUNT': 123,
            #                  'producT_TYPE_ID': 1, 'stackable': True, 'pickuP_TIME_TYPE_ID': 2,
            #                  'address': pickup_address}
            #
            # delivery_address = {'addresS_LINE_1': '', 'addresS_LINE_2': '', 'city': '', 'statE_ID': 1, 'ziP_CODE': ''}
            # delivery_object = {'deliverY_WORK_HOURS_FROM': '', 'deliverY_WORK_HOURS_TO': '', 'address': delivery_address}
            #
            # request_object = {'mC_LOUD_LOAD_ID': '', 'entereD_BY': '', 'approved': True, 'mode': 3, 'repeatable': False,
            #                   'awarD_TO_CHEAPEST': False, 'loadDelivery': [delivery_object],
            #                   'loadPickup': [pickup_object]}


if __name__ == "__main__":
    # print(get_states())
    # print(get_customer_by_external_id('1234'))
    # address = {
    #     'address_1': '3701 Centrella St',
    #     'address_2': '',
    #     'city': 'FRANKLIN PARK',
    #     'zip_code': '60131',
    #     'state': 'IL',
    # }
    # customer = {
    #     'name': 'Test Customer - CHI',
    #     'phone': '847-640-1819',
    #     'contact_person': 'testperson',
    #     'externaL_id': 'TESTCUS'
    # }
    # print(create_customer(customer, address))
    print(get_customer_by_external_id('APEXLIL'))
    # print(get_load_weight_units())
    # print(get_package_types())
    # print(get_product_types())
    # print(get_pickup_time_types())
    # print(get_vehicle_types())
    # insert_all_existing_customers_in_dgltms()
    # insert_existing_loads(False)
    # print(get_load_statuses())
    # print(get_vehicle_types())
    # insert_customers_from_json('customers.json')
    # print(get_users())






