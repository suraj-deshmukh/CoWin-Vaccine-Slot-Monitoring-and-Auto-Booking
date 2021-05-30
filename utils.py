from functools import partial
from threading import Thread
import time
from tornado import gen
import requests, json
from config import *
import hashlib

session = requests.Session()
session.headers = headers

def send_otp(mobno):
    data = {"secret":"U2FsdGVkX196RKSOE31ozbO/QRHGJ6RuEqacJuqWO4NQaA+7SO/1Ixzhqe/fkMtk4HjsB7Bjy1GKdC7qGOHeBg==","mobile": mobno}
    resp = session.post('https://cdn-api.co-vin.in/api/v2/auth/generateMobileOTP', data=json.dumps(data))
    if resp.status_code == 200:
        print("OTP SENT SUCCESSFULLY")
        out_json = resp.json()
        print(f"Transaction ID: {out_json}")
        return True, out_json
    else:
        print(f"Generate otp Status code: {resp.status_code}\n{resp.text}")
        return False, resp.text

def send_capcha():
    out = session.post("https://cdn-api.co-vin.in/api/v2/auth/getRecaptcha")
    if out.status_code == 200:
        captcha = out.json()['captcha']                                                                                                                                                                     
        return True, captcha
    else:
        print("capcha downloading failed: {out.text}")
        return False, out.text

def verify_otp(mobno, otp, txnId):
    pin = hashlib.sha256(bytes(otp, 'utf-8')).hexdigest()
    validate = {"otp": pin, "txnId": txnId} 
    resp = session.post('https://cdn-api.co-vin.in/api/v2/auth/validateMobileOtp', data=json.dumps(validate))
    if resp.status_code == 200:
        print("OTP SUCCESSFULLY VERIFIED")
        out_json = resp.json()
        token = out_json['token']
        get_authenticated_session(token)
        return True, out_json
    else:
        print(f"Validate otp Status code: {resp.status_code}\n{resp.text}")
        return False, resp.text

def get_authenticated_session(token):
    header = {'Authorization': f"Bearer {token}"}
    session.headers.update(header)
    
def book_slot(book, capcha):
    book["captcha"] = capcha
    book = json.dumps(book)
    resp = session.post("https://cdn-api.co-vin.in/api/v2/appointment/schedule", data=book)
    if resp.status_code == 200:
        print("Scheduled Successfully.")
        print(f"response: {resp.json()}")
        return True, resp.json()
    else:
        print(f"booking error. {resp.status_code}\n{resp.text}")
        return False, resp.text

def filter(sessions ,center, age_group, fees, vaccine, dose, refids):
    if (center['fee_type'] == fees or fees == 'Any') and (vaccine == 'ANY' or vaccine == sessions['vaccine']):
        capacity = sessions.get(f'available_capacity_dose{dose}', None)
        print(capacity, age_group)
        print(sessions)
        if capacity >= len(refids) and str(sessions['min_age_limit']) == age_group:
            center_details = {
                'name': center['name'],
                'center_id': center['center_id'],
                'sessions': sessions
            }
            print(f"\nbooking available for below center:\n{center_details} and vaccine: {sessions['vaccine']}")
            return  {
                "center_id": center['center_id'],
                "session_id": sessions['session_id'],
                "beneficiaries": refids,
                "slot": sessions['slots'][0],
                "dose": dose
            }