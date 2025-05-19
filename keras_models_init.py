from keras.models import load_model
from joblib import load
import traceback
import json
import numpy as np
from datetime import datetime, timedelta


# Загрузка моделей и конфигураций
MODELS = {
    "covid19_model": {
        "model": load_model('keras_models/covid19_model.keras'),
        "config": json.load(open('keras_models/covid19_model.keras.json')),
        "scalers": {}
    },
    "pneumania_model": {
        "model": load_model('keras_models/pneumania_model.keras'),
        "config": json.load(open('keras_models/pneumania_model.keras.json')),
        "scalers": {}
    }
}

# Загрузка нормализаторов
SCALER_FILES = [
    'day_of_week',
    'day_of_year',
    'infected_daily',
    'is_weekend',
    'month',
    'quarter',
    'season'
]

for model_name in MODELS:
    for feature in SCALER_FILES:
        scaler_name = f"scalers/{feature}scaler.joblib"
        MODELS[model_name]['scalers'][feature] = load(scaler_name)

def generate_input_vector(model_name, X, dates):
    model_data = MODELS[model_name]
    config = model_data['config']
    window = config['window']
    horizon = config['horizon']
    
    # Валидация входных данных
    if len(X) != window:
        raise ValueError(f"X length must be {window}")
    if len(dates) != horizon:
        raise ValueError(f"Dates length must be {window}")
    
    valid_dates, msg = validate_dates(dates)
    if not valid_dates:
        raise ValueError(msg)
    
    # Создание матрицы признаков
    cols = config['cols']
    matrix = np.zeros((window, len(cols)))
    
    for i, date_str in enumerate(dates):
        date = datetime.strptime(date_str, "%Y-%m-%d")
        features = {
            'infected_daily': X[i],
            'day_of_week': date.weekday(),
            'month': date.month,
            'quarter': (date.month - 1) // 3 + 1,
            'is_weekend': int(date.weekday() >= 5),
            'season': (date.month % 12) // 3 + 1,
            'day_of_year': date.timetuple().tm_yday
        }
        
        # Заполнение матрицы в правильном порядке
        for j, col in enumerate(cols):
            matrix[i, j] = features[col]
    
    # Нормализация
    for j, col in enumerate(cols):
        scaler = model_data['scalers'][col]
        matrix[:, j] = scaler.transform(matrix[:, j].reshape(-1, 1)).flatten()
    
    # Линеаризация
    #print(matrix)
    return matrix.reshape(1, -1)

def validate_dates(dates):
    try:
        dates = [datetime.strptime(d, "%Y-%m-%d") for d in dates]
        for i in range(1, len(dates)):
            if dates[i] - dates[i-1] != timedelta(days=1):
                return False, "Dates are not consecutive"
        return True, dates
    except ValueError:
        return False, "Invalid date format"