import requests
import os
import environs
import random


API_VERSION = '5.131'
IMG_URL = 'https://xkcd.com/{id}/info.0.json'
VK_API_URL = 'https://api.vk.com/method/{metod}'


def download_image(url, image_name):
    response = requests.get(url)
    response.raise_for_status()
    with open(image_name, 'wb') as file:
        file.write(response.content)


def check_vk_response(response):
    if 'error' in response:
        error_code = response['error']['error_code']
        error_msg = response['error']['error_msg']
        raise requests.HTTPError(f'{error_code}: {error_msg}')


def get_wall_upload_server(vk_token, vk_group_id, api_version):
    params = {
        'access_token': vk_token,
        'v': api_version,
        'owner_id': vk_group_id,
    }
    response = requests.get(
        VK_API_URL.format(
            metod='photos.getWallUploadServer'),
            params=params
    )
    response.raise_for_status()
    response = response.json()
    check_vk_response(response)
    return response['response']['upload_url']


def get_xkcd_comic(id=1):
    response = requests.get(IMG_URL.format(id=id))
    response.raise_for_status()
    return response.json()


def upload_photo(img_name, upload_url, vk_token, vk_group_id, api_version):
    with open(img_name, 'rb') as photo:
        response = requests.post(
            upload_url,
            files={'photo': photo}
        )
    response.raise_for_status()
    photo_meta = response.json()
    check_vk_response(photo_meta)
    params = {
        'access_token': vk_token,
        'v': api_version,
        'owner_id': vk_group_id,
        'server': photo_meta['server'],
        'photo': photo_meta['photo'],
        'hash': photo_meta['hash'],
    }
    response = requests.post(
        VK_API_URL.format(metod='photos.saveWallPhoto'),
        params=params
    )
    response.raise_for_status()
    response = response.json()
    check_vk_response(response)
    return response['response'][0]


def post_photo(media_id, owner_id, img_description, vk_token, vk_group_id, api_version):
    params = {
        'access_token': vk_token,
        'v': api_version,
        'owner_id': f'-{vk_group_id}',
        'from_group': 1,
        'message': img_description,
        'attachments': f'photo{owner_id}_{media_id}'
    }
    response = requests.post(
        VK_API_URL.format(metod='wall.post'),
        params=params
    )
    response.raise_for_status()
    response = response.json()
    check_vk_response(response)
    return response


def get_xkcd_random_comic(max_comic_num):
    img_meta = get_xkcd_comic(id=random.randint(0, max_comic_num))
    img_description = img_meta['alt']
    img_name = os.path.basename(img_meta['img'])
    download_image(img_meta['img'], img_name)
    return img_name, img_description


def get_max_comic_num():
    response = requests.get('https://xkcd.com/info.0.json')
    response.raise_for_status()
    return response.json()['num']


if __name__ == '__main__':
    env = environs.Env()
    env.read_env()
    vk_token = env('VK_IMPLICIT_FLOW_TOKEN')
    vk_group_id = env.int('VK_GROUP_ID')
    params = {
        'access_token': vk_token,
        'v': API_VERSION,
        'owner_id': vk_group_id,
    }
    img_name, img_description = get_xkcd_random_comic(get_max_comic_num())
    try:
        upload_url = get_wall_upload_server(vk_token, vk_group_id, API_VERSION)
        photo_meta = upload_photo(img_name, upload_url, vk_token, vk_group_id, API_VERSION)
        media_id = photo_meta['id']
        owner_id = photo_meta['owner_id']
        post_photo(media_id, owner_id, img_description, vk_token, vk_group_id, API_VERSION)
    finally:
        os.remove(img_name)
