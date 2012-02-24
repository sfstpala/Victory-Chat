
import cherrypy
import os.path
import mako.lookup
import modules.site
import modules.openid
import modules.chat
import modules.helpers
import modules.onebox
import time


class Root (modules.onebox.OneBoxMixIn,
        modules.helpers.HelperMixIn,
        modules.chat.ChatMixIn,
        modules.openid.OpenIDMixIn,
        modules.site.Root):

    class Static (object):

        _cp_config = {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(os.path.split(
                os.path.realpath(__file__))[0], "../", "static"),
            'tools.gzip.on': True,
            'tools.gzip.mime_types': ['text/*'],
        }

    _cp_config = {
        'tools.sessions.on': True,
        'tools.sessions.timeout': 60 * 24,
        'tools.gzip.on': True,
        'tools.gzip.mime_types': ['text/*', 'application/json'],
    }

    openid_providers = {
        'google': "https://www.google.com/accounts/o8/id",
        'launchpad': "https://login.launchpad.net/",
        'myopenid': "https://www.myopenid.com/",
        'stackexchange': "https://openid.stackexchange.com/",
        'ubuntu': "https://login.ubuntu.com/",
        'yahoo': "https://yahoo.com/",
    }

    static = Static()
    # sessions keeps user dictionaries associated with the
    # session id in cherrypy.session["token"], if it's there
    sessions = dict()
    revision = "%.2f" % ((int(time.time() - 1317428453) // 60 // 60) / 100)

    view = mako.lookup.TemplateLookup(directories=[os.path.join(
        os.path.split(os.path.realpath(__file__))[0], "../", "views")],
        input_encoding="utf8").get_template

    def get_defaults(self):
        ''' default arguments that are passed to every template '''
        user = self.get_user()
        if user:
            self.update_user(user["_id"], {'last_seen_date': time.time()})
        return {
            'base_url': self.base_url,
            'user': user,
            'fuzzy_delta': self.fuzzy_delta,
            'revision': self.revision,
            'n_users': self.get_n_users(),
            'n_rooms': self.get_n_rooms(),
        }
