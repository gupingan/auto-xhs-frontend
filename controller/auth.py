import time
import pytz
import hashlib
import hmac
from datetime import datetime


def getGPASign(secret_key, api_path):
    gpa_t = int(time.mktime(datetime.now(pytz.utc).timetuple()))
    message = f"{api_path}:{gpa_t}"
    gpa_s = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()
    return gpa_s, gpa_t
