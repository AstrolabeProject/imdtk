class RequestException (Exception):
    status_code = 400

    def __init__(self, message, status_code=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        retdict = dict()
        retdict['status_code'] = self.status_code
        retdict['message'] = self.message
        return retdict

    def to_tuple(self):
        return (self.message, self.status_code)


class FileNotFound (Exception):
    status_code = 404

    def __init__(self, message, status_code=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        retdict = dict()
        retdict['status_code'] = self.status_code
        retdict['message'] = self.message
        return retdict

    def to_tuple(self):
        return (self.message, self.status_code)


class ProcessingException (Exception):
    status_code = 500

    def __init__(self, message, status_code=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        retdict = dict()
        retdict['status_code'] = self.status_code
        retdict['message'] = self.message
        return retdict

    def to_tuple(self):
        return (self.message, self.status_code)
