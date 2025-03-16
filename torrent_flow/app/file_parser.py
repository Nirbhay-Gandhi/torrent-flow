from torrent_flow.exceptions import InvalidFileFormatError


class TorrentFileParser: 
    def __init__(self,file_path):
        self.file_path = file_path
        self.set_file_name()
        self.validate_file_extension()

    def set_file_name(self):
        self.file_name = ''
        if self.file_path.find('/') != -1:
            self.file_name = self.file_path.split('/')[-1]
        else:
            self.file_name = self.file_path.split('\\')[-1]

    def get_file_name(self):
        return self.file_name
    
    def get_file_path(self):
        return self.file_path
    
    def validate_file_extension(self):
        if not self.file_name.endswith('.torrent'):
            raise InvalidFileFormatError(self.file_name, 'Invalid file extension, supported file extension is .torrent')

    def decode_bencoded_file(self):
        with open(self.file_path, 'rb') as f:
            data = f.read()
        return data 
