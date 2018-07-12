import sys
import requests
from datetime import (
    datetime, timedelta
)
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from robobrowser import RoboBrowser


SMTP_ADDRESS = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_EMAIL_ADDRESS = ''
SMTP_EMAIL_PASSWORD = ''

USER_ZABBIX_EMAIL_ADDRESS = ''
USER_ZABBIX_PASSWORD = ''
URL_ZABBIX_SERVER = ''
URL_ZABBIX_API = ''

EMAIL_FROM_STR = ''
GRAPH_WIDTH = 900
GRAPH_HEIGHT = 200
GRAPH_COLOR = '00C800'

def print_green(name):
        """grenn letter"""
        print("\033[92m {}\033[00m".format(name))

def get_body_email():
    try:
        return sys.argv[3]
    except IndexError:
        body_email = """
            <html>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8"> 
                    <body>
                        <p><img src="cid:image1"></p>
                    </body> 
            </html>
        """
        return body_email

def get_subject_email():
    try:
        return sys.argv[2]
    except IndexError:
        return 'teste envio de email de alerta zabbix'
    
def get_email_to():
    try: 
        return sys.argv[1]
    except IndexError: 
        raise 'o email de destino deve ser setado'

def get_item_history(itemid, stime):
    pass

def make_login():
    browser = RoboBrowser(history=True)
    browser.open(URL_ZABBIX_SERVER)
    form_login = browser.get_form(action='')
    form_login['login'] = USER_ZABBIX_EMAIL_ADDRESS
    form_login['password'] = USER_ZABBIX_PASSWORD
    browser.submit_form(form_login)
    return browser if browser.response.status_code == 200 else None 

def get_image():
    url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Star_Wars_Logo.svg/2000px-Star_Wars_Logo.svg.png'
    browser = RoboBrowser(history=True)
    browser.open(url)
    return browser.response.content

def get_graph_image(item_id, item_name, period, stime, color):
    browser = make_login()
    if browser:
        url_image = URL_ZABBIX_SERVER + "chart3.php?name={0}&period={1}&width={2}&height={3}&stime={4}&items[0][itemid]={5}&items[0][drawtype]=5&items[0][color]={6}"\
        .format(item_name, 3600, GRAPH_WIDTH, GRAPH_HEIGHT, stime, item_id, GRAPH_COLOR)
        browser.open(url_image)
        image_data = browser.response.content 
        return image_data
    return None


def mount_email_message():
    args = [
        1,
        'MEMORIA DISPONIVEL', 
        3600,
        (datetime.now() - timedelta(hours=1)).strftime('%Y%m%d%H%M%S%f'),
        '00C800'
    ]
    
    image = get_image()

    if image:
        msg_root = MIMEMultipart('related')
        msg_root['Subject'] = get_subject_email()
        msg_root['From'] = EMAIL_FROM_STR
        msg_root['To'] = get_email_to()
        msg_root.preamble = 'This is a multi-part message in MIME format.'

        msg_alternative = MIMEMultipart('alternative')
        msg_root.attach(msg_alternative)
        body_email = MIMEText(get_body_email(), 'html')
        msg_alternative.attach(body_email) 
        
        msg_image = MIMEImage(image)
        msg_image.add_header('Content-ID', '<image1>')
        msg_root.attach(msg_image)
        return msg_root.as_string() 
    return None

def send_alert_email():
    import smtplib 
    email_to = get_email_to()
    server = smtplib.SMTP(SMTP_ADDRESS, SMTP_PORT)
    server.ehlo()
    server.starttls()
    server.login(SMTP_EMAIL_ADDRESS, SMTP_EMAIL_PASSWORD)
    server.sendmail(EMAIL_FROM_STR, email_to, mount_email_message())
    server.close()
    print_green('OK')

if __name__ == '__main__':
    send_alert_email()