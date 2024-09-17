from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory, make_response, flash, current_app
import mysql.connector
import hashlib
import jwt
import os
import re
import uuid
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from app.email import send_email

# Função para criptografar senha
def hash_password(password):
    return generate_password_hash(password)

def check_password(stored_password, provided_password):
    return check_password_hash(stored_password, provided_password)

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
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    except Exception as e:
        print(f"Erro ao gerar token: {e}")
        return None

# Função para decodificar o token JWT
def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(auth_token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        print("Token expirado. Faça login novamente.")
        return 'Token expirado. Faça login novamente.'
    except jwt.InvalidTokenError:
        print("Token inválido. Faça login novamente.")
        return 'Token inválido. Faça login novamente.'

# Função para verificar se o usuário está autenticado e obter o ID do usuário
def is_authenticated_and_get_user():
    token = request.cookies.get('authToken')
    if token:
        user_id = decode_auth_token(token)
        if not isinstance(user_id, str):  # Se não for uma mensagem de erro, o token é válido
            return user_id
    return None

# Função para configurar as rotas
def configure_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
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
        else:
            return render_template('register.html')

    @app.route('/forgot-password', methods=['GET', 'POST'])
    def forgot_password_page():
        if request.method == 'POST':
            email = request.form.get('email')

            if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                flash('Por favor, insira um e-mail válido.', 'warning')
                return redirect(url_for('forgot_password_page'))

            conn = get_db_connection()
            if conn is None:
                flash('Erro ao conectar ao banco de dados.', 'danger')
                return redirect(url_for('forgot_password_page'))

            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
                user = cursor.fetchone()

                if user:
                    reset_token = str(uuid.uuid4())
                    reset_url = url_for('reset_password_page', token=reset_token, _external=True)
                    expires_at = datetime.utcnow() + timedelta(hours=1)

                    cursor.execute(
                        "INSERT INTO reset_tokens (user_id, token, expires_at) VALUES (%s, %s, %s)",
                        (user[0], reset_token, expires_at)
                    )
                    conn.commit()

                    send_email(
                        email,
                        'Instruções para Redefinição de Senha',
                        render_template('email_reset_password.html', reset_url=reset_url)
                    )
                    flash('Um e-mail com instruções para redefinir sua senha foi enviado.', 'success')
                else:
                    flash('E-mail não encontrado.', 'warning')

            except mysql.connector.Error as err:
                flash(f'Erro ao processar a solicitação: {err}', 'danger')

            finally:
                cursor.close()
                conn.close()

            return redirect(url_for('index'))

        return render_template('forgot_password.html')

    @app.route('/reset-password', methods=['GET', 'POST'])
    def reset_password_page():
        token = request.args.get('token')

        if request.method == 'POST':
            # Obtém a nova senha do formulário
            new_password = request.form.get('new_password')
            if not new_password:
                flash('A nova senha não pode estar vazia.', 'warning')
                return jsonify({'success': False, 'message': 'A nova senha não pode estar vazia.'})

            conn = get_db_connection()
            if conn is None:
                return jsonify({'success': False, 'message': 'Erro ao conectar ao banco de dados.'})

            try:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id, expires_at FROM reset_tokens WHERE token = %s", (token,))
                token_data = cursor.fetchone()

                if token_data:
                    user_id, expires_at = token_data
                    if datetime.utcnow() > expires_at:
                        flash('O link de redefinição de senha expirou. Solicite um novo.', 'warning')
                        cursor.execute("DELETE FROM reset_tokens WHERE token = %s", (token,))
                        conn.commit()
                        return jsonify({'success': False, 'message': 'O link de redefinição de senha expirou.'})

                    # Criptografa a nova senha
                    hashed_password = hash_password(new_password)

                    # Atualiza a senha do usuário
                    cursor.execute("UPDATE usuarios SET senha = %s WHERE id = %s", (hashed_password, user_id))
                    conn.commit()

                    # Remove o token após a redefinição
                    cursor.execute("DELETE FROM reset_tokens WHERE token = %s", (token,))
                    conn.commit()

                    return jsonify({'success': True, 'message': 'Senha alterada com sucesso! Faça login.'})

                else:
                    flash('Token inválido ou expirado. Solicite um novo.', 'warning')
                    return jsonify({'success': False, 'message': 'Token inválido ou expirado.'})

            except mysql.connector.Error as err:
                print(f"Erro ao processar a redefinição de senha: {err}")  # Log para depuração
                return jsonify({'success': False, 'message': 'Erro ao processar a redefinição de senha.'})

            finally:
                cursor.close()
                conn.close()

        # Se for um GET request, renderiza a página com o token se válido
        if token:
            conn = get_db_connection()
            if conn is None:
                flash('Erro ao conectar ao banco de dados.', 'danger')
                return redirect(url_for('forgot_password_page'))

            try:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id, expires_at FROM reset_tokens WHERE token = %s", (token,))
                token_data = cursor.fetchone()

                if token_data:
                    user_id, expires_at = token_data
                    if datetime.utcnow() > expires_at:
                        flash('O link de redefinição de senha expirou. Solicite um novo.', 'warning')
                        cursor.execute("DELETE FROM reset_tokens WHERE token = %s", (token,))
                        conn.commit()
                        return redirect(url_for('forgot_password_page'))
                    
                    return render_template('reset_password.html', token=token)
                else:
                    flash('Token inválido ou expirado. Solicite um novo.', 'warning')
                    return redirect(url_for('forgot_password_page'))

            except mysql.connector.Error as err:
                print(f"Erro ao verificar o token: {err}")  # Log para depuração
                flash(f'Erro ao verificar o token: {err}', 'danger')
                return redirect(url_for('forgot_password_page'))

            finally:
                cursor.close()
                conn.close()

        # Se o token não for fornecido ou não for válido, redireciona para a página de redefinição de senha
        return redirect(url_for('forgot_password_page'))

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
        user_id = is_authenticated_and_get_user()
        if user_id:
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
        return redirect(url_for('index'))

    @app.route('/logout', methods=['POST'])
    def logout():
        resp = make_response(redirect(url_for('index')))
        resp.set_cookie('authToken', '', expires=0, httponly=True, secure=True)
        return resp

    @app.route('/', methods=['POST'])
    def login_user():
        data = request.json
        email = data.get('email')
        senha = data.get('password')

        if not email or not senha:
            return jsonify({'mensagem': 'Dados inválidos!'}), 400

        conn = get_db_connection()
        if conn is None:
            return jsonify({'mensagem': 'Erro ao conectar ao banco de dados.'}), 500

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome_usuario, tipo_usuario, senha FROM usuarios WHERE email = %s", (email,))
            user = cursor.fetchone()
            if user:
                user_id, nome_usuario, tipo_usuario, stored_password = user
                if check_password(stored_password, senha):
                    token = encode_auth_token(user_id)
                    if token:
                        redirect_url = url_for('admin' if tipo_usuario == 'admin' else 'user')
                        resp = make_response(jsonify({'redirect': redirect_url}))
                        resp.set_cookie('authToken', token, httponly=True, secure=True)
                        return resp
                    return jsonify({'mensagem': 'Erro ao gerar o token.'}), 500
                return jsonify({'mensagem': 'Senha incorreta.'}), 401
            else:
                return jsonify({'mensagem': 'Email não encontrado.'}), 401

        except mysql.connector.Error as err:
            print(f"Erro ao autenticar o usuário: {err}")
            return jsonify({'mensagem': 'Erro ao autenticar o usuário.'}), 500

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
            if not isinstance(user_id, str):  # Se for um ID válido, o token é válido
                return jsonify({'message': 'Autenticado com sucesso!'}), 200
        return jsonify({'message': 'Não autenticado!'}), 401
