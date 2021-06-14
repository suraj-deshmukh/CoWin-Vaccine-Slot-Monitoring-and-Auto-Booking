from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import Div, Select, TextInput, Button, CustomJS, MultiChoice
from bokeh.models.widgets import DatePicker
from datetime import timedelta, datetime
from utils import *
import os, sys

@gen.coroutine
def book(one_time_pin, error):
    # print(f"otp_response: {one_time_pin}")
    if one_time_pin == False:
        login_stats.text = error
    else: 
        otp.value = one_time_pin
        verify_otp_callback()
    thread_stat.text = "STOPPED"

@gen.coroutine
def update(notification_json):
    global txnId, check_date
    process_status = notification_json.get('status')
    code = notification_json.get('code', None)
    output = notification_json.get('session', None)
    name = notification_json.get('name', None)
    pincode = notification_json.get('pin', None)
    if process_status == 'SUCCESS':
        # pin.text = f"Checking for Pincode: {pincode}"
        thread_stat.text = "RUNNING..."
        slot_available = notification_json.get('slot_available', None)
        if slot_available == True:
            thread_stat.text = "Waiting...to fetch OTP" if mode.value == 'Auto' else "STOPPED"
            stop.disabled = True
            button.disabled = False
            notifications.text = "Status:<br>" + f"status code: {code}(success)<br>" + f"response text:<br> <pre>{json.dumps(output, indent=4)}</pre>"
            center_name.text = f"{name}"
            check_date = datetime.now().replace(second=0, microsecond=0)
            otp_stat = send_otp(mobno.value)
            if otp_stat[0] == True:
                login_stats.text = "OTP sent Successfully on Reg Mob No. Please enter the OTP within 3 minutess"
                txnId = otp_stat[1]['txnId']
            else:
                login_stats.text = f"Unable to send OTP on Reg Mob No.<br><pre>{json.dumps(otp_stat[1], indent=4)}</pre>"
                txnId = False
    elif process_status == 'STOPPED_BY_USER':
        thread_stat.text = "STOPPED"
        notifications.text = "NA"
        login_stats.text="NA"
        # pin.text="Checking for Pincode: NA"
        center_name.text="NA"
    elif process_status == 'FAILED':
        thread_stat.text = f"status code: {code}(Failed)<br>" + f"response text:<br> <pre>{json.dumps(output, indent=4)}</pre>"

