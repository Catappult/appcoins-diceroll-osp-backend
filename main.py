import json
import os
from fastapi import FastAPI, Response
from expiringdict import ExpiringDict
import urllib.parse
import hmac
import hashlib
import httpx
import random
import string

SECRET_KEY = bytes(os.getenv('SECRET_KEY'), 'utf-8')
BASE_URL = os.getenv('BASE_URL')
if not SECRET_KEY and not BASE_URL:
    raise SystemExit('SECRET_KEY and CALLBACK_URL must be set')

def generate_order_reference(prefix='XYZ', length=8):
    digits = ''.join(random.choice(string.digits) for _ in range(length))
    return prefix + digits

# We use ExpiringDict as a placeholder for the database
orders = ExpiringDict(max_len=1000, max_age_seconds=60 * 5)

async def verify_data_integrity(callback_data: dict) -> bool:
    url = f"https://api.catappult.io/broker/8.20220927/transactions/{callback_data['uid']}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response_data = response.json()
        return compare_data(response_data, callback_data)
    
def compare_data(response_data: dict, callback_data: dict) -> bool:
    keys_to_check = ['uid', 'reference', 'domain', 'product', 'price']

    if not all(key in response_data and key in callback_data for key in keys_to_check):
        return False
    for key in keys_to_check:
        if isinstance(response_data[key], dict) and isinstance(callback_data[key], dict):
            if not response_data[key] == callback_data[key]:
                return False 
        elif response_data[key] != callback_data[key]:
            return False
    return True



app = FastAPI()

@app.get("/osp_url/{product}")
def get_url(product: str):
    order_reference = generate_order_reference()
    callback_url = BASE_URL + "/callback_handler"
    encoded_callback_url = urllib.parse.quote(callback_url, safe="")
    url = f"https://apichain.catappult.io/transaction/inapp?product={product}&domain=com.appcoins.diceroll&callback_url={encoded_callback_url}&order_reference={order_reference}"
    signature = hmac.new(SECRET_KEY, url.encode("utf-8"), hashlib.sha256).hexdigest()
    orders[order_reference] = "PENDING"
    return {"url": url + "&signature=" + signature, "order_reference": order_reference}

@app.post("/callback_handler")
async def handle_callback(data: dict):
    transaction_data = json.loads(data["transaction"])
    reference = transaction_data["reference"]
    is_valid = await verify_data_integrity(transaction_data)
    if is_valid:
        orders[reference] = transaction_data["status"]
    else:
        orders[reference] = "FAILED"
    return Response(status_code=200)

@app.get("/callback_result/{order_reference}")
def read_order(order_reference: str):
    if order_reference in orders:
        return {"status": orders[order_reference]}
    else:
        return Response(status_code=404)