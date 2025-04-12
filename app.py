# Citation for Flask starter app
# Date retrieved: August 2024
# Adapted from source URL: https://github.com/osu-cs340-ecampus/flask-starter-app

import os
from dotenv import load_dotenv
from flask import redirect, render_template, request, Flask
from flask_mysqldb import MySQL

# configuration

load_dotenv('.env')

app = Flask(__name__)

app.config['MYSQL_HOST'] = os.getenv('DB_HOST')
app.config['MYSQL_USER'] = os.getenv('DB_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PW')
app.config['MYSQL_DB'] = os.getenv('DB_NAME')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# routes 

@app.route('/')
def home():
    return render_template('home.j2')

@app.route('/reload', methods=['POST'])
def reload():
    cur = mysql.connection.cursor()

    with open('database/DDL.sql') as f:
        commands = f.read()
        for cmd in commands.split(';'):
            if cmd.strip():
                cur.execute(cmd)
    
    mysql.connection.commit()

    return redirect('/')

@app.route('/service-categories', methods=['POST', 'GET'])
def service_categories():
    if request.method == 'POST':
        service_category = request.form['serviceCategory']
        category_description = request.form['categoryDescription']
        query = """
            INSERT INTO ServiceCategories (name, description)
            VALUES (%s, %s);
        """

        try:
            cur = mysql.connection.cursor()
            cur.execute(query, (service_category, category_description))
            mysql.connection.commit()
        except mysql.connection.IntegrityError as err:
            return render_template('errors.j2', err_code=err.args[0], err_msg=err.args[1], page_name='Service Categories')

        return redirect('/service-categories')

    elif request.method == 'GET':
        query = """
            SELECT service_category_id, name, description 
            FROM ServiceCategories
            ORDER BY service_category_id ASC;
        """
        
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()
        
        return render_template('service-categories.j2', data=data)

@app.route('/services', methods=['POST', 'GET'])
def services():
    if request.method == 'POST':
        service = request.form['service']
        service_description = request.form['serviceDescription']
        service_category_id = request.form['idFromServiceCategory'] if request.form['idFromServiceCategory'] else None
        query = """
            INSERT INTO Services (name, description, service_category_id)
            VALUES (%s, %s, %s);
        """

        try:
            cur = mysql.connection.cursor()
            cur.execute(query, (service, service_description, service_category_id))
            mysql.connection.commit()
        except mysql.connection.IntegrityError as err:
            return render_template('errors.j2', err_code=err.args[0], err_msg=err.args[1], page_name='Services')

        return redirect('/services')
        
    elif request.method == 'GET':
        query = """
            SELECT Services.service_id, 
            Services.name, 
            Services.description, 
            ServiceCategories.name, 
            MIN(RequestServices.request_service_id) AS request_service_id
            FROM Services
            LEFT JOIN ServiceCategories ON Services.service_category_id = ServiceCategories.service_category_id
            LEFT JOIN RequestServices ON Services.service_id = RequestServices.service_id
            GROUP BY Services.service_id
            ORDER BY Services.service_id ASC;
        """
        
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()

        service_categories_query = """
            SELECT service_category_id, name
            FROM ServiceCategories
            ORDER BY service_category_id ASC;
        """
        cur = mysql.connection.cursor()
        cur.execute(service_categories_query)
        service_categories_data = cur.fetchall()

        return render_template('services.j2', data=data, service_categories_data=service_categories_data)

@app.route('/customers', methods=['POST', 'GET'])
def customers():
    if request.method == 'POST':
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        address = request.form['address']
        phone = request.form['phone']
        email = request.form['email']
        query = """
            INSERT INTO Customers (first_name, last_name, address, phone, email)
            VALUES (%s, %s, %s, %s, %s);
        """

        try:
            cur = mysql.connection.cursor()
            cur.execute(query, (first_name, last_name, address, phone, email))
            mysql.connection.commit()
        except mysql.connection.IntegrityError as err:
            return render_template('errors.j2', err_code=err.args[0], err_msg=err.args[1], page_name='Customers')

        return redirect('/customers')

    elif request.method == 'GET':
        query = """
            SELECT customer_id, first_name, last_name, address, phone, email
            FROM Customers
            ORDER BY customer_id ASC;
        """
        
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()

        return render_template('customers.j2', data=data)

