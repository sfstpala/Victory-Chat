
import cherrypy
import time
import uuid

class Root (object):

    @cherrypy.expose
    def index(self):
        return self.view("index.html").render(**self.get_defaults())

    @cherrypy.expose
    def login(self, provider="", claimed="", ref="/", **query):
        return self.do_login(provider, claimed, ref, **query)

    @cherrypy.expose
    def logout(self, ref="/"):
        token = cherrypy.session.get("token")
        if token and token in self.sessions:
            del self.sessions[token]
            del cherrypy.session["token"]
        raise cherrypy.HTTPRedirect(ref)

    def user(self, num_id="", link_name="", action=None,
            website="", country="", about="", birthday="", name=""):
        if action == "edit":
            if cherrypy.request.method == "POST":
                user = self.get_user()
                if not user:
                    raise cherrypy.HTTPError(404)
                update = {
                    'website': self.safe(website),
                    'country': self.safe(country),
                    'about_me': self.safe(about),
                    'birthday': self.safe(birthday),
                    'name': self.safe(name),
                    'link_name': self.get_link_name(name),
                }
                self.update_user(user["_id"], update)
                self.sessions[cherrypy.session["token"]].update(update)
                raise cherrypy.HTTPRedirect("/users/%s/%s" % (
                    num_id, self.get_link_name(name)))
            else:
                u = self.find_user(num_id)
                user = self.get_user()
                if user and user["_id"] == u["_id"]:
                    return self.view("edit_user.html").render(
                        u=u, **self.get_defaults())
                raise cherrypy.HTTPError(404)
        elif action is None:
            user = self.find_user(num_id)
            if not user:
                raise cherrypy.HTTPError(404)
            if link_name != user["link_name"]:
                raise cherrypy.HTTPRedirect("/users/%s/%s" % (
                    num_id, user["link_name"]))
            return self.view("user.html").render(
                u=user, **self.get_defaults())
        else:
            raise cherrypy.HTTPError(404)

    @cherrypy.expose
    def new(self, room_name="", room_type="", description=""):
        if cherrypy.request.method == "POST" and self.get_user():
            num_id = self.create_new_room({
                'name': self.safe(room_name),
                'type': "private" if room_type == "private" else "public",
                'desc': self.safe(description),
                'creation_date': time.time(),
                'num_id': self.get_num_id(),
                'owner': self.get_user()["_id"],
                'link_name': self.get_link_name(room_name),
                'users': [self.get_user()["num_id"]],
                'n_messages': 0,
            })
            self.add_room_to_user(self.get_user()["_id"], num_id)
            raise cherrypy.HTTPRedirect("/rooms/%s" % num_id)
        else:
            if self.get_user():
                return self.view("new.html").render(**self.get_defaults())
            raise cherrypy.HTTPError(404)

    def room(self, num_id, link_name):
        room = self.find_room(num_id)
        if room:
            if link_name != room["link_name"]:
                raise cherrypy.HTTPRedirect("/rooms/%s/%s" % (
                    num_id, room["link_name"]))
            if self.get_user() and (room["type"] == "public" or
                    self.get_user()["num_id"] in room["users"]):
                if room["type"] == "private":
                    room["users"] = [self.find_user(i) for i in room["users"]]
                return self.view("room.html").render(
                    room=room, **self.get_defaults())
            return self.view("forbidden.html").render(room=room,
                **self.get_defaults())
        raise cherrypy.HTTPError(404)

    @cherrypy.expose
    def rooms(self, num_id="", link_name="", page="1", pagesize="4"):
        if num_id:
            return self.room(num_id, link_name)
        else:
            try:
                page, pagesize = int(page) - 1, int(pagesize)
            except ValueError:
                raise cherrypy.HTTPError(404)
            req = self.db.request("GET", ("/%s_rooms/_design/by_msg_count/"
                "_view/by_msg_count/") % self.couchdb_prefix)
            x = list(sorted((i for i in (req["rows"] if "rows" in req else [])),
                key=lambda x: x["value"], reverse=True))
            n_pages = (len(x) // pagesize) + (1 if len(x) % pagesize else 0)
            x = x[pagesize * page:pagesize * page + pagesize]
            rooms = list(self.find_room(i["key"]) for i in x)
            for i in rooms:
                # the __wrapped__ attributed accesses the function
                # without accessing the lru_cache decorating it
                i["chatting"] = len(self.get_user_list.__wrapped__(self, i["num_id"])["data"])
            return self.view("rooms.html").render(rooms=rooms,
                n_pages=n_pages, page=page+1, **self.get_defaults())

    @cherrypy.expose
    def users(self, *args, page="1", pagesize="10", **kwargs):
        if args or kwargs:
            return self.user(*args, **kwargs)
        try:
            page, pagesize = int(page) - 1, int(pagesize)
        except ValueError:
            raise cherrypy.HTTPError(404)
        req = self.db.request("GET", ("/%s_users/_design/by_msg_count/"
            "_view/by_msg_count/") % self.couchdb_prefix)
        x = list(sorted(req["rows"],
            key=lambda x: x["value"], reverse=True))
        n_pages = (len(x) // pagesize) + (1 if len(x) % pagesize else 0)
        x = x[pagesize * page:pagesize * page + pagesize]
        users = list(self.find_user(i["key"]) for i in x)
        return self.view("users.html").render(users=users,
            n_pages=n_pages, page=page+1, **self.get_defaults())

    @cherrypy.expose
    def faq(self):
        return self.view("faq.html").render(**self.get_defaults())
