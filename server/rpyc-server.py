__author__ = "Alexandre - Léo - Maxime"

from rpyc import Service
from rpyc.utils.server import ThreadedServer
import serial
from colorama import Fore, Style
from time import sleep
from function.json_manager import jsonopen


def callanswer():
    """
    Cette fonction permet de gérer la communication avec l'arduino elle demande l'action à réaliser avec la carte arduino
    :return: Cette fonction ne renvoi rien
    """
    print(
        Fore.RED,
        Style.BRIGHT,
        "Une action est requise faite entrer pour essayer encore une fois et skip pour continuer --> ",
        Style.RESET_ALL,
        end="",
    )
    statinput = str(input(""))  # on va bien préciser que c'est du str
    if statinput == "skip":
        pass
    else:
        activecard()


def find_arduino_port():
    """
    Cette fonction permet de trouver le port de l'arduino
    :return: Cette fonction renvoi le port de l'arduino ou alors None dans le cas où il n'est pas trouvé
    """
    import serial.tools.list_ports

    # on obtient une liste de tous les ports disponible
    ports = list(serial.tools.list_ports.comports())
    # On parcourt l'enssembles des ports
    for port in ports:
        # on sait qu'un port arduino à dans sa description 'Arduino' donc on cherche si la description du port la possède
        if "Arduino" in port.description:
            # ont renvoi ici le port dans le cas ou le port est bien trouvé
            return port.device
    # si on ne trouve pas le port on renvoi None
    return None


def activecard():
    """
    Cette fonction permet d'activer la carte arduino
    :return:
    Cette fonction ne renvoi rien
    """
    try:
        global ser
        port = find_arduino_port()
        if port:
            ser = serial.Serial(
                port, timeout=1, dsrdtr=None, xonxoff=True, rtscts=True, baudrate=9600
            )
            ser.setDTR(False)
            print(Fore.GREEN + "Carte arduino activée" + Style.RESET_ALL)
        else:
            print(
                Fore.RED
                + "Erreur: Impossible de trouver la carte arduino"
                + Style.RESET_ALL
            )
            callanswer()
    except:
        pass


############################################
#   Fonction pour envoyer des informations #
############################################
def send(code: str, max_attempts: int = 3, delay: float = 1.0):
    """
    Cette fonction a pour but d'envoyer les données vers la carte arduino
    :param code:
    Sur le programme arduino 2 correspond à l'allumage de la led bleu par exemple
    Ainsi, nous traitons le code à envoyer à la carte qui va décider de l'action à réaliser.
    :param max_attempts:
    Le nombre d'essais avant de stopper la tentative
    :param delay:
    Le délai entre chaque essai
    :return:
    Cette fonction renvoie un Booléen True ou False selon le résultat (une erreur ou non)
    """
    import time

    attempts = 0
    # on fait plusieurs essais pour envoyer les données
    while attempts < max_attempts:
        try:
            ser.write(code.encode("utf-8"))
            return True
        except:
            attempts += 1
            time.sleep(delay)
    return False


def getdata():
    """
    Cette fonction a pour but de renvoyer des données de la carte à python
    :return:
    Cette fonction renvoi du text (STR) et en l'occurrence  soit la valeur ou Erreur
    """
    try:
        # on lit les données de la carte (en l'occurence sur la ligne)
        data = ser.readline()
        decoded_data = data.decode().rstrip()
        # on renvoie les données
        return decoded_data
    except:
        pass


activecard()  # on active la carte arduino


class CommandService(Service):
    """
    Cette classe est particulière et appartient à la librairie rpyc
    Les différentes fonctions qui seront disponibles devonrt être renseigné ici
    """

    def exposed_execute(self, command):
        """
        Cette methode de la classe permet d'envoyer des commandes à la carte arduino en passant par la fonction send
        :param command: Cette fonction prend en paramètre une commande (STR) qui sera envoyé à la carte arduino
        :return: Cette fonction renvoi un Booléen True ou False selon le résultat (une erreur ou non)
        """
        print(
            Fore.GREEN
            + f"Execution de la commande send({command}) appelé"
            + Style.RESET_ALL
        )
        # on envoie la commande à la carte arduino
        return send(command)

    def exposed_get_info(self):
        """
        Cette methode de la classe permet de récupérer des informations de la carte arduino en passant par la fonction getdata
        :return: Cette fonction renvoi du text (STR) et en l'occurrence la valeur
        """
        print(
            Fore.GREEN
            + "Récupération des informations get_data() appelé"
            + Style.RESET_ALL
        )
        return getdata()


print(
    Fore.GREEN
    + Style.BRIGHT
    + "Serveur RPYC démarré avec succès IP: localhost Port : 18861"
    + Style.RESET_ALL
)


def activate_job():
    """
    Cette procédure a pour but d'initialiser la carte lors du démarrage de l'application. Ainsi au démarrage de\n
    l'application si le chauffage était allumé avant l'extinction alors il l'est toujours ainsi, on rallume les\n
    différentes leds qui correspondent à un objet en particulier ici.\n
    :return:
    Cette procédure ne renvoie pas de résultat.
    """
    print(
        Fore.LIGHTYELLOW_EX,
        Style.BRIGHT,
        "Envoi des données enregistrés de manière hors ligne ...",
        Style.RESET_ALL,
    )
    Data = jsonopen("state.json", "r")
    if Data["red"] == "ON":
        send("3")
        sleep(3)

    if Data["blue"] == "ON":
        send("7")
        sleep(3)

    if Data["yellow"] == "ON":
        send("5")
    print(
        Fore.LIGHTGREEN_EX,
        Style.BRIGHT,
        "L'ensemble des actions ont été réalisé",
        Style.RESET_ALL,
    )


# on lance la procédure
activate_job()
# on renseigne les paramètres du serveur rpyc sur le port 18861
server = ThreadedServer(CommandService, port=18861)
# on lance le serveur
server.start()
