import requests
# https://vk.com/dev/methods - методы в вк
# Тупо информация о пользователе
method = 'users.get'  # метод
id = '0'  # id пользователя
information_request = f'https://api.vk.com/method/{method}?user_id={id}&v=5.52'
#Шо-то про чат-ботов https://vk.com/dev/bots_docs
response = requests.get(information_request)
print(response.id)
