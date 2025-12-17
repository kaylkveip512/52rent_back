import base64
import hashlib
import json

LIQPAY_PUBLIC_KEY = "sandbox_i88058663478"
LIQPAY_PRIVATE_KEY = "sandbox_0urODQ35XoZCpHyz4GwivS3y2jY9EevKzUJGosct"


def create_payment(order_id: int, amount: float):

    data = {
        "public_key": LIQPAY_PUBLIC_KEY,
        "version": "3",
        "action": "pay",
        "amount": amount,
        "currency": "UAH",
        "description": f"Оплата замовлення #{order_id}",
        "order_id": str(order_id),
        "result_url": "http://127.0.0.1:5500/index.html",
        "server_url": "https://monomolecular-tonja-nonglutenous.ngrok-free.dev/payments/pay/callback/",
    }

    json_data = json.dumps(data)
    data_base64 = base64.b64encode(json_data.encode()).decode()

    sign_str = LIQPAY_PRIVATE_KEY + data_base64 + LIQPAY_PRIVATE_KEY
    signature = base64.b64encode(hashlib.sha1(sign_str.encode()).digest()).decode()

    payment_url = f"https://www.liqpay.ua/api/checkout?data={data_base64}&signature={signature}"

    return {
        "payment_url": payment_url,
        "data": data_base64,
        "signature": signature,
    }
