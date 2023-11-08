import requests 
import shutil 
from uuid import uuid1
from os.path import join

image_url = 'blob:https://mangadex.org/14c984a4-b91d-4d02-8f72-d19a170736de'

print(image_url)
r = requests.get(image_url, stream = True)
r.raw.decode_content = True

ext = r.headers['content-type'].split("/")[-1]
name = f"{uuid1()}.{ext}"
    
with open(join(".", name),'wb') as f:
    shutil.copyfileobj(r.raw, f)
