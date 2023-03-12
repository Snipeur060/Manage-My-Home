import importlib.util

listemodule = [
    "time","flask","flask_session",
    "atexit","json","colorama",
    "random","passlib.hash","serial",
    "socket","os","functools",
    "apscheduler.schedulers.background","datetime","rpyc"
    ]
counter = 0

for i in range(len(listemodule)):
    if importlib.util.find_spec(listemodule[i]) is None:
        counter += 1
        print('Le module / librairie ' + str(listemodule[i]) + ' n\'est pas installé')
if counter == 0:
    print("L'ensemble des modules sont installés.")
