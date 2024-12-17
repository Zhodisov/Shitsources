import requests

print('Enter key: ', end='')
key = input()

print('Enter uuid: ', end='')
uuid = input()

token = 'moha333400555'

print(key.encode(), uuid.encode())
s = requests.Session()
s.headers.update({
    'Host': 'tfmdisney.herokuapp.com',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) disneyclient/1.1.5 Chrome/91.0.4472.124 Electron/13.1.7 Safari/537.36',
    'Accept': '*/*',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://tfmdisney.herokuapp.com/',
    'Accept-Encoding': 'gzip, deflate'
})

s.get('https://tfmdisney.herokuapp.com/')
data = s.get('https://tfmdisney.herokuapp.com/api/auth', params={'key': key, 'uuid': uuid}).json()
if not data.get('success'):
    print('[fail]', data)
else:

    token = data.get('access_token')

    print('URL:', 'https://tfmdisney.herokuapp.com/transformice?access_token=' + token)

x = input()