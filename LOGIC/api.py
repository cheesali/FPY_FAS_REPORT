from django.db import connections
from django.http import HttpRequest, JsonResponse
from server import app_urls_api
from datetime import date, datetime, timedelta
from LOGIC.api_config import api_except_decorator
from LOGIC.query import (
        get_contract_info,
        get_customers,
        get_dublicates,
        get_emails,
        get_errors_info,
        get_lots,
        get_report_for_kns_yadro,
    )
from services import hex_to_dec_list
from django.utils import timezone
CONNECTION_MSSQL = "mssql_main_prod"


def grouping_by_lot(start_date_str, end_date_str, lotid = 0):
    """
    Группировка информации по лотам.

    Аргументы:
    start_date_str -- начальная дата в виде строки
    end_date_str -- конечная дата в виде строки
    lotid -- идентификатор лота (по умолчанию 0)

    Возвращает:
    Список словарей с информацией о лотах
    """
    all_info = get_contract_info(start_date_str, end_date_str, lotid)
    if not all_info:
        return []
    result = []
    for lot in all_info:
        # Проверяем, есть ли уже такой лот в результате
        check = False
        for current_lot in result:
            if current_lot['LOTID'] == lot['LOTID']:
                check = True
                continue
        if check:
            continue
        # Создаем новую запись для лота
        lot_info = {
            "LOTID": lot['LOTID'],
            "TITLE": lot['TITLE'],
            "FPY": round( (lot['PASS']/lot['COUNT_RESULT']) * 100, 2),
            "GENERAL_FPY": [],
            "STEPS_SEQ": hex_to_dec_list(lot['STEPS_SEQ']),
            "STEPS": [],
            "OTHER_STEPS": [],
            "OBJECTIVE": lot['OBJECTIVE']
        }
        result.append(lot_info)
    # Заполнение информации о шагах для каждого лота
    for info in all_info:
        for lot in result:
            if lot['LOTID'] == info['LOTID']:
                # Проверяем, является ли шаг основным или дополнительным
                step_find = False
                for step_id in lot['STEPS_SEQ']:
                    if step_id == info['STEP_ID']:                        
                        lot['STEPS'].append({
                            "STEP_ID": info['STEP_ID'],
                            "STEP_NAME": info['STEP_NAME'],
                            "PASS": info['PASS'],
                            "FAIL": info['FAIL'],
                            "OTHER": info['OTHER'],
                            "COUNT_RESULT": info['COUNT_RESULT'],
                            "DESCR": info['DESCR'],
                            "LINE_NAME": info['LINE_NAME'], 
                            "LINE_ID": info['LINE_ID'],
                            "FPY": round( (info['PASS']/info['COUNT_RESULT']) * 100, 2),
                            
                        })
                        step_find = True
                        break
                if not step_find:
                    lot['OTHER_STEPS'].append({
                        "STEP_ID": info['STEP_ID'],
                        "STEP_NAME": info['STEP_NAME'],
                        "PASS": info['PASS'],
                        "FAIL": info['FAIL'],
                        "OTHER": info['OTHER'],
                        "COUNT_RESULT": info['COUNT_RESULT'],
                        "DESCR": info['DESCR'],
                        "LINE_NAME": info['LINE_NAME'],
                        "LINE_ID": info['LINE_ID'],
                        "FPY": round( (info['PASS']/info['COUNT_RESULT']) * 100, 2),
                        
                    })
    # endregion lot_inf
    for lot in result:
        # OTHER_STEPS -------------------------------------------------------------------------------------------------------------------------
        # Обработка дополнительных шагов
        step_other_list_temp = lot['OTHER_STEPS']
        lot['OTHER_STEPS'] = []
        for step_other in step_other_list_temp:
            find_step = False
            for lot_step in lot['OTHER_STEPS']:
                if step_other['STEP_ID'] == lot_step['STEP_ID']:
                    find_step = True
                    break
            if find_step:
                continue
            # Добавление уникальных дополнительных шагов
            lot['OTHER_STEPS'].append({
                "STEP_ID": step_other['STEP_ID'],
                "STEP_NAME": step_other['STEP_NAME'],
                "DESCR": step_other['DESCR'],
                "LINES_INFO": []
            })
        
        # Заполнение информации о линиях для дополнительных шагов
        for other_step in lot['OTHER_STEPS']:
            for info in all_info:
                if lot['LOTID'] == info['LOTID'] and other_step['STEP_ID'] == info['STEP_ID']:
                    other_step['LINES_INFO'].append({
                        "PASS": info['PASS'],
                        "FAIL": info['FAIL'],
                        "OTHER": info['OTHER'],
                        "COUNT_RESULT": info['COUNT_RESULT'],
                        "LINE_NAME": info['LINE_NAME'],
                        "LINE_ID": info['LINE_ID'],
                        "FPY": round( (info['PASS']/info['COUNT_RESULT']) * 100, 2),
                    })

        # STEPS -------------------------------------------------------------------------------------------------------------------------------
        # Обработка основных шагов
        step_list_temp = lot['STEPS']
        lot['STEPS'] = []
        for step_other in step_list_temp:
            find_step = False
            for lot_step in lot['STEPS']:
                if step_other['STEP_ID'] == lot_step['STEP_ID']:
                    find_step = True
                    break
            if find_step:
                continue
            # Добавление уникальных основных шагов
            lot['STEPS'].append({
                "STEP_ID": step_other['STEP_ID'],
                "STEP_NAME": step_other['STEP_NAME'],
                "DESCR": step_other['DESCR'],
                
                "LINES_INFO": []
            })
        # region LINE_INFO STEPS
        # Заполнение информации о линиях для основных шагов
        for other_step in lot['STEPS']:
            for info in all_info:
                if lot['LOTID'] == info['LOTID'] and other_step['STEP_ID'] == info['STEP_ID']:
                    # Проверяем, есть ли информация о дубликатах для этой линии
                    other_step['LINES_INFO'].append({
                        "PASS": info['PASS'],
                        "FAIL": info['FAIL'],
                        "OTHER": info['OTHER'],
                        "COUNT_RESULT": info['COUNT_RESULT'],
                        "LINE_NAME": info['LINE_NAME'],
                        "LINE_ID": info['LINE_ID'],
                        "FPY": round( (info['PASS']/info['COUNT_RESULT']) * 100, 2),
                    })

        # Сортировка основных шагов в соответствии с STEPS_SEQ
        step_list_temp = lot['STEPS']
        # lot.pop('STEPS_SEQ', None)
        lot['STEPS'] = []
        for step_id in lot['STEPS_SEQ']:
            for step in step_list_temp:
                if step_id == step['STEP_ID']:
                    lot['STEPS'].append(step)

        # Сбор FPY для шагов с 'fpy' в описании
        fpy_list = []
        for step in lot['STEPS']:
            if step['DESCR'] is not None and 'fpy' in step['DESCR'].lower():
                for line_info in step['LINES_INFO']:
                    fpy_list.append(float(line_info['FPY']))
        
    # region GENERAL_FPY
        # Расчет общего FPY для лота
        lot['GENERAL_FPY'] = fpy_list
        if len(fpy_list) > 0:
            lot['GENERAL_FPY'] = round(sum(fpy_list) / len(fpy_list), 2)
        else:
            lot['GENERAL_FPY'] = '-'
    return result
    # endregion GENERAL_FPY


