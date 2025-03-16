# torrent_flow/run.py
import sys
import os

# Add the project root (torrent-flow/) to Python's search path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Now import from the torrent_flow package
import  torrent_flow.app.file_parser as tfp

# path = "C:\\Users\\DELL-LAPTOP\\Downloads\\ubuntu.torrent"
path = "D:\\3. PROJECTS\\Bit torrent clone\\torrent-flow\\assets\\planet-250310.osm.pbf.torrent"

if __name__ == "__main__":
    tfp = tfp.TorrentFileParser(path)
