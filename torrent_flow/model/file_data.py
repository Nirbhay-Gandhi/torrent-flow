
class TorrentFileData:
    def __init__(self, torrent_data_dict):
        self.torrent_data_dict = torrent_data_dict
        self.parse_file_data(torrent_data_dict)
        self.peek_file_data()

    def parse_file_data(self, torrent_data_dict):
        self.announce = torrent_data_dict.get('announce')
        self.announce_list = torrent_data_dict.get('announce-list')
        self.comment = torrent_data_dict.get('comment')
        self.created_by = torrent_data_dict.get('created by')
        self.creation_date = torrent_data_dict.get('creation date')
        self.encoding = torrent_data_dict.get('encoding')

        info_dict = torrent_data_dict.get('info')
        self.info_length = info_dict.get('length')
        self.info_name = info_dict.get('name')
        self.info_piece_length = info_dict.get('piece length')
        self.info_pieces = info_dict.get('pieces')
    
    def peek_file_data(self):
        display_piece = self.info_pieces
        display_piece = display_piece[:20]

        small_data =  {
            "announce": self.announce,
            "announce_list": self.announce_list,
            "comment": self.comment,
            "created_by": self.created_by,
            "creation_date": self.creation_date,
            "encoding": self.encoding,
            "info_length": self.info_length,
            "info_name": self.info_name,
            "info_piece_length": self.info_piece_length,
            "info_pieces": display_piece  # Only show the first 20 characters of the pieces hash
        }
        print(small_data)

    
    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            print(f"Key '{key}' does not exist, chave a look at the file data")
            self.peek_file_data()
            return ''
