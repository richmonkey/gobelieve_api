import requests

class FS:
    HOST = None
    PORT = None
    @classmethod
    def upload(self, path, data):
        url = "http://%s:%d/upload%s"%(HOST, PORT, path)
        resp = requests.post(url, data)
        return resp.status_code == 200

    @classmethod
    def download(self, path):
        url = "http://%s:%d%s"%(HOST, PORT, path)
        resp = requests.get(path)
        return resp.content if resp.status_code == 200 else ""
