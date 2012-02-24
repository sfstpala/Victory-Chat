
import time


class HelperMixIn (object):

    @staticmethod
    def fuzzy_delta(u):
        # this is a static method so that it can be
        # passed to templates via the get_defaults method
        u = round(u)
        names = ((("seconds", "second"), 60),
                 (("minutes", "minute"), 60),
                 (("hours", "hour"), 24),
                 (("days", "day"), 7),
                 (("weeks", "week"), 4),
                 (("months", "month"), 12),
                 (("years", "year"), 1))
        for n, i in names:
            if u < i:
                break
            else:
                u /= i
        return "%.0f %s" % (round(u), n[1] if round(u) == 1 else n[0])

    def get_num_id(self):
        ''' generate a base36 number based on the current time '''
        def b36(n):
            alphabet = ("abcdefghijklmnopqrstuvwxyz"
                "0123456789")
            if n == 0:
                return alphabet[0]
            r = ""
            while n != 0:
                n, i = divmod(n, len(alphabet))
                r = alphabet[i] + r
            return r
        return b36(int(time.time() * 1000) - (1262304000 * 1000))
