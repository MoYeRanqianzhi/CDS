import requests
import os

def URL(host, port):
    return f'http://{host}:{port}/upload/file'


def upload(file, url):
    if requests.post(url=url, files={'file': file}).status_code == 200:
        return True
    else:
        return False


def CDF(path, host, port):
    """
    本地文件呈递
    Parameters:
        path(str):
        host(str):
        port(int):
    """
    if not os.path.exists(path):
        return False
    if not os.path.isfile(path):
        return False
    with open(file=path, mode='rb') as f:
        return upload(file=f, url=URL(host=host, port=port))


def CDW(webURL, host, port):
    """
    网络文件呈递
    Parameters:
        webURL(str):
        host(str):
        port(int):
    """
    resource = requests.get(webURL)
    if resource.status_code == 200:
        return upload(file=(webURL.split('/')[-1], resource.content), url=URL(host=host, port=port))
    else:
        return False
