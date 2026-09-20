import base64
import requests
from datetime import datetime
import os

CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY",
    "nm9Q8HjlISlkALk0TcWicZCsinctBqIA5gRTY2vhSSjAL TFE".replace(" ", ""))
CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET",
    "41a7gxjWNdyS1e0fRITIPOLL77zAst8WbE8DJM WwWYM5029J FyX2zBbgr2utJwuH".replace(" ", ""))

SHORTCODE = os.getenv("MPESA_SHORTCODE", "174379")
PASSKEY = os.getenv("MPESA_PASSKEY",
    "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919")
CALLBACK_URL = os.getenv("MPESA_CALLBACK",
    "https://localhost.run/callback")

BASE_URL = "https://sandbox.safaricom.co.ke"


def get_access_token():
    url = f"{BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(url, auth=(CONSUMER_KEY, CONSUMER_SECRET), timeout=30)
    if r.status_code != 200:
        print(f"Auth failed: HTTP {r.status_code} - {r.text[:200]}")
        return None
    try:
        return r.json().get("access_token")
    except Exception as e:
        print("Parse error:", e, "Body:", r.text[:200])
        return None


def stk_push(phone, amount, account_ref="ABAWERA", desc="Abawera Investor"):
    token = get_access_token()
    if not token:
        return {"error": "Failed to get access token"}
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(
        f"{SHORTCODE}{PASSKEY}{timestamp}".encode()
    ).decode()
    if phone.startswith("0"):
        phone = "254" + phone[1:]
    elif phone.startswith("+"):
        phone = phone[1:]
    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": account_ref,
        "TransactionDesc": desc
    }
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(f"{BASE_URL}/mpesa/stkpush/v1/processrequest",
                      json=payload, headers=headers, timeout=30)
    return r.json()


def b2c_payout(phone, amount, remarks="Abawera Payout"):
    token = get_access_token()
    if not token:
        return {"error": "Failed to get token"}
    if phone.startswith("0"):
        phone = "254" + phone[1:]
    payload = {
        "InitiatorName": "testapi",
        "SecurityCredential": "YOUR_SECURITY_CREDENTIAL",
        "CommandID": "BusinessPayment",
        "Amount": int(amount),
        "PartyA": SHORTCODE,
        "PartyB": phone,
        "Remarks": remarks,
        "QueueTimeOutURL": CALLBACK_URL,
        "ResultURL": CALLBACK_URL,
        "Occasion": "Withdrawal"
    }
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(f"{BASE_URL}/mpesa/b2c/v1/paymentrequest",
                      json=payload, headers=headers, timeout=30)
    return r.json()
