import uuid
from django.conf import settings
import smtplib 
from email.message import EmailMessage
from rest_framework.response import Response
from rest_framework import status


def make_bulk(num, obj):
    bulk = []
    counter = 1
    while counter <= num:
        bulk.append(obj)
        counter += 1
    return bulk

def upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    # return 'images/{filename}'.format(filename=filename)
    return filename

def html_tickets(title, count):
    return f'''
    <div style="width: 100%; margin: 10px 0; border: 1px solid black; border-radius: 3px; display: flex; padding: 10px; height: 220px">
            <img src="https://www.freeiconspng.com/thumbs/hd-tickets/download-ticket-ticket-free-entertainment-icon-orange-ticket-design-0.png" alt="logo" height="200px" width="200px" style="display: inline-block">
            <div style="margin-left: 15px; display: inline-block">
                <h2>{title}</h2>
                <div>Билетов: {count}</div>               
            </div>
        </div>
    '''
def make_html(body):
    return f'''
        <!DOCTYPE html>
        <html>
            <body>
                <div style="width: 800px;">
                     {body}
                </div>
            </body>
        </html>
        '''
   
def email_tickets(tickets, email_to):

    if not tickets:
        return
    list = []
    for ticket in tickets:
        list.append(html_tickets(ticket.get('title'), ticket.get('count')))
    html = ''.join(list)   
    msg = EmailMessage()
    msg['Subject'] = 'Вот ваши билеты!'
    msg['From'] = settings.EMAIL_ADDRESS 
    msg['To'] = email_to 
    msg.set_content(make_html(html), subtype='html')
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(settings.EMAIL_ADDRESS, settings.EMAIL_PASSWORD) 
        smtp.send_message(msg)
        return Response(status=status.HTTP_200_OK)
    
    
def payment_item_gen(title, price, count):
    return {
        "name": title,
        "unit_amount": {
            "currency_code": "USD",
            "value": price
        },
        "quantity": count
    }


def payment_obj_gen(items, id, amount):
    return {
        "purchase_units": [
            {
                "reference_id": id,
                "description": "Some description",
                "custom_id": id,
                "amount": {
                    "currency_code": 'USD',
                    "value": amount,
                    "breakdown": {
                        "item_total": {
                            "currency_code": "USD",
                            "value": amount
                        }
                    }
                },
                "items": items
            }
        ],
    }

