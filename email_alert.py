import sys
import requests
from datetime import (
    datetime, 
    timedelta
)
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from robobrowser import RoboBrowser

USER_ZABBIX_EMAIL_ADDRESS = ''  
USER_ZABBIX_PASSWORD = ''
URL_ZABBIX_SERVER = ''
URL_ZABBIX_API = URL_ZABBIX_SERVER + 'api_jsonrpc.php'

EMAIL_FROM_STR = ''
GRAPH_WIDTH = 900
GRAPH_HEIGHT = 200
GRAPH_COLOR = '00C800'

def print_green(name):
        """grenn letter"""
        print("\033[92m {}\033[00m".format(name))

def get_type_by_item_id():
    pass

def make_api_auth():
	"""
		Must return the user token
	"""
	json = {
    		"jsonrpc": "2.0",
    		"method": "user.login",
    		"params": {
        		"user": "{0}".format(USER_ZABBIX_EMAIL_ADDRESS),
        		"password": "{0}".format(USER_ZABBIX_PASSWORD) 
    		},
    		"id": 1,
    		"auth": None
	}
	response = requests.post(URL_ZABBIX_API, json=json)
	return response.json()['result'] if response.status_code == 200 else None 

def make_logout_api():
	json = json = {
                "jsonrpc": "2.0",
                "method": "user.logout",
                "id": 1,
		"params":{}
                "auth": None
        }
	response = requests.post(URL_ZABBIX_API, json=json)
	return response.json()['result'] if response.status_code == 200 else None

def send_event_alert(auth, event_id):
    json = {
		'jsonrpc':'2.0',    
		'method':'event.acknowledge',
		'params': {
			'eventids': event_id,
			'message': "Email enviado com sucesso para {0}".format(sys.argv[1])
		},
		'auth':auth,
		'id':3
	}
    response = requests.post(URL_ZABBIX_API, json=json)    
    return response.json()['result'] if response.status_code == 200 else None 

def get_body_email():
    try:
        return sys.argv[3].split('@')[-1]
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
        return 'teste envio de email de alerta zabbix sem parametros'
    
def get_email_to():
    try: 
        return sys.argv[1]
    except IndexError: 
        raise 'o email de destino deve ser setado'
    
def make_login_by_browser(): 
    from robobrowser.forms.fields import BaseField
    
    browser = RoboBrowser(history=True)
    browser.open(URL_ZABBIX_SERVER)
    form_login = browser.get_form(action='index.php')
    #get the necessary field with id='enter' and add to form fields to be abble submit form 
    button_field_required_to_submit = browser.find(id='enter')
    attrs_button = button_field_required_to_submit.attrs 
    form_login.add_field(BaseField(button_field_required_to_submit))
    
    form_login[attrs_button['id']] = attrs_button['value']
    
    form_login['name'] = USER_ZABBIX_EMAIL_ADDRESS
    form_login['password'] = USER_ZABBIX_PASSWORD
    
    browser.submit_form(form_login)
    return browser if browser.response.status_code == 200 else None 

def get_image_test():
    url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Star_Wars_Logo.svg/2000px-Star_Wars_Logo.svg.png'
    browser = RoboBrowser(history=True)
    browser.open(url)
    return browser.response.content

def get_graph_image(item_name, item_id, period, color, stime):
    browser = make_login_by_browser()
    if browser:
        url_image = URL_ZABBIX_SERVER + "chart3.php?name={0}&period={1}&width={2}&height={3}&stime={4}&items[0][itemid]={5}&items[0][drawtype]=5&items[0][color]={6}"\
        .format(item_name, 3600, GRAPH_WIDTH, GRAPH_HEIGHT, stime, item_id, GRAPH_COLOR)
        browser.open(url_image)
        image_data = browser.response.content 
        return image_data
    return None

def get_history(time, item_id):
    auth = make_api_auth()
    json = {
        "jsonrpc": "2.0",
        "method": "history.get",
        "params": {
            "output": "extend",
            "history": 1,
            "itemids": str(item_id),
            "sortfield": "clock",
            "sortorder": "DESC",
            "limit": 10,
            "time_till":time
        },
        "auth": auth,
        "id": 1
    }
    response = requests.get(URL_ZABBIX_API, json=json)
    return response.json()['result'] if response.status_code == 200 else None

def mount_email_message():
    subject = get_subject_email()
    item_name, _, item_id, color, period = tuple(subject.split('@')[:5])
    stime =  (datetime.now() - timedelta(hours=1)).strftime('%Y%m%d%H%M%S%f')
    history = get_history(stime, item_id)
    image = get_graph_image(item_name, item_id, period, color, stime)

    if image:
        msg_root = MIMEMultipart('related')
        msg_root['Subject'] = get_subject_email()
        msg_root['From'] = EMAIL_FROM_STR
        msg_root['To'] = get_email_to()
        msg_root.preamble = 'This is a multi-part message in MIME format.'

        msg_alternative = MIMEMultipart('alternative')
        msg_root.attach(msg_alternative)
        body_email = MIMEText(get_body_email().format(value_history=history[-1]['value']), 'html')
        msg_alternative.attach(body_email) 
        
        msg_image = MIMEImage(image)
        msg_image.add_header('Content-ID', '<image1>')
        msg_root.attach(msg_image)
        return msg_root.as_string() 
    return None

def connect_smtp_server():
    import smtplib 
    server = smtplib.SMTP()
    server.connect('localhost')
    return server 

if __name__ == '__main__':
    server = connect_smtp_server()
    message = mount_email_message()
    email_to = get_email_to()    
    server.sendmail(EMAIL_FROM_STR, email_to, mount_email_message)
    server.close()
    print_green('OK')
