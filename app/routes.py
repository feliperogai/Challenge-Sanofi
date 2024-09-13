from flask import render_template, request, jsonify, redirect, url_for, send_from_directory
import mysql.connector
from mysql.connector import pooling
import hashlib
import uuid
from flask_mail import Mail, Message
import os

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_db_connection():
    db_config = {
        'user': 'admin',
        'password': 'sanofi12345',
        'host': 'database-sanofi.ctg4cskwkes6.us-east-1.rds.amazonaws.com',
        'database': 'sistema_login'
    }
    try:
        db_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=5,
            **db_config
        )
        return db_pool.get_connection()
    except mysql.connector.Error as err:
        print(f"Erro ao obter conexão: {err}")
        return None

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
        return render_template('user_settings.html')

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
        email = request.args.get('email')
        nome = request.args.get('nome')
        if email and nome:
            return render_template('user.html', email=email, nome=nome)
        return redirect(url_for('index'))

    @app.route('/admin')
    def admin():
        email = request.args.get('email')
        nome = request.args.get('nome')
        if email and nome:
            return render_template('admin.html', email=email, nome=nome)
        return redirect(url_for('index'))

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

            cursor.execute("SELECT nome_usuario, tipo_usuario FROM usuarios WHERE email = %s AND senha = %s", (email, senha))
            user = cursor.fetchone()

            if user:
                nome_usuario, tipo_usuario = user
                if tipo_usuario == 'admin':
                    redirect_url = url_for('admin', email=email, nome=nome_usuario)
                else:
                    redirect_url = url_for('user', email=email, nome=nome_usuario)
                return jsonify({'redirect': redirect_url})

            return jsonify({'mensagem': 'Email ou senha incorretos.'}), 401

        except mysql.connector.Error as err:
            print(f"Erro ao autenticar o usuário: {err}")
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
            print(f"Erro ao atualizar o nome de usuário: {err}")
            return jsonify({'mensagem': 'Erro ao atualizar o nome.'}), 500

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
            print(f"Erro ao atualizar a senha: {err}")
            return jsonify({'mensagem': 'Erro ao atualizar a senha.'}), 500

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
            print(f"Erro ao enviar o e-mail: {err}")
            return jsonify({'mensagem': 'Erro ao enviar o e-mail.'}), 500

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
            print(f"Erro ao atualizar a senha: {err}")
            return jsonify({'mensagem': 'Erro ao atualizar a senha.'}), 500

        finally:
            cursor.close()
            conn.close()

    @app.route('/static/<path:filename>')
    def send_asset(filename):
        return send_from_directory(os.path.join(app.root_path, 'app/static'), filename)
