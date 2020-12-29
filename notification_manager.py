import os
from twilio.rest import Client

class NotificationManager:
    #This class is responsible for sending notifications with the deal flight details.
    def __init__(self):
        pass

    def send_sms(msg):

        if len(msg) != 0:
            # Your Account Sid and Auth Token from twilio.com/console
            # and set the environment variables. See http://twil.io/secure
            account_sid = os.environ["TWILIO_API_ACCOUNT_SID"]
            auth_token = os.environ["TWILIO_API_AUTH_TOKEN"]
            client = Client(account_sid, auth_token)

            message = client.messages \
                .create(
                body=msg,
                from_='+14793483596',
                to='+XXXXXXXXXXX'
            )

            print(message.status)
        else:
            print("No deals today. No message sent.")
