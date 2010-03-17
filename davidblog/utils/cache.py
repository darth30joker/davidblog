from settings import mc
import pickle

class MCache(object):

    def set(self, name, value):
        return mc.set(name, pickle.dumps(value))

    def get(self, name):
        value = mc.get(name)
        if value is not None:
            return pickle.loads(value)
        return None

    def delete(self, name):
        return mc.delete(name)

mcache = MCache()
