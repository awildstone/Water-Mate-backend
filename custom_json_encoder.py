""" Custom JSON Encoder. """

from flask.json import JSONEncoder
from datetime import datetime, timedelta
import decimal

class CustomJSONEncoder(JSONEncoder):
  """Converts timedelta and decimal to string for JSON responses."""

  def default(self, o):
    if isinstance(o, decimal.Decimal):
        return str(o)
    elif type(o) == timedelta:
      return str(o)
    elif type(o) == datetime:
      return o.isoformat()
    else:
      return super().default(o)