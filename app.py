# This application will fetch crypto currency data from coingecko site
# Find top 10 to sell
# find bottom 10 to buy
# send mail to me everyday at 8AM
import smtplib # sednding email
from email.mime.text import MIMEText    #text 
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase #this for including attachment
import email.encoders # this function is going encode the attachment
import requests
import schedule
import pandas as pd 
from datetime import datetime
import time

def send_mail(subject,body,file_name):
    # setup email config
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_mail = "maryferdin02@gmail.com"
    email_password = "Shimo@27"
    receiver_mail = "mariainfant5@gmail.com"

    # compose mail
    message = MIMEMultipart()
    message["From"] = sender_mail
    message["To"] = receiver_mail
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # include attachment 
    with open(file_name, "rb") as file:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(file.read())
        email.encoders.encode_base64(part)
        part.add_header("Content-Disposition",f"attachment; filename='{file_name}'")
        message.attach(part)
    
    # start server
    try:
        with smtp.SMTP(smtp_server,smtp_port)as server:
            server.starttls() #secure connection
            server.login(sender_mail,email_password) #login
            server.sendmail(sender_mail,receiver_mail,message.as_string())
            print("email sent successful")
    except Exception as e:
        print(f"Unable to send email {e}")
    

def get_crypto_data():
    # API Information

    url = "https://api.coingecko.com/api/v3/coins/markets"
    param = {
        "vs_currency":"usd",
        "order":"market_cap_desc",
        "per_page":250,
        "page":1
    }

    # Sending requests

    response = requests.get(url,params=param)
    if response.status_code==200:
        print("Connection Successful!\nGetting the data...")

        # storing the response into data

        data = response.json()
        # creating df dataframe
        df = pd.DataFrame(data)
        # selecting only columns we need-data cleaning
        df = df[["id","current_price","market_cap","price_change_percentage_24h","high_24h", "low_24h","ath","atl"]]

        # Creating new columns

        today = datetime.now().strftime("%d-%m-%Y %H-%M-%S")
        df["time_stamp"] = today

        # getting top 10

        top_negative_10 = df.nsmallest(10,"price_change_percentage_24h")
         
        # getting positive top

        top_positive_10 = df.nlargest(10,"price_change_percentage_24h")
        
        # saving the data

        file_name = f"Crypto_data {today} .csv"
        df.to_csv(file_name,index = False)
        print("Data saved successfully as {file_name}")

        # call email function to send reports

        subject = f"Top 10 crypto currency data to invest for {today}"
        body = f"""
        Good Morning!\n\n

        Your crypto report is here!\n\n

        Top 10 crypto with highest price increase in last 24 hour!\n
        {top_positive_10}\n\n\n

        Top 10 crypto with highest price decrease in last 24 hour!\n
        {top_negative_10}\n\n\n

        Attached 250 plus crypto currency latest reports\n

        Regards!\n

        See you tomorrow!\n
        Your Crypto Python Application"""

        send_mail(subject,body,file_name)
    else:
        print(f"Connection Failed Error code {response.status_code}")

# Calling the function

if __name__=="__main__":

    # scheduling the task at 8AM

    schedule.every().day.at("18:55").do(get_crypto_data)
    while True:
        schedule.run_pending()
