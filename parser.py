import itertools
import re
import sys
import yaml

class Parser(object):
    TYPES = {"int", "float", "str"}
    TYPE_NUMBER = {"int", "float"}
    TYPE_FUNC = {"int": int, "float": float, "str": str}
    TYPE_PATTERN = {
        r"%d": r"([+-]?\d+)",
        r"%f": r"([+-]?\d+"
               r"|[+-]?\d+\.\d+"
               r"|[+-]?\d+\.\d+[eE][+-]?\d+"
               r"|[+-]?\d+\.\d+[eE][+-]?\d+\.\d+)",}

    def __init__(self):
        self.handlers = {t: [] for t in Parser.TYPES}

    def register(self, t, pattern, handler):
        if t not in Parser.TYPES:
            raise Exception(t + " is unknown type")
        for before, after in Parser.TYPE_PATTERN.iteritems():
            pattern = pattern.replace(before, after)
        if not pattern.startswith("^"):
            pattern = r"^" + pattern
        if not pattern.endswith("$"):
            pattern = pattern + r"$"
        self.handlers[t].append((re.compile(pattern), handler))

    def parse(self, t, v):
        for pattern in self.handlers[t]:
            m = pattern[0].match(v)
            if m:
                arg = [Parser.TYPE_FUNC[t](s) for s in m.groups()]
                return pattern[1](*arg)
        raise Exception("No matching pattern for {}".format(v))

    def generate(self, filename):
        with open(filename) as f:
            # TODO load json
            for param in self.generate_impl(yaml.load(f)):
                yield param

    def generate_impl(self, dic):
        keys = []
        values = []
        for k, v in dic.iteritems():
            typ = v["t"]    # type
            val = v["v"]    # value configuration

            keys.append(k)
            if isinstance(val, int) or isinstance(val, float):
                values.append([val])
            elif typ == "str":
                if isinstance(val, str):
                    values.append([str(val)])
                elif isinstance(val, unicode):
                    values.append([unicode(val)])
            else:
                try:
                    values.append(self.parse(v["t"], v["v"]))
                except Exception as e:
                    print "Error at '{}':".format(k), str(e)
                    sys.exit(1)
        # Loop for all the possible combinations among values
        for product in itertools.product(*values):
            yield {k: product[i] for i, k in enumerate(keys)}


def CreateParser(args_list):
    parser = Parser()
    for args in args_list:
        parser.register(*args)
    return parser
