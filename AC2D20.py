import json
import re


class AC2D20Character:
    """Read info from character json file,
    can set some value : stress and injuries"""
    def __init__(self, id):
        f = open(f'{id}.json', 'r')
        self.id = id
        self.allstats = json.loads(f.read())
        f.close()

    def stats(self, key):
        return self.allstats[key]

    def stress(self, what, value):
        if not re.match(r'perdus|fatigue', what):
            return False
        if value >= 0 and value <= self.allstats['stress']['max']:
            self.allstats['stress'][what] = value
            self.save()
            return self.stats('stress')
        else:
            return False

    def fortune(self, value):
        if value >= 0 and value <= 3:
            self.allstats['fortune'] = value
            self.save()
            return self.stats['fortune']

    def save(self):
        f = open(f'{self.id}.json', 'w')
        json.dump(self.allstats, f, ensure_ascii=False, indent=4)
        f.close()

    def injury(self, arg=None):
        if not arg:
            return self.stats('blessures')
        max_injuries = self.allstats['blessures']['max']
        cur_injuries = self.allstats['blessures']['descriptions']
        if arg == "remove":
            self.allstats['blessures']['descriptions'] = []
            self.save()
            return self.stats('blessures')
        elif arg == "status":
            if len(cur_injuries) > max_injuries:
                return "dead"
            elif len(cur_injuries) == max_injuries:
                return "defeated"
            else:
                return f"{len(cur_injuries)} injuries/{max_injuries}"
        else:
            cur_injuries.append(arg)
            self.save()
