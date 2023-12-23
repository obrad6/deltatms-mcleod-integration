import csv
from app import db
from app.models.comodity import Commodity

LOCKFILE = "scheduler.lock"

ZIP_CODE_API_KEY = "z1LAdcyZSdn6RKtZrjrYnJFQfiNd88WJJBcjRy2SxhYIcd2xDkUoLJr8J4TKazQP"
ZIP_CODE_URL = "https://www.zipcodeapi.com/rest/"

STATES = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "American Samoa": "AS",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Guam": "GU",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Northern Mariana Islands": "MP",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Puerto Rico": "PR",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Trust Territories": "TT",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Virgin Islands": "VI",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY"
}


def pickup_valid(location: dict) -> bool:
    """Check if pickup is valid."""
    if 'address' not in location or location['address'] == '':
        return False
    elif 'city' not in location or location['city'] == '':
        return False
    elif 'state' not in location or location['state'] == '':
        return False
    elif 'country' not in location or location['country'] == '':
        return False
    return True


def delivery_valid(location: dict) -> bool:
    """Check if delivery is valid."""
    if 'address' not in location or location['address'] == '':
        return False
    elif 'city' not in location or location['city'] == '':
        return False
    elif 'state' not in location or location['state'] == '':
        return False
    elif 'country' not in location or location['country'] == '':
        return False
    elif 'totalPieceCount' not in location or location['totalPieceCount'] <= 0:
        return False
    elif 'totalWeightKgs' not in location or location['totalWeightKgs'] <= 0:
        return False
    elif 'totalVolumeCbm' not in location or location['totalVolumeCbm'] <= 0:
        return False
    return True


def booking_valid(booking: dict) -> bool:
    """Check if booking is valid."""
    message = ''
    if 'customerName' not in booking or booking['customerName'] == '':
        message = "Customer name(customerName) is required."
        return False
    if 'customerRefNo' not in booking or booking['customerRefNo'] == '':
        message = "Customer reference number(customerRefNo) is required."
        return False
    if 'pickupList' not in booking or not booking['pickupList']:
        message = "Pickup list(pickupList) is required."
        return False
    if 'pickupList' not in booking or not booking['pickupList']:
        message = "Pickup list(pickupList) is required."
        return False
    for pickup in booking['pickupList']:
        valid_pickup = pickup_valid(pickup)
        if not valid_pickup:
            message = "For each pickup, address, city, state and country are required fields."
            return False
    if 'deliveryList' not in booking or not booking['deliveryList']:
        message = "Delivery list(deliveryList) is required."
        return False
    for delivery in booking['deliveryList']:
        valid_delivery = delivery_valid(delivery)
        if not valid_delivery:
            message = "For each delivery, totalPieceCount, totalWeightKgs, totalVolumeCbm, address, city, " \
                      "state and country are required fields."
            return False
    return True


def get_state_abbreviation(state):
    """Get state abbreviation for a give US State name."""
    st = state.lower().title()
    if st in STATES:
        return STATES[st]


def convert_kgs_to_lb(kilos: float) -> float:
    """Get pounds for a given kilos value."""
    lbs = kilos * 2.20462
    return round(lbs, 1)


def format_date_time_for_mcleod(dt: str) -> str:
    """Get date and time in the format expected by McLeod API."""
    date_and_time = dt.split(' ')
    date_string = date_and_time[0]
    day = date_string.split('-')[2]
    month = date_string.split('-')[1]
    year = date_string.split('-')[0]
    time_string = date_and_time[1]
    return f"{month}/{day}/{year} {time_string}"


def get_mcleod_equipment_type_id(mode: str) -> str:
    """Get McLeod equipment type id based on the equipment type string received"""
    print(f"Getting equipment type id for {mode}")
    equipment_type_ids = {"Conestoga": "CN", "Flatbed": "F", "Flatbed Tarps": "FT", "Flatbed Team": "FM", "Reefer": "R",
                          "Reefer Team": "RM", "Sprinter Van": "SPR", "Step Deck": "SD", "Straight Box Truck": "SB",
                          "Van 48": "V", "Van 48 Team": "VM", "Van 53": "V", "Van 53 Team": "VM"}
    if mode not in equipment_type_ids:
        return ''
    return equipment_type_ids[mode]


def is_team_required_based_on_the_equipment(equipment_type_id: str) -> bool:
    """Get boolean flag if team is required or not based on the McLeod equipment type id."""
    if len(equipment_type_id) == 1:
        return False
    if equipment_type_id[-1] == 'M':
        return True
    return False


def get_delta_status_id_for_mcleod_order_status(order_status: str) -> int:
    """Get Delta status for a given McLeod order status."""
    if order_status == 'C':
        return 2
    elif order_status == 'V':
        return 1
    elif order_status == 'P':
        return 10
    elif order_status == 'A':
        return 1
    elif order_status == 'D':
        return 11
    else:
        return 0


def get_delta_vehicle_type_id_for_mc_leod_mode(mode: str) -> int:
    """Get Delta vehicle type id for a given McLeod mode."""
    if mode == 'V':
        return 3
    elif mode == 'F':
        return 1
    elif mode == 'CN':
        return 10
    elif mode == 'FT':
        return 8
    elif mode == 'FM':
        return 9
    elif mode == 'CN':
        return 6
    elif mode == 'R':
        return 4
    elif mode == 'RM':
        return 11
    elif mode == 'SPR':
        return 12
    elif mode == 'SD':
        return 14
    elif mode == 'SB':
        return 13
    elif mode == 'VM':
        return 6
    else:
        return 0


def insert_commodities_from_csv(filename: str):
    """Insert commodities from a csv file."""
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            commodity = Commodity(product_type=row['product_type'], commodity_id=row['commodity_id'],
                                  commodity_description=row['commodity_description'])
            db.session.add(commodity)
        db.session.commit()

