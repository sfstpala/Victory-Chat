
import time
import json
import cherrypy
import markdown
import urllib.parse
import functools
import collections
import hashlib


def jsonify(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        cherrypy.response.headers["Content-Type"] = "application/json"
        return json.dumps(function(*args, **kwargs)).encode()
    return wrapper


class ChatMixIn (object):

    def create_new_room(self, room):
        self.db.request("POST", "/%s_rooms/" %
            (self.couchdb_prefix), body=room)
        self.db.request("PUT", "/%s_room_%s_messages" % (
            self.couchdb_prefix, room["num_id"]))
        self.db.request("PUT", "/%s_room_%s_messages/_design/messages/" % (
            self.couchdb_prefix, room["num_id"]), body={
                '_id': "_design/by_date",
                'language': 'javascript',
                "views": {
                   "by_date": {
                        "map": "function (doc) { emit(doc[\"date\"], doc); }"
                   }
               }
            })
        self.db.request("PUT", "/%s_room_%s_messages/_design/highlight/" % (
            self.couchdb_prefix, room["num_id"]), body={
                '_id': "_design/user_by_message",
                'language': 'javascript',
                "views": {
                   "user_by_message": {
                        "map": "function (doc) { emit(doc[\"num_id\"], doc[\"user\"]); }"
                   }
               }
            })
        return room["num_id"]

    def find_room(self, num_id):
        rooms = self.db.request("GET", "/%s_rooms/_design/"
            "by_num_id/_view/by_num_id/" % self.couchdb_prefix)
        s = [i for i in rooms['rows'] if i["key"] == num_id]
        return self.db.request("GET", "/%s_rooms/%s" %
            (self.couchdb_prefix, s[0]['id'])) if s else None

    def get_n_rooms(self):
        try:
            return len(self.db.request("GET", ("/%s_rooms/_design/by_msg_count/"
                "_view/by_msg_count/") % self.couchdb_prefix)["rows"])
        except KeyError:
            return 0

    @cherrypy.expose
    def post_message(self, room, message):
        if cherrypy.request.method != "POST":
            raise cherrypy.HTTPError(400)
        user = self.get_user()
        if not user:
            raise cherrypy.HTTPError(402)
        reply, highlight, prepend = None, [], None
        if message.startswith("::") and " " in message:
            reply = message.split()[0][2:]
            r_msg = self.find_message(room, reply)
            if r_msg:
                message = message.replace("::" + reply, "")
                highlight = [r_msg]
                p = self.find_user(r_msg)
                if p:
                    if p["name"]:
                        p = ("@" + p["name"].split()[0])
                    else:
                        p = "@User" + p["num_id"]
                    prepend = p
            else:
                reply = None
        for i in [j[1:] for j in message.lower().split() if j.startswith("@")]:
            u = list(self.find_user_by_name(''.join(j for j in i if j in
                "abcdefghijklmnopqrstuvwxyz")))
            if u:
                highlight.extend(u)
        self.update_user(user["_id"], {'last_seen_date': time.time()})
        message = {
            'raw': self.safe(message),
            'markdown': self.onebox_html(self.markdown(self.onebox(message))),
            'date': time.time(),
            'user': user["num_id"],
            'num_id': self.get_num_id(),
            'stars': [],
            'reply_to': reply,
            'highlight': highlight,
            'prepend': prepend,
        }
        self.inc_message_count(room)
        self.do_get_messages.cache_clear()
        self.db.request("POST", "/%s_room_%s_messages/" %
            (self.couchdb_prefix, room), body=message)

    def find_user_by_name(self, name):
        users = self.db.request("GET", "/%s_users/_design/"
            "by_name/_view/by_name/" % self.couchdb_prefix)
        name = ''.join(i for i in name.lower() if i in
            "abcdefghijklmnopqrstuvwxyz0123456789")
        if "rows" in users:
            for i in users["rows"]:
                n, i = i["key"], i["value"]
                if n and name.strip() == n.split()[0].lower().strip():
                    yield i

    def find_message(self, room, num_id):
        r = self.db.request("POST", ("/%s_room_%s_messages/_design/" +
            "highlight/_view/user_by_message/") %
            (self.couchdb_prefix, room))
        if "rows" in r:
            r = [i for i in r["rows"] if i["key"] == num_id]
            return r[0]["value"] if r else None

    def markdown(self, content):
        return markdown.markdown(content, safe_mode="escape")

    @jsonify
    @cherrypy.expose
    def read_messages(self, room="", last_atime=""):
        if self.get_user():
            self.active_users[room][self.get_user()["num_id"]] = time.time()
            return self.do_get_messages(room, last_atime)
        raise cherrypy.HTTPError(404)

    @functools.lru_cache(100)
    def do_get_messages(self, room, last_atime):
        if float(last_atime) <= 1:
            last_atime = time.time() - (60 * 60 * 24 * 7)
        user = self.get_user()
        if not user:
            raise cherrypy.HTTPError(404)
        room_data = self.find_room(room)
        if room_data["type"] == "private" and user["num_id"] not in room_data["users"]:
            raise cherrypy.HTTPError(404)
        data = self.db.request("GET", ("/%s_room_%s_messages/"
            "_design/messages/_view/by_date/?startkey=%s") % (
            self.couchdb_prefix, room, json.dumps(float(last_atime))))
        if "rows" in data:
            data = [i['value'] for i in data["rows"]]
        else:
            data = []
        data = list(sorted(data, key=lambda x: x["date"]))
        if len(data) >= 50:
            data = data[-50:]
        for i in data:
            i['user'] = self.find_user(i["user"])
            del i["user"]["email"]
            del i["user"]["identity"]
            del i["user"]["website"]
            del i["user"]["creation_date"]
            del i["user"]["openid_provider"]
            del i["user"]["country"]
            del i["user"]["_rev"]
            del i["user"]["messages"]
            del i["user"]["last_login_date"]
            del i["user"]["last_login_ip"]
            del i["user"]["about_me"]
            del i["user"]["owns_rooms"]
            del i["user"]["birthday"]
            del i["user"]["last_seen_date"]
            i["user"]["name"] = self.safe(i["user"]["name"])
        if data:
            last_atime = max(i["date"] for i in data)
        for i in data:
            i["nice_date"] = time.strftime("%Y-%m-%d %H:%MZ", time.gmtime(i["date"]))
        return {'last_atime': last_atime, 'data': data}

    def inc_message_count(self, num_id):
        room = self.find_room(num_id)
        room["n_messages"] += 1
        self.db.request("PUT", "/%s_rooms/%s" % (
            self.couchdb_prefix, room["_id"]), body=room)

    @cherrypy.expose
    def star(self, room, message_id):
        user = self.get_user()
        if not user:
            raise cherrypy.HTTPError(404)
        d = self.db.request("GET", "/%s_room_%s_messages/%s" % (
            self.couchdb_prefix, room, message_id))
        if user["num_id"] not in d["stars"] and user["num_id"] != d["user"]:
            d["stars"].append(user["num_id"])
            self.get_starred.cache_clear()
        self.db.request("PUT", "/%s_room_%s_messages/%s" % (
            self.couchdb_prefix, room, message_id), body=d)
        cherrypy.response.headers["Content-Type"] = "application/json"
        return json.dumps(True).encode()

    @cherrypy.expose
    def unstar(self, room, message_id):
        user = self.get_user()
        if not user:
            raise cherrypy.HTTPError(404)
        d = self.db.request("GET", "/%s_room_%s_messages/%s" % (
            self.couchdb_prefix, room, message_id))
        if user["num_id"] in d["stars"]  and user["num_id"] != d["user"]:
            d["stars"].remove(user["num_id"])
            self.get_starred.cache_clear()
        self.db.request("PUT", "/%s_room_%s_messages/%s" % (
            self.couchdb_prefix, room, message_id), body=d)
        cherrypy.response.headers["Content-Type"] = "application/json"
        return json.dumps(True).encode()

    @jsonify
    @cherrypy.expose
    @functools.lru_cache(100)
    def get_starred(self, room=""):
        if self.get_user():
            last_atime = time.time() - (60 * 60 * 24)
            data = self.db.request("GET", ("/%s_room_%s_messages/"
                "_design/messages/_view/by_date/?startkey=%s") % (
                self.couchdb_prefix, room, json.dumps(float(last_atime))))
            if "rows" in data:
                data = [i['value'] for i in data["rows"]]
            else:
                data = []
            for i in data:
                i['user'] = self.find_user(i["user"])
                del i["user"]["email"]
                del i["user"]["identity"]
                del i["user"]["website"]
                del i["user"]["creation_date"]
                del i["user"]["openid_provider"]
                del i["user"]["country"]
                del i["user"]["_rev"]
                del i["user"]["messages"]
                del i["user"]["last_login_date"]
                del i["user"]["last_login_ip"]
                del i["user"]["about_me"]
                del i["user"]["owns_rooms"]
                del i["user"]["birthday"]
                del i["user"]["last_seen_date"]
                i["user"]["name"] = self.safe(i["user"]["name"])
            data = sorted(data, key=lambda x: len(x["stars"]), reverse=True)
            data = list(i for i in data if i["stars"])[:10]
            data = sorted(data, key=lambda x: x["date"], reverse=True)
            cherrypy.response.headers["Content-Type"] = "application/json"
            h = hashlib.md5("".join(i["_id"] + str(len(i["stars"]))
                for i in data).encode()).hexdigest()
            for i in data:
                i["nice_date"] = time.strftime("%Y-%m-%d %H:%MZ", time.gmtime(i["date"]))
            return {'last_atime': last_atime, 'data': data, 'hash': h}
        raise cherrypy.HTTPError(404)

    @jsonify
    @cherrypy.expose
    def get_user_list(self, room):
        self.active_users[room] = {k: v for k, v in
            self.active_users[room].items() if time.time() - v < 10}
        r = list(self.find_user(i) for i in self.active_users[room].keys())
        for i in r:            
            del i["email"]
            del i["identity"]
            del i["website"]
            del i["creation_date"]
            del i["openid_provider"]
            del i["country"]
            del i["_rev"]
            del i["messages"]
            del i["last_login_date"]
            del i["last_login_ip"]
            del i["about_me"]
            del i["owns_rooms"]
            del i["birthday"]
            del i["last_seen_date"]
            i["name"] = self.safe(i["name"])
        data = sorted(r, key=lambda x: x["num_id"] or "")
        h = hashlib.md5("".join(i["_id"]
            for i in data).encode()).hexdigest()
        return {"data": data, "hash": h}

    @cherrypy.expose
    def remove_user_from_room(self, room, num_id):
        room_num_id = room
        room = self.find_room(room)
        user = self.get_user()
        if user and user["_id"] == room["owner"]:
            if num_id in room["users"]:
                room["users"].remove(num_id)
                self.db.request("PUT", "/%s_rooms/%s" % (
                    self.couchdb_prefix, room["_id"]), body=room)
                self.do_get_messages.cache_clear()
        raise cherrypy.HTTPRedirect("/rooms/%s" % room_num_id)

    @jsonify
    @cherrypy.expose
    def add_user_to_room(self, room, user_url=""):
        room_num_id = room
        room = self.find_room(room)
        user = self.get_user()
        if user and user["_id"] == room["owner"]:
            u = urllib.parse.urlparse(user_url).path.split("/")
            if len(u) > 2 and u[1] == "users" and self.find_user(u[2]):
                if u[2] not in room["users"]:
                    room["users"].append(u[2])
                self.db.request("PUT", "/%s_rooms/%s" % (
                    self.couchdb_prefix, room["_id"]), body=room)
        raise cherrypy.HTTPRedirect("/rooms/%s" % room_num_id)
