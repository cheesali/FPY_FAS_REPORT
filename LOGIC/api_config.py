import hashlib
from json.decoder import JSONDecodeError
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    JsonResponse,
    HttpResponseNotAllowed,
)
import os
from pathlib import Path

from django.shortcuts import redirect

CONNECTION_MSSQL = "mssql_event"

# Декоратор для отлова ошибок в REST-Запросах
def api_except_decorator(type_method: str):
    def decorator(func):
        def api_except(*args, **kwargs):
            if args[0].method == type_method:
                try:
                    return func(*args, **kwargs)
                except KeyError as e:
                    return HttpResponseBadRequest(f"Нет свойства {e}")
                except TimeoutError as e:
                    return HttpResponseBadRequest(f"Нет доступа на сервер")
                except JSONDecodeError as e:
                    return HttpResponseBadRequest(f"Ошибка в формате JSON {e}")
                except Exception as e:
                    return HttpResponseBadRequest(f"Ошибка на сервере {e}")
            else:
                return HttpResponseBadRequest(f"Ошибка в выборе типа запроса")
        return api_except
    return decorator