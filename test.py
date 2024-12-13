import requests

def testRequest():
    data = {"text": "你好", "request_id": "4000517517", "rank": 0}
    headers = {"Content-Type": "application/json"}

    response = requests.post("http://183.131.7.9:5011/tts", json=data, headers=headers)

    json=response.json()

    print(json['path'])

if __name__ == "__main__":
    testRequest()