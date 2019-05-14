from flask import Flask, request
import logging
import json

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}


def get_json():
    global sessionStorage
    with open("data/sessionStorage.json", "r") as fp:
        sessionStorage = json.load(fp)


def save_json():
    global sessionStorage
    with open("data/sessionStorage.json", "w") as fp:
        sessionStorage = json.dump(sessionStorage, fp)


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info('Response: %r', request.json)

    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:

        # sessionStorage[ user_id ] = {
        #     'suggests': [
        #         "Не хочу.",
        #         "Не буду.",
        #         "Отстань!",
        #     ]
        # }        res[ 'response' ][ 'text' ] = 'Привет! Купи слона!'
        # # Получим подсказки
        # res[ 'response' ][ 'buttons' ] = get_suggests(user_id)
        return

    # if req[ 'request' ][ 'original_utterance' ].lower() in [
    #     'ладно',
    #     'куплю',
    #     'покупаю',
    #     'хорошо'
    # ]:
    #     # Пользователь согласился, прощаемся.
    #     res[ 'response' ][ 'text' ] = 'Слона можно найти на Яндекс.Маркете!'
    #     res[ 'response' ][ 'end_session' ] = True
    #     return
    #
    # # Если нет, то убеждаем его купить слона!
    # res[ 'response' ][ 'text' ] = 'Все говорят "%s", а ты купи слона!' % (
    #     req[ 'request' ][ 'original_utterance' ]
    # )
    # res[ 'response' ][ 'buttons' ] = get_suggests(user_id)


def get_suggests(user_id):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests']
    ]

    session['suggests'] = session['suggests']
    sessionStorage[user_id] = session

    return suggests


if __name__ == '__main__':
    app.run()
