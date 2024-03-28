from collections import namedtuple
import configparser
import secrets
import socket
from flask import Flask, render_template,request, jsonify
import logging
import psycopg2


# logging.basicConfig(filename='logs/INFO.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.basicConfig(filename='logs/DEBUG.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.basicConfig(filename='logs/WARNING.log', level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.basicConfig(filename='logs/ERROR.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.basicConfig(filename='logs/CRITICAL.log', level=logging.CRITICAL, format='%(asctime)s - %(levelname)s - %(message)s')
PORT = 4242


app = Flask(__name__)

InviteRequest = namedtuple(
    'InviteRequest', ['name','email','telephone_no','second_email',\
                      'organization_name','role_in_organization','validity']
)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/logged-in', methods=['POST'])
def invite():
    if request.method == 'POST':
        login_type = request.form.get('role')
#   logging.info('ROOT URL ACCESSED')
        if login_type == 'admin':
           return render_template('admin_invite.html')
        elif login_type == 'user':
           return 'hi'
  

@app.route('/submit_invite', methods=['POST'])
def send_invitation():
    post_request_data = request.form
#   logging.debug(f'POST Request received {post_request_data}')
    invitee_data = InviteRequest(name=post_request_data['Name'],email=post_request_data['Email'],\
                            telephone_no=post_request_data['TelephoneNumber'],\
                            second_email=post_request_data['SecondEmail'],\
                            organization_name=post_request_data['OrgName'],\
                            role_in_organization=post_request_data['Role'],\
                            validity=post_request_data['ValidTill'])

    unique_id = secrets.token_hex(12)
    

    try:

        cursor = connection.cursor()
        cursor.execute("INSERT INTO invite_requests (name,email,telephone_no,second_email,\
                       organization_name ,role_in_organization,validity,unique_id) \
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", \
                        (invitee_data.name, invitee_data.email, invitee_data.telephone_no, \
                        invitee_data.second_email, invitee_data.organization_name, \
                        invitee_data.role_in_organization, invitee_data.validity, unique_id))
        connection.commit()
        
    except psycopg2.Error as e:
        print(f"Error creating table: {e}")
    finally:
        cursor.close()

    server_ip = get_server_ip()
    url = (f'http://{server_ip}:{PORT}/signup/{unique_id}')
    return jsonify({'unique_id': unique_id, 'signupURL':url}),200

@app.route('/signup/<unique_id>', methods=['GET', 'POST'])
def signup(unique_id):
    credentials_status = check_credentials(connection=connection,unique_id=unique_id)
    if credentials_status == False:
        return 'not a valid user',404
    

    return render_template('password_reset.html')
    


        


def connect_to_db(config):
    try:
        return psycopg2.connect(
            host=config['database']['host'],
            user=config['database']['user'],
            password=config['database']['password'],
            database=config['database']['database']
        )
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

def create_table(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS invite_requests (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255),
        email VARCHAR(255),
        telephone_no VARCHAR(20),
        second_email VARCHAR(255),
        organization_name VARCHAR(255),
        role_in_organization VARCHAR(50),
        validity DATE,
        unique_id VARCHAR(50),
        password VARCHAR(50)              
        );"""
                       ,
        """
        CREATE INDEX idx_unique_id ON invite_requests (unique_id);
        """
        )
        connection.commit()
    except psycopg2.Error as e:
        print(f"Error creating table: {e}")
    finally:
        cursor.close()
    

def get_server_ip():
    try:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Connect to a remote server
        s.connect(("8.8.8.8", 80))

        # Get the local IP address
        ip_address = s.getsockname()[0]

        # Close the socket
        s.close()

        return ip_address
    except Exception as e:
        print(f"Error: {e}")
        return None

def check_credentials(connection, unique_id):
    try:
        cursor = connection.cursor()
        cursor.execute(f"SELECT email FROM invite_requests WHERE unique_id = '{unique_id}'")
        row = cursor.fetchone()
        
        if not row:
            return False
        
        return True
    
    except psycopg2.Error as e:
        print(f"Error creating table: {e}")
    finally:
        cursor.close()


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('../conf/config.ini')
    connection = connect_to_db(config=config)
    create_table(connection=connection)
    app.run(debug=True, host='0.0.0.0', port=PORT)
