from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from werkzeug.utils import secure_filename
import os, datetime
from helper.middleware import Middleware
from helper.action_method import PaymentMethod, UserMethod, ClientMethod, StatusMethod
management_app = Blueprint('management_app', __name__, static_folder=os.getenv('STATIC_FOLDER'))

upload_path = os.getenv('PATH_UPLOAD')
middleware = Middleware()
paymentMethod = PaymentMethod()
userMethod = UserMethod()
clientMethod = ClientMethod()
statusMethod = StatusMethod()

@management_app.route('/')
def main():
    if middleware.is_login() == False:
        return redirect(url_for('login'))
    data = paymentMethod.fetchPayment({
        'user_id': session.get('id')
    })

    transaction_data = paymentMethod.historyPaymentWeek({
        'user_id': session.get('id')
    })

    sum_transaction_data = paymentMethod.historyPaymentMonthly({
        'user_id': session.get('id')
    })
    sum_transaction = []
    for x in sum_transaction_data:
        sum_transaction.append(x.get('amount'))
    sum_clean_data = sum(sum_transaction)

    return render_template("admin/index.html", data=data, transaction_data = transaction_data, sum_clean_data = sum_clean_data)

@management_app.route('/account-settings', methods=['POST', 'GET'])
def account_management():
    if middleware.is_login() == False:
        return redirect(url_for('login'))
    if request.method == "POST":
        if 'new_image' not in request.files:
            flash('No File part')
            return redirect(request.url)
        file = request.files['new_image']
        path = session.get('profile_picture')
        if file.filename != '':
            filename = secure_filename(file.filename)
            path = os.path.join(upload_path, filename)
            file.save(os.path.join('.{}'.format(upload_path), filename))
            try:
                os.remove(".{}".format(session.get('profile_picture')))
            except FileNotFoundError:
                pass
        input_data = {
            "user_id": session.get('id'),
            "old_username": session.get('username'),
            "username": request.form['username'],
            "new_password": request.form['new_password'],
            "profile_picture": path
        }
        new_data = userMethod.editUserById(input_data)
        if new_data != False:
            session['username'] = new_data[1]
            session['profile_picture'] = new_data[4]
            return redirect(url_for('management_app.main'))
        return False
    
    data = userMethod.fetchUserById({
        'user_id': session.get('id')
    })
    return render_template("admin/account/user.html", data=data)


@management_app.route('/account-settings-delete', methods=['POST'])
def account_management_delete():
    if middleware.is_login() == False:
        return redirect(url_for('login'))
    if request.method == "POST":
        delete_data = userMethod.deleteUserById({
                "user_id": session.get("id")
            })
        if delete_data != False:
            if session.get('profile_picture') != None:
                os.remove(".{}".format(session.get('profile_picture')))
            return redirect(url_for('logout'))
        return redirect(url_for('management_app.main'))
    
@management_app.route('/queue-management', methods=['GET'])
def queue_management():
    if middleware.is_login() == False:
        return redirect(url_for('login'))
    data = paymentMethod.fetchAllPayment({
        'user_id': session.get('id'),
        'status': 'unpaid'
    })
    return render_template('admin/table/page_table.html', data = data)

@management_app.route('/queue-management-add', methods=['GET', 'POST'])
def queue_management_add():
    if middleware.is_login() == False:
        return redirect(url_for('login'))
    
    row_client_data = clientMethod.fetchAllClient()
    if request.method == "POST":
        status_inp = True

        date_in = request.form['dateline']
        date_processing = date_in.replace('T', '-').replace(':', '-').split('-')
        date_processing = [int(v) for v in date_processing]
        date_out = datetime.datetime(*date_processing)

        input_data = {
            "title": request.form['title_payment'],
            "client_id": request.form['client'],
            "user_id": session.get('id'),
            "dateline": str(date_out),
            "amount": request.form['amount'],
            "status": 1003
        }
        for x in input_data.values():
            if x == '':
                status_inp = False
        
        if status_inp != False:
            print(input_data)
            paymentMethod.insertPayment(input_data)

        return redirect(url_for('management_app.queue_management'))
    

    return render_template('admin/table/page_table_manage.html', client_data = row_client_data)

  
@management_app.route('/queue-management-pay/<id_transaction>', methods=['GET', 'POST'])
def queue_management_pay(id_transaction):
    if middleware.is_login() == False:
        return redirect(url_for('login'))
    paymentMethod.actionPayment({
        "status": "pay",
        "user_id": session.get('id'),
        "transaction_id": id_transaction
    })
    return redirect(url_for('management_app.main'))

@management_app.route('/queue-management-cancel/<id_transaction>', methods=['GET', 'POST'])
def queue_management_cancel(id_transaction):
    if middleware.is_login() == False:
        return redirect(url_for('login'))
    paymentMethod.actionPayment({
        "status": "cancel",
        "user_id": session.get('id'),
        "transaction_id": id_transaction
    })
    return redirect(url_for('management_app.main'))


@management_app.route('/queue-management-delete/<id_transaction>', methods=['GET', 'POST'])
def queue_management_delete(id_transaction):
    if middleware.is_login() == False:
        return redirect(url_for('login'))
    paymentMethod.deletePayment({
        "status": "cancel",
        "user_id": session.get('id'),
        "transaction_id": id_transaction
    })
    return redirect(url_for('management_app.main'))


@management_app.route('/history-transaction-monthly')
def historyTransaction():
    if middleware.is_login() == False:
        return redirect(url_for('login'))
    
    transaction_data = paymentMethod.historyPaymentMonthly({
        'user_id': session.get('id')
    })

    return render_template('admin/transactions/page_transaction.html', transaction_data=transaction_data )