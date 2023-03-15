__author__ = "Alexandre - Léo - Maxime"
from datetime import datetime
import socket
from sys import platform
import json
from colorama import Fore, Style
from passlib.handlers.sha2_crypt import sha256_crypt
import rpyc
from function.json_manager import *


def callanswer():
    """
    Cette fonction demande à l'utilisateur entre deux possibilitées
    """
    print(
        Fore.RED,
        Style.BRIGHT,
        "Une action est requise (pensez bien à démarrer le serveur rpyc-server.py) ",
        "faite entrer pour essayer encore une fois et skip pour continuer --> ",
        Style.RESET_ALL,
        end="",
    )
    statinput = str(input(""))  # on va bien préciser que c'est du str
    if statinput == "skip":
        pass
    else:
        startconnection()


def startconnection():
    # Connexion au serveur

    try:
        global conn
        global command_service
        conn = rpyc.connect("localhost", 18861)
        command_service = conn.root
    except:
        callanswer()


# Récupération du service
startconnection()


def send(code):
    """
    Cette fonction permet d'envoyer une commande à l'arduino
    :param code:
    Le paramètre code correspond à la commande à envoyer à l'arduino
    :return:
    Cette fonction ne renvoi rien
    """
    try:
        response = command_service.exposed_execute(code)
    except:
        pass


def getdata(code):
    """
    Cette fonction permet de récupérer les données de l'arduino
    :param code:
    Le paramètre code correspond à la commande à envoyer à l'arduino
    """
    try:
        response = command_service.exposed_get_info(code)
        return response
    except:
        pass


################################################################################################## PRINCIPALE


def menu():
    """
    Cette fonction permet de traiter les actions dans le menu afin de rederiger l'utilisateur vers les differentes fonctions voulues
    :return:
    Cette fonction ne renvoie rien
    """
    r = quefaire()
    if r == 1:
        obtenirOS()
    elif r == 2:
        modifmdp()
    elif r == 3:
        chauff()
    elif r == 4:
        lumiere()
    elif r == 5:
        fontaine()
    elif r == 6:
        print(getlastlog())
    elif r == 7:
        inf()
    elif r == 8:
        print(" Vous avez fermé le terminal")
        return None
    else:
        print(" Veuillez saisir une action valide")
    menu()


def quefaire():
    test = False
    while test == False:
        rslt = input(" Que souhaitez vous faire (menu): ")
        try:
            int(rslt)
            test = True
        except:
            print(" Veuillez saisir une action valide")

    return int(rslt)


def affichage():
    print(" ***** MENU *****")
    print(
        " 1/ Réinitialiser  la console",
        "\n",
        "2/ Modifier le mot de passe",
        "\n",
        "3/ Gérer le chauffage",
        "\n",
        "4/ Gérer la lumière",
        "\n",
        "5/ Gérer la fontaine",
        "\n",
        "6/ Obtenir la dernière action effectué",
        "\n",
        "7/ Information",
        "\n",
        "8/ Fermer le terminal",
        "\n",
    )
    menu()


################################################################################################## REINITIALISATION DE LA CONSOLE


def obtenirOS():
    if platform not in ("win32", "cygwin"):
        reinit("unix")
    else:
        reinit("windows")


def reinit(os):
    from subprocess import call

    if os == "unix":
        command = "clear"
    else:
        command = "cls"
    call(command, shell=True)
    affichage()


################################################################################################## MODIFACATION MDP


def modifmdp():
    """
    Cette fonction permet de modifier le mot de passe sur le site
    :return:
    Cette fonction ne renvoie rien mais modifie le mot de l'utilisateur
    """
    nv_mdp = input(" Veuillez saisir votre nouveau mot de passe : ")
    hashedmp = sha256_crypt.hash(nv_mdp)
    Data = jsonopen("user.json", "r")
    for data in Data:
        for x in Data[data]:
            if "test" == x["username"]:
                x["password"] = hashedmp
    jsonwritter("w", Data, "user.json")


################################################################################################## CHAUFFAGE


def chauff():
    """
    Cette fonction permet d'éteindre ou d'allumer le chauffage sous les intructions donnée par l'utilisateur
    :return:
    Cette fonction ne renvoie rien
    """
    print(" ***** CHAUFFAGE *****")
    print(" 1/ Eteindre le chauffage", "\n", "2/ Allumer le chauffage")
    test_c = False
    while test_c == False:
        rslt_c = input(" Que souhaitez vous faire (gestion chauffage): ")
        try:
            rslt_c = int(rslt_c)
            test_c = True
        except:
            print(" Veuillez saisir une action valide")
    if rslt_c == 1:
        send("4")
        changestate("red", "OFF")
        logg("Chauffage éteint", "Client Admin")
    elif rslt_c == 2:
        send("3")
        changestate("red", "ON")
        logg("Allumage chauffage", "Client Admin")
    else:
        chauff()