@app.route('/requests', methods=['POST', 'GET'])
def requests():
    if request.method == 'POST':
        request_date = request.form['requestDate']
        completion_date = request.form['completionDate'] if request.form['completionDate'] else None
        customer_id = request.form['idFromCustomer'] if request.form['idFromCustomer'] else None
        query = """
            INSERT INTO Requests (request_date, completion_date, customer_id)
            VALUES (%s, %s, %s);
        """

        try:
            cur = mysql.connection.cursor()
            cur.execute(query, (request_date, completion_date, customer_id))
            mysql.connection.commit()
        except mysql.connection.IntegrityError as err:
            return render_template('errors.j2', err_code=err.args[0], err_msg=err.args[1], page_name='Requests')

        return redirect('/requests')

    elif request.method == 'GET':
        query = """
            SELECT Requests.request_id, 
            Requests.request_date, 
            Requests.completion_date, 
            CONCAT(Customers.first_name, ' ', Customers.last_name) AS full_name, 
            Payments.date,
            MIN(RequestServices.request_service_id) AS request_service_id
            FROM Requests
            LEFT JOIN Customers ON Requests.customer_id = Customers.customer_id
            LEFT JOIN Payments ON Requests.payment_id = Payments.payment_id
            LEFT JOIN RequestServices ON Requests.request_id = RequestServices.request_id
            GROUP BY Requests.request_id
            ORDER BY Requests.request_id ASC;
        """
        
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()

        customers_query = """
            SELECT customer_id, CONCAT(first_name, ' ', last_name) AS full_name
            FROM Customers
            ORDER BY customer_id ASC;
        """
        cur = mysql.connection.cursor()
        cur.execute(customers_query)
        customers_data = cur.fetchall()

        return render_template('requests.j2', data=data, customers_data=customers_data)

@app.route('/requested-services', methods=['POST', 'GET'])
def requested_services():
    if request.method == 'POST':
        request_id = request.form['idFromRequestInfo']
        service_id = request.form['idFromService'] if request.form['idFromService'] else None
        quotation_price = request.form['quotationPrice']
        query = """
            INSERT INTO RequestServices (request_id, service_id, quotation_price)
            VALUES (%s, %s, %s);
        """

        payments_query = """
            UPDATE Payments
            SET amount = (
                SELECT SUM(RequestServices.quotation_price)
                FROM RequestServices
                WHERE RequestServices.request_id = %s
                GROUP BY RequestServices.request_id
            )
            WHERE payment_id = %s;
        """

        try:
            cur = mysql.connection.cursor()
            cur.execute(query, (request_id, service_id, quotation_price))
            cur.execute(payments_query, (request_id, request_id))
            mysql.connection.commit()
        except mysql.connection.IntegrityError as err:
            return render_template('errors.j2', err_code=err.args[0], err_msg=err.args[1], page_name='Requested Services')

        return redirect('/requested-services')

    elif request.method == 'GET':
        query = """
            SELECT RequestServices.request_service_id,
            IFNULL(CONCAT(Requests.request_date, ', ', Customers.first_name, ' ', Customers.last_name), CONCAT(Requests.request_date, ', None')) AS request_info,
            Services.name,
            RequestServices.quotation_price
            FROM RequestServices
            LEFT JOIN Requests ON RequestServices.request_id = Requests.request_id
            LEFT JOIN Services ON RequestServices.service_id = Services.service_id
            LEFT JOIN Customers ON Requests.customer_id = Customers.customer_id
            ORDER BY RequestServices.request_service_id ASC;
        """
        
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()

        requests_query = """
            SELECT Requests.request_id,
            IFNULL(CONCAT(Requests.request_date, ', ', Customers.first_name, ' ', Customers.last_name), CONCAT(Requests.request_date, ', None')) AS request_info
            FROM Requests
            LEFT JOIN Customers ON Requests.customer_id = Customers.customer_id
            ORDER BY Requests.request_id ASC;
        """

        cur = mysql.connection.cursor()
        cur.execute(requests_query)
        requests_data = cur.fetchall()

        services_query = """
            SELECT Services.service_id, Services.name
            FROM Services
            ORDER BY Services.service_id ASC;
        """

        cur = mysql.connection.cursor()
        cur.execute(services_query)
        services_data = cur.fetchall()

        return render_template('requested-services.j2', data=data, requests_data=requests_data, services_data=services_data)

