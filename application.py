from flask import Flask, render_template, request, send_from_directory
from flask import jsonify
import os
import pandas as pd
import db_handler
import json

template_dir = os.path.abspath('./templates')
application = Flask(__name__, template_folder=template_dir)

@application.route('/')
def index():

    return render_template('index.html')

@application.route('/rsvp')
def rsvp():
    return render_template('rsvp.html')

@application.route('/info')
def info():
    return render_template('info.html')

@application.route('/get_guest/<name>')
def get_guest(name):
    print('G')
    connection = db_handler.create_connection()
    guest_df = pd.read_sql(con=connection, sql="SELECT * FROM guest WHERE name=?", params=(name,))
    connection.close()
    return guest_df.to_json(orient='records')

@application.route('/get_invitation/<id>')
def get_invitation(id):
    print('I')
    connection = db_handler.create_connection()
    invitation_df = pd.read_sql(con=connection, sql="SELECT * FROM invitation WHERE id=?", params=(id,))
    connection.close()
    return invitation_df.to_json(orient='records')

@application.route('/get_guests_for_invitation/<name>')
def get_guests_for_invitation(name):
    connection = db_handler.create_connection()
    guest_df = pd.read_sql(con=connection, sql= "SELECT * FROM guest WHERE invitation=?", params=(name,))
    connection.close()
    return guest_df.to_json(orient='records')


def update_guest(name, attendance, invite):
    connection = db_handler.create_connection()
    cursor = connection.cursor()



    if 'Guest' in name:
        print('Updating the guest!!!')
        sql = "UPDATE guest SET attendance=?, name = ? WHERE name like '%Guest%' and invitation=?"
        cursor.execute(sql, (attendance, name, invite))
    else:
        sql = "UPDATE guest SET attendance=? WHERE name=?"
        cursor.execute(sql, (attendance, name))
    connection.commit()
    connection.close()


def update_invitation(id, accomodation_accepted, phone):
    connection = db_handler.create_connection()
    cursor = connection.cursor()
    sql = "UPDATE invitation SET accommodation_accepted = ?, phone = ?, rsvp = 1 WHERE id=?"
    cursor.execute(sql, (accomodation_accepted, phone, id))
    connection.commit()
    connection.close()


@application.route('/thankyou', methods=['POST'])
def thankyou():
    # Retrieve the guest list data (JSON string)
    guest_list_data = request.form.get('guest_list_data')

    # Retrieve accommodation option
    accommodation = request.form.get('accommodation')
    phone = request.form.get('phone')
    invite_id = request.form.get('invitation_id')

    if guest_list_data:
        # Parse the guest list data (JSON string) into a Python list
        guest_list = json.loads(guest_list_data)


        if accommodation == 'yes':
            accommodation_input = 1
        else:
            accommodation_input = 0

        rsvp = 1

        update_invitation(invite_id, accommodation_input, phone)
        for guest in guest_list:
            print(guest)
            if guest['confirmed'] == True:
                attendance = 1
            else:
                attendance = 0
            update_guest(guest['name'], attendance, invite_id)

    return render_template('thankyou.html')


if __name__ == '__main__':
    application.run(debug=True)