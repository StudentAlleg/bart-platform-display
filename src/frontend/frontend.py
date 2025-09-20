import requests

if __name__ == "__main__":
    response: requests.Response = requests.put("http://127.0.0.1:5000/stop/C50-1")
    print(response.status_code)
    print(response.content)