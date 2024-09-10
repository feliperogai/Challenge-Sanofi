from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
import mysql.connector
from mysql.connector import pooling
import hashlib
import os
from flask_mail import Mail, Message
import secrets
from datetime import datetime, timedelta

# Inicializa o Flask
app = Flask(__name__)

# Configurações do Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.example.com'  # Substitua pelo servidor SMTP
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your_email@example.com'
app.config['MAIL_PASSWORD'] = 'your_password'
app.config['MAIL_USE_TLS'] = True
mail = Mail(app)

# Configurações do banco de dados
db_config = {
    'user': 'root',
    'password': '010403',  # Substitua pela sua senha do MySQL
    'host': 'localhost',
    'database': 'sistema_login'
}

# Configura o pool de conexões
try:
    db_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="mypool",
        pool_size=5,
        **db_config
    )
except mysql.connector.Error as err:
    print(f"Erro ao configurar pool de conexões: {err}")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_db_connection():
    try:
        return db_pool.get_connection()
    except mysql.connector.Error as err:
        print(f"Erro ao obter conexão: {err}")
        return None

# Rota para a página inicial (index.html)
@app.route('/login')
def index():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'index.html')

# Rota para a página de cadastro (cadastro.html)
@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

# Rota para a página de configuração do usuário
@app.route('/configuracao')
def configuracao():
    return render_template('configuracao.html')

# Rota para cadastro de usuário
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

        # Verifica se o e-mail já está cadastrado
        cursor.execute("SELECT email FROM usuarios WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            return jsonify({'mensagem': 'E-mail já cadastrado!'}), 400

        # Insere o novo usuário no banco de dados
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

# Rota para login de usuário
@app.route('/login', methods=['POST'])
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

        # Verifica se o e-mail e a senha estão corretos
        cursor.execute("SELECT nome_usuario, tipo_usuario FROM usuarios WHERE email = %s AND senha = %s", (email, senha))
        user = cursor.fetchone()

        if user:
            nome_usuario, tipo_usuario = user
            if tipo_usuario == 'admin':
                redirect_url = url_for('admin_page')
            else:
                redirect_url = url_for('user_page', email=email, nome=nome_usuario)
            return jsonify({'redirect': redirect_url})

        return jsonify({'mensagem': 'Email ou senha incorretos.'}), 401

    except mysql.connector.Error as err:
        print(f"Erro ao autenticar o usuário: {err}")
        return jsonify({'mensagem': 'Erro ao autenticar o usuário.'}), 500

    finally:
        cursor.close()
        conn.close()

# Rota para a página de admin
@app.route('/admin')
def admin_page():
    return render_template('admin.html')

# Rota para a página do usuário
@app.route('/user')
def user_page():
    email = request.args.get('email')
    nome = request.args.get('nome')
    return render_template('user.html', email=email, nome=nome)

# Rota para atualização do nome de usuário
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

        # Atualiza o nome do usuário no banco de dados
        cursor.execute("UPDATE usuarios SET nome_usuario = %s WHERE email = %s", (new_name, email))
        conn.commit()

        return jsonify({'mensagem': 'Nome de usuário atualizado com sucesso!'})

    except mysql.connector.Error as err:
        print(f"Erro ao atualizar o nome de usuário: {err}")
        return jsonify({'mensagem': 'Erro ao atualizar o nome.'}), 500

    finally:
        cursor.close()
        conn.close()

# Rota para atualização de senha
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

        # Verifica se a senha atual está correta
        cursor.execute("SELECT senha FROM usuarios WHERE email = %s", (email,))
        stored_password = cursor.fetchone()

        if stored_password and stored_password[0] == current_password:
            # Atualiza a senha no banco de dados
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

# Rota para solicitar a redefinição de senha
@app.route('/reset-password', methods=['POST'])
def request_reset_password():
    email = request.form['email']
    conn = get_db_connection()
    if conn is None:
        return jsonify({'mensagem': 'Erro ao conectar ao banco de dados.'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute('SELECT email FROM usuarios WHERE email = %s', (email,))
        user = cursor.fetchone()

        if user:
            token = secrets.token_urlsafe(20)
            cursor.execute('INSERT INTO password_reset_tokens (token, email) VALUES (%s, %s)', (token, email))
            conn.commit()

            reset_link = url_for('reset_password', token=token, _external=True)
            msg = Message('Password Reset Request', recipients=[email])
            msg.body = f'Click the link to reset your password: {reset_link}'
            mail.send(msg)
            return jsonify({'mensagem': 'Instruções para redefinir a senha foram enviadas por e-mail.'})

        return jsonify({'mensagem': 'E-mail não encontrado.'}), 404

    except mysql.connector.Error as err:
        print(f"Erro ao solicitar a redefinição de senha: {err}")
        return jsonify({'mensagem': 'Erro ao solicitar a redefinição de senha.'}), 500

    finally:
        cursor.close()
        conn.close()

# Rota para redefinir a senha
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM password_reset_tokens WHERE token = %s', (token,))
    token_data = cursor.fetchone()

    if token_data is None or datetime.now() > datetime.strptime(token_data['created_at'], '%Y-%m-%d %H:%M:%S') + timedelta(hours=1):
        return "O link de redefinição de senha é inválido ou expirou.", 400

    if request.method == 'POST':
        new_password = request.form['password']
        hashed_password = hash_password(new_password)
        email = token_data['email']
        cursor.execute('UPDATE usuarios SET senha = %s WHERE email = %s', (hashed_password, email))
        cursor.execute('DELETE FROM password_reset_tokens WHERE token = %s', (token,))
        conn.commit()
        return "Senha atualizada com sucesso!"

    cursor.close()
    conn.close()
    return render_template('reset_password.html')

# Rota para servir arquivos estáticos da pasta assets
@app.route('/assets/<path:filename>')
def send_asset(filename):
    return send_from_directory(os.path.join(app.root_path, 'static/assets'), filename)

if __name__ == '__main__':
    app.run(debug=True)
