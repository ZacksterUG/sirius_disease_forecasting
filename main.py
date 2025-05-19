import json
import traceback
import numpy as np
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from datasets.dataset import get_infection_data
from keras_models_init import MODELS, generate_input_vector
import sqlite3
import bcrypt
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from database.db_connection import get_db_connection
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])
app.config['SECRET_KEY'] = 'your-super-secret-key'  # Замените в продакшене!
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 час
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 604800  # 7 дней
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

jwt = JWTManager(app)

"""
    POST /register
    Создает нового пользователя.
    JSON-формат:
    {
        "login": string,
        "password": string,
        "fio": string (optional)
    }
    Возвращает:
    {
        "message": string
    }
    :statuscode 201: Created
    :statuscode 400: Bad Request
"""
@app.route('/register', methods=['POST'])
def register():
    # Проверяем, что запрос содержит JSON
    if not request.is_json:
        return jsonify({"error": "Request must be in JSON format"}), 400

    data = request.get_json()
    # Извлекаем данные из JSON-тела
    login = data.get('login')
    password = data.get('password')
    fio = data.get('fio')

    # Валидация обязательных полей
    if not login or not password:
        return jsonify({"error": "Login and password are required"}), 400

    # Проверка длины логина и пароля
    if len(login) < 5 or len(login) > 32:
        return jsonify({"error": "Login must be 5-32 characters"}), 400
    if len(password) < 6 or len(password) > 32:
        return jsonify({"error": "Password must be 6-32 characters"}), 400

    # Хеширование пароля
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    # Сохранение в БД
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO USERS (LOGIN, PASSWORD, FIO) VALUES (?, ?, ?)',
            (login, hashed_password.decode(), fio)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Login already exists"}), 400
    finally:
        conn.close()

    return jsonify({"message": "User registered successfully"}), 201

"""
    Login user and generate access and refresh tokens.

    :param login: login of user
    :param password: password of user
    :return: access token, refresh token
    :rtype: (str, str)
    :statuscode 200: OK
    :statuscode 401: Unauthorized
"""
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    login = data.get('login')
    password = data.get('password')

    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM USERS WHERE LOGIN = ?', (login,)
    ).fetchone()
    conn.close()

    if not user or not bcrypt.checkpw(password.encode(), user['PASSWORD'].encode()):
        return jsonify({'error': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=str(user['ID']))
    refresh_token = create_refresh_token(identity=str(user['ID']))
    return jsonify(access_token=access_token, refresh_token=refresh_token), 200

"""
    Generates a new access token if the provided refresh token is valid.

    :return: New access token
    :rtype: str
    :statuscode 200: OK
    :statuscode 401: Unauthorized
"""
@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_token), 200

"""
    Checks if a JWT token has been revoked.

    :param jwt_header: The decoded JWT header
    :param jwt_payload: The decoded JWT payload
    :return: True if the token is revoked, False otherwise
    :rtype: bool
"""
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    conn = get_db_connection()
    jti = jwt_payload['jti']
    token = conn.execute(
        'SELECT * FROM JWT_BLACKLIST WHERE JTI = ?', (jti,)
    ).fetchone()
    conn.close()
    return token is not None

"""
    Invalidates the JWT token provided in the Authorization header.

    :statuscode 200: Successfully logged out
    :statuscode 400: Bad Request
"""
@app.route('/logout', methods=['DELETE'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO JWT_BLACKLIST (JTI) VALUES (?)', (jti,)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Token already revoked'}), 400
    finally:
        conn.close()
    return jsonify({'message': 'Successfully logged out'}), 200

"""
    Возвращает данные заболеваемости COVID-19 или пневмонией
    за указанный период.

    :param ds_name: Название датасета ('covid19' или 'pneumania')
    :param date_begin: Дата начала периода (YYYY-MM-DD)
    :param date_end: Дата конца периода (YYYY-MM-DD)

    :return: JSON-ответ с данными типа {'date': 'YYYY-MM-DD', 'value': число}
    :rtype: dict

    :statuscode 200: OK
    :statuscode 400: Bad Request
    :statuscode 500: Internal Server Error
"""
@app.route('/data', methods=['GET'])
@jwt_required()
def handle_data_request():
    # Получение параметров из запроса
    ds_name = request.args.get('ds_name')
    date_begin_str = request.args.get('date_begin')
    date_end_str = request.args.get('date_end')
    
    # Валидация имени датасета
    if ds_name not in ['covid19', 'pneumania']:
        return jsonify({'error': 'Неверное имя датасета'}), 400
    
    # Валидация и преобразование дат
    try:
        date_begin = datetime.strptime(date_begin_str, '%Y-%m-%d').date()
        date_end = datetime.strptime(date_end_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return jsonify({'error': 'Неверный формат даты. Используйте YYYY-MM-DD.'}), 400
    
    if date_begin > date_end:
        return jsonify({'error': 'date_begin должен быть меньше или равен date_end'}), 400
    
    # Получение данных
    try:
        data = get_infection_data(ds_name, date_begin, date_end)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return jsonify(data)

"""
    Выполняет прогнозирование заболеваемости COVID-19 или пневмонией
    по указанной модели и входным данным.

    :param model: Название модели ('covid19' или 'pneumania')
    :param date_begin: Дата начала периода (YYYY-MM-DD)
    :param date_end: Дата конца периода (YYYY-MM-DD)
    :param X: JSON-массив с числами, описывающими заболеваемость
        за последние `window` дней.

    :return: JSON-ответ с прогнозом типа {'forecast': [число, число, ...]}
    :rtype: dict

    :statuscode 200: OK
    :statuscode 400: Bad Request
    :statuscode 500: Internal Server Error
"""
@app.route('/predict', methods=['POST'])
@jwt_required()
def predict():
    try:
        # Парсинг параметров
        model_name = request.args.get('model')
        date_begin = request.args.get('date_begin')
        date_end = request.args.get('date_end')
        X = request.json.get('X')
        
        # Валидация модели
        if model_name not in MODELS:
            return jsonify({"error": f"Invalid model: {model_name}"}), 400
        
        model_data = MODELS[model_name]
        config = model_data['config']
        
        # Валидация дат
        try:
            print(date_begin, date_end)
            start_date = datetime.strptime(date_begin, "%Y-%m-%d")
            end_date = datetime.strptime(date_end, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400
            
        if start_date > end_date:
            return jsonify({"error": "date_begin must be <= date_end"}), 400
        
        days_requested = (end_date - start_date).days + 1
        if days_requested > config['horizon']:
            return jsonify({"error": f"Requested period exceeds model horizon ({config['horizon']} days)"}), 400
        
        if days_requested < config['horizon']:
            end_date = start_date + timedelta(days=config['horizon'])
        
        # Генерация dates
        dates = [
            (start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(config['horizon'])
        ]
        
        # Генерация входного вектора
        input_vector = generate_input_vector(model_name, X, dates)
        
        # Прогнозирование
        prediction = model_data['model'].predict(np.array([input_vector]))[0]
        
        # Обрезка и обработка прогноза
        prediction = prediction[:days_requested]
        prediction = MODELS[model_name]['scalers']['infected_daily'].inverse_transform(prediction.reshape(-1, 1)).flatten()
        prediction = [max(0, int(x)) for x in prediction]
        
        return jsonify({"forecast": prediction})
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)