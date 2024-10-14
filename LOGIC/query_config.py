from django.db import connections

from settings import APP_DEBUG

CONNECTION_MSSQL = "mssql_main_prod"

def query_execute_decorator(fetchall: bool, not_result: bool = False):
    def decorator(func) -> bool:
        def query_execut(*args, **kwargs):
            list_bolvanka = []
            with connections[CONNECTION_MSSQL].cursor() as cursor:
                # if APP_DEBUG:
                    # print(func(*args, **kwargs))
                cursor.execute(func(*args, **kwargs))
                if cursor.rowcount == 0:
                    return False
                if not_result:
                    return True
                if fetchall:
                    result = cursor.fetchall()
                    headers = [description[0] for description in cursor.description]
                    for row in result:
                        dict_item = {}
                        for i in range(len(headers)):
                            dict_item[headers[i]] = row[i]
                        list_bolvanka.append(dict_item)
                    return list_bolvanka
                else:
                    dict_item = {}
                    result = cursor.fetchone()
                    if result is None:
                        return None
                    headers = [description[0] for description in cursor.description]
                    for i in range(len(headers)):
                        dict_item[headers[i]] = result[i]
                    return dict_item
        return query_execut
    return decorator
