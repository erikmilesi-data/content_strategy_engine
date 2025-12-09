import requests
from pprint import pprint

# ==========================
# PREENCHA ESTES DOIS CAMPOS
# ==========================
ACCESS_TOKEN = "EAAWNGBU72t8BQLL6Taa9s8oa3haNsjiZAL4eihDgAYJqSh7iBdZAbCImrKXkqFxTYmLG6HILN8Mqjaa8ujv267PrZAAN9pzbjsvCX8f5NiO5ZBV61RQcp8d0nZBx1rZB2FHDcGm4wdRFhLJGDmPyZArGjjT0KuVdpZAvAgZCzdS0XepZBjlQbx9Qcii9Jt9HFHDJGBAGq3HYIPeGLtM24GMNZAXZA5LKMaPhbqkNOBpipZCCN5h7G8wZBXdJsqp8STtgZCZCA7lGgA52aHckM8XjzXWqXLhm2gkVl3dpFrbrcqwoNwZDZD"
IG_USER_ID = "17841466888769598"

# Uma imagem qualquer pública só para teste
IMAGE_URL = "https://www.w3schools.com/w3images/lights.jpg"
CAPTION = "Post de teste via API da StratifyAI 🚀"


def main():
    print("=== StratifyAI :: Teste de Publicação no Instagram ===")

    if (
        "COLE_SEU_TOKEN_AQUI" in ACCESS_TOKEN
        or "COLE_SEU_IG_USER_ID_AQUI" in IG_USER_ID
    ):
        print("\n[ERRO] Você ainda não preencheu ACCESS_TOKEN e/ou IG_USER_ID.")
        print("Edite o arquivo test_ig_publish.py e coloque os valores corretos.")
        return

    # 1) Criar container de mídia
    create_url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media"
    create_payload = {
        "image_url": IMAGE_URL,
        "caption": CAPTION,
        "access_token": ACCESS_TOKEN,
    }

    print("\n[1/2] Criando container de mídia...")
    print("URL:", create_url)
    resp = requests.post(create_url, data=create_payload)
    print("Status HTTP:", resp.status_code)
    print("Resposta JSON:")
    try:
        data = resp.json()
        pprint(data)
    except Exception:
        print(resp.text)
        return

    if resp.status_code != 200:
        print("\n[ERRO] A API retornou um status diferente de 200 ao criar a mídia.")
        return

    creation_id = data.get("id")
    if not creation_id:
        print("\n[ERRO] Não veio 'id' na resposta ao criar mídia.")
        return

    print(f"\nCreation ID obtido: {creation_id}")

    # 2) Publicar a mídia
    publish_url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media_publish"
    publish_payload = {
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN,
    }

    print("\n[2/2] Publicando mídia no feed...")
    print("URL:", publish_url)
    resp_pub = requests.post(publish_url, data=publish_payload)
    print("Status HTTP:", resp_pub.status_code)
    print("Resposta JSON:")
    try:
        data_pub = resp_pub.json()
        pprint(data_pub)
    except Exception:
        print(resp_pub.text)
        return

    if resp_pub.status_code == 200:
        print("\n✅ Sucesso! A mídia foi publicada no seu Instagram.")
    else:
        print("\n[ERRO] A publicação não foi concluída com sucesso.")


if __name__ == "__main__":
    main()
