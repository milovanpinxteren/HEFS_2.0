import warnings
from datetime import datetime

from hefs.models import ErrorLogDataGerijptebieren


class ErrorHandler():
    def log_error(self, message):
        warnings.filterwarnings("ignore")
        ErrorLogDataGerijptebieren.objects.create(error_message=message, timestamp=datetime.now())
        print(message)