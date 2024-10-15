import threading
import time
from django.core.mail import EmailMessage
from django.http import HttpRequest, HttpResponse

from django.conf import settings
from django.shortcuts import render
from django.urls import path
from django.utils.module_loading import import_string
from django.utils import timezone
from datetime import date, datetime, timedelta
from django.template.loader import render_to_string
import schedule
from LOGIC.api import get_datetime_now, grouping_by_lot, grouping_errors
from LOGIC.query import get_customers, get_dublicates, get_emails, get_lots, get_report_for_kns_yadro
from server import app_urls_pages

CORE_TEMPLATE = "build/core.html"
NAME_APP = "Отчет по FPY"


# @app_urls_pages.path('', name='index')
# def view_graph(request: HttpRequest) -> HttpResponse:
#     template = "index.html"
#     tailwind_styles = [
#         "build/tailwind_style.html",
#     ]
#     styles = [
#     ]
#     scripts = [
#         "js/index.js",
#         "libs/xlsx.full.min.js",
#         "libs/flowbite.min.js"
#     ]
#     context = {
#         "template": template, 
#         "tailwind_styles":tailwind_styles, 
#         "name_app": NAME_APP,
#         "scripts":scripts,
#         "styles":styles,
#     }
#     return render(
#         request,
#         CORE_TEMPLATE,
#         context=context,
#     )
    
    
# @app_urls_pages.path('fpy_report', name='fpy_report')
# def view_graph(request: HttpRequest) -> HttpResponse:
#     template = "fpy_report.html"
#     tailwind_styles = [
#         "build/tailwind_style.html",
#     ]
#     styles = [
#     ]
#     scripts = [
#         "js/fpy_report.js",
#         "libs/xlsx.full.min.js",
#     ]
#     context = {
#         "template": template, 
#         "tailwind_styles":tailwind_styles, 
#         "name_app": NAME_APP,
#         "scripts":scripts,
#         "styles":styles,
#     }
#     return render(
#         request,
#         CORE_TEMPLATE,
#         context=context,
#     )
    

# @app_urls_pages.path('get_fas_card/', name='get_fas_card')
# def get_fas_card(request: HttpRequest) -> HttpResponse:
#   # Получаем параметры даты начала и конца из запроса
#   start_date_str = request.GET.get('start_date')
#   end_date_str = request.GET.get('end_date')
#   # Преобразуем даты в нужный формат
#   start_date_str, end_date_str = get_datetime_now(start_date_str, end_date_str)

#   # Получаем параметр lot из запроса
#   lotid = request.GET.get('lot', 0)

#   # Инициализируем словари для хранения информации
#   all_info = {}
#   errors_info = {}
#   dublicats_info = {}

#   # Если указан lotid, выполняем группировку с учетом лота
#   if lotid is not None and lotid != "" and lotid != 0:
#     all_info = grouping_by_lot(start_date_str, end_date_str, lotid=lotid)
#     errors_info = grouping_errors(start_date_str, end_date_str, lotid=lotid)
#     dublicats_info = get_dublicates(start_date_str, end_date_str, lotid=lotid)
#   # Иначе выполняем группировку без учета лота
#   else:
#     all_info = grouping_by_lot(start_date_str, end_date_str)
#     errors_info = grouping_errors(start_date_str, end_date_str)
#     dublicats_info = get_dublicates(start_date_str, end_date_str)

#   # Задаем шаблон и стили
#   template = "get_fas_card_page.html"
#   tailwind_styles = [
#     "build/tailwind_style.html",
#   ]
#   styles = [
#   ]
#   scripts = [
#     # "js/fpy_report.js",
#     # "libs/xlsx.full.min.js",
#   ]
#   # Формируем контекст для рендеринга шаблона
#   context = {
#     "template": template, 
#     "tailwind_styles":tailwind_styles, 
#     "name_app": NAME_APP,
#     "scripts":scripts,
#     "styles":styles,
#     "all_info": all_info,
#     "errors_info": errors_info,
#     "dublicats_info": dublicats_info,
#     "start_date": start_date_str,
#     "end_date": end_date_str,
#     "customers": get_customers(),
#     "lots": get_lots(),
#     "emails": get_emails()
#   }
#   try:
#       # Отправляем email с информацией из контекста
#       send_email_report(all_info, errors_info, dublicats_info, start_date_str, end_date_str)
#       print("Email успешно отправлен!")
#   except Exception as e:
#       print(f"Ошибка при отправке email: {str(e)}")

