import requests
import pandas as pd


token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtYnJ1ZXJlQG1vYmluLXNvbHV0aW9ucy5mciIsImFkbWluIjpmYWxzZX0.5F7yxZaA-7Wj0t7x3C5Lyj1vP5NVxUgtEuNvK7CzmKk"


def get_di_structures():
    r = requests.get(
        "https://api.data.inclusion.beta.gouv.fr/api/v0/structures",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}"
        }, )
    print(r)
    datasets = r.json()
    print(datasets)


def get_di_services():
    r = requests.get(
        "https://api.data.inclusion.beta.gouv.fr/api/v0/search/services?sources=dora&code_insee=15014&code_insee=79048&thematiques=mobilite",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}"
        }, )
    print(r)
    datasets = r.json()
    print(datasets)
    print(pd.DataFrame([item["service"] for item in datasets["items"]]))


if __name__ == '__main__':
    pd.set_option('display.max_columns', 15)
    pd.set_option('display.width', 2000)

    get_di_services()


