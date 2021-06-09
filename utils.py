from bs4 import BeautifulSoup
from functools import partial
from threading import Thread
import time
from tornado import gen
import requests, json
from config import *
import hashlib, re
import pandas as pd
import email as eb
import datetime as dt
import dateparser
from imapclient import IMAPClient
import email, time

with open ('cowin-app/lookup.json', 'r') as f:
    lookup = json.load(f)

session = requests.Session()
session.headers = headers

# def get_otp(email, password):
#     server = 'imap.gmail.com'
#     mail = imaplib.IMAP4_SSL(server)
#     mail.login(email, password)
#     start = dt.datetime.now()
#     while True:
#         try:
#             mail.select('inbox')
#             status, data = mail.search(None, "UNSEEN SUBJECT", '"[SMSForwarder] new otp"')
#             if data[0]:
#                 print(f"data: {data}")
#                 status, msg = mail.fetch(data[0], '(RFC822)')
#                 message = eb.message_from_string(msg[0][1].decode('utf-8')).get_payload()
#                 print(f"msg: {message}")
#                 return re.search(r'\d{6}', message).group()
#             time.sleep(1)
#             diff = (dt.datetime.now() - start).total_seconds()
#             if diff > 180:
#                 return False
#         except Exception as e:
#             print(f"exception: {e}")
#             return False

def get_otp(email_id, password, check_date):
    HOST = "imap.gmail.com"
    USERNAME = email_id
    PASSWORD = password
    
    # server = IMAPClient(HOST,use_uid=False)
    # server.login(USERNAME, PASSWORD)
    start = dt.datetime.now()
    try:
        with IMAPClient(HOST,use_uid=False,timeout=180) as server:
            server.login(USERNAME, PASSWORD)
            while True:
                # print("checking")
                server.select_folder("INBOX")
                date = dt.datetime.now().strftime("%m-%b-%Y")
                emails = server.search(['UNSEEN', 'SUBJECT', f'"[SMSForwarder] new otp"','SINCE', date])
                if emails:       
                    for msg_id in emails:
                        item = server.fetch(msg_id, "RFC822")
                        email_message = email.message_from_bytes(item[msg_id][b"RFC822"])
                        print(f"subject:{email_message.get('Subject')}")
                        subject = email_message.get("Subject")
                        if "[SMSForwarder] new otp" in subject:
                            email_date = dateparser.parse(subject.replace("[SMSForwarder] new otp ", ""))
                            print(f"email_date: {email_date}")
                            if email_date >= check_date:
                                print(f"required email found : {email_message.get_payload()}")
                                return re.search(r'\d{6}', email_message.get_payload()).group(), None
                time.sleep(1.5)
                diff = (dt.datetime.now() - start).total_seconds()
                if diff > 180:
                    return False, "OTP Email not received"
    except Exception as e:
        print(f"exception: {e}")
        return False, str(e)

def get_states():
    try:
        resp = session.get('https://cdn-api.co-vin.in/api/v2/admin/location/states', timeout=3)
        if resp.status_code == 200:
            states = resp.json()['states']
            states = [(str(state['state_id']), state['state_name']) for state in states]
            return states
    except Exception as e:
        print(f"Unable to fetch states: {e}")
        return []

def get_districts(state_id):
    try:
        resp = session.get(f'https://cdn-api.co-vin.in/api/v2/admin/location/districts/{state_id}', timeout=3)
        if resp.status_code == 200:
            districts = [(str(district['district_id']), district['district_name']) for district in resp.json()['districts']]
            return districts
    except Exception as e:
        print(f"Unable to fetch districts: {e}")
        return []
    

def send_otp(mobno):
    try:
        data = {"secret":"U2FsdGVkX196RKSOE31ozbO/QRHGJ6RuEqacJuqWO4NQaA+7SO/1Ixzhqe/fkMtk4HjsB7Bjy1GKdC7qGOHeBg==","mobile": mobno}
        resp = session.post('https://cdn-api.co-vin.in/api/v2/auth/generateMobileOTP', data=json.dumps(data), timeout=10)
        if resp.status_code == 200:
            print("OTP SENT SUCCESSFULLY")
            out_json = resp.json()
            print(f"Transaction ID: {out_json}")
            return True, out_json
        else:
            print(f"Generate otp Status code: {resp.status_code}\n{resp.text}")
            return False, resp.text
    except Exception as e:
        print(f"error occurred while sending otp: {e}")
        return False, "Could Not Send OTP"

