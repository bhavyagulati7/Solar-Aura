from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, abort
from flaskext.mysql import MySQL
import stripe

app = Flask(__name__)

app.config['SECRET_KEY'] = '8d3c2c136be85cf7de1435eb'  # Replace with a secret key
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'solaraura'

app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51QXQVe01UphHcAEg8hv22DvowBVnowSCeKsZByTIiyEJb5eIEI8n7rcPPURmBiFUVXQofUgzlN8bqDvOOrK7S5bB00Kz5erODR'
app.config['STRIPE_SECRET_KEY'] = 'sk_test_51QXQVe01UphHcAEgEyY1vaUO4n8j5FSmhYSMRrjqMHI1kTnT7b21FAFlOvOTkPu1xspAYDpFgQfoZHiuvLtLUJou00HzGQKvuZ'

stripe.api_key = app.config['STRIPE_SECRET_KEY']

mysql = MySQL(app)

@app.route("/")
@app.route("/home")
def home_page():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''

    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        # Create a cursor using flaskext.mysql
        cursor = mysql.get_db().cursor()

        # Execute the SQL query
        cursor.execute('SELECT * FROM accounts WHERE email = %s AND password = %s', (email, password))

        # Fetch the result
        account = cursor.fetchone()

        if account:
            session['loggedin'] = True
            session['email'] = account[2]  # Assuming email is in the second column
            session['fname'] = account[0]  # Assuming fname is in the third column
            return render_template('home.html')
        else:
            msg = 'Incorrect email/password!'
            cursor.close()

    return render_template('login1.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('email', None)
    session.pop('fname', None)
    return redirect(url_for('home_page'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''

    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        fname = request.form['fname']
        lname = request.form['lname']
        country = request.form.get('country')
        
        cursor = mysql.get_db().cursor()

        cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        else:
            cursor.execute('INSERT INTO accounts (fname, lname, email, country, password) VALUES (%s, %s, %s, %s, %s)', (fname, lname, email, country, password))
            mysql.get_db().commit()
            
            msg = 'You have successfully registered!'
            
            cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
            account = cursor.fetchone()
            
            if account:
                session['loggedin'] = True
                session['email'] = email
                session['fname'] = fname
                msg = 'Logged in successfully!'
                return render_template('home.html', msg=msg)

    elif request.method == 'POST':
        msg = 'Please fill out the form!'

    return render_template('register1.html', msg=msg)

@app.route('/about')
def about():
	return render_template('aboutus.html')

@app.route('/commercial', methods=['GET', 'POST'])
def commercial():
    if request.method == 'POST' and 'bizName' in request.form:
        bizName = request.form['bizName']
        contactName = request.form['contactName']
        bizType = request.form['bizType']
        phone = request.form['phone']
        energy = request.form['energy']
        roofArea = request.form['roofArea']
        address = request.form['address']
        comments = request.form['comments']
        latitude = request.form['latitude']
        longitude = request.form['longitude']

        cursor = mysql.get_db().cursor()

        cursor.execute(
            'INSERT INTO commercial (email, bizname, contactname, biztype, phone, energy, roofarea, address, comments, latitude, longitude) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
            (session['email'], bizName, contactName, bizType, phone, energy, roofArea, address, comments, latitude, longitude)
        )
        mysql.get_db().commit()
        return redirect(url_for('payment'))

        # Optional: You can set a success message here
        # msg = 'You have successfully registered!'

    return render_template('commercial.html')

# @app.route('/residential')
# def residential():
#     '''
#     session = stripe.checkout.Session.create(
#         payment_method_types=['card'],
#         line_items=[{
#             'price': 'price_1GtKWtIdX0gthvYPm4fJgrOr',
#             'quantity': 1,
#         }],
#         mode='payment',
#         success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
#         cancel_url=url_for('index', _external=True),
#     )
#     '''
#     return render_template(
#         'residential.html', 
#         #checkout_session_id=session['id'], 
#         #checkout_public_key=app.config['STRIPE_PUBLIC_KEY']
#     )

@app.route('/residential', methods=['GET', 'POST'])
def residential():
    if request.method == 'POST' and 'Name' in request.form:
        name = request.form['Name']
        roofArea = request.form['roofArea']
        electric = request.form['electric']
        phone = request.form['phone']
        address = request.form['address']
        choice = request.form.get('choice')
        latitude = request.form['latitude']
        longitude = request.form['longitude']

        cursor = mysql.get_db().cursor()

        cursor.execute(
            'INSERT INTO residential (email, name, roofarea, electric, phone, address, choice, latitude, longitude) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
            (session['email'], name, roofArea, electric, phone, address, choice, latitude, longitude)
        )
        mysql.get_db().commit()

        # Optional: You can set a success message here
        # msg = 'You have successfully registered!'
        return redirect(url_for('payment'))

    return render_template('residential.html')

@app.route('/payment')
def payment():
    if 'loggedin' in session and session['loggedin']:
        foo=0
        cursor = mysql.get_db().cursor()
        cursor.execute('SELECT * FROM residential WHERE email = %s', (session['email'],))
        res = cursor.fetchone()
        cursor.execute('SELECT * FROM commercial WHERE email = %s', (session['email'],))
        com = cursor.fetchone()
        cursor.close()

        if res:
            foo=1
        elif (com):
            foo=-1
        return render_template('payment.html', foo=foo)


    return render_template('payment.html')
    

@app.route('/stripe_pay')
def stripe_pay():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1NyqstSFPzAEdpQf3AKmu26L',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('residential', _external=True),
    )
    return {
        'checkout_session_id': session['id'], 
        'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
    }

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')

@app.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():
    print('WEBHOOK CALLED')

    if request.content_length > 1024 * 1024:
        print('REQUEST TOO BIG')
        abort(400)
    payload = request.get_data()
    sig_header = request.environ.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = 'YOUR_ENDPOINT_SECRET'
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        print('INVALID PAYLOAD')
        return {}, 400
    except stripe.error.SignatureVerificationError as e:
        print('INVALID SIGNATURE')
        return {}, 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print(session)
        line_items = stripe.checkout.Session.list_line_items(session['id'], limit=1)
        print(line_items['data'][0]['description'])

    return {}

@app.route('/get_location', methods=['POST'])
def get_location():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    location = f"Latitude: {latitude}, Longitude: {longitude}"
    return jsonify({'location': location})

@app.route('/careers')
def careers():
	return render_template('careers.html')

@app.route('/contact')
def contact():
	return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
