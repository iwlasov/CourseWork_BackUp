import requests
import os
import json
import time
from datetime import datetime
from tqdm import tqdm

class VKAPIClient:

    def __init__(self, token, id, folder_name: str, version='5.236'):
        self.token = token
        self.id = id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}
        self.folder_name = folder_name

    def get_user_info(self):

        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': self.id}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def get_profile_photo(self, offset=0, count=5):

        #count = 5 # количество фоток для скачивания
        json_result = []  # список для создания json файла
        save_result = {}  # словарь для сохранения фоток на диске

        # создаём папку на компьютере для скачивания фотографий
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)

        # получаем фото из профиля
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': user_id, 'album_id': 'profile', 'access_token': vk_token, 'v': '5.236',
                  'extended': '1', 'photo_sizes': '1', 'count': count, 'offset': offset}
        response = requests.get(url=url, params=params).json()

        # цикл для фото полученных из профиля
        for photo in response['response']['items']:
            photo_info = {} # словарь для создания json файла

            #реализация прогресс бара
            for i in tqdm(range(count)):
                time.sleep(0.1)

            # формирование имени фотографий
            if photo['likes']['count'] not in save_result.keys():
                save_result[photo['likes']['count']] = photo['sizes'][-1]['url'] #берем фотку с конца списка - самую большую
                photo_info['file_name'] = f"{photo['likes']['count']}.jpg"
            else:
                date_photo = str(datetime.fromtimestamp(photo['date'])).split(' ')[0]
                save_result[f"{photo['likes']['count']}_{date_photo}"] = photo['sizes'][-1]['url'] #берем фотку с конца списка - самую большую
                photo_info['file_name'] = f"{photo['likes']['count']}_{date_photo}.jpg"

            photo_info['size'] = photo['sizes'][-1]['type'] #получаем размер фотки
            json_result.append(photo_info)

        #print('save_result:', save_result)
        #print('json_result:', json_result)

        # сохраняем фотографии на диск
        for photo_name, photo_url in save_result.items():
            with open(f'{folder_name}/{photo_name}.jpg', 'wb') as file:
                response = requests.get(photo_url)
                file.write(response.content)
        print(f'В папку {folder_name} сохранено {len(save_result)} фотографий')

        # записываем данные о скачанных фоторафиях json файл
        with open("photos.json", "w") as file:
            json.dump(json_result, file, indent=4)
        print('Json файл photos.json с информацией о скачанныx фото сформирован')

class YAAPIClient:
    def __init__(self, token: str, folder_name: str):
        self.token = token
        self.folder_name = folder_name

    def folder_creation(self):

        url = f'https://cloud-api.yandex.net/v1/disk/resources/'
        headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {ya_token}'}
        params = {'path': f'{folder_name}', 'overwrite': 'false'}
        response = requests.put(url=url, headers=headers, params=params)

    def save_profile_photo(self):

        photos_list = os.listdir(folder_name)
        count = 0
        for photo in photos_list:
            file_name = photo
            files_path = os.path.join(os.getcwd(), folder_name, photo)

            url = f'https://cloud-api.yandex.net/v1/disk/resources/upload'
            headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {ya_token}'}
            params = {'path': f'{folder_name}/{file_name}', 'overwrite': 'true'}

            # получение ссылки на загрузку
            response = requests.get(url=url, headers=headers, params=params)
            href = response.json().get('href')

            # загрузка фотки
            response = requests.put(href, data=open(files_path, 'rb'))
            count += 1
            print(f'Фотографий загружено на Яндекс диск: {count}')

if __name__ == '__main__':

    user_id = input('Введите ID пользователя VK: ')
    #user_id = '37764871'

    #токен получаем из файла token.txt
    with open('token.txt') as f:
        vk_token = f.read()

    ya_token = input('Введите токен с Полигона Яндекс Диска: ')
    #ya_token = ''
    # folder_name = input('Введите имя папки на Яндекс диске: '))
    folder_name = 'vk_images'

    download = VKAPIClient(vk_token, user_id, folder_name)
    print('Фото будут загружены из профиля пользователя:')
    print(download.get_user_info()['response'][0]['first_name'], download.get_user_info()['response'][0]['last_name'])
    download.get_profile_photo()

    upload = YAAPIClient(ya_token, folder_name)
    upload.folder_creation()
    upload.save_profile_photo()
