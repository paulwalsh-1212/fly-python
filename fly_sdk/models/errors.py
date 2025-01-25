from requests import Response

class FlyError(Exception):
    """Base exception for Fly SDK"""
    pass

class FlyAPIError(FlyError):
    """Exception raised when API requests fail"""
    
    def __init__(self, message: str, response: Response):
        self.message = message
        self.response = response
        self.status_code = response.status_code
        
        try:
            self.error_details = response.json()
        except:
            self.error_details = response.text
            
        super().__init__(self.message)
