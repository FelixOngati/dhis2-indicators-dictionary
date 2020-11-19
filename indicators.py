import os
import requests
import re
import csv


class Indicators:
    username = os.environ.get('DHIS2_USER')
    password = os.environ.get('DHIS2_PASS')
    auth = requests.auth.HTTPBasicAuth(username, password)
    filename = ''

    def indicator_group_metadata(self, uid):
        request = requests.get(
            'https://hiskenya.org/api/indicatorGroups/' + uid + '.json',
            auth=self.auth
        )
        inds = []
        for indicator in request.json().get('indicators'):
            inds.append(indicator.get('id'))
        self.filename = request.json().get('name') + "_indicators.csv"
        self.create_csv(self.filename)
        return self.fetch_indicator(inds)

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
            self.add_to_csv([uid, name, numerator, denominator, last_updated])
            translated_inds.append([uid, name, numerator, denominator, last_updated])
        return translated_inds

    def translate_formula(self, param):
        uids_string = param
        try:
            print(param)
            return int(param)
        except:
            for item in param.split():
                uid = re.findall('{(.*)}', item)
                if uid:
                    request = requests.get(
                        'https://hiskenya.org/api/dataElements/' + uid[0].split('.')[0] + '.json',
                        auth=self.auth
                    )
                    uids_string = uids_string.replace(uid[0], request.json().get('name'))
            uids_string = uids_string.replace('}', '')
            uids_string = uids_string.replace('#{', '')
            print(uids_string)
            return uids_string

    def create_csv(self, filename):
        ''' create a new csv file'''
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(
                ['uid', 'name', 'numerator', 'denominator', 'last_updated']
            )
        print("File Created")

    def add_to_csv(self, details):
        ''' add data to the csv file '''
        with open(self.filename, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(details)


if __name__ == '__main__':
    indicators = Indicators()
    # receives indicator group as uid
    print(indicators.indicator_group_metadata('LfgaY9O4EP8'))
