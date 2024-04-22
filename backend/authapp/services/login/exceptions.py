class WrongTempCode(Exception):
    pass


class TempCodeDoesNotExist(Exception):
    pass


class TempCodeMaxRetryAttempts(Exception):
    pass


class TempCodeExpired(Exception):
    pass
