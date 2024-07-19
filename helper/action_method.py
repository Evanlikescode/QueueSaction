from helper.db import db
import uuid

class BaseMethod(object):
    def __init__(self) :
        self.cur = db.cursor()
        self.tableName = {
            "client": "clients",
            "payment": "payments",
            "role": "role",
            "status": "status",
            "user": "users"
        }


class AuthMethod(BaseMethod):
    def login(self, value):
        self.cur.execute(f"SELECT * FROM {self.tableName.get('user')} WHERE username = %s AND password = %s ", 
                         (value.get('username'), value.get('password'), ))
        data = self.cur.fetchone()
        self.cur.close
        if data != None:
            return data
        else:
            return False
    
    def register(self, value):
        self.cur.execute(f"SELECT username FROM {self.tableName.get('user')} WHERE username = %s ", 
                         (value.get('username'), ))
        data = self.cur.fetchone()
        if data == None:
            self.cur.execute(f"INSERT INTO {self.tableName.get('user')} (id, username, password, role) VALUES {f'{uuid.uuid1()}', value.get('username'), value.get('password'), 1002} ")
            db.commit()
            self.cur.execute(f"SELECT * FROM {self.tableName.get('user')} WHERE username = %s AND password = %s ", 
                         (value.get('username'), value.get('password'), ))
            row_data = self.cur.fetchone()
            self.cur.close
            return row_data
        else:
            self.cur.close
            return False
       

class PaymentMethod(BaseMethod):
    def fetchPayment(self, value):
        self.cur.execute(f"SELECT {self.tableName.get('payment')}.*, {self.tableName.get('user')}.username, {self.tableName.get('client')}.username, {self.tableName.get('status')}.title  FROM {self.tableName.get('payment')} JOIN {self.tableName.get('user')} ON {self.tableName.get('payment')}.user_id = {self.tableName.get('user')}.id JOIN {self.tableName.get('client')} ON {self.tableName.get('payment')}.client_id = {self.tableName.get('client')}.id JOIN {self.tableName.get('status')} ON {self.tableName.get('payment')}.status = {self.tableName.get('status')}.id  WHERE {self.tableName.get('payment')}.user_id = %s AND ({self.tableName.get('payment')}.dateline BETWEEN CURDATE() AND CURDATE() + INTERVAL 5 DAY) AND {self.tableName.get('payment')}.status = 1003  ", (value.get('user_id')))
        data = self.cur.fetchall()
        self.cur.close
        if data != None:
            lists = []
            for x in data:
                lists.append({
                    "id": x[0],
                    "title_payment": x[1],
                    "client_id": x[2],
                    "user_id": x[3],
                    "dateline": x[4],
                    "amount": x[5],
                    "status": x[6],
                    "user_name": x[9],
                    "client_name": x[10],
                    "status_name": x[11]
                })
            for i in range(int(len(lists) / 2)):
                lists.pop()
            print(lists)
            return lists
        return False
    
    def fetchAllPayment(self, value):
        status = 1003
        if value.get('status') == 'paid':
            status = 1001
        elif value.get('status') == 'cancelled':
            status = 1002
        self.cur.execute(f"SELECT {self.tableName.get('payment')}.*, {self.tableName.get('user')}.username, {self.tableName.get('client')}.username, {self.tableName.get('status')}.title FROM {self.tableName.get('payment')} JOIN {self.tableName.get('user')} ON {self.tableName.get('payment')}.user_id = {self.tableName.get('user')}.id JOIN {self.tableName.get('client')} ON {self.tableName.get('payment')}.client_id = {self.tableName.get('client')}.id JOIN {self.tableName.get('status')} ON {self.tableName.get('payment')}.status = {self.tableName.get('status')}.id  WHERE {self.tableName.get('payment')}.user_id = %s  AND {self.tableName.get('payment')}.status = %s ORDER BY {self.tableName.get('payment')}.dateline ASC  ", (value.get('user_id'), status))
        data = self.cur.fetchall()
        self.cur.close
        if data != None:
            lists = []
            for x in data:
                lists.append({
                    "id": x[0],
                    "title_payment": x[1],
                    "client_id": x[2],
                    "user_id": x[3],
                    "dateline": str(x[4]),
                    "amount": x[5],
                    "status": x[6],
                    "user_name": x[9],
                    "client_name": x[10],
                    "status_name": x[11]
                })
            return lists
        return False
    
    def insertPayment(self, value):
        self.cur.execute(f"INSERT INTO {self.tableName.get('payment')} (title_payment, client_id, user_id, dateline, amount, status) VALUES {value.get('title'), value.get('client_id'), value.get('user_id'), value.get('dateline'), value.get('amount'), value.get('status')} ")
        db.commit()
        self.cur.close
        return True
    
    def deletePayment(self, value):
        self.cur.execute(f"DELETE FROM {self.tableName.get('payment')} WHERE id = %s AND user_id = %s ", (value.get('transaction_id'), value.get('user_id'), ))
        db.commit()
        self.cur.close
        return True
    
    def historyPaymentWeek(self, value):
        self.cur.execute(f"SELECT title_payment, amount FROM {self.tableName.get('payment')} WHERE user_id = %s AND status = 1001 AND updated_at >= DATE_SUB(CURDATE(), INTERVAL 1 WEEK) LIMIT 10", (value.get('user_id'),))
        data = self.cur.fetchall()
        self.cur.close
        if data != None:
            lists = []
            for x in data:
                lists.append({
                    'title_payment': x[0],
                    'amount': x[1]
                })
            return lists
        return False

    def historyPaymentMonthly(self, value):
        self.cur.execute(f"SELECT title_payment, amount FROM {self.tableName.get('payment')} WHERE user_id = %s AND status = 1001 AND updated_at >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)", (value.get('user_id'),))
        data = self.cur.fetchall()
        self.cur.close
        if data != None:
            lists = []
            for x in data:
                lists.append({
                    'title_payment': x[0],
                    'amount': x[1]
                })
            return lists
        return False


    def actionPayment(self, value):
        status = 1001
        if value.get('status').lower() == "cancel":
            status = 1002
        self.cur.execute(f"UPDATE {self.tableName.get('payment')} SET status = %s WHERE id = %s AND user_id = %s", (status, value.get('transaction_id'), value.get('user_id'),))
        db.commit()
        return True
    
