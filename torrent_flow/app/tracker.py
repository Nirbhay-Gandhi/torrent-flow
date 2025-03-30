from flask import Flask, request, jsonify

app = Flask(__name__)

"""
- To keep the track of the files and with how many people they are present in the swarm
- Format: {info_hash: [{"ip": str, "port": int, "peer_id": str}]}
- ex: 
'file-1'-PeerA, PeerB | 'file-2'-PeerC, PeerD | 'file-3'-PeerF 
- swarms = { 'file-1' [{'PeerA_details'}, {'PeerB_details'}], 
             'file-2' [{'PeerC_details'}, {'PeerD_details'}], 
             'file-3' [{'PeerF_details'}]  }
- The tracker will be able to handle multiple torrents and multiple peers for each torrent.
"""
swarms = {}  # 


@app.route('/')
def index():
    return "Torrent Tracker is running!"


@app.route('/announce', methods=['GET'])
def announce():
    try:
        print(f'args: {request.args}')  # Log the request parameters for debugging

        # Extract query parameters
        info_hash = request.args.get('info_hash')
        peer_id = request.args.get('peer_id')
        ip = request.remote_addr  # Peer's IP address
        port = int(request.args.get('port'))

        # Initialize swarm if it doesn't exist
        if info_hash not in swarms:
            swarms[info_hash] = []

        # Add/update peer in the swarm
        peer_info = {"ip": ip, "port": port, "peer_id": peer_id}
        if peer_info not in swarms[info_hash]:
            swarms[info_hash].append(peer_info)

        # Return peer list and sync interval
        return jsonify({
            "interval": 1800,  # Re-announce every 30 mins
            "peers": swarms[info_hash]
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/view', methods=['GET'])
def view():
    """View the current state of swarms."""
    return jsonify(swarms)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Run tracker on port 5000