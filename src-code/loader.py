
import pickle
from os import path


def load(name : str, builder=None, force=False):
    filename = name + ".bin"

    if not force and path.exists(filename):
        return pickle.load( open( filename, "rb" ) )

    if builder is None:
        raise Exception(f"File {filename} not found")


    obj = builder()
    pickle.dump( obj, open( filename, "wb" ) )
    return obj
