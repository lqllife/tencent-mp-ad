class WxError(Exception):
    def __init__(self, ErrorInfo, ErrorCode=0):
        super().__init__(self)
        self.errorinfo = ErrorInfo
        self.errorcode = ErrorCode
    
    def __str__(self):
        return self.errorinfo
