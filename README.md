<br />
<p align="center">
  <h3 align="center">CoWIN Vaccine Slot Monitoring and Auto Booking<strike>(With Auto Capcha Solver)</strike></h3>

  <p align="center">
    <a href="#demo">View Demo</a>
    ·
    <a href="https://github.com/suraj-deshmukh/CoWin-Vaccine-Slot-Monitoring-and-Auto-Booking/issues">Report Bug</a>
    ·
    <a href="https://github.com/suraj-deshmukh/CoWin-Vaccine-Slot-Monitoring-and-Auto-Booking/issues">Request Feature</a>
  </p>
</p>



## About The Project
![new_cowin](https://user-images.githubusercontent.com/14833831/120936221-5ee8d780-c724-11eb-85e0-01e25bb1e1d4.png)

The Dashboard is developed using <a href="https://docs.bokeh.org/en/latest/index.html#">Bokeh</a> and python 3.5+. This dashboard is useful for you if you are looking for something which will help you to book the vaccine slot once slots become available. Other Vaccine Finders will notify you once slots become available but you will still need to login to the portal and book the slot manually. This dashboard will look for slot availability continuously and will send the OTP itself once slots become available. 

There are two modes available i.e **Auto** and **Manual** mode. In **Manual** mode, user will need to stay alert to enter the OTP manually. 

And in **Auto** mode, user will need to do some installation and configuration as given ![here](https://github.com/suraj-deshmukh/CoWin-Vaccine-Slot-Monitoring-and-Auto-Booking/blob/main/README.md#prior-gmail-settings-and-sms-forwarder-app-configuration-for-auto-modenot-required-for-manual-mode), so that script can detect the otp and will book the slot automatically. **Auto Mode May not work all the time as this is a experimental feature**

## Why this project

Being software developer I always try to automate things which are important to me. I really struggled to book the slot on cowin portal and other vaccine finder scripts did not helped me at all. So I wanted to do build something which will not just look for vaccine availability but also help me in automating the otp sending and slot booking tasks.

## Getting Started
## Prerequisites

* Docker: Click here to install <a href="https://docs.docker.com/engine/install/">Docker</a>

If you don't want to use Docker then you will need python 3.5+ installed on your system and then clone this repository using into `cowin-app` folder using `git clone https://github.com/suraj-deshmukh/CoWin-Vaccine-Slot-Monitoring-and-Auto-Booking.git cowin-app` and install prequisites using `pip install -r cowin-app/requirements.txt`

## Prior Gmail Settings and SMS Forwarder App Configuration for Auto Mode(Not required for Manual Mode)

<h6>Gmail App Password</h6>

You will need to generate gmail **application password** to use auto mode. The **application password** can be generated from <a href="https://support.google.com/mail/answer/185833?hl=en-GB">here</a>. This **application password** is different from you **login password**

<h6>Enable IMAP</h6>

Follow only **Step 1** from this <a href="https://support.google.com/mail/answer/7126229?hl=en">link</a>

<h6>Android</h6>

You will need to install **SMS Forwarder - Auto forward SMS to PC or Phone** from google <a href="https://play.google.com/store/apps/details?id=com.frzinapps.smsforward&hl=en_IN&gl=US">play store</a>

Once you install above app from google <a href="https://play.google.com/store/apps/details?id=com.frzinapps.smsforward&hl=en_IN&gl=US">play store</a>. Follow below steps.

1. Open **SMS Forwarder - Auto forward SMS to PC or Phone** App. Click on bottom-right *plus* icon like below

![plus](https://user-images.githubusercontent.com/14833831/120938194-4e8a2a00-c72f-11eb-8539-01007ba4e419.png)

2. Enter your email id under **Set up recipients** as shown in below screenshot

<div align="center">
  <img src="https://user-images.githubusercontent.com/14833831/120938320-b93b6580-c72f-11eb-9360-b45ba85eed8d.png" alt="drawing" width="300"/>
</div>

3. Enter `Your OTP to register/access CoWIN is` text under **Rule for text** as shown in below screenshot.

<div align="center">
  <img src="https://user-images.githubusercontent.com/14833831/120938509-a37a7000-c730-11eb-8ee8-b810c95c43d2.png" alt="drawing" width="300"/>
</div>

4. Scroll down to **More Settings** and enter `cowin` under **Filter Name** and click on edit button to edit `Email Subject` and type `[SMSForwarder] new otp %t` and click on `ok`. Refer below image for the same.

<div align="center">
  <img src="https://user-images.githubusercontent.com/14833831/120938661-8c884d80-c731-11eb-9208-f482cc59b47b.png" alt="drawing" width="300"/>
</div>

<div align="center">
  <img src="https://user-images.githubusercontent.com/14833831/120938664-91e59800-c731-11eb-8122-4c4f3d06b6eb.png" alt="drawing" width="300"/>
</div>

Finally Click on `SAVE` button on **top-right** corner. You can always enable or disable this filter.  

### Usage for Docker
<h6>Auto Mode</h6>

* Open Command Prompt and run `docker run --pull always -p 5100:5100 -e TZ=Asia/Kolkata suraj20/cowin-vaccine-monitoring-n-booking-dashboard:latest --args "you_gmail@gmail.com" "app_password_here"`. The argument `--pull always` makes sure you are pulling latest image from docker hub. 
* Open browser and type `http://localhost:5100/cowin-app`. 

<h6>Manual Mode</h6>

* Open Command Prompt and run `docker run --pull always -p 5100:5100 suraj20/cowin-vaccine-monitoring-n-booking-dashboard:latest`. The argument `--pull always` makes sure you are pulling latest image from docker hub. 
* Open browser and type `http://localhost:5100/cowin-app`. 

### Usage for non Docker
<h6>Auto Mode</h6>

* Make sure your system clock has set to IST(Indian Standard Time)
* Clone this repo into folder 'cowin-app'
* Change directory to the folder where you cloned this repository and then run `bokeh serve --port 5100 cowin-app/ --args "you_gmail@gmail.com" "app_password_here"` 
* Open browser and type `http://localhost:5100/cowin-app`.  

<h6>Manual Mode</h6>

* Clone this repo into folder 'cowin-app'
* Change directory to the folder where you cloned this repository and then run `bokeh serve --port 5100 cowin-app/` 
* Open browser and type `http://localhost:5100/cowin-app`. 

I recommend using docker option to run this dashboard. The docker option will make sure you always run latest image with latest features and bug fixes.

## How to use

1. Enter your name, select state, select districts, enter pincodes(incase of mulitple pincodes use csv format like `411001,411002` etc)associated with selected district only, 10 digit registered mobile number and reference ids(incase of mulitple ids use csv format like `12345678911234,12345678911111` etc. You will get this reference ids from cowin portal.
2. Other Fields like date, dose number, age group,vaccine fee and vaccine type have default values. This are self explanatory fields and change as per your requirement.  
3. Select Mode. There are two modes i.e Auto and Manual. Select the one as per your choice
4. For Dose 2, select the vaccine that you received on dose 1.

## How does it work

1. Enter all the details as explained above and the click on `Submit Information` button. All fields except OTP and Captcha one will be disabled.
2. Once you click on `Submit Information` button, `Start` button will get enabled and then you can start the background process in seperate thread. The background thread will then monitor the given picodes continuously for slots availability as per the given filters. Once slots becomes available in **any of the center in given pincodes**, script will send otp to registered mobile number and background thread will stop checking for slots. You will get message as ***OTP sent successfully pn Reg Mob No. Please enter the OTP within 3 minutes***. The center details for which slots are availbale will get populated under `Center Name` as shown below
![session](https://user-images.githubusercontent.com/14833831/120108972-1ad65f80-c185-11eb-8476-476276ffe199.png)
3. If you have selected Manual mode then enter the OTP received on registered mobile number and click on `Submit OTP`. If otp is correct then you will get message on dashboard as below

![Screenshot from 2021-06-06 22-37-15 (copy)](https://user-images.githubusercontent.com/14833831/120936906-22b77600-c728-11eb-8f08-83bcad8f0c16.png)

4. If selected mode is Auto mode then user will not have to enter otp manually. The **SMS Forwarder Application** will forward the sms on given gmail id and python script has incoming email monioring code to check incoming emails related to cowin otp. Once script detects otp email it then parse the otp and book the slots directly. **User will need to keep the mobile phone connected to wifi or mobile data all the time for SMS Forwarder to work**

## Demo

https://user-images.githubusercontent.com/14833831/120937107-30213000-c729-11eb-9fa2-6932d4d57581.mp4

## To Do
* Validations on input fields
* Resend OTP option 
* <strike>Resend Captcha if captcha verfication fails.</strike>

## How to Contribute to this repo

![Follow this](https://github.com/firstcontributions/first-contributions)