def send_capcha():
    out = session.post("https://cdn-api.co-vin.in/api/v2/auth/getRecaptcha")
    if out.status_code == 200:
        captcha = out.json()['captcha']
        captcha_str = solve_captcha(captcha)
        return True, [captcha, captcha_str]
    else:
        print("capcha downloading failed: {out.text}")
        return False, out.text

def verify_otp(mobno, otp, txnId):
    try:
        pin = hashlib.sha256(bytes(otp, 'utf-8')).hexdigest()
        validate = {"otp": pin, "txnId": txnId} 
        resp = session.post('https://cdn-api.co-vin.in/api/v2/auth/validateMobileOtp', data=json.dumps(validate), timeout=10)
        if resp.status_code == 200:
            print("OTP SUCCESSFULLY VERIFIED")
            out_json = resp.json()
            token = out_json['token']
            get_authenticated_session(token)
            return True, out_json
        else:
            print(f"Validate otp Status code: {resp.status_code}\n{resp.text}")
            return False, resp.text
    except Exception as e:
        print(f"error while verifying otp: {e}")
        return False, str(e)

def solve_captcha(svg_string):
    try:
        captcha_letter = {}
        svg = BeautifulSoup(svg_string,'html.parser')
        for d in svg.find_all('path',{'fill' : re.compile("#")}):
            svg_path = d.get('d').upper()
            coords = re.findall('M(\d+)',svg_path)
            letter_seq = "".join(re.findall("([A-Z])", svg_path))
            captcha_letter[int(coords[0])] =  lookup.get(letter_seq) #get letter from sequence
        string = "".join(list(map(lambda l: l[-1], sorted(captcha_letter.items()))))
        if string:
            return string
        else:
            return None
    except Exception as e:
        print(f"unable to convert captch to string: {e}")
        return None

def get_authenticated_session(token):
    header = {'Authorization': f"Bearer {token}"}
    session.headers.update(header)
    
def book_slot(book, capcha=None):
    if capcha:
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

# def filter(sessions ,center, age_group, fees, vaccine, dose, refids):
#     if (center['fee_type'] == fees or fees == 'Any') and (vaccine == 'ANY' or vaccine == sessions['vaccine']):
#         capacity = sessions.get(f'available_capacity_dose{dose}', None)
#         print(capacity, age_group)
#         print(sessions)
#         if capacity >= len(refids) and str(sessions['min_age_limit']) == age_group:
#             center_details = {
#                 'name': center['name'],
#                 'center_id': center['center_id'],
#                 'sessions': sessions
#             }
#             print(f"\nbooking available for below center:\n{center_details} and vaccine: {sessions['vaccine']}")
#             return  {
#                 "center_id": center['center_id'],
#                 "session_id": sessions['session_id'],
#                 "beneficiaries": refids,
#                 "slot": sessions['slots'][0],
#                 "dose": dose
#             }

def filter(sessions, pincodes, age_group, fees, vaccine, dose, refids):
    df = pd.DataFrame(sessions['centers'])
    filter_str = [f"pincode == {pincodes}"]
    if fees != 'Any':
        filter_str.append(f"fee_type == '{fees}'")
    query = " and ".join(filter_str) if len(filter_str) != 1 else filter_str[0]
    df_sliced = df.query(query)
    print(f"centers: {len(df_sliced)} at {dt.datetime.now()}")
    for index, (_, row) in enumerate(df_sliced.iterrows()):
        for sess in row['sessions']:
            if sess['vaccine'] in vaccine:
                # print(f"{sess['vaccine']}/{row['center_id']}/{row['name']}")
                capacity = sess.get(f'available_capacity_dose{dose}', None)
                if capacity >= len(refids) and str(sess['min_age_limit']) == age_group:
                    center_details = {
                        'name': row['name'],
                        'center_id': row['center_id'],
                        'sessions': sess
                    }
                    print(f"\nbooking available for below center:\n{center_details} and vaccine: {sess['vaccine']}")
                    return  [{
                        "center_id": row['center_id'],
                        "session_id": sess['session_id'],
                        "beneficiaries": refids,
                        "slot": sess['slots'][0],
                        "dose": dose
                    },{'name': row['name'], 'session': sess, 'pin': row['pincode']}]
    print(f"finished filtering: {dt.datetime.now()}")
    