def fun():
    global partial_filter
    global filtered_session
    global txnId, email, password, check_date
    district_id = districts.value
    print(f"district_id: {district_id}")
    DATE = datetime.strptime(date.value, "%Y-%m-%d").strftime("%d-%m-%Y")
    session.headers.pop('Authorization', None) #don
    while True:
        try:
            start = datetime.now()
            out = session.get(f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict?district_id={district_id}&date={DATE}", timeout=3)
            # total_seconds = 3 - (datetime.now() - start).total_seconds()
            if stop_checking:
                doc.add_next_tick_callback(partial(update, notification_json = {'status': 'STOPPED_BY_USER'}))
                print("Exiting......")
                return None
            if out.status_code == 200:
                doc.add_next_tick_callback(partial(update, {'status': 'SUCCESS', 'code': 200}))
                filtered_session = partial_filter(sessions = out.json())
                if filtered_session:
                    print(f"slot: {filtered_session[0]}")
                    # print(f"before txnId: {txnId}")
                    doc.add_next_tick_callback(partial(update, {'status': 'SUCCESS', 'code': 200, 'name': filtered_session[1]['name'], 'session': filtered_session[1]['session'] , 'pin': filtered_session[1]['pin'],'slot_available': True}))
                    # print(f"after txnId: {txnId}")
                    time.sleep(1)
                    print(f"txnId: {txnId}")
                    # check_date = datetime.now()
                    if mode.value == 'Auto' and txnId != False:
                        print(f"otp sent at: {check_date}")
                        otp_response, error = get_otp(email, password, check_date)
                        # print(f"otp_response: {otp_response}")
                        doc.add_next_tick_callback(partial(book, one_time_pin=otp_response, error=error))
                    return None
            else:
                print(f"status code: {out.status_code}")
                print(f"response: {out.text}")
                doc.add_next_tick_callback(partial(update, notification_json={'status': 'FAILED', 'code': out.status_code, 'session': out.text}))
            # if total_seconds < 0:
            #     pass
            # else:
            #     time.sleep(total_seconds)
            time.sleep(3)
        except Exception as e:
            print(f"\nthread exception: {e} at {start}\n")
            # time.sleep(1)

doc = curdoc()
user = {}

name = TextInput(title="Enter Name", placeholder="Your Name")
date = DatePicker(title="Select date", value=datetime.today().strftime("%Y-%m-%d"))
mobno = TextInput(title="Enter Registered Mob no", placeholder="Your Number")
pincodes = TextInput(title="Enter Pincodes", placeholder="Pincodes in comma seperated format. like pin1,pin2")

states = Select(title="State", options=[('None', '----Select State----')]+get_states())
districts = Select(title="District", options=[('None', '----Select District----')])

vaccines = MultiChoice(title="Select Vaccine Type", options=vaccine_multi, value=vaccine_multi)
# vaccines = Select(title="Select Vaccine Type", options=vaccine, value="COVAXIN")
doseno = Select(title="Select Dose Number", options=dose, value="1")
fees = Select(title="Select Fees", options=fee, value="Any")
group = Select(title="Select Age Group", options=age, value="18")
mode = Select(title="Select Mode", options=[("Auto", "Auto"),("Manual", "Manual")], value='Manual',disabled = True)
refids = TextInput(title="Enter Ref IDs for above selected group", placeholder="Ref IDs in comma seperated format. like id1,id2")
button = Button(label="Submit Information", button_type="success", height=50)
start = Button(label="Start", button_type="success", height=50, disabled = True)
stop = Button(label="Stop", button_type="success", height=50, disabled = True)

otp = TextInput(title="Enter OTP", placeholder="OTP")
otp_submit = Button(label="Submit OTP", button_type="success", height=50)
# resend = Button(label="Resend OTP", button_type="success", height=50)
capcha = Div(text="""Captcha<br>"""+"""<svg xmlns="http://www.w3.org/2000/svg" width="150" height="50" viewBox="0,0,150,50"></svg>""",css_classes=["capcha"])
capcha_input = TextInput(title="Enter Captcha", placeholder="captcha", sizing_mode='scale_width', disabled = True)
capcha_submit = Button(label="Submit Captcha and Book Slot", button_type="success", height=50, disabled = True)
# resend_capcha = Button(label="Resend Capcha", button_type="success")

login_stats = Div(text="NA")
pin = Div(text="NA")
center_name = Div(text="NA")
notifications = Div(text="NA")
thread_stat = Div(text="NA")

def check_mode():
    if len(sys.argv) == 8:
        # print('here')
        mode.disabled = False
    else:
        mode.disabled = True

def get_creds(attr, old, new):
    if mode.value == 'Auto':
        global email, password
        email = sys.argv[6]
        password = sys.argv[7]
        print(email, password)

def dropdown(attr, old, new):
    district = get_districts(states.value)
    districts.options = [('None', '----Select District----')] + district

def toggle(inputs):
    for i in inputs:
        if i.disabled == True:
            i.disabled = False
        else:
            i.disabled =  True

def submit():
    global partial_filter
    print("fetching the entered data")
    toggle([name, date, mobno, pincodes, vaccines, doseno, fees, group, refids, states, districts])
    start.disabled = False
    pincode = [k.strip() for k in pincodes.value.split(",")]
    partial_filter = partial(filter, pincodes=pincode, age_group=group.value, fees=fees.value, vaccine=vaccines.value, dose=doseno.value, refids=[k.strip() for k in refids.value.split(",")])

def start_process():
    global stop_checking
    toggle([start, stop, button])
    stop_checking =  False
    thread = Thread(target=fun)
    thread.start()
    thread_stat.text = "RUNNING...."
    login_stats.text = "NA"
    center_name.text = "NA"
    notifications.text = "NA"
    print("thread started")

def stop_process():
    toggle([name, date, mobno, pincodes, vaccines, doseno, fees, group, refids, stop, button, states, districts])
    global stop_checking
    print(f"stop command received for user: {name.value}")
    stop_checking =  True

def verify_otp_callback():
    global txnId
    stat, out_json = verify_otp(mobno.value, otp.value, txnId)
    if stat:
        print('otp verified successully')
        # print(f"booking json: {filtered_session}")
        slot_out = book_slot(filtered_session[0])
        if slot_out[0]:
            login_stats.text = "Booking successful<br>"+f"response text:<br> <pre>{json.dumps(slot_out[1], indent=4)}</pre>"
        else:
            print('booking failed')
            login_stats.text = "Booking Failed<br>"+f"response text:<br> <pre>{json.dumps(slot_out[1], indent=4)}</pre>"
        # caphca_out = send_capcha()
        # if caphca_out[0]:
        #     captcha_svg, captcha_str = caphca_out[1]
        #     print('capcha send successfully')
        #     if captcha_str:
        #         login_stats.text = "OTP and Captcha Status: OTP verified Successfully and Pls cross check SOLVED CAPTCHA. If Captcha is correct then press 'Submit Captcha and Book Slot'"
        #         login_stats.background = "green"
        #         capcha.text = """Captcha<br>"""+f"{captcha_svg}"
        #         capcha_input.value = captcha_str
        #     else:
        #         login_stats.text = "OTP and Captcha Status: OTP verified Successfully and Pls enter capcha. Script COULDN'T SOLVE CAPTCHA"
        #         login_stats.background = "red"
        #         capcha.text = """Captcha<br>"""+f"{captcha_svg}"
    else:
        login_stats.text = "OTP and Captcha Status: OTP verification failed."
        notifications.text = "Status: Failed<br>" + f"response text:<br> <pre>{json.dumps(out_json, indent=4)}</pre>"

def verify_capcha():
    slot_out = book_slot(filtered_session, capcha_input.value.strip())
    if slot_out[0]:
        login_stats.text = "OTP and Captcha Status: Booking successful<br>"+f"response text:<br> <pre>{json.dumps(slot_out[1], indent=4)}</pre>"
    else:
        print('booking failed')
        login_stats.text = "OTP and Captcha Status: Booking Failed<br>"+f"response text:<br> <pre>{json.dumps(slot_out[1], indent=4)}</pre>"

callback = CustomJS(args = {'doseno':doseno, 'button': button, 'vaccines': vaccines}, code="""
console.log(doseno.value)
console.log(vaccines.value)
if (doseno.value == 2 && vaccines.value.length > 1){
 button.disabled = true;
    Swal.fire({
      icon: 'error',
      title: 'Oops...',
      text: 'For Dose 2 select single Vaccine'
    });
}else{
 button.disabled = false;
}
""")

button.on_click(submit)
start.on_click(start_process)
stop.on_click(stop_process)
otp_submit.on_click(verify_otp_callback)
capcha_submit.on_click(verify_capcha)
doseno.js_on_change('value', callback)
vaccines.js_on_change('value', callback)
states.on_change('value', dropdown)
mode.on_change('value', get_creds)

# row1 = row([column([name, mobno, date]),column([pincodes, vaccines, doseno]), column([fees, group, refids]), column([button, start, stop])])
# row2 = row([column([otp, otp_submit]), column([capcha_input, capcha_submit]), capcha])
# row3 = column([login_stats,pin,center_name,notifications, states, districts])
# l = column([row1, row2, row3], css_classes=["middle"])

row1 = row([column([name, mobno, date, otp, row([capcha, capcha_input], width=310)]),column([states, districts, pincodes, otp_submit, capcha_submit]), column([fees, group, refids, vaccines, doseno]), column([button, start, stop, mode])])
# row2 = row([Div(text="\200b"),capcha, capcha_input, capcha_submit])

row3 = column([row([Div(text="Background Thread Status:"), thread_stat]),
              row([Div(text="OTP and Capcha Status:"), login_stats]),
              # row([Div(text="Checking for Pincode:"), pin]),
              row([Div(text="Center Name:"), center_name]),
              row([Div(text="Slot Availability:"), notifications])])
l = column([row1,row3], css_classes=["middle"])

doc.add_root(l)
doc.title = "CoWin"
doc.add_next_tick_callback(check_mode)
