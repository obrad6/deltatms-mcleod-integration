from flask import Flask, jsonify, request, make_response
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_swagger_ui import get_swaggerui_blueprint
from zip_code_api import get_zip_codes_for_city_and_state
from mcleod import save_customer, save_order, get_customer_by_name

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'Delt@wwerw434rewfer4334rdefwe'
jwt = JWTManager(app)


SWAGGER_URL = '/api-reference'
API_URL = '/static/swagger.yaml'
SWAGGER_BLUEPRINT = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
app.register_blueprint(SWAGGER_BLUEPRINT, url_prefix=SWAGGER_URL)


@app.route('/auth', methods=['POST'])
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


@app.route('/orders', methods=['POST'])
@jwt_required()
def post_order():
    """"""
    data = request.get_json()
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

        # TODO: Figure out bellow fields in DeltaTMS
        # pickup_contact_name = pickup['contactName']
        # pickup_contact_phone = pickup['contactPhoneNumber']
        # pickup_contact_email = pickup['contactEmail']
        # pickup_ref_booking_number = ""
        # if "refBookingNo" in pickup:
        #     pickup_ref_booking_number = pickup['refBookingNo']

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
            'package_count': pickup_package_count
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

        #TODO: Figure oout bellow fields in DeltaTMS

        # delivery_do_number = delivery['doNumber']
        # delivery_instruction = delivery['instruction']
        # delivery_company = delivery['company']
        # delivery_bol_url = delivery['bolUrl']
        # delivery_contact_name = delivery['contactName']
        # delivery_contact_phone = delivery['contactPhoneNumber']
        # delivery_contact_email = delivery['contactEmail']
        # delivery_total_piece_count = delivery['totalPieceCount']
        # delivery_total_weight_kgs = delivery['totalWeightKgs']
        # delivery_total_volume_cbm = delivery['totalVolumeCbm']
        # delivery_dg_notes = delivery['dgNotes']
        # delivery_remarks = delivery['remarks']
        # delivery_dn_number = delivery['dnNumber']
        # delivery_ref_booking_number = delivery['refBookingNo']

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
        except Exception as e:
            print(f"Error saving order: {str(e)}")
            response_object = {'status_code': 500,
                               'message': f"Failed to save order.\nError:\n{str(e)}",
                               'success': False}
            response = make_response(jsonify(response_object))
            response.status_code = 500
            return response


@app.route('/customers', methods=['POST'])
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


