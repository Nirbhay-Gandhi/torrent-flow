import json
import bencodepy
import base64
from torrent_flow.exceptions import InvalidFileFormatError
from torrent_flow.model.file_data import TorrentFileData

class TorrentFileParser: 
    def __init__(self,file_path):
        self.file_path = file_path
        self.data_handler = None

        self.set_file_name()
        self.validate_file_extension()
        self.decode_bencoded_file()


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

    def decode_bytes(self, data):
        if isinstance(data, bytes):
            try:
                # Try decoding as UTF-8 (for text fields)
                return data.decode("utf-8")
            except UnicodeDecodeError:
                # If it fails, encode as Base64 (for binary fields)
                return base64.b64encode(data).decode("utf-8")
        elif isinstance(data, dict):
            return {self.decode_bytes(key): self.decode_bytes(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.decode_bytes(item) for item in data]
        else:
            return data  # Return as-is for int, float, bool, None, etc.
    

    def decode_bencoded_file(self):
        with open(self.file_path, 'rb') as f:
            torrent_data = f.read()

        decoded_data = bencodepy.decode(torrent_data)

        decoded_data = self.decode_bytes(decoded_data)  # Convert bytes to strings

        torrent_json = json.dumps(decoded_data, indent=4) #convert json file to dict

        with open('decoded_torrent.json', 'w') as json_file:
            json_file.write(torrent_json)

        torrent_json_dict = json.loads(torrent_json)
        self.data_handler = TorrentFileData(torrent_json_dict)

    
    def get_file_attribute(self, attribute):
        return self.data_handler[attribute]