import configparser
import class_work

def main():

    # токены получаем из settings.ini
    config = configparser.ConfigParser()  # создаём объекта парсера
    config.read("settings.ini")  # читаем конфиг

    vk_token_ini = config['VK']['vk_token']  # обращаемся как к обычному словарю!
    ya_token_ini = config['YA']['ya_token']

    while True:

        input_user = input('Введите ID или ScreenName пользователя VK: ')
        #input_user = '37764871' # ID
        #input_user = 'id37764871' #ScreenName

        input_count = int(input('Введите количество фотографий сохраняемых из профиля VK: '))
        #input_count = 5 #количество загружаемых фото

        # создаем объкт download класса VKAPIClient из модуля class_work
        download = class_work.VKAPIClient(vk_token_ini, input_user, input_count)

        try:
            download.get_user_info()
        except IndexError:
            print('Неверный ID или ScreenName - попробуйте снова')
        else:
            break

    # folder_name = str(input('Введите имя папки на Яндекс диске: '))
    input_folder_name = ('VK_images')

    print('\nФото будут загружены из профиля пользователя:', download.get_user_info()['response'][0]['first_name'],
                                                           download.get_user_info()['response'][0]['last_name'])
    print(f'ID: {download.get_user_info()['response'][0]['id']} ScreenName: {download.get_user_info()['response'][0]['screen_name']}')

    # get_save_result = {} словарь с необходимым именем фото и путем для скачивания и(или) сохранения
    get_save_result = download.get_profile_photo()
    #print('get_save_result:', get_save_result)

    upload = class_work.YAAPIClient(ya_token_ini, input_folder_name, get_save_result)
    print('\nЗагружаем фото на Яндекс диск в папку', input_folder_name)
    upload.folder_creation()
    upload.save_profile_photo()

if __name__ == '__main__':
    main()