class UserMethod(BaseMethod):
    def fetchUserById(self, value):
        self.cur.execute(f"SELECT * FROM {self.tableName.get('user')} WHERE id = %s ", (value.get('user_id'),))
        data = self.cur.fetchone()
        self.cur.close
        if data != None:
            return data
        return False
    
    def editUserById(self, value):
        self.cur.execute(f"SELECT username FROM {self.tableName.get('user')} WHERE username = %s ", (value.get('username')))
        data = self.cur.fetchone()
        print(data)
        if data == None or value.get('old_username') == value.get('username'):
            self.cur.execute(f"UPDATE {self.tableName.get('user')} SET username = %s, password = %s, profile_picture = %s WHERE id = %s", (value.get('username'), value.get('new_password'), value.get('profile_picture'), value.get('user_id'),))
            db.commit()
            self.cur.execute(f"SELECT * FROM {self.tableName.get('user')} WHERE id = %s ", (value.get('user_id'),))
            new_data = self.cur.fetchone()
            self.cur.close
            return new_data
        else:
            return False
    
    def deleteUserById(self, value):
        if value.get('id') != '':
            self.cur.execute(f"DELETE FROM {self.tableName.get('user')} WHERE id = %s", (value.get('user_id'),))
            db.commit()
            return True
        return False

class ClientMethod(BaseMethod):
     def fetchAllClient(self):
        self.cur.execute(f"SELECT id, username, job_title FROM {self.tableName.get('client')} ")
        data = self.cur.fetchall()
        self.cur.close
        if data != None:
            lists = []
            for x in data:
                lists.append({
                    "client_id": x[0],
                    "client_name": x[1],
                    "job_title": x[2],
                })
            return lists
        return False

class StatusMethod(BaseMethod):
    def fetchAllStatus(self):
        self.cur.execute(f"SELECT * FROM {self.tableName.get('status')} ")
        data = self.cur.fetchall()
        self.cur.close
        if data != None:
            lists = []
            for x in data:
                lists.append({
                    "id": x[0],
                    "title": x[1],
                })
            return lists
        return False