#   # Возвращаем ответ на запрос
#   return render(
#     request,
#     CORE_TEMPLATE,
#     context=context,
#   )


@app_urls_pages.path('get_fas_card/', name='get_fas_card')
def get_fas_card(request: HttpRequest) -> HttpResponse:
  # Получаем параметры даты начала и конца из запроса
  start_date_str = request.GET.get('start_date')
  end_date_str = request.GET.get('end_date')
  # Преобразуем даты в нужный формат
  start_date_str, end_date_str = get_datetime_now(start_date_str, end_date_str)

  # Получаем параметр lot из запроса
  lotid = request.GET.get('lot', 0)

  # Инициализируем словари для хранения информации
  all_info = {}
  errors_info = {}
  dublicats_info = {}

  # Если указан lotid, выполняем группировку с учетом лота
  if lotid is not None and lotid != "" and lotid != 0:
    all_info = grouping_by_lot(start_date_str, end_date_str, lotid=lotid)
    errors_info = grouping_errors(start_date_str, end_date_str, lotid=lotid)
    dublicats_info = get_dublicates(start_date_str, end_date_str, lotid=lotid)
  # Иначе выполняем группировку без учета лота
  else:
    all_info = grouping_by_lot(start_date_str, end_date_str)
    errors_info = grouping_errors(start_date_str, end_date_str)
    dublicats_info = get_dublicates(start_date_str, end_date_str)

  # Задаем шаблон и стили
  template = "get_fas_card_page.html"
  tailwind_styles = [
    "build/tailwind_style.html",
  ]
  styles = [
  ]
  scripts = [
    # "js/fpy_report.js",
    # "libs/xlsx.full.min.js",
  ]
  # Формируем контекст для рендеринга шаблона
  context = {
    "template": template, 
    "tailwind_styles":tailwind_styles, 
    "name_app": NAME_APP,
    "scripts":scripts,
    "styles":styles,
    "all_info": all_info,
    "errors_info": errors_info,
    "dublicats_info": dublicats_info,
    "start_date": start_date_str,
    "end_date": end_date_str,
    "customers": get_customers(),
    "lots": get_lots()
  }

  # Возвращаем ответ на запрос
  return render(
    request,
    CORE_TEMPLATE,
    context=context,
  )

def send_email_report(all_info, errors_info, dublicats_info, start_date_str, end_date_str):
  # try:
    # Формируем контекст для рендеринга шаблона письма
    email_context = {
      "all_info": all_info,
      "errors_info": errors_info,
      "dublicats_info": dublicats_info,
      "start_date": start_date_str,
      "end_date": end_date_str,
    }

    # Рендерим шаблон email
    html_content = render_to_string('get_fas_card_email.html', context=email_context)

    # Отправляем email
    email = EmailMessage(
      subject="FAS отчет",
      body=html_content,
      from_email='REPORT_FPY@dtvs.ru',
      to=['a.nazarova@dtvs.ru']
    )
    email.content_subtype = "html"
    email.send()
    print("Email успешно отправлен!")
  # except Exception as e:
    # print(f"Ошибка при отправке email: {str(e)}")

# Функция для планирования отправки email
def schedule_email_reports():
  hours = ["00:00", "02:00", "04:00", "06:00", "09:59", "08:52", "08:53", "11:37", "16:00", "18:00", "20:00", "22:00"]
  for hour in hours:
    schedule.every().day.at(hour).do(send_email_report_task)

# Функция для выполнения задачи отправки email
def send_email_report_task():
  start_date_str, end_date_str = get_datetime_now(None, None)
  all_info = grouping_by_lot(start_date_str, end_date_str)
  errors_info = grouping_errors(start_date_str, end_date_str)
  dublicats_info = get_dublicates(start_date_str, end_date_str)
  send_email_report(all_info, errors_info, dublicats_info, start_date_str, end_date_str)

