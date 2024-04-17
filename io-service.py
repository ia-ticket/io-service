from flask import Flask, request, jsonify
import psycopg2


app = Flask(__name__)
conn = psycopg2.connect(dbname='ticketing_app_db', user='admin', password='admin', host='db', port='5432')

@app.route('/ticket', methods=['POST'])
def create_ticket():
    data = request.json
    show_id = data.get('show_id')
    costumer_id = data.get('costumer_id')
    place_number = data.get('place_number')
    ticket_status = data.get('ticket_status')
    price = data.get('price')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tickets (show_id, costumer_id, place_number, ticket_status, price) VALUES (%s, %s, %s, %s, %s) RETURNING ticket_id", 
                   (show_id, costumer_id, place_number, ticket_status, price))
    ticket_id = cursor.fetchone()[0]
    
    if ticket_status == 'available':
        cursor.execute("UPDATE shows SET inventory = inventory + 1 WHERE show_id = %s", (show_id,))

    conn.commit()
    cursor.close()
    return jsonify({'ticket_id': ticket_id})


@app.route('/ticket', methods=['GET'])
def get_ticket():
    data = request.json
    ticket_id = data.get('ticket_id')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE ticket_id = %s", (ticket_id,))
    ticket = cursor.fetchone()
    cursor.close()
    return jsonify({
        'ticket_id': ticket[0],
        'show_id': ticket[1],
        'costumer_id': ticket[2],
        'place_number': ticket[3],
        'ticket_status': ticket[4],
        'price': ticket[5]
    })

@app.route('/ticket-price', methods=['PUT'])
def update_ticket_price():
    data = request.json
    ticket_id = data.get('ticket_id')
    price = data.get('price')
    cursor = conn.cursor()
    cursor.execute("UPDATE tickets SET price = %s WHERE ticket_id = %s RETURNING ticket_id, show_id, costumer_id, place_number, ticket_status, price",
                   (price, ticket_id))
    ticket = cursor.fetchone()
    conn.commit()
    cursor.close()
    return jsonify({
        'ticket_id': ticket[0],
        'show_id': ticket[1],
        'costumer_id': ticket[2],
        'place_number': ticket[3],
        'ticket_status': ticket[4],
        'price': ticket[5]
    })

@app.route('/ticket-status', methods=['PUT'])
def update_ticket_status():
    data = request.json
    ticket_id = data.get('ticket_id')
    ticket_status = data.get('ticket_status')
    cursor = conn.cursor()
    cursor.execute("UPDATE tickets SET ticket_status = %s WHERE ticket_id = %s RETURNING ticket_id, show_id, costumer_id, place_number, ticket_status, price",
                   (ticket_status, ticket_id))
    ticket = cursor.fetchone()

    if ticket_status == 'sold':
        show_id = ticket[1]
        cursor.execute("UPDATE shows SET inventory = inventory - 1 WHERE show_id = %s", (show_id,))

    conn.commit()
    cursor.close()
    return jsonify({
        'ticket_id': ticket[0],
        'show_id': ticket[1],
        'costumer_id': ticket[2],
        'place_number': ticket[3],
        'ticket_status': ticket[4],
        'price': ticket[5]
    })

@app.route('/shows', methods=['GET'])
def get_shows():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shows")
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
