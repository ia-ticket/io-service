from flask import Flask, request, jsonify
import psycopg2
from datetime import datetime


app = Flask(__name__)
conn = psycopg2.connect(
    host='db-io',
    database='ticketing_app_db',
    user='admin',
    password='admin'
)


@app.route('/ticket', methods=['GET'])
def get_ticket():
    data = request.json
    ticket_id = data.get('ticket_id')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE tickets.ticket_id = %s", (ticket_id,))
    ticket = cursor.fetchone()
    cursor.close()
    return jsonify({
        'ticket_id': ticket[0],
        'show_id': ticket[1],
        'costumer_email': ticket[2],
        'place_number': ticket[3],
        'ticket_status': ticket[4],
        'price': ticket[5]
    })


@app.route('/show', methods=['GET'])
def get_show():
    data = request.json
    show_id = data.get('show_id')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shows WHERE show_id = %s", (show_id,))
    show = cursor.fetchone()
    cursor.close()
    return jsonify({
        'show_id': show[0],
        'show_name': show[1],
        'date_and_time': show[2].isoformat(),
        'place': show[3],
        'show_description': show[4],
        'inventory': show[5]
    })


@app.route('/my-tickets', methods=['GET'])
def get_my_tickets():
    costumer_email = request.json.get('email')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE tickets.costumer_email = %s", (costumer_email,))
    tickets = cursor.fetchall()
    cursor.close()

    formatted_tickets = []
    for ticket in tickets:
        ticket_dict = {
            'ticket_id': ticket[0],
            'show_id': ticket[1],
            'costumer_email': ticket[2],
            'place_number': ticket[3],
            'ticket_status': ticket[4],
            'price': ticket[5]
        }
        formatted_tickets.append(ticket_dict)

    return jsonify(formatted_tickets)


@app.route('/costumer-email', methods=['PUT'])
def update_ticket_costumer_email():
    data = request.json
    ticket_id = data.get('ticket_id')
    costumer_email = data.get('email')
    cursor = conn.cursor()
    if costumer_email is not None:
        cursor.execute("UPDATE tickets SET costumer_email = %s WHERE ticket_id = %s RETURNING ticket_id, show_id, costumer_email, place_number, ticket_status, price",
                       (costumer_email, ticket_id))
    else:
        cursor.execute("UPDATE tickets SET costumer_email = NULL WHERE ticket_id = %s RETURNING ticket_id, show_id, costumer_email, place_number, ticket_status, price",
                       (ticket_id,))
    ticket = cursor.fetchone()
    conn.commit()
    cursor.close()
    return jsonify({
        'ticket_id': ticket[0],
        'show_id': ticket[1],
        'costumer_email': ticket[2],
        'place_number': ticket[3],
        'ticket_status': ticket[4],
        'price': ticket[5]
    })


@app.route('/status', methods=['PUT'])
def update_ticket_status():
    data = request.json
    ticket_id = data.get('ticket_id')
    ticket_status = data.get('ticket_status')
    cursor = conn.cursor()
    cursor.execute("UPDATE tickets SET ticket_status = %s WHERE ticket_id = %s RETURNING ticket_id, show_id, costumer_email, place_number, ticket_status, price",
                   (ticket_status, ticket_id))
    ticket = cursor.fetchone()

    if ticket_status == 'sold':
        show_id = ticket[1]
        cursor.execute("UPDATE shows SET inventory = inventory - 1 WHERE show_id = %s", (show_id,))

    if ticket_status == 'available':
        show_id = ticket[1]
        cursor.execute("UPDATE shows SET inventory = inventory + 1 WHERE show_id = %s", (show_id,))

    conn.commit()
    cursor.close()
    return jsonify({
        'ticket_id': ticket[0],
        'show_id': ticket[1],
        'costumer_email': ticket[2],
        'place_number': ticket[3],
        'ticket_status': ticket[4],
        'price': ticket[5]
    })


@app.route('/tickets', methods=['GET'])
def get_tickets():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets")
    tickets = cursor.fetchall()
    cursor.close()

    formatted_tickets = []
    for ticket in tickets:
        ticket_dict = {
            'ticket_id': ticket[0],
            'show_id': ticket[1],
            'costumer_email': ticket[2],
            'place_number': ticket[3],
            'ticket_status': ticket[4],
            'price': ticket[5]
        }
        formatted_tickets.append(ticket_dict)

    return jsonify(formatted_tickets)


@app.route('/tickets-by-show', methods=['GET'])
def get_tickets_by_show():
    show_id = request.json.get('show_id')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE tickets.show_id = %s", (show_id,))
    tickets = cursor.fetchall()
    cursor.close()

    formatted_tickets = []
    for ticket in tickets:
        ticket_dict = {
            'ticket_id': ticket[0],
            'show_id': ticket[1],
            'costumer_email': ticket[2],
            'place_number': ticket[3],
            'ticket_status': ticket[4],
            'price': ticket[5]
        }
        formatted_tickets.append(ticket_dict)

    return jsonify(formatted_tickets)


@app.route('/shows', methods=['GET'])
def get_shows():
    cursor = conn.cursor()
    current_time = datetime.now()
    cursor.execute("SELECT * FROM shows WHERE date_and_time >= %s", (current_time,))
    shows = cursor.fetchall()
    cursor.close()

    formatted_shows = []
    for show in shows:
        show_dict = {
            'show_id': show[0],
            'show_name': show[1],
            'date_and_time': show[2].isoformat(),
            'place': show[3],
            'show_description': show[4],
            'inventory': show[5]
        }
        formatted_shows.append(show_dict)

    return jsonify(formatted_shows)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
