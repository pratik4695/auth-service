class ApiException(Exception):
    """
    A base exception for API related exceptions. Inherit this class to create new API related exceptions
    Created By: Sohel Tarir
    Created On: 30/11/2015
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.message = kwargs.get('message')
        if self.message is None and self.args and self.args[0]:
            self.message = self.args[0]
        elif self.message is None:
            self.message = None
        self.status_code = kwargs.get('status_code', 500)
        self.error_type = kwargs.get('error_type', self.__class__.__name__)


class InvalidMobileNumber(ApiException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_code = 400
        self.error_type = self.__class__.__name__