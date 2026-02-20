from google import genai
client = genai.Client(api_key='AIzaSyAaGWrLEo7Jv_imdUVxxeLkFjL1MDnRAq4')

for model_id in ["text-embedding-004", "models/text-embedding-004"]:
    try:
        res = client.models.embed_content(model=model_id, contents="Hello")
        print(f"SUCCESS with {model_id}: {len(res.embeddings[0].values)} dims")
    except Exception as e:
        print(f"FAIL with {model_id}: {e}")
