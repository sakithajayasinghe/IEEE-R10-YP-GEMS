from collections import namedtuple
import configparser
from datetime import datetime
import json
import secrets
import socket
from flask import Flask, render_template,request, jsonify
import logging
import psycopg2
import flask
from pydantic import BaseModel

logging.basicConfig(filename='logs/INFO.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(filename='logs/DEBUG.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(filename='logs/WARNING.log', level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(filename='logs/ERROR.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(filename='logs/CRITICAL.log', level=logging.CRITICAL, format='%(asctime)s - %(levelname)s - %(message)s')
PORT = 4242
app = Flask(__name__)

class InviteRequest(BaseModel):
    name: str
    email: str
    telephone_no: str
    second_email: str = None
    organization_name: str = None
    role_in_organization: str = None
    validity: str = None
    unique_id: str = None

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
           return render_template('login.html')
  

@app.route('/submit_invite', methods=['POST'])
def send_invitation():
    post_request_data = request.form
    logging.debug(f'POST Request received {post_request_data}')
    invitee_data = InviteRequest(name=post_request_data['Name'],email=post_request_data['Email'],\
                            telephone_no=post_request_data['TelephoneNumber'],\
                            second_email=post_request_data['SecondEmail'],\
                            organization_name=post_request_data['OrgName'],\
                            role_in_organization=post_request_data['Role'],\
                            validity=post_request_data['ValidTill'])

    validity = datetime.strptime(post_request_data['ValidTill'], '%Y-%m-%d')\
          if post_request_data['ValidTill'] else None

    unique_id = secrets.token_hex(12)
    

    try:

        cursor = connection.cursor()
        cursor.execute("INSERT INTO invite_requests (name,email,telephone_no,second_email,\
                       organization_name ,role_in_organization,validity,unique_id) \
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", \
                        (invitee_data.name, invitee_data.email, invitee_data.telephone_no, \
                        invitee_data.second_email, invitee_data.organization_name, \
                        invitee_data.role_in_organization, validity, unique_id))
        connection.commit()
        
    except psycopg2.Error as e:
        logging.error(f"Error inserting data into database: {e}")
    finally:
        cursor.close()

    server_ip = get_server_ip()
    url = (f'http://{server_ip}:{PORT}/signup/{unique_id}')
    return jsonify({'unique_id': unique_id, 'signupURL':url}),200

@app.route('/signup/<unique_id>', methods=['GET', 'POST'])
def signup(unique_id):

    credentials_status = check_credentials(connection=connection, placeholder1='email',\
                                           placeholder2='unique_id', placeholder3= unique_id)
    if not credentials_status:
        return 'not a valid user',404
    
    
    return render_template('password_reset.html')
    

@app.route('/reset_password', methods=['POST'])
def reset_password():
    if request.method == 'POST':
        password = request.form.get('password')
        u_id = request.form.get('unique_id')
        
        try:

            cursor = connection.cursor()
            cursor.execute(f"UPDATE invite_requests SET password = \
                           '{password}' WHERE unique_id = '{u_id}'")
            connection.commit()
            
        except psycopg2.Error as e:
            print(f"Error creating table: {e}")
        finally:
            cursor.close()
        
    return '200 OK',200

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')
    
@app.route('/login_validate', methods=['POST'])
def login_validate():
    if request.method == 'POST':
        user_email = request.form.get('useremail')
        user_password = request.form.get('userpassword')
        
        
        credentials_status = check_credentials(connection=connection, placeholder1='password',
                                                placeholder2='email', placeholder3=user_email)

        if credentials_status[0] is not None and user_password == credentials_status[0]:
            
            user_details = check_credentials(connection=connection,\
                                            placeholder1='name,email,telephone_no,\
                                                second_email,organization_name,\
                                                role_in_organization,validity,unique_id',
                                            placeholder2='email', placeholder3=user_email)

            user_details_dict = details_to_dict(user_details=user_details)
            return jsonify(user_details_dict),200
        else:
            
            return jsonify({'response': 'Invalid email or password'}),404

@app.route('/get_edited_user_details', methods=['POST'])
def get_edited_user_details():
    post_request_data = request.form

    invitee_data = InviteRequest(
        name=post_request_data['Name'],
        email=post_request_data['Email'],
        telephone_no=post_request_data['TelephoneNumber'],
        second_email=post_request_data['SecondEmail'],
        organization_name=post_request_data['OrgName'],
        role_in_organization=post_request_data['Role'],
        unique_id=post_request_data['UniqueId']
    )

    cursor = connection.cursor()
    cursor.execute("UPDATE invite_requests SET name = %s, email = %s, telephone_no = %s,\
                    second_email = %s, organization_name = %s, role_in_organization = %s \
                    WHERE unique_id = %s",
                    (invitee_data.name, invitee_data.email, invitee_data.telephone_no,
                    invitee_data.second_email, invitee_data.organization_name,
                    invitee_data.role_in_organization, invitee_data.unique_id))

    connection.commit()
    cursor.close()

    return jsonify({'status': 'DATA UPDATED COMPLETED'})

@app.route('/logout', methods=['GET'])
def logout():
    return jsonify({'status':'Logged Out'})


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
        )

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_unique_id ON invite_requests (unique_id);
        """)
        logging.info('Table creation successful.')
    
        connection.commit()
    except psycopg2.Error as e:
        logging.error(f"Error creating table: {e}")
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
        logging.info(f"Local IP address: {ip_address}")
        return ip_address
    except Exception as e:
        logging.error(f"Error: {e}") 
        return None

def check_credentials(connection, placeholder1, placeholder2, placeholder3):
    try:
        cursor = connection.cursor()
        cursor.execute(f"SELECT {placeholder1} FROM invite_requests WHERE \
                       {placeholder2} = '{placeholder3}'")
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return row
    
    except psycopg2.Error as e:
        logging.error(f"Error executing SQL query: {e}")
    finally:
        cursor.close()

def details_to_dict(user_details):
    return {
        'name':user_details[0],
        'email':user_details[1],
        'telephone_no':user_details[2],
        'second_email':user_details[3],
        'organization_name':user_details[4],
        'role_in_organization':user_details[5],
        'validity':user_details[6],
        'unique_id':user_details[7]
    }

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('conf/config.ini')
    connection = connect_to_db(config=config)
    create_table(connection=connection)
    app.run(debug=True, host='0.0.0.0', port=PORT)
