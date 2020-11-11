import os
import requests
import re


class Indicators:
    username = os.environ.get('DHIS2_USER')
    password = os.environ.get('DHIS2_PASS')
    auth = requests.auth.HTTPBasicAuth(username, password)

    # receives @ind_arr array containing uids
    # @ returns an array list of indicators metadata
    def fetch_indicator(self, ind_arr):
        translated_inds = []
        for uid in ind_arr:
            request = requests.get(
                'https://hiskenya.org/api/indicators/' + uid + '.json',
                auth=self.auth
            )

            result = request.json()
            numerator = self.translate_formula(result.get('numerator'))
            denominator = self.translate_formula(result.get('denominator'))
            uid = result.get('id')
            name = result.get('name')
            last_updated = result.get('lastUpdated')
            translated_inds.append([uid, name, numerator, denominator, last_updated])
        return translated_inds

    def translate_formula(self, param):
        try:
            return int(param)
        except:
            uids_string = re.search('{(.*)}', param).group(1)
            # operator_index = [pos for pos, char in enumerate(uids_string) if char == '+' or char == '-'
            # or char == '/' or char == '(' or char == ')']
            uids = uids_string.split('} + #{')
            for uid in uids:
                request = requests.get(
                    'https://hiskenya.org/api/dataElements/' + uid.split('.')[0] + '.json',
                    auth=self.auth
                )
                uids_string = uids_string.replace(uid, request.json().get('name'))
            uids_string = uids_string.replace('}', '')
            uids_string = uids_string.replace('#{', '')
            return uids_string


if __name__ == '__main__':
    indicators = Indicators()
    print(indicators.fetch_indicator(['BvOQZuISXdw']))
