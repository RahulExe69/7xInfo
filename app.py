from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
from cachetools import TTLCache
import lib2
import json
import asyncio

app = Flask(__name__)
CORS(app)

# Create a cache with a TTL of 300 seconds
cache = TTLCache(maxsize=100, ttl=300)

def cached_endpoint(ttl=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = (request.path, tuple(request.args.items()))
            if cache_key in cache:
                return cache[cache_key]
            else:
                result = func(*args, **kwargs)
                cache[cache_key] = result
                return result
        return wrapper
    return decorator

# Add root endpoint
@app.route('/')
def home():
    return jsonify({
        "status": "active",
        "endpoint": "/api/account?uid=<player_id>&region=<region_code>",
        "supported_regions": lib2.SUPPORTED_REGIONS
    })

# Modified API endpoint with strict_slashes=False
@app.route('/api/account', strict_slashes=False)
@cached_endpoint()
def get_account_info():
    region = request.args.get('region')
    uid = request.args.get('uid')
    
    if not uid:
        return jsonify({
            "error": "Invalid request",
            "message": "Missing 'uid' parameter"
        }), 400

    if not region:
        return jsonify({
            "error": "Invalid request",
            "message": "Missing 'region' parameter"
        }), 400

    return_data = asyncio.run(lib2.GetAccountInformation(
        uid, 
        "7", 
        region.upper(), 
        "/GetPlayerPersonalShow"
    ))
    
    return jsonify(return_data)

if __name__ == '__main__':
    app.run(port=3000, host='0.0.0.0', debug=True)
