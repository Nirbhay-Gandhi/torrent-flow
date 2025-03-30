import asyncio
import logging
import random
from typing import List, Dict, Set
from urllib.parse import urlencode
import aiohttp
from .peer_protocol import PeerProtocol, MessageType, PeerMessage
from .piece_manager import PieceManager

logging.basicConfig(level=logging.INFO)

class TorrentClient:
    def __init__(self, tracker_url: str, info_hash: bytes, peer_id: bytes,
                 pieces: List[bytes], piece_length: int, total_length: int,
                 port: int = 6881):
        self.tracker_url = tracker_url
        self.info_hash = info_hash
        self.peer_id = peer_id
        self.port = port

        # Initialize managers
        self.piece_manager = PieceManager(pieces, piece_length, total_length)
        self.peers: Dict[str, PeerProtocol] = {}
        self.peer_connections: Dict[str, asyncio.StreamWriter] = {}

        # Download state
        self.uploaded = 0
        self.downloaded = 0
        self.left = total_length

    async def start(self):
        """Start the torrent client"""
        try:
            # Start peer connection manager
            asyncio.create_task(self._manage_peers())
            
            # Start main download loop
            while self.left > 0:
                await self._announce('started' if not self.peers else None)
                await asyncio.sleep(30)  # Wait before next announce

        except Exception as e:
            logging.error(f'Client error: {str(e)}')
            await self._announce('stopped')

    async def _announce(self, event: str = None):
        """Send announce request to tracker"""
        params = {
            'info_hash': self.info_hash,
            'peer_id': self.peer_id,
            'port': self.port,
            'uploaded': self.uploaded,
            'downloaded': self.downloaded,
            'left': self.left,
            'compact': 1
        }
        if event:
            params['event'] = event

        url = f'{self.tracker_url}?{urlencode(params)}'
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self._handle_announce_response(data)
                    else:
                        logging.error(f'Tracker announce failed: {response.status}')
        except Exception as e:
            logging.error(f'Tracker announce error: {str(e)}')

    async def _handle_announce_response(self, response: dict):
        """Handle tracker announce response"""
        if 'failure reason' in response:
            logging.error(f'Tracker error: {response["failure reason"]}')
            return

        # Connect to new peers
        for peer in response.get('peers', []):
            peer_id = peer.get('peer_id')
            if peer_id not in self.peers:
                host = peer.get('ip')
                port = peer.get('port')
                asyncio.create_task(self._connect_peer(host, port))

    async def _connect_peer(self, host: str, port: int):
        """Establish connection with a peer"""
        try:
            reader, writer = await asyncio.open_connection(host, port)
            
            # Send handshake
            protocol = PeerProtocol(self.info_hash, self.peer_id)
            writer.write(protocol.create_handshake())
            await writer.drain()

            # Receive and verify handshake
            data = await reader.read(68)
            info_hash, peer_id = protocol.parse_handshake(data)
            
            if info_hash != self.info_hash:
                writer.close()
                await writer.wait_closed()
                return

            # Store peer connection
            peer_addr = f'{host}:{port}'
            self.peers[peer_addr] = protocol
            self.peer_connections[peer_addr] = writer

            # Start peer message handler
            asyncio.create_task(self._handle_peer_messages(peer_addr, reader))

        except Exception as e:
            logging.error(f'Peer connection error ({host}:{port}): {str(e)}')

    async def _handle_peer_messages(self, peer_addr: str, reader: asyncio.StreamReader):
        """Handle incoming messages from a peer"""
        try:
            while True:
                # Read message length
                length_prefix = await reader.read(4)
                if not length_prefix:
                    break

                length = int.from_bytes(length_prefix, 'big')
                if length > 0:
                    message_data = await reader.read(length)
                    if not message_data:
                        break

                    protocol = self.peers[peer_addr]
                    message = protocol.parse_message(length_prefix + message_data)
                    
                    if message:
                        await self._process_message(peer_addr, message)

        except Exception as e:
            logging.error(f'Peer message handling error ({peer_addr}): {str(e)}')
        finally:
            await self._disconnect_peer(peer_addr)

    async def _process_message(self, peer_addr: str, message: PeerMessage):
        """Process a peer message"""
        protocol = self.peers[peer_addr]
        protocol.handle_message(message)

        if message.type == MessageType.BITFIELD:
            self.piece_manager.add_peer(peer_addr.encode(), message.payload)
        elif message.type == MessageType.HAVE:
            piece_index = int.from_bytes(message.payload, 'big')
            self.piece_manager.update_peer_have(peer_addr.encode(), piece_index)
        elif message.type == MessageType.PIECE:
            # Handle received piece data
            if len(message.payload) >= 8:
                index = int.from_bytes(message.payload[0:4], 'big')
                begin = int.from_bytes(message.payload[4:8], 'big')
                block = message.payload[8:]
                
                if self.piece_manager.handle_block(index, begin, block):
                    self.downloaded += len(block)
                    self.left = max(0, self.left - len(block))

    async def _disconnect_peer(self, peer_addr: str):
        """Disconnect from a peer"""
        if peer_addr in self.peer_connections:
            writer = self.peer_connections.pop(peer_addr)
            writer.close()
            await writer.wait_closed()
        
        self.peers.pop(peer_addr, None)
        self.piece_manager.remove_peer(peer_addr.encode())

    async def _manage_peers(self):
        """Manage peer connections and piece requests"""
        while True:
            for peer_addr, protocol in self.peers.items():
                if not protocol.peer_choking:
                    # Request next piece from peer
                    next_request = self.piece_manager.next_request(peer_addr.encode())
                    if next_request:
                        piece_index, begin, length = next_request
                        payload = (
                            piece_index.to_bytes(4, 'big') +
                            begin.to_bytes(4, 'big') +
                            length.to_bytes(4, 'big')
                        )
                        message = protocol.create_message(MessageType.REQUEST, payload)
                        
                        if peer_addr in self.peer_connections:
                            writer = self.peer_connections[peer_addr]
                            writer.write(message)
                            await writer.drain()

            await asyncio.sleep(1)  # Throttle request rate