
import cherrypy
import json
import mako.template
import mako.lookup
import random
import time
import hashlib
import markdown
import collections
import threading
import urlparse
import mimetypes


class Root (object):

    sessions = set()
    logged_in = set()
    user_database = {
        'guest': {
            'user_id': '0',
            'password': hashlib.sha512("").hexdigest(),
            'email': "test@example.com",
        },
        'stefano': {
            'user_id': '1',
            'password': hashlib.sha512("password").hexdigest(),
            'email': "stefano.palazzo@gmail.com",
        }
    }
    messages = []
    stars = collections.defaultdict(set)
    current_sessions = []
    active_user_list = []

    def log(self, message):
        print "\33[1;32m" + str(message) + "\33[m"

    def __init__(self):
        try:
            data = json.load(open("backup.dat"))
            self.sessions = set(data['sessions'])
            self.logged_in = set(data['logged_in'])
            self.user_database = data['user_database']
            self.messages = data['messages']
            self.stars = collections.defaultdict(set)
            for i in data['stars']:
                self.stars[int(i)] = set(data['stars'][i])
        except Exception as e:
            print repr(e)
        else:
            self.log("backup loaded")
        self.md = markdown.Markdown(safe_mode="escape", output_format='html4')
        threading.Thread(target=self.backup).start()

    def backup(self):
        while 1:
            self.active_user_list = list(set(self.current_sessions[:]))
            self.current_sessions = []
            if len(self.messages) > 100:
                self.messages = self.messages[-100:]
            time.sleep(5)
            data = {
                'sessions': list(self.sessions),
                'logged_in': list(self.logged_in),
                'user_database': self.user_database,
                'messages': self.messages,
                'stars': dict((i, list(self.stars[i])) for i in self.stars),
            }
            open("backup.dat", "w").write(json.dumps(data, indent=4))

    @cherrypy.expose
    def index(self):
        lookup = mako.lookup.TemplateLookup(directories=['.'])
        index = mako.template.Template(filename="index.mako", lookup=lookup)
        return index.render(
            logged_in=cherrypy.session.get('session_key') in self.sessions,
            session=dict(cherrypy.session)
        )

    @cherrypy.expose
    def do_login(self, username=None, password=None, email=None):
        if username in self.user_database:
            if hashlib.sha512(password).hexdigest() == self.user_database[username]['password']:
                key = hex(random.randint(0, 2**128-1))[2:].rstrip("L").rjust(32, "0")
                self.sessions |= {key}
                self.logged_in |= {username}
                cherrypy.session['session_key'] = key
                cherrypy.session['username'] = username
                cherrypy.session['user_id'] = self.user_database[username]['user_id']
                self.log(str(cherrypy.session.get('username')) + " logs in")
            else:
                cherrypy.session['login_error'] = 'password'
        elif username is not None:
            cherrypy.session['login_error'] = 'username'
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def do_register(self, username=None, password=None, email=None):
        if username not in self.user_database:
            if email not in [self.user_database[i]['email'] for i in self.user_database]:
                if password:
                    self.user_database[username] = {
                        'user_id': str(max(int(self.user_database[i]['user_id']) for i in self.user_database) + 1),
                        'password': hashlib.sha512(password).hexdigest(),
                        'email': email,
                    }
                    key = hex(random.randint(0, 2**128-1))[2:].rstrip("L").rjust(32, "0")
                    self.sessions |= {key}
                    self.logged_in |= {username}
                    cherrypy.session['session_key'] = key
                    cherrypy.session['username'] = username
                    cherrypy.session['user_id'] = self.user_database[username]['user_id']
                    self.log(cherrypy.session['username'] + " registered a new account and logged in")
                    raise cherrypy.HTTPRedirect("/")
                else:
                    cherrypy.session['login_error'] = 'no_password'
                    raise cherrypy.HTTPRedirect("/register")
            else:
                cherrypy.session['login_error'] = 'email_taken'
                raise cherrypy.HTTPRedirect("/register")
        elif username is not None:
            cherrypy.session['login_error'] = 'username_taken'
            raise cherrypy.HTTPRedirect("/register")

    @cherrypy.expose
    def login(self):
        cherrypy.session['register'] = False
        if 'login_skipped' in cherrypy.session:
            del cherrypy.session['login_skipped']
        return self.index()

    @cherrypy.expose
    def register(self):
        if 'login_skipped' in cherrypy.session:
            del cherrypy.session['login_skipped']
        cherrypy.session['register'] = True
        return self.index()

    @cherrypy.expose
    def login_skipped(self):
        cherrypy.session['login_skipped'] = True

    @cherrypy.expose
    def users(self, user_id, username):
        return self.index()

    @cherrypy.expose
    def user_list(self):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps([{
                'user_id': self.user_database[i]['user_id'],
                'username': i,
                'emailhash': hashlib.md5(self.user_database[i]['email']).hexdigest(),
            } for i in self.active_user_list])

    @cherrypy.expose
    def logout(self):
        self.log(str(cherrypy.session.get('username')) + " logs out manually")
        self.sessions -= {cherrypy.session.get('session_key')}
        self.logged_in -= {cherrypy.session.get('username')}
        cherrypy.lib.sessions.expire()
        raise cherrypy.HTTPRedirect("/")

    
    @cherrypy.expose
    def post_message(self, message=""):
        if cherrypy.session.get('session_key') in self.sessions:
            self.log(cherrypy.session['username'] + " posts message: " + message)
            raw_message = message
            if (bool(''.join(list(urlparse.urlparse(message)[:2]))) and "://" in message and
                    str(mimetypes.guess_type(message)[0]).startswith("image")):
                message = "[![](%s)](%s)" % (message, message)
            if "://" in message:
                message = " ".join("[%s](%s)" % (i.lstrip("http://"), i)
                    if bool(''.join(list(urlparse.urlparse(i)[:2])))
                    else i for i in message.split(" "))
            message = self.md.convert(message.decode("utf8")).replace(
                "\n", "<br />").replace("<code>\n", "").replace("\n</code>", "")
            if message.strip():
                self.messages.append({
                    'message_id': (max(i['message_id'] for i in self.messages) + 1) if self.messages else 0,
                    'message': message,
                    'raw_message': raw_message,
                    'user_id': cherrypy.session['user_id'],
                    'username': cherrypy.session['username'],
                    'time': time.time(),
                    'stime': time.strftime("%H:%M"),
                    'emailhash': hashlib.md5(self.user_database[cherrypy.session['username']]['email']).hexdigest(),
                })

    @cherrypy.expose
    def read_messages(self, last_atime):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        if cherrypy.session.get('username'):
            self.current_sessions.append(cherrypy.session.get('username'))
        messages = [i for i in self.messages if float(i['time']) > float(last_atime)]
        for i in messages:
            i['own_message'] = i['username'] == cherrypy.session.get('username')
            i['message_for_me'] = (("@" + cherrypy.session.get('username').split()[0].lower()) in i['message'].lower()
                if cherrypy.session.get('username') else False)
        return json.dumps(messages)

    @cherrypy.expose
    def get_starred_messages(self):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps(sorted([(i, len(self.stars[i['message_id']]))
            for i in self.messages if i['message_id'] in self.stars], key=lambda i: i[1], reverse=True))

    @cherrypy.expose
    def star_message(self, message_id=None):
        if message_id is not None:
            msg = [i for i in self.messages if i['message_id'] == int(message_id)]
            if int(msg[0]['user_id']) != int(cherrypy.session['user_id']):
                self.log(cherrypy.session['username'] + " stars message " + message_id)
                self.stars[int(message_id)] |= {int(cherrypy.session['user_id'])}

    @cherrypy.expose
    def ding(self):
        cherrypy.response.headers['Content-Type'] = 'audio/x-wav'
        return open("ding.wav").read()

    @cherrypy.expose
    def message_for_me(self):
        cherrypy.response.headers['Content-Type'] = 'audio/x-wav'
        return open("message_for_me.wav").read()

    @cherrypy.expose
    def background(self):
        cherrypy.response.headers['Content-Type'] = 'image/png'
        return open("bg.png").read()


cherrypy.quickstart(Root(), config={
    'global':{
        'log.screen': False,
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8080,
        'tools.sessions.on': True,
        'tools.sessions.timeout': 1,
    }
})
