from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory, make_response, flash, current_app
import mysql.connector
import hashlib
import jwt
import os
import re
import uuid
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import Usuario, Treinamento, UsuarioTreinamento
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
    
    # Rota para exibir o formulário
    @app.route('/submit', methods=['GET', 'POST'])
    def check():
        if request.method == 'POST':
            nome = request.form.get('name')
            email = request.form.get('email')
            data_hora = request.form.get('date')
            assinatura = request.form.get('signature')

            # Validação dos dados do formulário
            if not nome or not email or not data_hora or not assinatura:
                flash('Todos os campos são obrigatórios.', 'danger')
                return redirect(url_for('check'))

            # Conectar ao banco de dados
            conn = get_db_connection()
            if conn is None:
                flash('Erro ao conectar ao banco de dados.', 'danger')
                return redirect(url_for('check'))

            try:
                cursor = conn.cursor()

                # Verificar se o email existe na tabela de usuários
                cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
                usuario = cursor.fetchone()

                if not usuario:
                    flash('Usuário não encontrado.', 'danger')
                    return redirect(url_for('check'))

                usuario_id = usuario[0]

                # Obter treinamentos vinculados ao usuário
                cursor.execute("""
                    SELECT t.id, t.data_hora 
                    FROM treinamentos t 
                    JOIN usuario_treinamento ut ON ut.treinamento_id = t.id 
                    WHERE ut.usuario_id = %s
                """, (usuario_id,))
                treinamentos = cursor.fetchall()

                # Verificar presença para cada treinamento
                for treinamento in treinamentos:
                    treinamento_id, treinamento_data_hora = treinamento
                    
                    # Verificar se a data e hora estão dentro dos limites
                    if data_hora.startswith(treinamento_data_hora.date().isoformat()):
                        # Converter data_hora para datetime
                        data_hora_dt = datetime.strptime(data_hora, '%Y-%m-%dT%H:%M')
                        
                        # Verificar se não ultrapassa 4 horas após o treinamento
                        if (data_hora_dt - treinamento_data_hora).total_seconds() <= 14400:
                            # Inserir na tabela de presença
                            query = """
                                INSERT INTO presenca (nome, email, data_hora, assinatura)
                                VALUES (%s, %s, %s, %s)
                            """
                            cursor.execute(query, (nome, email, data_hora, assinatura))

                            # Obter o ID da presença inserida
                            presenca_id = cursor.lastrowid

                            # Atualizar a tabela de usuario_treinamento
                            cursor.execute("""
                                UPDATE usuario_treinamento 
                                SET presenca_id = %s 
                                WHERE usuario_id = %s AND treinamento_id = %s
                            """, (presenca_id, usuario_id, treinamento_id))

                            conn.commit()
                            flash('Presença registrada com sucesso!', 'success')
                            return redirect(url_for('check'))

                flash('Nenhuma presença válida encontrada para registrar.', 'warning')
                return redirect(url_for('check'))

            except mysql.connector.Error as err:
                print(f"Erro ao inserir dados: {err}")
                flash('Erro ao registrar presença. Tente novamente.', 'danger')
                return redirect(url_for('check'))
            finally:
                cursor.close()
                conn.close()

        return render_template('check.html')
    
    @app.route('/admin-management')
    def admin_management():
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
                            return render_template('admin_management.html', email=email, nome=nome)
                finally:
                    conn.close()
        return redirect(url_for('index'))
    
    @app.route('/api/users')
    def get_users():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id, nome_usuario AS nome, email, tipo_usuario AS tipo FROM usuarios')
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(users)

    @app.route('/api/user-settings', methods=['POST'])
    def manage_user_settings():
        conn = get_db_connection()
        cursor = conn.cursor()
        user_id = request.form.get('user-id')

        if 'change-user-type' in request.form:
            new_type = request.form.get('new-type')
            cursor.execute('UPDATE usuarios SET tipo_usuario = %s WHERE id = %s', (new_type, user_id))
            conn.commit()
            response = {'status': 'success', 'message': 'Tipo de usuário alterado com sucesso!'}

        elif 'delete-user' in request.form:
            cursor.execute('DELETE FROM usuarios WHERE id = %s', (user_id,))
            conn.commit()
            response = {'status': 'success', 'message': 'Usuário excluído com sucesso!'}

        cursor.close()
        conn.close()
        return jsonify(response)

    @app.route('/user-settings', methods=['GET', 'POST'])
    def user_settings():
        user_id = is_authenticated_and_get_user()
        if not user_id:
            return redirect(url_for('index'))

        conn = get_db_connection()
        if conn is None:
            flash('Erro ao conectar ao banco de dados.', 'danger')
            return redirect(url_for('index'))

        if request.method == 'POST':
            if 'update-name' in request.form:
                new_name = request.form.get('new-name')
                if not new_name:
                    return jsonify({'message': 'O nome não pode estar vazio.', 'status': 'error'})
                try:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE usuarios SET nome_usuario = %s WHERE id = %s", (new_name, user_id))
                    conn.commit()
                    return jsonify({'message': 'Nome de usuário atualizado com sucesso!', 'status': 'success'})
                except mysql.connector.Error as err:
                    return jsonify({'message': f'Erro ao atualizar nome: {err}', 'status': 'error'})
                finally:
                    cursor.close()

            elif 'update-password' in request.form:
                current_password = request.form.get('current-password')
                new_password = request.form.get('new-password')

                if not current_password or not new_password:
                    return jsonify({'message': 'Senha atual e nova senha são obrigatórias.', 'status': 'error'})
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT senha FROM usuarios WHERE id = %s", (user_id,))
                    stored_password = cursor.fetchone()[0]

                    if check_password(stored_password, current_password):
                        hashed_password = hash_password(new_password)
                        cursor.execute("UPDATE usuarios SET senha = %s WHERE id = %s", (hashed_password, user_id))
                        conn.commit()

                        # Atualiza o token JWT para manter o usuário autenticado
                        token = encode_auth_token(user_id)
                        if token:
                            resp = make_response(jsonify({'message': 'Senha atualizada com sucesso!', 'status': 'success'}))
                            resp.set_cookie('authToken', token, httponly=True, secure=True)
                            return resp

                        return jsonify({'message': 'Senha atualizada com sucesso!', 'status': 'success'})
                    else:
                        return jsonify({'message': 'Senha atual incorreta.', 'status': 'error'})
                except mysql.connector.Error as err:
                    return jsonify({'message': f'Erro ao atualizar senha: {err}', 'status': 'error'})
                finally:
                    cursor.close()

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT nome_usuario, email, tipo_usuario FROM usuarios WHERE id = %s", (user_id,))
            user_info = cursor.fetchone()
            if user_info:
                nome_usuario, email, tipo_usuario = user_info
                return render_template('user_settings.html', nome=nome_usuario, email=email, user_type=tipo_usuario)
            else:
                flash('Erro ao carregar informações do usuário.', 'danger')
                return redirect(url_for('index'))
        except mysql.connector.Error as err:
            flash(f'Erro ao obter informações do usuário: {err}', 'danger')
            return redirect(url_for('index'))
        finally:
            cursor.close()
            conn.close()

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            # Obtém os dados do formulário
            data = request.json
            nome_usuario = data.get('name')
            email = data.get('email')
            senha = hash_password(data.get('password'))

            # Valida os dados
            if not nome_usuario or not email or not senha:
                return jsonify({'mensagem': 'Dados inválidos!'}), 400

            # Conecta ao banco de dados
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

                # Insere o novo usuário
                cursor.execute(""" 
                    INSERT INTO usuarios (nome_usuario, email, senha)
                    VALUES (%s, %s, %s)
                """, (nome_usuario, email, senha))
                conn.commit()
                
                # Redireciona para a página de login com mensagem de sucesso
                return jsonify({'mensagem': 'Usuário cadastrado com sucesso!', 'redirect': url_for('index')})

            except mysql.connector.Error as err:
                print(f"Erro ao registrar o usuário: {err}")
                return jsonify({'mensagem': 'Erro ao registrar o usuário.'}), 500

            finally:
                cursor.close()
                conn.close()

        # Renderiza a página de registro para GET requests
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
    
    @app.route('/api/tickets', methods=['GET'])
    def get_tickets():
        page = request.args.get('page', default=0, type=int)
        limit = 4
        offset = page * limit

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.id, t.nome_treinamento, t.data_hora, t.link,
                COUNT(u.id) as num_usuarios,
                GROUP_CONCAT(u.nome_usuario) as usuarios
            FROM treinamentos t
            LEFT JOIN usuario_treinamento ut ON t.id = ut.treinamento_id
            LEFT JOIN usuarios u ON ut.usuario_id = u.id
            GROUP BY t.id
            ORDER BY t.data_hora DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        tickets = cursor.fetchall()
        cursor.close()
        conn.close()

        # Formatar dados para incluir data e horário separadamente
        for ticket in tickets:
            ticket['data'] = ticket['data_hora'].strftime('%Y-%m-%d')
            ticket['time'] = ticket['data_hora'].strftime('%H:%M')
            del ticket['data_hora']  # Remove o campo original

        return jsonify(tickets)

    @app.route('/api/tickets/<int:ticket_id>', methods=['GET'])
    def get_ticket_details(ticket_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Query para obter detalhes do treinamento, incluindo usuários que participaram
        cursor.execute("""
            SELECT t.nome_treinamento, t.data_hora, t.link,
                GROUP_CONCAT(u.nome_usuario) as usuarios
            FROM treinamentos t
            LEFT JOIN usuario_treinamento ut ON t.id = ut.treinamento_id
            LEFT JOIN usuarios u ON ut.usuario_id = u.id
            WHERE t.id = %s
            GROUP BY t.id
        """, (ticket_id,))
        
        ticket = cursor.fetchone()

        # Query para obter usuários que participaram mas não confirmaram presença
        cursor.execute("""
            SELECT u.nome_usuario FROM usuarios u
            WHERE u.id IN (
                SELECT usuario_id FROM usuario_treinamento ut 
                WHERE ut.treinamento_id = %s
            ) AND u.id NOT IN (
                SELECT ut.usuario_id FROM usuario_treinamento ut 
                JOIN treinamentos t ON ut.treinamento_id = t.id
                WHERE ut.treinamento_id = %s AND ut.presenca_id = TRUE
            )
        """, (ticket_id, ticket_id))
        
        non_completers = cursor.fetchall()
        
        cursor.close()
        conn.close()

        if ticket:
            ticket['data'] = ticket['data_hora'].strftime('%d-%m-%Y')
            ticket['time'] = ticket['data_hora'].strftime('%H:%M')  # Adiciona horário formatado
            ticket['usuarios'] = ticket['usuarios'].split(',') if ticket['usuarios'] else []
            ticket['usuarios_nao_concluintes'] = [user['nome_usuario'] for user in non_completers]  # Usuários que não confirmaram presença
            del ticket['data_hora']  # Remove o campo original
            return jsonify(ticket)
        else:
            return jsonify({'mensagem': 'Ticket não encontrado.'}), 404

    @app.route('/cadastrar-treinamento', methods=['GET', 'POST'])
    def cadastrar_treinamento():
        user_id = is_authenticated_and_get_user()
        if not user_id:
            return redirect(url_for('index'))

        if request.method == 'POST':
            data = request.json
            usuario_ids = data.get('usuario_ids')
            nome_treinamento = data.get('treinamento')
            data_treinamento = data.get('data')
            hora_treinamento = data.get('time')
            link = data.get('link')

            # Combina data e hora
            data_hora = datetime.strptime(f"{data_treinamento} {hora_treinamento}", '%Y-%m-%d %H:%M')

            conn = get_db_connection()
            if conn is None:
                return jsonify({'mensagem': 'Erro ao conectar ao banco de dados.'}), 500

            try:
                cursor = conn.cursor()
                
                # Verifica se já existe um treinamento com esses dados
                cursor.execute("""
                    SELECT id FROM treinamentos 
                    WHERE nome_treinamento = %s AND data_hora = %s AND link = %s
                """, (nome_treinamento, data_hora, link))
                existing_training = cursor.fetchone()

                if existing_training:
                    # Se já existe, só adiciona os usuários
                    treinamento_id = existing_training[0]
                    for usuario_id in usuario_ids:
                        cursor.execute("""
                            INSERT INTO usuario_treinamento (usuario_id, treinamento_id)
                            VALUES (%s, %s)
                        """, (usuario_id, treinamento_id))
                else:
                    # Se não existe, cria um novo
                    cursor.execute("""
                        INSERT INTO treinamentos (nome_treinamento, data_hora, link)
                        VALUES (%s, %s, %s)
                    """, (nome_treinamento, data_hora, link))
                    treinamento_id = cursor.lastrowid
                    
                    # Insere os usuários
                    for usuario_id in usuario_ids:
                        cursor.execute("""
                            INSERT INTO usuario_treinamento (usuario_id, treinamento_id)
                            VALUES (%s, %s)
                        """, (usuario_id, treinamento_id))

                conn.commit()
                return jsonify({'mensagem': 'Treinamento cadastrado com sucesso!'}), 201

            except mysql.connector.Error as err:
                print(f"Erro ao cadastrar o treinamento: {err}")
                return jsonify({'mensagem': 'Erro ao cadastrar o treinamento.'}), 500

            finally:
                cursor.close()
                conn.close()

        return render_template('admin.html', user_id=user_id)

    @app.route('/api/progress', methods=['GET'])
    def get_progress_data():
        try:
            print("Iniciando a busca de usuários...")
            users = Usuario.query.all()
            print(f"Usuários encontrados: {len(users)}")

            progress_data = []

            for user in users:
                print(f"Processando usuário: {user.nome_usuario}")
                try:
                    total_trainings = UsuarioTreinamento.query.filter_by(usuario_id=user.id).count()
                    print(f"Total de treinamentos para {user.nome_usuario}: {total_trainings}")

                    # Contar treinamentos concluídos com presenca_id não nulo
                    completed_trainings = UsuarioTreinamento.query.filter(
                        UsuarioTreinamento.usuario_id == user.id,
                        UsuarioTreinamento.presenca_id.isnot(None)  # Presença confirmada
                    ).count()
                    print(f"Treinamentos concluídos para {user.nome_usuario}: {completed_trainings}")

                    not_completed_trainings = total_trainings - completed_trainings
                    print(f"Treinamentos não concluídos para {user.nome_usuario}: {not_completed_trainings}")

                    progress_data.append({
                        'nome_usuario': user.nome_usuario,
                        'treinamentos_concluidos': completed_trainings,
                        'treinamentos_nao_concluidos': not_completed_trainings
                    })

                except Exception as user_error:
                    print(f"Erro ao processar o usuário {user.nome_usuario}: {user_error}")

            print("Dados de progresso:", progress_data)
            return jsonify(progress_data), 200

        except Exception as e:
            print(f"Erro na rota /api/progress: {e}")
            return jsonify([]), 500  # Retornar um array vazio em caso de erro
        
    @app.route('/api/tickets/user', methods=['GET'])
    def get_user_tickets():
        user_id = is_authenticated_and_get_user()  # Função para obter o ID do usuário autenticado
        if not user_id:
            return jsonify({'message': 'Não autenticado!'}), 401

        try:
            conn = get_db_connection()
            if conn is None:
                return jsonify({'message': 'Erro ao conectar ao banco de dados.'}), 500

            cursor = conn.cursor()

            # Pegar parâmetros de paginação
            page = int(request.args.get('page', 0))
            limit = int(request.args.get('limit', 4))
            offset = page * limit

            # Consulta para pegar os tickets (treinamentos) do usuário autenticado
            cursor.execute("""
                SELECT t.id, t.nome_treinamento, t.data_hora, t.link,
                    COUNT(ut.id) AS num_usuarios
                FROM treinamentos t
                LEFT JOIN usuario_treinamento ut ON t.id = ut.treinamento_id
                WHERE ut.usuario_id = %s
                GROUP BY t.id
                LIMIT %s OFFSET %s
            """, (user_id, limit, offset))

            tickets = cursor.fetchall()

            tickets_data = []
            for ticket in tickets:
                ticket_data = {
                    'id': ticket[0],
                    'nome_treinamento': ticket[1],
                    'data_hora': ticket[2],
                    'link': ticket[3],
                    'num_usuarios': ticket[4] if ticket[4] is not None else 0
                }
                tickets_data.append(ticket_data)

            return jsonify(tickets_data), 200

        except Exception as e:
            print(f"Erro ao obter tickets do usuário: {e}")
            return jsonify({'message': 'Erro ao carregar tickets.'}), 500

        finally:
            cursor.close()
            conn.close()

    @app.route('/api/progress/user', methods=['GET'])
    def get_user_progress():
        user_id = is_authenticated_and_get_user()
        if not user_id:
            return jsonify({'message': 'Não autenticado!'}), 401

        try:
            conn = get_db_connection()
            if conn is None:
                return jsonify({'message': 'Erro ao conectar ao banco de dados.'}), 500

            cursor = conn.cursor()
            # Ajustar a consulta para pegar apenas os dados do usuário autenticado
            cursor.execute("""
                SELECT u.nome_usuario, 
                    COUNT(ut.id) AS total_trainings, 
                    SUM(CASE WHEN ut.presenca_id IS NOT NULL THEN 1 ELSE 0 END) AS completed_trainings 
                FROM usuarios u
                LEFT JOIN usuario_treinamento ut ON u.id = ut.usuario_id
                WHERE u.id = %s
                GROUP BY u.id
            """, (user_id,))
            
            result = cursor.fetchone()
            
            if result:
                nome_usuario, total_trainings, completed_trainings = result
                not_completed_trainings = total_trainings - completed_trainings if total_trainings else 0

                progress_data = {
                    'nome_usuario': nome_usuario,
                    'treinamentos_concluidos': completed_trainings,
                    'treinamentos_nao_concluidos': not_completed_trainings
                }
                return jsonify(progress_data), 200
            else:
                return jsonify({'message': 'Usuário não encontrado.'}), 404

        except Exception as e:
            print(f"Erro ao obter progresso do usuário: {e}")
            return jsonify([]), 500
        finally:
            cursor.close()
            conn.close()

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
