import urllib.parse
from django.urls import reverse
from django.template import Context, Template, RequestContext
from django.template.loader import render_to_string, get_template
from django.core.mail import send_mail
from django.core.mail import EmailMessage


def email_send(subject='Уведомление', body='Тест', to='gudo.m@yandex.ru'):
    if type(to) == str:
        to = [to]
    EmailMessage(subject=subject, body=body, to=to).send()


def message(response, message, type=2):
    """
    :param response: Ответ сервера без сообщения
    :param message: Сообщение
    :param type: Тип сообщения: 1 - успешно, 2 - информация, 3 - предупреждение, 4 - ошибка
    :return: Ответ сервера с сообщением, хранящимся в cookie
    """
    response.set_cookie('emessage', urllib.parse.quote((str(type)+message)))
    return response

def allow_origins(response):
    response["Access-Control-Allow-Origin"] = "*"
    return response


def render_article(request, article):
    context = {
        'article': article,
    }
    message = render_to_string('articles/one_article.html', context=context, request=request)

    return message


def render_crm_profile(request, user):
    context = {
        'user': user,
    }
    message = render_to_string('crm/profiles/one_profile.html', context=context, request=request)

    return message


def render_article_on_moder(request, article):
    context = {
        'article': article,
    }
    message = render_to_string('articles/one_article_on_moder.html', context=context, request=request)

    return message


def render_crm_article(request, article):
    context = {
        'article': article,
    }
    message = render_to_string('crm/articles/one_article.html', context=context, request=request)

    return message


def render_crm_article_on_moder(request, article):
    context = {
        'article': article,
    }
    message = render_to_string('crm/articles/one_article_on_moder.html', context=context, request=request)

    return message


def render_comment(request, comment):

    context = {
        'comment': comment,
    }
    message = render_to_string('articles/one_comment.html', context=context, request=request)

    return message
