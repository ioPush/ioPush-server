#!/home/oliv/python/ioPush-server/virtualenv/bin/python
import sys
# TODO - Add it at the installation
sys.path.append('/Path/To/ioPush-server/')
from flipflop import WSGIServer
from app import app

if __name__ == '__main__':
    WSGIServer(app).run()