def grouping_errors(start_date_str, end_date_str, lotid=0):
    """
    Группирует информацию об ошибках по лотам и шагам.

    Аргументы:
    start_date_str -- начальная дата в виде строки
    end_date_str -- конечная дата в виде строки
    lotid -- идентификатор лота (по умолчанию 0)

    Возвращает:
    Список сгруппированных ошибок
    """
    # Получаем информацию об ошибках
    errors_info = get_errors_info(start_date_str, end_date_str, lotid)
    if not errors_info:
        return []

    # Создаем новый список для группировки ошибок по лотам
    new_errors_info = []
    for error in errors_info:
        for new_error in new_errors_info:
            if error['LOTID'] == new_error['LOTID']:
                break
        else:
            new_errors_info.append({"LOTID": error['LOTID'], "STEPS": []})

    # Группируем ошибки по шагам для каждого лота
    for new_error in new_errors_info:
        for error in errors_info:
            if error['LOTID'] == new_error['LOTID']:
                new_error['STEPS'].append({
                    "STEP_ID": error['STEP_ID'],
                    "LINES_INFO": []
                })
        
        # Удаляем дубликаты шагов
        new_error['STEPS'] = list({v['STEP_ID']:v for v in new_error['STEPS']}.values())
                
    # Заполняем информацию о линиях для каждого шага
    for i, new_error in enumerate(new_errors_info):
        for error in errors_info:
            if error['LOTID'] == new_error['LOTID']:
                for ii, new_error_step in enumerate(new_error['STEPS']):
                    if error['STEP_ID'] == new_error_step['STEP_ID']:
                        new_errors_info[i]['STEPS'][ii]['LINES_INFO'].append({
                            "FAIL_DESCR": error['FAIL_DESCR'],
                            "ERROR_CODE": error['ERROR_CODE'],
                            "COUNT_FAIL": error['COUNT_FAIL'],
                            "LINE_ID": error['LINE_ID'],
                        })
    return new_errors_info
    




