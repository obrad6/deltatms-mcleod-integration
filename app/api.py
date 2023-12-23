from flask import jsonify, request, make_response, Blueprint
from flask_jwt_extended import jwt_required, create_access_token
from zip_code_api import get_zip_codes_for_city_and_state
from mcleod import save_customer, save_order, get_customer_by_name


api = Blueprint('api', __name__)


@api.route('/auth', methods=['POST'])
def login():
    data = request.get_json()
    if 'username' not in data or 'password' not in data \
            or not data['username'] or not data['password']:
        response_object = {'status_code': 400, 'message': 'Please provide username and password', 'success': False}
        response = make_response(jsonify(response_object))
        response.status_code = 400
        return response
    username = data['username']
    password = data['password']
    if username != "DeltaTMSServiceUser" or password != "D3lt@P@ssw0rd09uij09k":
        response_object = {'status_code': 401, 'message': 'Authentication failed.', 'success': False}
        response = make_response(jsonify(response_object))
        response.status_code = 401
        return response
    else:
        access_token = create_access_token(identity=username)
        response_object = {'status_code': 200, 'access_token': access_token,
                           'message': 'Authentication Successful.', 'success': True}
        response = make_response(jsonify(response_object))
        response.status_code = 200
        return response


@api.route('/orders', methods=['POST'])
@jwt_required()
def post_order():
    """"""
    data = request.get_json()
    print(f"Received post order request: {data}")
    pickup_list = []
    delivery_list = []
    is_test = True if "test" in data and data["test"] else False

    if 'external_customer_id' not in data or 'pickup_list' not in data or 'delivery_list' not in data or \
            'mode' not in data or 'billing_number' not in data or not data['external_customer_id'] or \
            not data['pickup_list'] or not data['delivery_list'] or not data['mode'] or not data['billing_number']:
        response_object = {'status_code': 400,
                           'message': 'Please provide required info.',
                           'success': False}
        response = make_response(jsonify(response_object))
        response.status_code = 400
        return response

    # PICKUP
    for pickup in data['pickup_list']:
        pickup_address = pickup['address']
        pickup_city = pickup['city']
        pickup_state = pickup['state']
        pickup_country = pickup['country']
        pickup_zip_code = pickup['zip_code']
        pickup_est_dt = pickup['est_pickup_date_time']
        pickup_weight = pickup['weight']
        pickup_package_count = pickup['package_count']
        pickup_product_type = pickup['product_type']
        pickup_package_type = pickup['package_type']

        zip_codes_for_city_state = get_zip_codes_for_city_and_state(pickup_city, pickup_state)
        if pickup_zip_code not in zip_codes_for_city_state:
            response_object = {'status_code': 422, 'data': None,
                               'message': f"Pickup ZIP Code for {pickup_city}, {pickup_state} is invalid.",
                               'success': False}
            response = make_response(jsonify(response_object))
            response.status_code = 422
            return response

        pickup_object = {
            'pickup_address': pickup_address,
            'pickup_city': pickup_city,
            'pickup_state': pickup_state,
            'pickup_country': pickup_country,
            'pickup_zip_code': pickup_zip_code,
            'pickup_est_dt': pickup_est_dt,
            'weight': pickup_weight,
            'package_count': pickup_package_count,
            'product_type': pickup_product_type,
            'package_type': pickup_package_type
        }
        pickup_list.append(pickup_object)

    # DELIVERY
    for delivery in data['delivery_list']:
        delivery_address = delivery['address']
        delivery_city = delivery['city']
        delivery_state = delivery['state']
        delivery_country = delivery['country']
        delivery_zip_code = delivery['zip_code']
        delivery_est_dt = delivery['est_deliver_date_time']

        delivery_zip_codes_for_city_state = get_zip_codes_for_city_and_state(delivery_city, delivery_state)
        if delivery_zip_code not in delivery_zip_codes_for_city_state:
            response_object = {'status_code': 422, 'data': None,
                               'message': f"Delivery ZIP Code for {delivery_city}, {delivery_state} is invalid.",
                               'success': False}
            response = make_response(jsonify(response_object))
            response.status_code = 422
            return response

        delivery_object = {
            'delivery_address': delivery_address,
            'delivery_city': delivery_city,
            'delivery_state': delivery_state,
            'delivery_country': delivery_country,
            'delivery_zip_code': delivery_zip_code,
            'delivery_est_dt': delivery_est_dt
        }

        delivery_list.append(delivery_object)

        order_object = {
            'external_customer_id': data['external_customer_id'],
            'mode': data['mode'],
            'billing_number': data['billing_number']
        }
        try:
            order = save_order(pickup_list, delivery_list, is_test, order_object)
            print(f"order response is: {order}")
            if order:
                mc_leod_number = order['id']
                response_object = {
                    'status_code': 201,
                    'message': 'Order saved successfully.',
                    'success': True,
                    'mc_leod_number': mc_leod_number
                }
                response = make_response(jsonify(response_object))
                response.status_code = 201
                return response
        except Exception as e:
            print(f"Error saving order: {str(e)}")
            response_object = {'status_code': 500,
                               'message': f"Failed to save order.\nError:\n{str(e)}",
                               'success': False}
            response = make_response(jsonify(response_object))
            response.status_code = 500
            return response


@api.route('/customers', methods=['POST'])
@jwt_required()
def post_customer():
    data = request.get_json()
    if "name" not in data or not data['name']:
        response_object = {'status_code': 400,
                           'message': 'Please provide name for a customer.',
                           'success': False}
        response = make_response(jsonify(response_object))
        response.status_code = 400
        return response

    name = data['name']
    is_test = True if "test" in data and data["test"] else False
    print(f"is_test is: {is_test}")
    customer = get_customer_by_name(True, name)
    if customer:
        customer_id = customer[0]['id']
        response_object = {'status_code': 200,
                           'message': f'Customer: {name} already exists.',
                           'success': True,
                           'external_customer_id': customer_id}
        response = make_response(jsonify(response_object))
        response.status_code = 200
        return response
    else:
        customer = save_customer(is_test, name)
        if not customer:
            response_object = {'status_code': 500,
                               'message': f'Unable to save customer: {name}',
                               'success': False}
            response = make_response(jsonify(response_object))
            response.status_code = 500
            return response
        else:
            response_object = {'status_code': 201,
                               'message': f'Customer: {name} successfully saved.',
                               'success': True,
                               'external_customer_id': customer['id']}
            response = make_response(jsonify(response_object))
            response.status_code = 201
            return response


# if __name__ == "__main__":
#     app.debug = True
#     app.run(host='0.0.0.0', port=8080)

