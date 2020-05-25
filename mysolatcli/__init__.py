"""
A wrapper around the api.azanpro.com
"""
import requests,time
import requests_cache
from datetime import datetime,timedelta

def secondsinday():
    time_delta = datetime.combine(
        datetime.now().date() + timedelta(days=1), datetime.strptime("0000", "%H%M").time()
    ) - datetime.now()
    return time_delta.seconds

requests_cache.install_cache('mysolat_cache',expire_after=secondsinday())

__version__ = '1.1.0'

class SolatAPIError(Exception):
    """Raised when API fails"""
    pass

class SolatError(SolatAPIError):
    """Raised when API fails"""
    def __init__(self, expression, message=""):
        self.expression = expression
        self.message = message

class SolatAPI:

    BASE_URL = 'http://api.azanpro.com'

    def __init__(self, user_agent='Python SolatAPI Client/{}'.format(__version__)):
        self.headers = {'User-Agent': user_agent}

    @staticmethod
    def _validate_response(response):
        if response['success'] != '1' and response['success'] != 1:
            message = "\n".join([ f"{k}: {v}" for k,v in response.items() ])
            raise SolatAPIError("success != 1", message=message)
        return response

    def get_zones(self) -> dict:
        return requests.get(self.BASE_URL + "/zone/zones.json", headers=self.headers).json()

    def get_negeri(self, state="") -> dict:
        return requests.get(self.BASE_URL + "/zone/grouped.json?state=" + state, headers=self.headers).json()
    
    def get_week(self, zone) -> dict:
        return requests.get(self.BASE_URL + "/times/this_week.json?format=24-hour&zone=" + zone, headers=self.headers).json()
    
    def get_today(self, zone) -> dict:
        return requests.get(self.BASE_URL + "/times/today.json?format=24-hour&zone=" + zone, headers=self.headers).json()
