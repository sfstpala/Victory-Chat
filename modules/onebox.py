
import re

class OneBoxMixIn (object):

    url_regex = [
        re.compile("([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}|(((news|telnet|nttp|file|http|ftp|https)://)|(www|ftp)[-A-Za-z0-9]*\\.)[-A-Za-z0-9\\.]+)(:[0-9]*)?/[-A-Za-z0-9_\\$\\.\\+\\!\\*\\(\\),;:@&=\\?/~\\#\\%]*[^]'\\.}>\\),\\\"]"),
        re.compile("([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}|(((news|telnet|nttp|file|http|ftp|https)://)|(www|ftp)[-A-Za-z0-9]*\\.)[-A-Za-z0-9\\.]+)(:[0-9]*)?"),
        re.compile("(~/|/|\\./)([-A-Za-z0-9_\\$\\.\\+\\!\\*\\(\\),;:@&=\\?/~\\#\\%]|\\\\)+"),
        re.compile("'\\<((mailto:)|)[-A-Za-z0-9\\.]+@[-A-Za-z0-9\\.]+"),
    ]

    def onebox(self, message):
        if any(i.match(message.strip()) for i in self.url_regex):
            if any(message.lower().endswith(i) for i in (".jpg", ".jpeg",
                    ".png", ".gif")):
                return "[![%s](%s)](%s)" % (message, message, message)
            return "[%s](%s)" % (message, message)
        return message

    def onebox_html(self, message):
        if message.startswith("<p><a href=\""):
            m = message[9:]
            if "\">" in message and m.endswith("</a></p>"):
                m = message[:-8].split("\">")[1]
                if any(i.match(m.strip()) for i in self.url_regex):
                    if any(m.lower().endswith(i) for i in (".mp3", ".wav", ".ogg",
                            ".oga", ".wave")):
                        return """<a title=\"%s\" href=\"%s\"><audio src="%s" controls="controls">%s</audio></a>""" % (m, m, m, m)
                if any(m.endswith(i) for i in (".mp4", ".mpg", ".ogv",
                            ".avi", ".webm")):
                        return """<a title=\"%s\" href="%s"><video src="%s" controls="controls" width="320" height="240">%s</video></a>""" % (m, m, m, m)
        if "http://www.youtube.com/watch?v=" in message:
            m = message.split("http://www.youtube.com/watch?v=")[1].split("&")[0]
            return """<iframe width="560" height="315" src="http://www.youtube.com/embed/%s" frameborder="0" allowfullscreen></iframe>""" % m
        return message
