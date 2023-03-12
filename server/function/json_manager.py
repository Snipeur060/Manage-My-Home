from datetime import datetime
import json

def jsonopen(file: str, method: str):
    """
    Fonction qui sert à ouvrir les fichiers json et renvoyer leur contenu
    :param file:
    Le nom du fichier dans /json
    :param method:
    La methode r w etc ...
    :return:
    Renvoie le contenu du fichier
    """
    file = "json/" + file
    with open(file, method,encoding = "ISO-8859-1") as f:
        Data = json.load(f)
    return Data


def jsonwritter(method: str, data, file: str):
    """
    Cette fonction permet d'écrire dans un fichier json\n
    :param method: Le mode d'ouverture du fichier
    :param data: Les données à écrire
    :param file: Le fichier à écrire
    :return:
    """
    file = "json/"+ str(file)
    with open(file, method,encoding = "ISO-8859-1") as f:
        #print(data)
        json.dump(data, f, indent=4, ensure_ascii=False)

def getidlog():
    """
    Cette fonction a pour but de donné l'id du fichier id_log.json
    :return:
    La fonction renvoie un INTEGER (un entier) qui correspond à l'id stocké dans le fichier id_log.json
    """
    Data = jsonopen("id_log.json", "r")
    id = Data["id"]
    return id


def getlastlog():
    """
    Cette fonction est utilisée pour recueillir le dernier log.
    :return:
    Cette fonction a deux return possible :
        - author,date,action elle renvoie alors l'auteur, la date ainsi que l'action réalisée sur le dernier log
        - "Error","Error","Error" dans le cas où rien n'est trouvé
    """
    id = getidlog()
    Dat = jsonopen("log.json", "r")
    for data in Dat:
        for x in Dat[data]:
            if x["id"] == id:
                author = x["actionneur"]
                date = x["date"]
                action = x["action"]
                return author, date, action
    return "Pas encore défini", "Pas encore défini", "Pas encore défini"

def changestate(name: str, state: str):
    """
    Cette procédure a pour but de changer les états des leds dans un fichier json
    :param name:
    Le paramètre name correspond au nom de la led.
    Ici, il existe trois led possible :
        - yellow correspond à la led jaune
        - blue correspond à la led bleu
        - red correspond à la led rouge
    :param state:
    Le paramètre state correspond à l'état de la led.
    Il existe deux états :
        - ON correspond à l'état allumé
        - OFF correspond à l'état éteint
    :return:
    Cette procédure ne renvoi rien.
    """
    Data = jsonopen("state.json", "r")
    Data[name] = state
    namev = str(name) + "_date"
    Data[namev] = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    jsonwritter("w", Data, "state.json")
