from flask import session

class Middleware:
   
    def is_login(self):
        if 'is_login' in session:
            return True
        return False