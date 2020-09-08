#!/usr/bin/python3

# TODO: Update file structure in production to match the topo_build.yaml topology type and move these files to 'all'

import json
import tornado.websocket
from datetime import timedelta, datetime, timezone, date
from ruamel.yaml import YAML
from ConfigureTopology.ConfigureTopology import ConfigureTopology

DEBUG = False

class BackEnd(tornado.websocket.WebSocketHandler):
    connections = set()
    status = ''

    def open(self):
        self.connections.add(self)
        self.send_to_syslog('OK', 'Connection opened from {0}'.format(self.request.remote_ip))
        self.schedule_update()

    def on_message(self, message):
        data = json.loads(message)
        if data['type'] == 'openMessage':
            pass
        elif data['type'] == 'clientData':
            ConfigureTopology(selected_menu=data['selectedMenu'],selected_lab=data['selectedLab'])
        elif data['type'] == 'getStatus':
            self.send_status()

    def send_status(self):
        self.write_message(json.dumps({
            'type': 'serverData',
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': self.status
        }))


    def schedule_update(self):
        self.timeout = tornado.ioloop.IOLoop.instance().add_timeout(timedelta(seconds=60),self.keepalive)
          
    def keepalive(self):
        try:
            self.write_message(json.dumps({
                'type': 'keepalive',
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'data': 'ping'
            }))
        finally:
            self.schedule_update()

    def on_close(self):
        tornado.ioloop.IOLoop.instance().remove_timeout(self.timeout)
  
    def check_origin(self, origin):
      return True

    def send_to_socket(self,message):
        self.status = message
        self.write_message(json.dumps({
            'type': 'serverData',
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': message
        }))