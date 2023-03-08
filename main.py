import requests
from urllib.parse import urlparse
import os
import environs
import random


env = environs.Env()
env.read_env()
VK_TOKEN = env('VK_TOKEN')
API_VERSION = '5.131'
GROUP_ID = env.int('GROUP_ID')
IMG_URL = 'https://xkcd.com/{id}/info.0.json'
VK_API_URL = 'https://api.vk.com/method/{metod}'


def get_file_extension(url):
    path = urlparse(url).path
    path, extension = os.path.splitext(path)
    return extension


def download_image(url, path):
    folder, img_name = os.path.split(path)
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    with open(path, 'wb') as file:
        file.write(response.content)


def get_wall_upload_server():
    response = requests.get(
        VK_API_URL.format(metod='photos.getWallUploadServer'),
        params={
            'access_token': VK_TOKEN,
            'v': API_VERSION,
            'group_id': GROUP_ID
        }
    )
    response.raise_for_status()
    return response.json()['response']['upload_url']


def get_xkcd_comic(id=1):
    response = requests.get(IMG_URL.format(id=id))
    response.raise_for_status()
    return response.json()


def upload_photo(img_name, upload_url):
    with open(img_name, 'rb') as photo:
        response = requests.post(
            upload_url,
            files={'photo': photo}
        )
    response.raise_for_status()
    photo_meta = response.json()
    response = requests.post(
        VK_API_URL.format(metod='photos.saveWallPhoto'),
        params={
            'access_token': VK_TOKEN,
            'v': API_VERSION,
            'group_id': GROUP_ID,
            'server': photo_meta['server'],
            'photo': photo_meta['photo'],
            'hash': photo_meta['hash'],
        }
    )
    response.raise_for_status()
    return response.json()['response'][0]


def post_photo(photo_meta, img_description):
    media_id = photo_meta['id']
    owner_id = photo_meta['owner_id']
    response = requests.post(
        VK_API_URL.format(metod='wall.post'),
        params={
            'access_token': VK_TOKEN,
            'v': API_VERSION,
            'owner_id': f'-{GROUP_ID}',
            'from_group': 1,
            'message': img_description,
            'attachments': f'photo{owner_id}_{media_id}'
        }
    )
    response.raise_for_status()
    return response.json()


def get_xkcd_random_comic(max_comic_num):
    img_meta = get_xkcd_comic(id=random.randint(0, max_comic_num))
    img_description = img_meta['alt']
    img_name = os.path.basename(img_meta['img'])
    download_image(img_meta['img'], f'./{img_name}')
    return img_name, img_description


def get_max_comic_num():
    response = requests.get('https://xkcd.com/info.0.json')
    response.raise_for_status()
    return response.json()['num']


if __name__ == '__main__':
    img_name, img_description = get_xkcd_random_comic(get_max_comic_num())
    upload_url = get_wall_upload_server()
    photo_meta = upload_photo(img_name, upload_url)
    post_photo(photo_meta, img_description)
    os.remove(img_name)
