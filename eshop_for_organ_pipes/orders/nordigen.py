from eshop_for_organ_pipes import constants
import requests

from .models import Order


def get_new_token():
    """
    curl -X POST "https://ob.nordigen.com/api/v2/token/refresh/" \
                -H 'accept: application/json' \
                -H 'Content-Type: application/json' \
                -d '{
                    "refresh": "$REFRESH_TOKEN"
                }'
    """
    url = 'https://ob.nordigen.com/api/v2/token/refresh/'
    token = constants.NORDIGEN_TOKEN
    payload = f'{{ "refresh": "{token}" }}'
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    print("Token handling ....")
    r = requests.post(url, data=payload, headers=headers)
    print(f"Token status: {r.status_code}")
    return r.json()['access']


def get_all_transactions():
    bank_id = constants.NORDIGEN_BANK_ID
    url = f'https://ob.nordigen.com/api/v2/accounts/{bank_id}/transactions/'
    token = get_new_token()
    headers = {"accept": "application/json", "Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    print(f"Transactions status: {r.status_code}")
    return r.json()


def make_paid_bank_transfers():
    transaction_json = get_all_transactions()
    for transaction in transaction_json['transactions']['booked']:

        if transaction.get('additionalInformation', None) is None:
            continue

        order_id = transaction['additionalInformation']
        order_id = str(order_id).strip()
        orders = Order.objects.all().filter(order_id=order_id).exclude(status='paid')
        for order in orders:

            if order is None:
                continue

            amount = float(transaction['transactionAmount']['amount'])
            currency = transaction['transactionAmount']['currency']
            if order.order_total == amount and currency == constants.CURRENCY:
                print(f"{order_id} => {amount}")
                order.cart.mark_bought()
                order.mark_paid()
