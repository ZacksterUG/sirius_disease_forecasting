import pandas as pd
import datetime


def get_infection_data(ds_name, date_begin, date_end):
    # Определяем путь к файлу в зависимости от имени датасета
    if ds_name == 'covid19':
        filepath = 'datasets/covid19_enriched.csv'
    elif ds_name == 'pneumania':
        filepath = 'datasets/pneumania_enriched.csv'
    else:
        raise ValueError("Некорректное имя датасета")
    
    # Загрузка датасета
    df = pd.read_csv(filepath, sep=';')
    
    # Преобразование колонки 'date' в datetime и установка её как индекс
    df['date'] = pd.to_datetime(df['date']).dt.date
    df.set_index('date', inplace=True)
    
    # Создание диапазона дат от date_begin до date_end
    date_range = pd.date_range(start=date_begin, end=date_end).date
    
    # Переиндексация датафрейма по диапазону дат, заполнение пропусков нулями
    df_reindexed = df.reindex(date_range, fill_value=0)
    
    # Выбор только колонки 'infected_daily' и сброс индекса
    result = df_reindexed[['infected_daily']].reset_index()
    result.columns = ['date', 'value']
    result['date'] = result['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    
    # Преобразование в список словарей
    return result.to_dict('records')