@app.route('/payments', methods=['POST', 'GET'])
def payments():
    if request.method == 'POST':
        request_id = request.form['idFromRequestInfo']
        date = request.form['paymentDate']
        query = """
            INSERT INTO Payments (payment_id, date, amount)
            VALUES (%s, %s, IFNULL((
                    SELECT SUM(RequestServices.quotation_price) AS amount
                    FROM RequestServices
                    WHERE RequestServices.request_id = %s
                    GROUP BY RequestServices.request_id
                ), 0.00)
            );
        """

        requests_query = """
            UPDATE Requests
            SET payment_id = %s
            WHERE request_id = %s;
        """

        try:
            cur = mysql.connection.cursor()
            cur.execute(query, (request_id, date, request_id))
            cur.execute(requests_query, (request_id, request_id))
            mysql.connection.commit()
        except mysql.connection.IntegrityError as err:
            return render_template('errors.j2', err_code=err.args[0], err_msg=err.args[1], page_name='Payments')

        return redirect('/payments')

    elif request.method == 'GET':
        query = """
            SELECT Payments.payment_id,
            Requests.request_id,
            IFNULL(CONCAT(Requests.request_date, ', ', Customers.first_name, ' ', Customers.last_name), CONCAT(Requests.request_date, ', None')) AS request_info, 
            Payments.date, 
            Payments.amount
            FROM Payments
            LEFT JOIN Requests ON Payments.payment_id = Requests.payment_id
            LEFT JOIN Customers ON Requests.customer_id = Customers.customer_id
            ORDER BY Payments.payment_id ASC;
        """
        
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()

        requests_query = """
            SELECT Requests.request_id,
            IFNULL(CONCAT(Requests.request_date, ', ', Customers.first_name, ' ', Customers.last_name), CONCAT(Requests.request_date, ', None')) AS request_info
            FROM Requests
            LEFT JOIN Customers ON Requests.customer_id = Customers.customer_id
            WHERE Requests.completion_date is NOT NULL AND Requests.payment_id is NULL
            ORDER BY Requests.request_id ASC;
        """

        cur = mysql.connection.cursor()
        cur.execute(requests_query)
        requests_data = cur.fetchall()

        return render_template('payments.j2', data=data, requests_data=requests_data)

@app.route('/update-service-categories', methods=['POST'])
def update_service_categories():
    id = request.form['idFromServiceCategory']
    category_description = request.form['categoryDescription']
    query = """
        UPDATE ServiceCategories
        SET description = %s
        WHERE service_category_id = %s;
    """

    cur = mysql.connection.cursor()
    cur.execute(query, (category_description, id))
    mysql.connection.commit()

    return redirect('/service-categories')

@app.route('/update-services', methods=['POST'])
def update_services():
    id = request.form['idFromService']
    service_description = request.form['serviceDescription']
    service_category_id = request.form['idFromServiceCategory'] if request.form['idFromServiceCategory'] else None
    query = """
        UPDATE Services
        SET description = %s, service_category_id = %s
        WHERE service_id = %s;
    """

    cur = mysql.connection.cursor()
    cur.execute(query, (service_description, service_category_id, id))
    mysql.connection.commit()

    return redirect('/services')

@app.route('/update-customers', methods=['POST'])
def update_customers():
    id = request.form['idFromCustomer']
    address = request.form['address']
    phone = request.form['phone']
    email = request.form['email']
    query = """
        UPDATE Customers
        SET address = %s, phone = %s, email = %s
        WHERE customer_id = %s;
    """

    try:
        cur = mysql.connection.cursor()
        cur.execute(query, (address, phone, email, id))
        mysql.connection.commit()
    except mysql.connection.IntegrityError as err:
        return render_template('errors.j2', err_code=err.args[0], err_msg=err.args[1], page_name='Customers')

    return redirect('/customers')