################################################################################################## LUMIERE


def lumiere():
    """
    Cette fonction permet d'éteindre ou d'allumer la lumière sous les intructions donnée par l'utilisateur
    :return:
    Cette fonction ne renvoie rien
    """
    print(" ***** LUMIERE *****")
    print(" 1/ Eteindre les lumieres", "\n", "2/ Allumer les lumieres")
    test_l = False
    while test_l == False:
        rslt_l = input(" Que souhaitez vous faire (gestion lumière): ")
        try:
            rslt_l = int(rslt_l)
            test_l = True
        except:
            print(" Veuillez saisir une action valide")
    if rslt_l == 1:
        send("6")
        changestate("yellow", "OFF")
        logg("Lumière éteinte", "Client Admin")
    elif rslt_l == 2:
        send("5")
        changestate("yellow", "ON")
        logg("Allumage lumière", "Client Admin")
    else:
        lumiere()


################################################################################################## FONTAINE


def fontaine():
    """
    Cette fonction permet d'éteindre ou d'allumer la fontaine sous les intructions donnée par l'utilisateur
    :return:
    Cette fonction ne renvoie rien
    """
    print(" ***** FONTAINE *****")
    print(" 1/ Fermer la fontaine", "\n", "2/ Allumer la fontaine")
    test_f = False
    while test_f == False:
        rslt_f = input(" Que souhaitez vous faire (gestion fontaine): ")
        try:
            rslt_f = int(rslt_f)
            test_f = True
        except:
            print(" Veuillez saisir une action valide")
    if rslt_f == 1:
        send("8")
        changestate("blue", "OFF")
        logg("Fontaine éteint", "Client Admin")
    elif rslt_f == 2:
        send("7")
        changestate("blue", "ON")
        logg("Allumage fontaine", "Client Admin")
    else:
        fontaine()


################################################################################################## LOG
def genidlog():
    """
    Cette fonction a pour but de faciliter la génération d'un identifiant unique dans le fichier de log (Historique)
    :return:
    Cette fonction renvoie un INTEGER (un nombre entier)
    """
    Dte = jsonopen("id_log.json", "r")
    vf = Dte["id"] + 1
    fin = {"id": vf}
    tv = vf
    jsonFile = open("json/id_log.json", "w+")
    jsonFile.write(json.dumps(fin))
    jsonFile.close()
    return tv


def logg(text: str, ip: str = socket.gethostbyname(socket.gethostname())):
    """
    Cette procédure permet de mettre dans un fichier json un log (Un Historique). Exemple --> L'utilisateur a activé la lumière à 19h25
    :param text:
    Le paramètre text ici correspond au message à enregistrer. Exemple --> [CHAUFFAGE] Le chauffage a été allumé
    :return:
    Cette procédure ne renvoi aucune valeur ou résultat (ainsi l'application du mot procédure)
    """
    id = genidlog()
    Data = jsonopen("log.json", "r")
    Data["log"].append(
        {
            "id": id,
            "actionneur": ip,
            "action": text,
            "date": datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    jsonwritter("w", Data, "log.json")


################################################################################################## INFORMATION


def inf():
    """
    Cette fonction permet de donner des informations sur chacune des actions possible dans le menu
    :return:
    Cette fonction ne renvoie rien
    """
    print(
        "\n",
        "Sur quelle partie de la console souhaiter vous avoir des informations ?",
        "\n",
        "1/ Re-iniatiler la console",
        "\n",
        "2/ Modifier le mot de passe",
        "\n",
        "3/ Gérer le chauffage",
        "\n",
        "4/ Gérer la lumière",
        "\n",
        "5/ Gérer la fontaine",
        "\n",
        "6/ Obtenir la dernière action effectué",
        "\n",
        "7/ Information",
        "\n",
        "8/ Fermer le terminal",
        "\n",
    )
    test_i = False
    while test_i == False:
        rslt_i = input(" Que souhaitez vous faire (information) : ")
        try:
            rslt_i = int(rslt_i)
            test_i = True
        except:
            print(" Veuillez saisir une action valide")
    if rslt_i == 1:
        print(menu.__doc__)
    elif rslt_i == 2:
        print(modifmdp.__doc__)
    elif rslt_i == 3:
        print(chauff.__doc__)
    elif rslt_i == 4:
        print(lumiere.__doc__)
    elif rslt_i == 5:
        print(fontaine.__doc__)
    elif rslt_i == 6:
        print(
            "L'action obtenir les dernières actions effectué permet d'afficher les dernières log peut importe l'origine (cote client ou serveur)"
        )
    elif rslt_i == 7:
        print(inf.__doc__)
    elif rslt_i == 8:
        print(
            "L'action fermer le terminal est directement incluse dans le menu, elle permet de fermer le terminal"
        )


affichage()