# Запускаем планировщик в отдельном потоке
def run_scheduler():
  while True:
    schedule.run_pending()
    time.sleep(60)

# Инициализация планировщика
schedule_email_reports()

# Запуск планировщика в отдельном потоке
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.start()

# def send_email_report(all_info, errors_info, dublicats_info, start_date_str, end_date_str):
#     if not all_info or not errors_info or not dublicats_info:
#       print("Нет данных для отчета. Отправка письма отменена.")
#       return
#     # Формируем контекст для рендеринга шаблона письма
#     email_context = {
#       "all_info": all_info,
#       "errors_info": errors_info,
#       "dublicats_info": dublicats_info,
#       "start_date": start_date_str,
#       "end_date": end_date_str,
#     }

#     # Рендерим шаблон email
#     html_content = render_to_string('get_fas_card_email.html', context=email_context)

#     # Получаем список почт, которым надо отправить письмо
#     # email_list = [row['Email'] for row in get_emails]
#     # print(f'Почта: {email_list}')

#     #Отправляем email
#     email = EmailMessage(
#       subject="Отчет FPY по FAS станциям",
#       body=html_content,
#       from_email='REPORT_FPY@dtvs.ru',
#       # to=email_list
#       to=['a.nazarova@dtvs.ru']
#     )
#     email.content_subtype = "html"
#     email.send()

# # Запускаем планировщик в отдельном потоке


# def run_scheduler():
#   while True:
#     schedule.run_pending()
#     time.sleep(1)

# scheduler_thread = threading.Thread(target=run_scheduler)
# scheduler_thread.start()




# def send_email_report(all_info, errors_info, dublicats_info, start_date_str, end_date_str):
#   # Формируем контекст для рендеринга шаблона письма
#   email_context = {
#     "all_info": all_info,
#     "errors_info": errors_info,
#     "dublicats_info": dublicats_info,
#     "start_date": start_date_str,
#     "end_date": end_date_str,
#   }

#   # Рендерим шаблон email
#   html_content = render_to_string('get_fas_card_email.html', context=email_context)

#   # Отправляем email
#   email = EmailMessage(
#     subject="Отчет FPY по FAS станциям",
#     body=html_content,
#     from_email='REPORT_FPY@dtvs.ru',
#     to=['a.nazarova@dtvs.ru']
#   )
#   email.content_subtype = "html"
#   email.send()



@app_urls_pages.path('kns_yadro_report/', name='kns_yadro_report')
def get_report_kns_yadro_page(request: HttpRequest) -> HttpResponse:
    template = "kns_yadro_page.html"
    tailwind_styles = [
        "build/tailwind_style.html",
    ]
    styles = [
    ]
    scripts = [
        "js/fpy_report.js",
        "libs/xlsx.full.min.js",
    ]
    report_data = get_report_for_kns_yadro()  # Получаем данные для отчета
    context = {
        "template": template, 
        "tailwind_styles":tailwind_styles, 
        "name_app": NAME_APP,
        "scripts":scripts,
        "styles":styles,
        "report_data": report_data,  # Передаем данные в контекст
    }
    
    return render(
        request,
        CORE_TEMPLATE,
        context=context,
    )

def send_yadro_kns_report(data):
    current_date = datetime.now().strftime("%d-%m-%Y %H:%M") 
    try:
        email_context = {
            "report_data": data,
            "current_date": current_date
        }
        html_content = render_to_string('kns_yadro_page.html', context=email_context)

        # Отправляем email
        email = EmailMessage(
            subject=f"Prod Report Yadro/KNS-{current_date}",
            body=html_content,
            from_email='REPORT_FPY@dtvs.ru',
            to=['a.nazarova@dtvs.ru']
        )
        email.content_subtype = "html"
        
        email.send()
        print("Email успешно отправлен!")

    except Exception as e:
        print(f"Ошибка при отправке email: {str(e)}")

        import traceback
        print(traceback.format_exc())


def schedule_email_reports_yadro_kns():
    data = get_report_for_kns_yadro()
    schedule.every().day.at("18:41").do(send_yadro_kns_report, data)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

schedule_email_reports_yadro_kns()


scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.start()