@app.route('/update-requests', methods=['POST'])
def update_requests():
    id = request.form['idFromRequest']
    completion_date = request.form['completionDate'] if  request.form['completionDate'] else None
    customer_id = request.form['idFromCustomer'] if request.form['idFromCustomer'] else None
    query = """
    UPDATE Requests
    SET completion_date = %s, customer_id = %s
    WHERE request_id = %s;
    """

    cur = mysql.connection.cursor()
    cur.execute(query, (completion_date, customer_id, id))
    mysql.connection.commit()

    return redirect('/requests')

@app.route('/update-requested-services', methods=['POST'])
def update_requested_services():
    id = request.form['idFromRequestService']
    service_id = request.form['idFromService']
    quotation_price = request.form['quotationPrice']
    query = """
        UPDATE RequestServices
        SET service_id = %s, quotation_price = %s
        WHERE request_service_id = %s;
    """
    payments_query = """
        UPDATE Payments
        SET amount = (
            SELECT SUM(RequestServices.quotation_price)
            FROM RequestServices
            WHERE RequestServices.request_id = (SELECT request_id FROM RequestServices WHERE request_service_id = %s)
            GROUP BY RequestServices.request_id
        )
        WHERE payment_id = (
            SELECT request_id 
            FROM RequestServices
            WHERE request_service_id = %s
        );
    """

    try:
        cur = mysql.connection.cursor()
        cur.execute(query, (service_id, quotation_price, id))
        cur.execute(payments_query, (id, id))
        mysql.connection.commit()
    except mysql.connection.IntegrityError as err:
        return render_template('errors.j2', err_code=err.args[0], err_msg=err.args[1], page_name='Requested Services')

    return redirect('/requested-services')

@app.route('/update-payments', methods=['POST'])
def update_payments():
    request_id = request.form['idFromRequestInfo']
    payment_date = request.form['paymentDate']
    query = """
        UPDATE Payments
        SET date = %s
        WHERE payment_id = %s;
    """

    try:
        cur = mysql.connection.cursor()
        cur.execute(query, (payment_date, request_id))
        mysql.connection.commit()
    except mysql.connection.IntegrityError as err:
        return render_template('errors.j2', err_code=err.args[0], err_msg=err.args[1], page_name='Payments')

    return redirect('/payments')

@app.route('/delete-service-categories/<int:id>')
def delete_service_categories(id):
    query = """
        DELETE FROM ServiceCategories
        WHERE service_category_id = %s;
    """

    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    mysql.connection.commit()

    return redirect('/service-categories')

@app.route('/delete-services/<int:id>')
def delete_services(id):
    query = """
        DELETE FROM Services
        WHERE service_id = %s;
    """

    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    mysql.connection.commit()

    return redirect('/services')

@app.route('/delete-customers/<int:id>')
def delete_customers(id):
    query = """
        DELETE FROM Customers
        WHERE customer_id = %s;
    """

    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    mysql.connection.commit()

    return redirect('/customers')

@app.route('/delete-requests/<int:id>')
def delete_requests(id):
    query = """
        DELETE FROM Requests
        WHERE request_id = %s;
    """

    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    mysql.connection.commit()

    return redirect('/requests')

@app.route('/delete-requested-services/<int:id>', methods=['POST'])
def delete_requested_services(id):
    payments_query = """
        UPDATE Payments
        SET amount = IFNULL((
            SELECT SUM(RequestServices.quotation_price)
            FROM RequestServices
            WHERE RequestServices.request_id = (SELECT request_id FROM RequestServices WHERE request_service_id = %s)
            AND RequestServices.request_service_id != %s
            GROUP BY RequestServices.request_id
        ), 0.00)
        WHERE payment_id = (
            SELECT request_id
            FROM RequestServices
            WHERE request_service_id = %s
        );
    """
    query = """
        DELETE FROM RequestServices
        WHERE request_service_id = %s;
    """

    cur = mysql.connection.cursor()
    cur.execute(payments_query, (id, id, id))
    cur.execute(query, (id,))
    mysql.connection.commit()

    return redirect('/requested-services')

@app.route('/delete-payments/<int:id>')
def delete_payments(id):
    query = """
        DELETE FROM Payments
        WHERE payment_id = %s;
    """

    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    mysql.connection.commit()

    return redirect('/payments')

# listener

if __name__ == '__main__':
    port = os.getenv('PORT')
    
    app.run(port=port, debug=True)