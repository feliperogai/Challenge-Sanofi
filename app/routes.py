from flask import render_template, request, jsonify, redirect, url_for, send_from_directory, make_response
import mysql.connector
import hashlib
import jwt
import datetime
import uuid
import os
from flask_mail import Mail, Message

# Função para criptografar senha
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Função para obter conexão com o banco de dados
def get_db_connection():
    db_config = {
        'user': 'admin',
        'password': 'sanofi12345',
        'host': 'database-sanofi.ctg4cskwkes6.us-east-1.rds.amazonaws.com',
        'database': 'sistema_login'
    }
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Erro ao obter conexão: {err}")
        return None

# Função para codificar o token JWT
def encode_auth_token(user_id):
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(payload, 'decode_auth_token', algorithm='HS256')
    except Exception as e:
        print(f"Erro ao gerar token: {e}")
        return None

# Função para decodificar o token JWT
def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(auth_token, 'decode_auth_token', algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        print("Token expirado. Faça login novamente.")  # Log para depuração
        return 'Token expirado. Faça login novamente.'
    except jwt.InvalidTokenError:
        print("Token inválido. Faça login novamente.")  # Log para depuração
        return 'Token inválido. Faça login novamente.'

# Função para verificar se o usuário está autenticado e obter o ID do usuário
def is_authenticated_and_get_user():
    token = request.cookies.get('authToken')
    if token:
        user_id = decode_auth_token(token)
        if not isinstance(user_id, str):  # Se não for uma string de erro, o token é válido
            return user_id
    return None

# Função para configurar as rotas
def configure_routes(app):
    mail = Mail(app)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/register')
    def register():
        return render_template('register.html')
    
    @app.route('/check')
    def check():
        return render_template('check.html')

    @app.route('/user-settings')
    def user_settings():
        user_id = is_authenticated_and_get_user()
        if user_id:
            return render_template('user_settings.html')
        return redirect(url_for('index'))

    @app.route('/forgot-password')
    def forgot_password():
        return render_template('forgot_password.html')

    @app.route('/reset-password')
    def reset_password_page():
        token = request.args.get('token')
        if token:
            return render_template('reset_password.html', token=token)
        return redirect(url_for('index'))

    @app.route('/user')
    def user():
        user_id = is_authenticated_and_get_user()
        if user_id:
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT email, nome_usuario FROM usuarios WHERE id = %s", (user_id,))
                    user = cursor.fetchone()
                    if user:
                        email, nome = user
                        return render_template('user.html', email=email, nome=nome)
                finally:
                    conn.close()
        return redirect(url_for('index'))

    @app.route('/admin')
    def admin():
        user_id = is_authenticated_and_get_user()  # Verifica se o usuário está autenticado
        if user_id:  # Se estiver autenticado, continua
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT email, nome_usuario, tipo_usuario FROM usuarios WHERE id = %s", (user_id,))
                    user = cursor.fetchone()
                    if user:
                        email, nome, tipo_usuario = user
                        if tipo_usuario == 'admin':
                            return render_template('admin.html', email=email, nome=nome)
                finally:
                    conn.close()
        # Se não estiver autenticado, redireciona para a página de login
        return redirect(url_for('index'))


    @app.route('/logout', methods=['POST'])
    def logout():
        resp = make_response(redirect(url_for('index')))
        resp.set_cookie('authToken', '', expires=0, httponly=True, secure=True)
        return resp

    @app.route('/register', methods=['POST'])
    def register_user():
        data = request.json
        nome_usuario = data.get('name')
        email = data.get('email')
        senha = hash_password(data.get('password'))

        if not nome_usuario or not email or not senha:
            return jsonify({'mensagem': 'Dados inválidos!'}), 400

        conn = get_db_connection()
        if conn is None:
            return jsonify({'mensagem': 'Erro ao conectar ao banco de dados.'}), 500

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM usuarios WHERE email = %s", (email,))
            existing_user = cursor.fetchone()
            if existing_user:
                return jsonify({'mensagem': 'E-mail já cadastrado!'}), 400

            cursor.execute("""
                INSERT INTO usuarios (nome_usuario, email, senha)
                VALUES (%s, %s, %s)
            """, (nome_usuario, email, senha))
            conn.commit()
            return jsonify({'mensagem': 'Usuário cadastrado com sucesso!'})

        except mysql.connector.Error as err:
            print(f"Erro ao registrar o usuário: {err}")
            return jsonify({'mensagem': 'Erro ao registrar o usuário.'}), 500

        finally:
            cursor.close()
            conn.close()

    @app.route('/', methods=['POST'])
    def login_user():
        data = request.json
        email = data.get('email')
        senha = hash_password(data.get('password'))

        if not email or not senha:
            return jsonify({'mensagem': 'Dados inválidos!'}), 400

        conn = get_db_connection()
        if conn is None:
            return jsonify({'mensagem': 'Erro ao conectar ao banco de dados.'}), 500

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome_usuario, tipo_usuario FROM usuarios WHERE email = %s AND senha = %s", (email, senha))
            user = cursor.fetchone()
            if user:
                user_id, nome_usuario, tipo_usuario = user
                token = encode_auth_token(user_id)
                if token:
                    redirect_url = url_for('admin' if tipo_usuario == 'admin' else 'user')
                    print(f"Usuário autenticado com sucesso. Redirecionando para: {redirect_url}")  # Log para depuração
                    resp = make_response(jsonify({'redirect': redirect_url}))
                    resp.set_cookie('authToken', token, httponly=True)  # Lembre-se de remover `secure=True` se estiver em ambiente de desenvolvimento local
                    return resp
                return jsonify({'mensagem': 'Erro ao gerar o token.'}), 500
            else:
                print("Email ou senha incorretos.")  # Log para depuração
            return jsonify({'mensagem': 'Email ou senha incorretos.'}), 401

        except mysql.connector.Error as err:
            print(f"Erro ao autenticar o usuário: {err}")  # Log para depuração
            return jsonify({'mensagem': 'Erro ao autenticar o usuário.'}), 500

        finally:
            cursor.close()
            conn.close()

    @app.route('/update-nome', methods=['POST'])
    def update_nome():
        data = request.json
        email = data.get('email')
        new_name = data.get('new_name')

        if not email or not new_name:
            return jsonify({'mensagem': 'Dados inválidos!'}), 400

        conn = get_db_connection()
        if conn is None:
            return jsonify({'mensagem': 'Erro ao conectar ao banco de dados.'}), 500

        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET nome_usuario = %s WHERE email = %s", (new_name, email))
            conn.commit()
            return jsonify({'mensagem': 'Nome de usuário atualizado com sucesso!'})

        except mysql.connector.Error as err:
            return jsonify({'mensagem': f'Erro ao atualizar o nome de usuário: {err}'}), 500

        finally:
            cursor.close()
            conn.close()

    @app.route('/update-senha', methods=['POST'])
    def update_senha():
        data = request.json
        email = data.get('email')
        current_password = hash_password(data.get('current_password'))
        new_password = hash_password(data.get('new_password'))

        if not email or not current_password or not new_password:
            return jsonify({'mensagem': 'Dados inválidos!'}), 400

        conn = get_db_connection()
        if conn is None:
            return jsonify({'mensagem': 'Erro ao conectar ao banco de dados.'}), 500

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT senha FROM usuarios WHERE email = %s", (email,))
            stored_password = cursor.fetchone()
            if stored_password and stored_password[0] == current_password:
                cursor.execute("UPDATE usuarios SET senha = %s WHERE email = %s", (new_password, email))
                conn.commit()
                return jsonify({'mensagem': 'Senha atualizada com sucesso!'})
            else:
                return jsonify({'mensagem': 'Senha atual incorreta!'}), 401

        except mysql.connector.Error as err:
            return jsonify({'mensagem': f'Erro ao atualizar a senha: {err}'}), 500

        finally:
            cursor.close()
            conn.close()

    @app.route('/forgot-password', methods=['POST'])
    def reset_password_request():
        data = request.json
        email = data.get('email')

        if not email:
            return jsonify({'mensagem': 'E-mail inválido.'}), 400

        conn = get_db_connection()
        if conn is None:
            return jsonify({'mensagem': 'Erro ao conectar ao banco de dados.'}), 500

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            user = cursor.fetchone()
            if user:
                user_id = user[0]
                token = str(uuid.uuid4())
                cursor.execute("INSERT INTO reset_tokens (user_id, token) VALUES (%s, %s)", (user_id, token))
                conn.commit()
                reset_link = f"http://localhost:5000/reset-password?token={token}"
                msg = Message('Redefinição de Senha',
                              sender='your_email@example.com',
                              recipients=[email])
                msg.body = f'Clique no link para redefinir sua senha: {reset_link}'
                mail.send(msg)
                return jsonify({'mensagem': 'Instruções para redefinir a senha foram enviadas por e-mail.'})
            return jsonify({'mensagem': 'E-mail não encontrado.'}), 404

        except mysql.connector.Error as err:
            return jsonify({'mensagem': f'Erro ao enviar o e-mail: {err}'}), 500

        finally:
            cursor.close()
            conn.close()

    @app.route('/reset-password', methods=['POST'])
    def update_password():
        data = request.json
        token = data.get('token')
        new_password = data.get('new_password')

        if not token or not new_password:
            return jsonify({'mensagem': 'Dados inválidos.'}), 400

        conn = get_db_connection()
        if conn is None:
            return jsonify({'mensagem': 'Erro ao conectar ao banco de dados.'}), 500

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM reset_tokens WHERE token = %s", (token,))
            token_data = cursor.fetchone()
            if token_data:
                user_id = token_data[0]
                hashed_password = hash_password(new_password)
                cursor.execute("UPDATE usuarios SET senha = %s WHERE id = %s", (hashed_password, user_id))
                conn.commit()
                cursor.execute("DELETE FROM reset_tokens WHERE token = %s", (token,))
                conn.commit()
                return jsonify({'mensagem': 'Senha atualizada com sucesso!'})
            return jsonify({'mensagem': 'Token inválido.'}), 400

        except mysql.connector.Error as err:
            return jsonify({'mensagem': f'Erro ao atualizar a senha: {err}'}), 500

        finally:
            cursor.close()
            conn.close()

    @app.route('/static/<path:filename>')
    def send_asset(filename):
        return send_from_directory(os.path.join(app.root_path, 'static'), filename)

    @app.route('/check-auth', methods=['GET'])
    def check_auth():
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(" ")[1]
            user_id = decode_auth_token(token)
            if not isinstance(user_id, str):  # Se for um ID válido (número), o token é válido
                return jsonify({'message': 'Autenticado com sucesso!'}), 200
        return jsonify({'message': 'Não autenticado!'}), 401
