
class StoreResults(dict):
    def __setitem__(self, attrs, value):
        if not isinstance(attrs, dict):
            msg = 'Keys to this dictionary must be dicts'
            raise ValueError(msg)
        dict.__setitem__(self, frozendict(**attrs), value)

    def select(self, *cond, **condkeys):
        """ Returns another StoreResults with the filtered results. """
        r = StoreResults()
        for attrs in self.select_key(*cond, **condkeys):
            r[attrs] = self[attrs] 
        return r

    def select_key(self, *conditions, **condkeys):
        for attrs in self:
            for c in conditions:
                if not c(attrs):
                    break
            else:
                for k in condkeys:
                    if condkeys[k] != attrs[k]:
                        break
                else:
                    yield attrs

    def field(self, field):
        return (attrs[field] for attrs in self)  

try:
    frozenset
except NameError:
    from sets import ImmutableSet as frozenset

class frozendict(dict):
    __slots__ = ('_hash',)
    
    def __hash__(self):
        rval = getattr(self, '_hash', None)
        if rval is None:
            rval = self._hash = hash(frozenset(self.iteritems()))
        return rval