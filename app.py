from flask import Flask, request, jsonify
from flask_cors import CORS
from ldap3 import Server, Connection, ALL, NTLM

app = Flask(__name__)
CORS(app)

LDAP_SERVER = "ldap://localhost:389"
BASE_DN = "dc=test,dc=local"
LDAP_ADMIN = "cn=admin,dc=test,dc=local"
LDAP_PASSWORD = "admin"

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data['username']
        password = data['password']
        
        server = Server(LDAP_SERVER, get_info=ALL)
        conn = Connection(server, user=f"cn={username},{BASE_DN}", password=password, auto_bind=True)
        
        if conn.bound:
            return jsonify({"message": "Успешная аутентификация!"}), 200
        else:
            return jsonify({"message": "Неверные учетные данные!"}), 401

    except Exception as e:
        return jsonify({"message": f"Ошибка: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
