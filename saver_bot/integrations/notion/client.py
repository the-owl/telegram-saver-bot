from notion_client import Client


def get_notion_client(token: str):
    return Client(auth=token)
