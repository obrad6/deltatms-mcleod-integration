import requests
import json


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
        return json.loads(response.text)
    except Exception as e:
        print(f"Error: {str(e)} retrieving customer by id: {external_id}")
        return {}


def create_customer(customer: dict, address: dict) -> bool:
    """"""
    url = f"https://dgltmsapi.azurewebsites.net/api/v1/CreateCustomer"
    headers = {'Content-Type': 'application/json'}
    if not customer or not address:
        print("Customer and Address objects must be provided.")
        return False
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
        print(f"Sending request: {request_object}")
        response = requests.post(url, data=json.dumps(request_object), headers=headers, auth=('Misko', 'VoziM1$k0'))
        if response.status_code != 200:
            print(f"Failed to create new customer. Response: {response.text}")
            return False
        return True
    except Exception as e:
        print(f"Failed to create new customer. Error: {str(e)}")
        return False


def create_load(load: dict) -> bool:
    """"""
    url = f"https://dgltmsapi.azurewebsites.net/api/v1/CreateLoad"
    headers = {'Content-Type': 'application/json'}
    if not load:
        print("Load object must be provided.")
        return False

    pickup_address = {'addresS_LINE_1': '', 'addresS_LINE_2': '', 'city': '', 'statE_ID': 1, 'ziP_CODE': ''}
    pickup_object = {'loaD_WEIGHT_UNIT_ID': 2, 'loaD_WEIGHT': 12.33, 'packagE_TYPE_ID': 1, 'packagE_COUNT': 123,
                     'producT_TYPE_ID': 1, 'stackable': True, 'pickuP_TIME_TYPE_ID': 2, 'address': pickup_address}

    delivery_address = {'addresS_LINE_1': '', 'addresS_LINE_2': '', 'city': '', 'statE_ID': 1, 'ziP_CODE': ''}
    delivery_object = {'deliverY_WORK_HOURS_FROM': '', 'deliverY_WORK_HOURS_TO': '', 'address': delivery_address}

    request_object = {'mC_LOUD_LOAD_ID': '', 'entereD_BY': '', 'approved': True, 'mode': 3, 'repeatable': False,
                      'awarD_TO_CHEAPEST': False, 'loadDelivery': [delivery_object], 'loadPickup': [pickup_object]}


if __name__ == "__main__":
    # print(get_states())
    # print(get_customer_by_external_id('1234'))
    address = {
        'address_1': '3701 Centrella St',
        'address_2': '',
        'city': 'FRANKLIN PARK',
        'zip_code': '60131',
        'state': 'IL',
    }
    customer = {
        'name': 'Apex Logistics International Inc. - ORD',
        'phone': '847-640-1818',
        'contact_person': 'stefanfi',
        'externaL_id': 'APEXELIL'
    }
    # print(create_customer(customer, address))
    # print(get_customer_by_external_id('APEXELIL'))
    # print(get_load_weight_units())
    # print(get_package_types())
    # print(get_product_types())
    # print(get_pickup_time_types())
    print(get_vehicle_types())






