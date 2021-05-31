from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import Div, Select, TextInput, Button, CustomJS
from bokeh.models.widgets import DatePicker
from datetime import timedelta, datetime
from utils import *

@gen.coroutine
def update(notification_json):
    process_status = notification_json.get('status')
    code = notification_json.get('code', None)
    output = notification_json.get('session', None)
    name = notification_json.get('name', None)
    pincode = notification_json.get('pin', None)
    if process_status == 'SUCCESS':
        pin.text = f"Checking for Pincode: {pincode}"
        slot_available = notification_json.get('slot_available', None)
        if slot_available == True:
            stop.disabled = True
            notifications.text = "Status:<br>" + f"status code: {code}(success)<br>" + f"response text:<br> <pre>{json.dumps(output, indent=4)}</pre>"
            center_name.text = f"Center Name: {name}"
            otp_stat = send_otp(mobno.value)
            if otp_stat[0] == True:
                global txnId
                login_stats.text = "OTP and Captcha Status: OTP sent Successfully on Reg Mob No. Please enter the OTP within 3 minutess"
                txnId = otp_stat[1]['txnId']
            else:
                login_stats.text = f"OTP and Captcha Status: Unable to send OTP on Reg Mob No.<br><pre>{json.dumps(otp_stat[1], indent=4)}</pre>"
    elif process_status == 'STOPPED_BY_USER':
        notifications.text = "Status: Stopped"
        login_stats.text="OTP and Captcha Status:"
        pin.text="Checking for Pincode: NA"
        center_name.text="Center Name: NA"
    elif process_status == 'FAILED':
        notifications.text = "Status: <br>" + f"status code: {code}(Failed)<br>" + f"response text:<br> <pre>{json.dumps(output, indent=4)}</pre>"

def fun():
    global partial_filter
    global filtered_session
    PINCODES = [k.strip() for k in pincodes.value.split(",")]
    DATE = datetime.strptime(date.value, "%Y-%m-%d").strftime("%d-%m-%Y")
    session.headers.pop('Authorization', None) #don
    while True:
        for i in PINCODES:
            if stop_checking:
                doc.add_next_tick_callback(partial(update, notification_json = {'status': 'STOPPED_BY_USER'}))
                print("Exiting......")
                return None
            out = session.get(f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={i}&date={DATE}")
            if out.status_code == 200:
                doc.add_next_tick_callback(partial(update, {'status': 'SUCCESS', 'code': 200, 'pin': i}))
                for j in out.json()['centers']:
                    for sessions in j['sessions']:
                        # doc.add_next_tick_callback(partial(update, {'status': 'SUCCESS', 'code': 200, 'session': sessions, 'name': j['name']}))
                        filtered_session = partial_filter(sessions = sessions, center=j)
                        if filtered_session:
                            print(f"slot: {filtered_session}")
                            doc.add_next_tick_callback(partial(update, {'status': 'SUCCESS', 'code': 200, 'name': j['name'], 'session': sessions , 'pin': i,'slot_available': True}))
                            return None
            else:
                print(f"status code: {out.status_code}")
                print(f"response: {out.text}")
                doc.add_next_tick_callback(partial(update, notification_json={'status': 'FAILED', 'code': out.status_code, 'session': out.text}))
            time.sleep(3)

doc = curdoc()
user = {}

name = TextInput(title="Enter Name", placeholder="Your Name")
date = DatePicker(title="Select date", value=(datetime.today() + timedelta(0)).strftime("%d-%m-%Y"))
mobno = TextInput(title="Enter Registered Mob no", placeholder="Your Number")
pincodes = TextInput(title="Enter Pincodes", placeholder="Pincodes in comma seperated format. like pin1,pin2")
vaccines = Select(title="Select Vaccine Type", options=vaccine, value="COVAXIN")
doseno = Select(title="Select Dose Number", options=dose, value="1")
fees = Select(title="Select Fees", options=fee, value="Free")
group = Select(title="Select Age Group", options=age, value="18")
refids = TextInput(title="Enter Ref IDs for above selected group", placeholder="Ref IDs in comma seperated format. like id1,id2")
button = Button(label="Submit Information", button_type="success", height=50)
start = Button(label="Start", button_type="success", height=50, disabled = True)
stop = Button(label="Stop", button_type="success", height=50, disabled = True)

otp = TextInput(title="Enter OTP", placeholder="OTP")
otp_submit = Button(label="Submit OTP", button_type="success", height=50)
# resend = Button(label="Resend OTP", button_type="success", height=50)
capcha = Div(text="""Captcha<br>"""+"""<svg xmlns="http://www.w3.org/2000/svg" width="150" height="50" viewBox="0,0,150,50"></svg>""",css_classes=["capcha"])
capcha_input = TextInput(title="Enter Captcha", placeholder="captcha")
capcha_submit = Button(label="Submit Captcha and Book Slot", button_type="success", height=50)
# resend_capcha = Button(label="Resend Capcha", button_type="success")

login_stats = Div(text="OTP and Capcha Status:")
pin = Div(text="Checking for Pincode: NA")
center_name = Div(text="Center Name: NA")
notifications = Div(text="Slot Availability: NA")

def toggle(inputs):
    for i in inputs:
        if i.disabled == True:
            i.disabled = False
        else:
            i.disabled =  True

def submit():
    global  partial_filter
    print("fetching the entered data")
    toggle([name, date, mobno, pincodes, vaccines, doseno, fees, group, refids])
    start.disabled = False
    partial_filter = partial(filter, age_group=group.value, fees=fees.value, vaccine=vaccines.value, dose=doseno.value, refids=[k.strip() for k in refids.value.split(",")])

def start_process():
    toggle([start, stop, button])
    global stop_checking
    stop_checking =  False
    thread = Thread(target=fun)
    thread.start()
    print("thread started")

def stop_process():
    toggle([name, date, mobno, pincodes, vaccines, doseno, fees, group, refids, stop, button])
    global stop_checking
    print(f"stop command received for user: {name.value}")
    stop_checking =  True

def verify_otp_callback():
    global txnId
    stat, out_json = verify_otp(mobno.value, otp.value, txnId)
    if stat:
        print('otp verified successully')
        caphca_out = send_capcha()
        if caphca_out[0]:
            captcha_svg, captcha_str = caphca_out[1]
            print('capcha send successfully')
            if captcha_str:
                login_stats.text = "OTP and Captcha Status: OTP verified Successfully and Pls cross check SOLVED CAPTCHA. If Captcha is correct then press 'Submit Captcha and Book Slot'"
                login_stats.background = "green"
                capcha.text = """Captcha<br>"""+f"{captcha_svg}"
                capcha_input.value = captcha_str
            else:
                login_stats.text = "OTP and Captcha Status: OTP verified Successfully and Pls enter capcha. Script COULDN'T SOLVE CAPTCHA"
                login_stats.background = "red"
                capcha.text = """Captcha<br>"""+f"{captcha_svg}"
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
if (doseno.value == 2 && vaccines.value == 'ANY'){
 button.disabled = true;
    Swal.fire({
      icon: 'error',
      title: 'Oops...',
      text: 'Vaccine can not be set to Any for Dose 2'
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

row1 = row([column([name, mobno, date]),column([pincodes, vaccines, doseno]), column([fees, group, refids]), column([button, start, stop])])
row2 = row([column([otp, otp_submit]), column([capcha_input, capcha_submit]), capcha])
row3 = column([login_stats,pin,center_name,notifications])
l = column([row1, row2, row3], css_classes=["middle"])

doc.add_root(l)
doc.title = "CoWin"
