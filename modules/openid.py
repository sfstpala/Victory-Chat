
import cherrypy
import json
import uuid
import time
import hashlib

import modules.external.openid2rp as openid2rp


class OpenIDMixIn (object):

    openid_sessions = list()

    def openid_login(self, provider="", claimed="", **query):
        if provider and provider in self.openid_providers:
            services, url, op_local = openid2rp.discover(
                self.openid_providers[provider])
            try:
                session = openid2rp.associate(services, url)
            except Exception as e:
                raise ValueError("error")
            self.openid_sessions.append(session)
            raise cherrypy.HTTPRedirect(
                openid2rp.request_authentication(services, url,
                session['assoc_handle'], "http://%s/login?returned=1" %
                self.get_defaults()['base_url']), 307)
        elif "claimed" in query:
            kind, claimed = openid2rp.normalize_uri(query['claimed'])
            if kind == 'xri':
                res = openid2rp.resolve_xri(claimed)
                if res:
                    claimed = res[0]
                    res = res[1:]
            else:
                res = openid2rp.discover(claimed)
            if res is None:
                raise ValueError("discovery failed")
            services, url, op_local = res
            try:
                session = associate(services, url)
            except Exception as e:
                raise ValueError("error")
            self.openid_sessions.append(session)
            raise cherrypy.HTTPRedirect(
                openid2rp.request_authentication(services, url,
                session['assoc_handle'], "http://%s/login?returned=1" %
                self.get_defaults()['base_url']), 307)
        elif "returned" in query:
            if query["openid.mode"] == "cancel":
                raise ValueError("error")
            handle = query['openid.assoc_handle']
            for session in self.openid_sessions:
                if session['assoc_handle'] == handle:
                    break
            else:
                raise ValueError("no session")
            try:
                signed = openid2rp.authenticate(session, query)
            except Exception as e:
                return "login failed (%r)" % e
            if 'openid.claimed_id' in query:
                if 'claimed_id' not in signed:
                    raise ValueError("incomplete signature")
                claimed = query['openid.claimed_id']
            else:
                if 'identity' not in signed:
                    raise ValueError("incomplete identity")
                claimed = query['openid.identity']
            if "openid.ext1.value.first" in query:
                name = query["openid.ext1.value.first"]
                if "openid.ext1.value.last" in query:
                    name += " " + query["openid.ext1.value.last"]
            elif "openid.sreg.nickname" in query:
                name = query["openid.sreg.nickname"]
            elif query["openid.identity"].endswith(".myopenid.com/"):
                name = query["openid.identity"]
                name = name.replace("https://", "")
                name = name.replace("http://", "")
                name = name.replace(".myopenid.com/", "")
            elif "openid.sreg.email" in query:
                name = query["openid.sreg.email"].split("@")[0]
            elif "openid.ext1.value.email" in query:
                name = query["openid.ext1.value.email"].split("@")[0]
            else:
                name = ""
            name = name.strip() or None
            if "openid.sreg.email" in query:
                email = query["openid.sreg.email"]
            elif "openid.ext1.value.email" in query:
                email = query["openid.ext1.value.email"]
            elif "openid.ax.value.email" in query:
                email = query["openid.ax.value.email"]
            else:
                email = None
            return {
                'name': name,
                'identity': query["openid.identity"],
                'email': email,
            }
        return None

    def do_login(self, provider="", claimed="", ref="/", **query):
        if provider or claimed or query:
            try:
                user = self.openid_login(provider, claimed, **query)
            except ValueError as e:
                return self.view("login.html").render(error=str(e),
                    **self.get_defaults())
            if not user.get("email"):
                return self.view("login.html").render(error="email",
                    **self.get_defaults())
            users = self.db.request("GET", "/%s_users/_design/"
                "by_email/_view/by_email/" % self.couchdb_prefix)
            s = [i for i in users['rows'] if i["key"] == user["email"]]
            if s and user["email"] == s[0]["key"]:
                if s[0]["value"] == user["identity"]:
                    return self.finish_login(s[0]["id"])
                else:
                    try:
                        provider = s[0]["value"].replace("https://", "")
                        provider = provider.replace("http://", "")
                        provider = provider.replace(".net", ".com")
                        provider = provider.split(".com")[0].split(".")[-1]
                    except Exception as e:
                        provider = None
                    return self.view("login.html").render(error="taken",
                        provider=provider, **self.get_defaults())
            user["name"] = self.safe(user["name"])
            user["email"] = self.safe(user["email"])
            provider = user["identity"].replace("https://", "")
            provider = provider.replace("http://", "")
            provider = provider.replace(".net", ".com")
            provider = provider.split(".com")[0].split(".")[-1]
            user.update({
                "num_id": self.get_num_id(),
                "link_name": self.get_link_name(user["name"]),
                "owns_rooms": [],
                "messages": [],
                "is_moderator": False,
                "website": None,
                "about_me": None,
                "openid_provider": provider,
                "country": None,
                "birthday": None,
                "last_seen_date": time.time(),
                "last_login_date": time.time(),
                "last_login_ip":
                    cherrypy.request.headers["Remote-Addr"],
                "creation_date": time.time(),
                "email_hash": hashlib.md5(
                    user["email"].encode()).hexdigest(),
            })
            return self.finish_login(self.db.request("POST", "/%s_users" %
                self.couchdb_prefix, {}, body=user)['id'])
        else:
            return self.view("login.html").render(**self.get_defaults())

    def safe(self, s):
        if s:
            s = s.replace("&", "&amp;")
            s = s.replace("<", "&lt;")
            s = s.replace(">", "&gt;")
            s = s.replace("'", "&#39;")
            s = s.replace("\"", "&quot;")
        return s or ""

    def get_link_name(self, name):
        if name:
            n = ''.join(i if i in "0123456789abcdefghijklmnopqrstuvwxyz"
                else " " for i in name.lower().strip())
            while "  " in n:
                n = n.replace("  ", " ")
            return n.replace(" ", "-")
        return "--"

    def finish_login(self, id_):
        token = uuid.uuid4().hex
        user = self.db.request("GET", "/%s_users/%s" %
            (self.couchdb_prefix, id_))
        if user:
            user["last_login_date"] = time.time()
            user["last_login_ip"] = cherrypy.request.headers["Remote-Addr"]
            self.db.request("PUT", "/%s_users/%s" %
                (self.couchdb_prefix, id_), body=user)
            cherrypy.session["token"] = token
            self.sessions[token] = user
        raise cherrypy.HTTPRedirect("/rooms")

    def update_user(self, id_, update_dict):
        user = self.db.request("GET", "/%s_users/%s" %
            (self.couchdb_prefix, id_))
        user.update(update_dict)
        self.db.request("PUT", "/%s_users/%s" %
            (self.couchdb_prefix, id_), body=user)

    def add_room_to_user(self, id_, room_num_id):
        user = self.db.request("GET", "/%s_users/%s" %
            (self.couchdb_prefix, id_))
        user["owns_rooms"].append(room_num_id)
        self.db.request("PUT", "/%s_users/%s" %
            (self.couchdb_prefix, id_), body=user)

    def get_user(self):
        return self.sessions.get(cherrypy.session.get("token"))

    def find_user(self, num_id):
        users = self.db.request("GET", "/%s_users/_design/"
            "by_num_id/_view/by_num_id/" % self.couchdb_prefix)
        s = [i for i in users['rows'] if i["key"] == num_id]
        return self.db.request("GET", "/%s_users/%s" %
            (self.couchdb_prefix, s[0]['id'])) if s else None

    def get_n_users(self):
        try:
            return len(self.db.request("GET", ("/%s_users/_design/by_msg_count/"
                "_view/by_msg_count/") % self.couchdb_prefix)["rows"])
        except Exception as e:
            return 0
