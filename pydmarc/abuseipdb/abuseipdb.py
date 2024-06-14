import requests
import json
import pydmarc.common
import pandas as pd
from pydmarc.common.log import logger

class AbuseIPDB:
    abuseipdb_key: str
    ipgeo_key: str
    metadata: dict
    META_IPDB = []
    META_IPDB.clear()
    
    def __init__(self, metadata):
        self.metadata = metadata
        pydmarc.common.config.read(pydmarc.common.CONFIG_FILE)
        abuseipdb_settings = pydmarc.common.config['AbuseIPDB']
        self.abuseipdb_key = abuseipdb_settings['ApiKey']
        ipgeo_settings = pydmarc.common.config['IPGeolocation']
        self.ipgeo_key = ipgeo_settings['ApiKey']
    
    async def consult_abuse_ipdb_database(self):
        try:
            df = pd.DataFrame(self.metadata)
            ips = df.source_ip.unique()
        except Exception as e:
            logger.error(e)
            print(e)
    
        for ip in ips:
            try:
                # Defining the api-endpoint
                url_abuseipdb = 'https://api.abuseipdb.com/api/v2/check'
                
                querystring = {
                    'ipAddress': ip,
                    'maxAgeInDays': '30'
                }

                headers = {
                    'Accept': 'application/json',
                    'Key': self.abuseipdb_key
                }
                logger.info("URL Requested - {} {}".format(url_abuseipdb,querystring))
                response_abuseipdb = requests.request(method='GET', url=url_abuseipdb, headers=headers, params=querystring)
                if response_abuseipdb.status_code == 200:
                    decoded_response_abuseipdb = json.loads(response_abuseipdb.text)
                    logger.info("URL Response - {} - Status Code {}".format(url_abuseipdb,response_abuseipdb.status_code))
                else:
                    raise Exception("The request returned status code {}".format(response_abuseipdb.status_code)) # Alterar
                
                
                _url_geoip = 'https://api.ipgeolocation.io/ipgeo'
                params = '?apiKey={}&ip={}'.format(self.ipgeo_key,ip)
                url_geoip = _url_geoip + params
                logger.info("URL Requested - {}&ip={}".format(_url_geoip,ip))

                response_geoip = requests.get(url_geoip)
                if response_geoip.status_code == 200:
                    decoded_response_geoip = json.loads(response_geoip.text)
                    logger.info("URL Response - {} - Status Code {}".format(_url_geoip,response_geoip.status_code))
                else:
                    raise Exception("The request returned status code {}".format(response_geoip.status_code)) # Alterar
                
                dict_meta = decoded_response_abuseipdb['data']
                if len(dict_meta['hostnames']) > 1:
                    dict_meta['hostnames'] = dict_meta['hostnames'][0]
                temp = {'latitude': decoded_response_geoip['latitude'], 'longitude': decoded_response_geoip['longitude'] }
                dict_meta.update(temp)
                self.META_IPDB.append(dict_meta)
            except Exception as e:
                logger.error(e)
                continue
        return self.META_IPDB