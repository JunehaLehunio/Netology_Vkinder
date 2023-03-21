from vk_api import VkApi
from vk_api.upload import VkUpload
from vk_api.utils import get_random_id
import requests
from io import BytesIO

TOKEN = 'vk1.a.BFpndqfAp8qPPaYAy-gS1iFz5crBrfGJN8aU9iTE-d4KKPjZMRIQ-MZNNZjyK9MYVHD-jVXu5v6HpW0hFeJ1oyJjCnFvivOCpLiDJ_GcCNiKJz6j5FmCDpLA5eolAf9SThhN_L1soE3yghJFQNLHZZJbCthhpYA5IXIKaqFBG0oQ8NSl1GQhJUfj-ndg-WZ7_ZOlszpjHukNCCjDMNPXpg'
PEER_ID = 11861185
URL = 'https://sun1-97.userapi.com/s/v1/if1/EOMwfbhkAZqojI0gvK7Ol-0v35SKcQyhhgzYVdRi_vxm8HnwHbQQqOHbI9NBjtJEQDxeJMVi.jpg?size=400x400&quality=96&crop=102,109,432,432&ava=1'


def main():
    vk_session = VkApi(token=TOKEN)
    vk = vk_session.get_api()
    upload = VkUpload(vk)

    img = requests.get(URL).content
    f = BytesIO(img)

    response = upload.photo_messages(f)[0]

    owner_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']

    attachment = f'photo{owner_id}_{photo_id}_{access_key}'
    vk.messages.send(
        random_id=get_random_id(),
        peer_id=PEER_ID,
        attachment=attachment,
        message='Upload'
    )


if __name__ == '__main__':
    main()
