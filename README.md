<br />
<p align="center">
  <h3 align="center">CoWIN Vaccine Slot Monitoring and Auto Booking(With Auto Capcha Solver)</h3>

  <p align="center">
    <a href="#demo">View Demo</a>
    ·
    <a href="https://github.com/suraj-deshmukh/CoWin-Vaccine-Slot-Monitoring-and-Auto-Booking/issues">Report Bug</a>
    ·
    <a href="https://github.com/suraj-deshmukh/CoWin-Vaccine-Slot-Monitoring-and-Auto-Booking/issues">Request Feature</a>
  </p>
</p>



## About The Project
![cowin](https://user-images.githubusercontent.com/14833831/120104460-1e142000-c172-11eb-9d69-781b9479dd00.png)

The Dashboard is developed using ![Bokeh](https://docs.bokeh.org/en/latest/index.html#) and python 3.5+. This dashboard is useful for you if you are looking for something which will help you to book the vaccine slot once slots become available. Other Vaccine Finders will notify you once slots become available but you will still need to login to the portal and book the slot manually. This dashboard will look for slot availability continuously and will send the OTP itself once slots become available. You will need to stay alert to enter the OTP as soon as you received it.

## Why this project

Being software developer I always try to automate things which are important to me. I really struggled to book the slot on cowin portal and other vaccine finder scripts did not helped me at all. So I wanted to do build something which will not just look for vaccine availability but also help me in automating the otp sending and slot booking tasks.

## Getting Started
## Prerequisites

* Docker: Click here to install ![Docker](https://docs.docker.com/engine/install/)

If you don't want to use Docker then you will need python 3.5+ installed on your system and then clone this repository using into `cowin-app` folder using `git clone https://github.com/suraj-deshmukh/CoWin-Vaccine-Slot-Monitoring-and-Auto-Booking.git cowin-app` and install prequisites using `pip install -r cowin-app/requirements.txt`

### Usage for Docker
* Open Command Prompt and run `docker run --pull always -p 5100:5100 suraj20/cowin-vaccine-monitoring-n-booking-dashboard:latest`. The argument `--pull always` makes sure you are pulling latest image from docker hub. 
* Open browser and type `http://localhost:5100/cowin-app`.  

### Usage for non Docker
* Change directory to the folder where you cloned this repository and then run `bokeh serve --port 5100 cowin-app/` 
* Open browser and type `http://localhost:5100/cowin-app`.  

I recommend using docker option to run this dashboard. The docker option will make sure you always run latest image with latest features and bug fixes.

## How to use

1. Enter your name, pincodes(incase of mulitple pincodes use csv format like `411001,411002` etc), 10 digit registered mobile number and reference ids(incase of mulitple ids use csv format like `12345678911234,12345678911111` etc. You will get this reference ids from cowin portal.
2. Other Fields like date, dose number, age group,vaccine fee and vaccine type have default values. This are self explanatory fields and change as per your requirement.  
3. For Dose 2, select the vaccine that you received on dose 1.

## How does it work

1. Enter all the details and the click on `Submit Information` button. All fields except OTP and Captcha one will be disabled.n
2. Once you click on `Submit Information` button, `Start` button will get enabled and then you can start the background process in seperate thread. The background thread will then monitor the given picodes continuously for slots availability as per the given filters. Once slots becomes available in **any of the center in given pincodes**, script will send otp to registered mobile number and background thread will stop checking for slots. You will get message as ***OTP sent successfully pn Reg Mob No. Please enter the OTP within 3 minutes***. The center details for which slots are availbale will get populated under `Center Name` as shown below
![session](https://user-images.githubusercontent.com/14833831/120108972-1ad65f80-c185-11eb-8476-476276ffe199.png)
4. Enter the OTP received on registered mobile number and click on `Submit OTP`. If otp is correct then you will get message on dashboard as ***OTP verified Successfully and Pls enter captcha.***. The `captcha` field will get auto populated with captcha. 
5. Enter the captcha in `Enter Captcha` field and then click on `Submit Captcha and Book Slot`. If entered captcha is correct then script will book the slot and you will receive SMS from CoWIN portal.![booking](https://user-images.githubusercontent.com/14833831/120109119-b7006680-c185-11eb-8c72-53ef8c403283.png)

## Demo

https://user-images.githubusercontent.com/14833831/120110783-a69fba00-c18c-11eb-9ff3-005eeda48b7e.mp4

## To Do
* Validations on input fields
* Resend OTP option 
* Resend Captcha if captcha verfication fails.

## How to Contribute to this repo

![Follow this](https://github.com/firstcontributions/first-contributions)







