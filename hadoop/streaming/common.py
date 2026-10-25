"""Shared helpers for the Hadoop Streaming jobs (standard library only)."""
import re, sys, collections
STOP = set("""a about above after again all also am an and any are as at be because been before being below between both but by can could did do does doing down during each few for from further had has have having he her here hers him his how i if in into is it its just me more most my no nor not now of off on once only or other our out over own same she should so some such than that the their them then there these they this those through to too under until up us very was we were what when where which while who whom why will with would you your yours
 br amp quot didn doesn don isn wasn weren won wouldn couldn shouldn aren hasn haven hadn ive im youve thats one get got would also really much even""".split())
TOKEN = re.compile(r"[a-z]{3,}")

class Counters:
    """Hadoop counters: print 'reporter:counter:GROUP,NAME,N' to stderr; Hadoop adds them up across all mappers and shows them in the job summary."""
    def __init__(self, group): self.g, self.c = group, collections.Counter()
    def inc(self, name, n=1): self.c[name] += n
    def flush(self):
        for k, v in self.c.items(): sys.stderr.write(f"reporter:counter:{self.g},{k},{v}\n")

def sentiment(score):
    return "negative" if score <= 2 else "neutral" if score == 3 else "positive"
