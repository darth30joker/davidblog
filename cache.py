from settings import mc
import pickle

class MCache(object):

    def set(self, name, value):
        mc.set(name, pickle.dumps(value))
        return True

    def get(self, name):
        return pickle.loads(mc.get(name))

    def delete(self, name):
        return mc.delete(name)

mcache = MCache()
