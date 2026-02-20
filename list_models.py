from google import genai
client = genai.Client(api_key='AIzaSyAfPXR7LiMTACkM0rKQgfrzvh3ena5LSRk')
for m in client.models.list():
    if 'flash' in m.name:
        print(m.name)
