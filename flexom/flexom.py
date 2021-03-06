import requests
from time import time, sleep
from threading import Thread


class Flexom:
    def __init__(self, login, password):
        self._login = login
        self._password = password
        self._token = ''
        self._url = 'https://serene-turing-4cigeu08.eu-west.hemis.io/hemis/rest/'
        self._headers = {'Authorization': f'Bearer {self._token}'}
        self._master_password = self._signin()

        self._renew_token()
        Thread(target=self._renew_token_tread).start()

    def _signin(self):
        url = 'https://hemisphere.ubiant.com/users/signin'
        data = {
            "device":{
                "uid":"0",
                "name":"0",
                "model":"0",
                "operating_system":"0",
                "first_connection":0,
                "last_connection":0
                },
            "email":self._login,
            "password":self._password
        }
        r = requests.post(url, json=data).json()
        if 'message' in r:
            raise NameError(r['message'])

        master_token = r['token']
    
        url = 'https://hemisphere.ubiant.com/buildings/mine/infos'
        headers = {'Authorization': f'Bearer {master_token}'}
        r = requests.get(url, headers=headers).json()

        return r[0]['authorizationToken']

    def _renew_token(self):
        endpoint = 'WS_UserManagement/login'
        data = {'email':self._login, 'password':self._master_password, 'kernelId':'hemis4'}
        r = self._post(endpoint=endpoint, data=data, form_type='data')
        self._token = r['token']
        self._headers = {'Authorization': f'Bearer {self._token}'}

    def _renew_token_tread(self):
        while True:
            sleep(1800) # 30 minutes
            self._renew_token()

    def _get(self, endpoint):
        return requests.get(self._url+endpoint, headers=self._headers).json()

    def _put(self, endpoint, data, form_type='json'):
        if form_type == 'json':
            return requests.put(self._url+endpoint, json=data, headers=self._headers)
        elif form_type == 'data':
            return requests.put(self._url+endpoint, data=data, headers=self._headers)

    def _post(self, endpoint, data, form_type='json'):
        if form_type == 'json':
            return requests.post(self._url+endpoint, json=data, headers=self._headers)
        elif form_type == 'data':
            return requests.post(self._url+endpoint, data=data, headers=self._headers).json()

    def _get_actuators(self, room_id):
        endpoint = f'WS_ReactiveEnvironmentDataManagement/{room_id}/BRI/actuators'
        r = self._get(endpoint=endpoint)
        return [i['state'] for i in r if 'message' not in r]

    def get_list(self):
        endpoint = 'WS_ZoneManagement/list'
        r = self._get(endpoint=endpoint)
        rooms = [i for i in r if i['type']!=None]
        rooms_dict = {}

        for r in rooms:
            room_actuators = self._get_actuators(r['id'])
            actuators = [{'actuatorIds':a['actuatorId'], 'itId':a['itId']} for a in room_actuators]
            rooms_dict[r['id']] = {
                'name':r['name'],
                'actuators':actuators
            }
             
        return rooms_dict

    def set_light(self, actuatorIds, itId, state):
        endpoint = 'intelligent-things/actuators/state'
        data = {
            'pref':{'duration':4E+12, 'value':state},
            'actuators':[{'actuatorIds':[actuatorIds],'itId':itId}]
        }
        self._put(endpoint=endpoint, data=data)

    def get_light(self, room_id, itId):
        r = self._get_actuators(room_id=room_id)
        for actuator in r:
            if actuator['itId'] == itId:
                return bool(actuator['value'])
        return None

    def set_shutter(self, room_id, value):
        endpoint = f'WS_ReactiveEnvironmentDataManagement/{room_id}/settings/BRIEXT/value'
        data = {'value':value}
        self._put(endpoint=endpoint, data=data, form_type='data')

    def get_consumption(self):
        endpoint = 'WS_ReactiveEnvironmentDataManagement/list?factorsFilter=CPOW'
        r = self._get(endpoint=endpoint)
        for zone in r:
            if 'MyHemis' in zone['zone']['id']:
                last_update = int(abs(zone['values'][0]['timestamp']/1000-time()))
                return {'CPOW':zone['values'][0]['value'], 'last_update_duration':last_update}
