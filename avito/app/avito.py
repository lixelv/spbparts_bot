import requests


class Avito:
    def __init__(
        self, client_id, client_secret, user_id, api_url="https://api.avito.ru"
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_id = user_id
        self.api_url = api_url
        self.token = self.get_token()

    def get_token(self):
        resp = requests.post(
            f"{self.api_url}/token",
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
            },
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

    def get_chats(self, unread=False):
        # Можно добавить параметры: "?unread_only=true" и др.
        r = requests.get(
            f"{self.api_url}/messenger/v2/accounts/{self.user_id}/chats?unread_only={str(unread).lower()}",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        r.raise_for_status()
        return r.json().get("chats", [])

    def get_messages(self, chat_id):
        r = requests.get(
            f"{self.api_url}/messenger/v3/accounts/{self.user_id}/chats/{chat_id}/messages",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        r.raise_for_status()
        return r.json()

    def send_message(self, chat_id, text):
        r = requests.post(
            f"{self.api_url}/messenger/v1/accounts/{self.user_id}/chats/{chat_id}/messages",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            json={"type": "text", "message": {"text": text}},
        )
        r.raise_for_status()
