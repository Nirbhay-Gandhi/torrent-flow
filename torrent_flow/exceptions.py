class InvalidFileFormatError(ValueError):
    def __init__(self, file_name, message):
        self.file_name = file_name
        self.message = message

        """
        super().__init__(self.message) calls the __init__() method of the base ValueError class to 
        ensure the exception is properly initialized.        
        """
        super().__init__(self.message) 

    def __str__(self):
        return f'{self.message} - {self.file_name}'