def get_datetime_now(start_date_str, end_date_str):
    now = timezone.now()
    print(f'Сегодня: {now}')
    tomorrow = now + + timedelta(days=1)
    
    # Определяем текущий день и час
    current_day = now.date()
    current_hour = now.hour

    # Если даты не указаны, ставим период за сегодня
    if not start_date_str or not end_date_str:
        if current_hour < 20:  # Если время до 8 вечера, ставим период с 08:00 до 20:00 текущего дня
            start_date = now.replace(hour=8, minute=0, second=0, microsecond=0)
            end_date = now.replace(hour=20, minute=0, second=0, microsecond=0)
        else:  # Если время после 8 вечера, ставим период с 20:00 до 08:00 следующего дня
            start_date = now.replace(hour=20, minute=0, second=0, microsecond=0) 
            end_date = now.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    # Преобразование строк в формат даты/времени SQL Server
    # Используем '%Y-%m-%dT%H:%M' для парсинга строк из JavaScript
    else:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M')

    # Форматируем даты в нужный формат
    start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
    end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')

    return start_date_str, end_date_str




# def get_datetime_now(start_date_str, end_date_str):
#     # Если даты не указаны, ставим период за сегодня
#     if not start_date_str or not end_date_str:
#         #С сегодня в 8 утра до сегодня в 20 часов
        
#         today = timezone.now().replace(hour=8, minute=0, second=0, microsecond=0)
#         # print(f"Сегодня: {today}")
#         start_date = today
#         # start_date = today - timedelta(days=1)  # Вчерашний день
#         start_date = start_date.replace(hour=8, minute=0, second=0, microsecond=0)
#         # print(f"Вчерашний день: {start_date}")
#         end_date = today.replace(hour=20, minute=0, second=0, microsecond=0)
#         start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
#         end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
#         return start_date_str, end_date_str

#     # Преобразование строк в формат даты/времени SQL Server
#     # Используем '%Y-%m-%dT%H:%M' для парсинга строк из JavaScript
#     start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')
#     start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
#     end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M')
#     end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
#     return start_date_str, end_date_str


#Api для получение всех данных
@app_urls_api.path('get/contract_info/', name='contract_info')
def api_get_contract_info(request: HttpRequest):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    start_date_str, end_date_str = get_datetime_now(start_date_str, end_date_str)
    return JsonResponse(grouping_by_lot(start_date_str, end_date_str), safe=False)


#Api для получение ошибок
@app_urls_api.path('get/errors/', name='get_errors')
def api_get_errors(request: HttpRequest):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    start_date_str, end_date_str = get_datetime_now(start_date_str, end_date_str)
    return JsonResponse(grouping_errors(start_date_str, end_date_str), safe=False)


#Api для получение дубликатов
@app_urls_api.path('get/dubls/', name='get_dubls')
def api_get_dubls(request: HttpRequest):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    start_date_str, end_date_str = get_datetime_now(start_date_str, end_date_str)
    dublicates = get_dublicates(start_date_str, end_date_str)
    return JsonResponse(dublicates, safe=False)


#Api для получения заказчиков
@app_urls_api.path('get/customers/', name='get_customers')
def api_get_customers(request: HttpRequest):
    customers = get_customers()
    return JsonResponse(customers, safe=False)

@app_urls_api.path('get/lots/', name='get_lots')
def api_get_lots(request: HttpRequest):
    lots = get_lots()
    return JsonResponse(lots, safe=False)

@app_urls_api.path('get/emails/', name='get_emails')
def api_get_emails(request: HttpRequest):
    emails = get_emails()
    return JsonResponse(emails, safe=False)

@app_urls_api.path('get/report_kns_yadro/', name='report_kns_yadro')
def api_get_report_kns_yadro(request: HttpRequest):
    lots = get_report_for_kns_yadro()
    return JsonResponse(lots, safe=False)


