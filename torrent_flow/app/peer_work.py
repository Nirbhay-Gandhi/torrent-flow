class Peer:
    def announce_to_tracker(self):
        # HTTP GET to tracker
        pass

    def connect_to_peer(self):
        # TCP handshake + message exchange
        pass

    def download_piece(self):
        # Request piece from peers + validate hash
        pass

    def upload_piece(self):
        # Send piece data to requesting peer
        pass