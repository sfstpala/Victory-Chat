
import cherrypy
import modules.base
import os.path
import collections
import configparser

import modules.external.couch as couch


class Root (modules.base.Root):

    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.split(
        os.path.realpath(__file__))[0], "config.ini"))
    couchdb_prefix = config["database"]["prefix"]
    couchdb_server = config["database"]["host"]
    couchdb_username = config["database"]["username"]
    couchdb_password = config["database"]["password"]
    base_url = config["global"]["host"]

    def __init__(self):
        self.active_users = collections.defaultdict(collections.defaultdict)
        self.db = couch.Database(self.couchdb_username, self.couchdb_password,
            self.couchdb_server)
        # set up the databases in case they aren't there:
        self.db.request("PUT", "/%s_users" % self.couchdb_prefix)
        self.db.request("PUT", "/%s_users/_design/by_num_id/" % (
            self.couchdb_prefix), body={
                '_id': "_design/by_num_id",
                'language': 'javascript',
                "views": {
                   "by_num_id": {
                        "map": "function (doc) { emit(doc[\"num_id\"], null); }"
                   }
               }
            })
        self.db.request("PUT", "/%s_users/_design/by_email/" % (
            self.couchdb_prefix), body={
                '_id': "_design/by_email",
                'language': 'javascript',
                "views": {
                   "by_email": {
                        "map": "function (doc) { emit(doc[\"email\"], doc[\"identity\"]); }"
                   }
               }
            })
        self.db.request("PUT", "/%s_users/_design/by_name/" % (
            self.couchdb_prefix), body={
                '_id': "_design/by_name",
                'language': 'javascript',
                "views": {
                   "by_name": {
                        "map": "function (doc) { emit(doc[\"name\"], doc[\"num_id\"]); }"
                   }
               }
            })
        self.db.request("PUT", "/%s_users/_design/by_msg_count/" % (
            self.couchdb_prefix), body={
                '_id': "_design/by_msg_count",
                'language': 'javascript',
                "views": {
                   "by_msg_count": {
                        "map": "function (doc) { emit(doc[\"num_id\"], doc[\"messages\"].length); }"
                   }
               }
            })
        self.db.request("PUT", "/%s_rooms" % self.couchdb_prefix)
        self.db.request("PUT", "/%s_rooms/_design/by_num_id/" % (
            self.couchdb_prefix), body={
                '_id': "_design/by_num_id",
                'language': 'javascript',
                "views": {
                   "by_num_id": {
                        "map": "function (doc) { emit(doc[\"num_id\"], null); }"
                   }
               }
            })
        self.db.request("PUT", "/%s_rooms/_design/by_msg_count/" % (
            self.couchdb_prefix), body={
                '_id': "_design/by_msg_count",
                'language': 'javascript',
                "views": {
                   "by_msg_count": {
                        "map": "function (doc) { emit(doc[\"num_id\"], doc[\"n_messages\"]); }"
                   }
               }
            })
        modules.base.Root.__init__(self)


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.split(
        os.path.realpath(__file__))[0], "config.ini"))
    cherrypy.quickstart(Root(), config={'global': {
        'tools.encode.encoding': 'utf8',
        'server.socket_host': config["httpd"]["host"],
        'server.socket_port': int(config["httpd"]["port"]),
    }})
