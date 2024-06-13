import requests, json, time
from datetime import datetime
from tqdm import tqdm

def save_json(file_name: str, json_dict: dict):

    # записываем данные о скачанных фоторафиях json файл
    with open(file_name, "w") as file:
        json.dump(json_dict, file, indent=4)
    print(f'\nJson файл {file_name} с информацией о скачанныx фото сформирован')

class VKAPIClient:

    api_base_url = 'https://api.vk.com/method'

    def __init__(self, vk_token: str, user: str, photo_count: int, version='5.236'):
        self.vk_token = vk_token
        self.user_id = user
        self.screen_name = user
        self.photo_count = photo_count
        self.version = version
        self.params = {'access_token': self.vk_token, 'v': self.version}

    def _build_url(self, api_method):

        return f'{self.api_base_url}/{api_method}'

    def get_user_info(self):

        params = {'user_ids': self.user_id,
                  'fields': 'screen_name'}
        response = requests.get(self._build_url('users.get'), params={**self.params, **params}).json()

        # заполняем id и screename по введенному id или screename
        self.screen_name = response['response'][0]['screen_name']
        self.user_id = str(response['response'][0]['id'])

        return response

    def get_profile_photo(self):

        json_result = []  # список для создания json файла
        save_result = {}  # словарь для сохранения фоток на диске

        params = {'owner_id': self.user_id, 'album_id': 'profile', 'access_token': self.vk_token, 'v': '5.236',
                  'extended': '1', 'photo_sizes': '1', 'count': self.photo_count, 'offset': 0}
        response = requests.get(url=self._build_url('photos.get'), params=params).json()

        # цикл для фото полученных из профиля
        for photo in response['response']['items']:
            photo_info = {} # словарь для создания json файла

            # формирование имени фотографий
            if f'{photo['likes']['count']}.jpg' not in save_result.keys():
                save_result[f'{photo['likes']['count']}.jpg'] = photo['sizes'][-1]['url'] #берем фотку с конца списка - самую большую
                photo_info['file_name'] = f'{photo['likes']['count']}.jpg'
            else:
                date_photo = str(datetime.fromtimestamp(photo['date'])).split(' ')[0]
                save_result[f'{photo['likes']['count']}_{date_photo}.jpg'] = photo['sizes'][-1]['url'] #берем фотку с конца списка - самую большую
                photo_info['file_name'] = f'{photo['likes']['count']}_{date_photo}.jpg'

            photo_info['size'] = photo['sizes'][-1]['type'] #получаем размер фотки
            json_result.append(photo_info)

        # реализация прогресс бара
        for i in tqdm(range(self.photo_count)):
            time.sleep(0.5)

        # записываем данные о скачанных фоторафиях json файл
        save_json('photos.json', json_result)

        #print('save_result:', save_result)
        #print('json_result:', json_result)
        return save_result

class YAAPIClient:
    api_base_url = 'https://cloud-api.yandex.net'

    def __init__(self, ya_token: str, folder_name: str, upload_dict: dict):
        self.ya_token = ya_token
        self.folder_name = folder_name
        self.upload_dict = upload_dict

    def folder_creation(self):

        url = self.api_base_url + '/v1/disk/resources'
        headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {self.ya_token}'}
        params = {'path': f'{self.folder_name}', 'overwrite': 'true'}
        response = requests.put(url=url, headers=headers, params=params)

    def save_profile_photo(self):

        url = self.api_base_url + '/v1/disk/resources/upload'
        headers = {'Content-Type': 'application/json', 'Authorization': f'OAuth {self.ya_token}'}

        count = 1
        for file_name, photo_url in self.upload_dict.items():

            params = {'path': f'{self.folder_name}/{file_name}', 'overwrite': 'true'}

            # получение ссылки на загрузку
            response = requests.get(url=url, headers=headers, params=params)
            url_for_upload = response.json()['href']

            # загрузка фотки
            response = requests.get(photo_url)
            requests.put(url=url_for_upload, data=response)

            # реализация прогресс бара
            #for count in tqdm(range(len(list(self.upload_dict.keys())))):  # реализация прогресс бара
            for i in tqdm(range(count)): # реализация прогресс бара
                time.sleep(0.05)
            count +=1

