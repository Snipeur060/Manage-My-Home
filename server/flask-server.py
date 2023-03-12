__author__ = "Alexandre - Léo - Maxime"

#Important: Ici le terme Cron fait référence à une tâche qui s'exécute à une intervalle régulière


#####################################
#       On réalise les imports      #
#####################################
from time import sleep
from flask import Flask, render_template, request, redirect, session, json
from flask_session import Session
import atexit
import json
from colorama import Fore, Back, Style
import colorama
from passlib.hash import sha256_crypt
import socket
from functools import wraps
from apscheduler.schedulers.background import BackgroundScheduler
from function.json_manager import (
    jsonopen,
    jsonwritter,
    getidlog,
    getlastlog,
    changestate,
)
import rpyc
from datetime import datetime

#############################
#       Fin des imports     #
#############################

############################
#       Fonction RPYC      #
############################


def callanswer():
    """
    Cette fonction demande à l'utilisateur entre deux possibilités
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
        startconnexion()


def startconnexion():
    """
    Cette fonction permet de se connecter au serveur rpyc
    :return:
    Ne renvoie rien, mais défini les variables suivantes (global):
        - command_service
        - conn
    """

    try:
        # On a défini les différentes variables que nous utiliserons pour communiquer avec le serveur rpyc
        global conn
        global command_service
        # on se connecte au serveur rpyc
        conn = rpyc.connect("localhost", 18861)
        # on récupère les fonctions disponibles sur le serveur rpyc
        command_service = conn.root
    except:
        # en cas d'erreur, on demande à l'utilisateur de faire un choix
        callanswer()


# On lance l'appel de connexion au serveur rpyc

startconnexion()


def send(code):
    """
    Cette fonction permet d'envoyer une commande à l'Arduino
    :param code:
    Le paramètre code correspond à la commande à envoyer à l'Arduino
    :return:
    Cette fonction renvoie le résultat de la commande send exécuté sur le serveur rpyc
    """
    try:
        return command_service.exposed_execute(code)
    except:
        pass


def getdata():
    """
    Cette fonction permet de récupérer les données de l'Arduino
    :return: Renvoie les données de l'Arduino
    """
    try:
        return command_service.exposed_get_info()
    except:
        pass


#################################
#       Tâches programmées      #
#################################


def execute_action(action):
    """
    Cette fonction a pour but de gérer l'exécution d'une action tout en appelant les différentes fonctions nécessaires
    :param action: L'action à exécuter
    :return: Ne renvoie rien
    """
    # On affiche en console que l'action est en cours d'exécution
    print(f"Executing action: {action['name']} - command: {action['command']}")
    # On exécute la commande (celle de l'action) sur arduino en passant par rpyc
    send(str(action["command"]))
    # on fait le log de l'action
    logger(
        f"Execution de l'action: {action['name']} - commande : {action['command']}",
        "[Action programmée]",
    )
    # le sleep est dans le but d'éviter d'avoir des actions qui s'enchaînent de manière succincte
    sleep(2)


def create_action(name, command, date):
    """
    Cette fonction renvoie une action sous forme de dictionnaire et donc exploitable plus facilement
    par la suite
    :return: Renvoie sous un format adapté une action pour pouvoir mieux la traiter après
    """
    return {
        "name": name,
        "command": command,
        "date": date.isoformat(),
        "dejaexecute": False,
    }


def save_action(action):
    """
    Cette fonction sert à enregistrer dans le fichier actions.json une action dans le but de la sauvegarder
    :return: Ne renvoie rien
    """
    try:
        # on essaie dou'vire le fichier tout en prenant en compte le cas de corruption
        actions = jsonopen("actions.json", "r")
    except:
        # en cas de corruption le fichier ne voudra pas s'ouvrir alors remedions au problème en ajoutant
        # les valeurs / la structure necessaire
        actions = {"actions": []}
    # on ajoute l'action à la liste des actions (du moins dans le fichier json chargé au préalabe)
    actions["actions"].append(action)
    # on sauvegarde les modifications
    jsonwritter("w", actions, "actions.json")


def check_actions():
    """
    Fonction qui a pour but de gérer les actions qui remplissent les critères suivants -->
    l'action n'a pas déjà été exécuté et elle correspond à la date actuelle (à la minute près)
    :return: Ne renvoie rien
    """
    actions = jsonopen("actions.json", "r")
    # on mémorise la date actuelle
    now = datetime.now()
    # on parcourt toutes les actions du fichier actions.json
    for action in actions["actions"]:
        # on formate la date à un format qui nous permettra de mieux la travailler
        action_time = datetime.fromisoformat(action["date"])
        # Ici, nous analysons le temps à la minute prêt, mais aussi dans le cas où le temps serait déjà dépassé ou alors déja exécuté
        if (
            action_time.replace(second=0, microsecond=0)
            <= now.replace(second=0, microsecond=0)
            and action["dejaexecute"] == False
        ):
            # on exécute l'action
            execute_action(action)
            # ont redéfini le paramètre dejaexecute à True pour éviter de l'exécuter à nouveau
            action["dejaexecute"] = True
            # on enregistre l'action
            save_action_updates(action)


def save_action_updates(action):
    """
    Permet de sauvegarder les modifications apportées à une action (après son exécution)
    :param action: L'action à sauvegarder
    :return: Ne renvoie rien
    """
    actions = jsonopen("actions.json", "r")
    # on énumère toutes les actions
    for i, act in enumerate(actions["actions"]):
        if act["name"] == action["name"]:
            actions["actions"][i] = action
    jsonwritter("w", actions, "actions.json")


######################################################
#       Fin des fonctions de tâches programmées      #
######################################################


#######################################################
#       Décorateur pour simplifier la connexion       #
#######################################################


def login_required(f):
    """
    Cette fonction permet de vérifier si la personne est connectée
    :param f:
    Ce paramètre est déterminé par wraps, il permet de poursuivre sur la fonction d'après lorsque la fonction possède toutes les conditions
    https://python.doctor/page-decorateurs-decorator-python-cours-debutants
    :return:
    Lorsque la personne n'est pas connectée, la fonction peut rediriger vers la page login
    Quand l'utilisateur est connecté, on lance la fonction qui suit.
    """

    @wraps(f)
    def wrap(*args, **kwargs):
        if "username" in session:
            return f(*args, **kwargs)
        else:
            print(
                Back.RED
                + Fore.BLACK
                + "Erreur: L'utilisateur n'était pas connecté"
                + Style.RESET_ALL
            )
            return redirect("/login")

    return wrap


##############################################################
#       Fonction pour récupérer les valeurs de capteurs      #
#           Les différentes conversions y sont réalisées     #
##############################################################


def getstat():
    """
    Cette fonction gère les tâches CRON
    Ici, le programme gère :
     - Récupérer la valeur du capteur de lumière en lux et le transformer en pourcentage
     - Appliquer la tâche automatique concernant la lumière → Défini par l'utilisateur exemple : si luminosité < 50% alors allumer
    :return:
    Cette fonction ne renvoie rien.
    """
    try:
        print("[CRON] Update des valeurs des capteurs")
        # On récupère la valeur du capteur de lumière et de la température
        lumandtemp = getdata()
        # on sépare les valeurs pour obtenir des valeurs exploitables
        lumandtemp = lumandtemp.replace(",", " ").split(" ")
        # on récupère et stock ces valeurs
        lum = float(lumandtemp[1])
        temp = float(lumandtemp[0])
        Data = jsonopen("infos.json", "r")
        # on calcul la lumière pour obtenir les % de luminosité
        lum = round(100 - round((100 - (int(lum) / 1000) * 100), 2),2)

        # print("[CRON] Valeur du capteur de lumière : " + str(lum) + " %")
        # print("[CRON] Valeur du capteur de température : " + str(temp) + " °C")

        # on met au format qui nous intéresse et facilite le traitement
        datetoday = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        Data["lumin"] = lum
        Data["lumin_date"] = datetoday
        Data["temperature"] = temp
        Data["temperature_date"] = datetoday
        # on sauvegarde les modifications
        jsonwritter("w", Data, "infos.json")
        dtv = jsonopen("task.json", "r")

        # ici, on vérifie les différentes conditions pour savoir si oui ou non, on doit exécuter une action
        # en l'occurrence exemple : L'utilisateur va définir à 50% si la luminosité est inférieure à 50% alors allumer la lumière

        if dtv["lum"] != -1 and float(dtv["lum"]) >= float(lum):
            send("5")
            changestate("yellow", "ON")
            sleep(2)
        elif dtv["lum"] != -1 and float(dtv["lum"]) < float(lum):
            send("6")
            # pour changer l'état de la lumière
            changestate("yellow", "OFF")
        if dtv["temp"] != -1 and float(dtv["temp"]) >= float(temp):
            send("3")
            changestate("red", "ON")
        elif dtv["temp"] != -1 and float(dtv["temp"]) < float(temp):
            send("4")
            changestate("red", "OFF")
    except:
        pass


##################################################
#       Tâche cron réalisé avec Apscheduler      #
##################################################


sched = BackgroundScheduler(daemon=True)
# on ajoute les fonctions à exécuter dans les tâches cron / programmées
sched.add_job(getstat, "interval", minutes=5)
sched.add_job(check_actions, "interval", minutes=0.8)
# on lance les taches
sched.start()

######################################################
#       Fin Tâche cron réalisé avec Apscheduler      #
######################################################


###############################################
#       Paramètre de l'application Flask      #
###############################################

app = Flask(__name__)
# On défini si la session sera permanente ou non
app.config["SESSION_PERMANENT"] = False
# ici la méthode pour enregistrer les sessions (en l'occurrence, on utilise filesystem donc dans des fichiers)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
# on retire le mode debug
app.debug = False

##################################################
#      Fin paramètre de l'application Flask      #
##################################################

print(
    Fore.LIGHTGREEN_EX + Style.BRIGHT + "IP acutelle du serveur --> ",
    socket.gethostbyname(socket.gethostname()) + Style.RESET_ALL,
)

################################################################
#       Fonction pour enregistrer les logs dans logs.json      #
################################################################


def logger(text: str, ip: str = socket.gethostbyname(socket.gethostname())):
    """
    Cette procédure permet de mettre dans un fichier json un log (Un Historique). Exemple --> L'utilisateur a activé la lumière à 19 h 25
    :param text:
    Le paramètre text ici correspond au message à enregistrer. Exemple --> [CHAUFFAGE] Le chauffage a été allumé
    :param ip: (optionnel) L'adresse IP de l'utilisateur par défaut, il prend l'ip utilisé par le serveur
    :return:
    Cette procédure ne renvoie aucune valeur ou résultat (ainsi l'application du mot procédure)
    """
    Data = jsonopen("log.json", "r")
    # La fonction genidlog nous permet d'obtenir un identifiant unique pour le log
    Data["log"].append(
        {
            "id": genidlog(),
            "actionneur": ip,
            "action": text,
            "date": datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    # on enregistre les modifications
    jsonwritter("w", Data, "log.json")


########################################
#       Fin de la fonction logger      #
########################################


#############################################################################################
#       Fonction pou rendre plus simple la collecte de données ainsi que leurs analyses     #
#############################################################################################


def getinfo():
    """
    Cette fonction permet le renvoi de valeurs stockées dans un fichier json
    :return:
    Renvoie les valeurs suivantes :
        - La température actuelle en degrés.
        - La luminosité en %.
        - La date ainsi que l'heure à laquelle les valeurs ont été mises à jour.
    """
    Data = jsonopen("infos.json", "r")
    temp = Data["temperature"]
    lum = Data["lumin"]
    lumdate = Data["lumin_date"]
    tempdate = Data["temperature_date"]
    # on renvoie les valeurs
    return temp, lum, lumdate, tempdate


def genidlog():
    """
    Cette fonction a pour but de faciliter la génération d'un identifiant unique dans le fichier de log (Historique)
    :return:
    Cette fonction renvoie un INTEGER (un nombre entier)
    """
    # on ouvre notre fichier
    Dte = jsonopen("id_log.json", "r")
    vf = Dte["id"] + 1
    fin = {"id": vf}
    tv = vf
    jsonFile = open("json/id_log.json", "w+")
    jsonFile.write(json.dumps(fin))
    jsonFile.close()
    return tv


####################################################
#       Fin des fonctions d'aide au traitement     #
####################################################

##################################################################################
#       Fonction pour remettre à l'état précèdent la déconnexion du serveur      #
##################################################################################


def activate_job():
    """
    Cette procédure a pour but d'initialiser la carte lors du démarrage de l'application. Ainsi au démarrage de\n
    l'application si le chauffage était allumé avant l'extinction alors il l'est toujours ainsi, on rallume les\n
    différentes leds qui correspondent à un objet en particulier ici.\n
    :return:
    Cette procédure ne renvoie pas de résultat.
    """
    print("Activation des jobs")
    Data = jsonopen("state.json", "r")
    if Data["red"] == "ON":
        send("3")
    sleep(3)
    if Data["blue"] == "ON":
        send("7")
    sleep(3)
    if Data["yellow"] == "ON":
        send("5")


############################
#       Page de login      #
############################
@app.route("/login")
def logind():
    """
    Cette fonction est spéciale, elle est utilisée par le décorateur de flask elle ne fait que de l'affichage
    :return:
    Elle va renvoyer la page auth-signin.html contenu dans le dossier templates
    """
    print(Back.GREEN + "La page login a été request " + Style.RESET_ALL)
    return render_template("auth-signin.html")


####################################
#           Route /loging          #
#       Permet de se connecter     #
####################################


@app.route("/login", methods=["POST"])
def login():
    """
    Cette fonction est, elle aussi, spéciale. Elle réalise le traitement concernant la connexion
    :return:
    Elle peut retourner :
        - Un code d'erreur qui signifie que l'utilisateur n'a pas était trouvé.
        - Une redirection flask vers / (ce qui signifie que la connexion s'est bien effectuée)
    """
    # on récupère les données du formulaire
    theusername = request.form["username"]
    thepassword = request.form["password"]
    Data = jsonopen("user.json", "r")
    # on parcourt le fichier en l'occurrence la structure est la suivante {user: []} ce qui explique l'imbrication des for
    for data in Data:
        for x in Data[data]:
            # on vérifie si le username correspond ainsi que le mot de passe en l'occurrence encrypté en sha256
            if (
                theusername == x["username"]
                and sha256_crypt.verify(thepassword, x["password"]) == True
            ):
                # on enregistre l'utilisateur dans la session avec ses différentes données
                session["username"] = theusername
                session["picture"] = x["picture"]
                session["email"] = x["email"]
                session["ip"] = socket.gethostbyname(socket.gethostname())
                print(Back.BLUE + "L'utilisateur s'est login " + Style.RESET_ALL)
                return redirect("/")

    print(Back.RED + "Une tentative de login a échoué" + Style.RESET_ALL)
    return redirect("/login?code=L'utilisateur n'a pas été trouvé")


#######################
######  FIN LOGIN  ####
#######################

#####################################################################################
#                                   Route /                                         #
#       Correspond à la page où l'on peut exécuter de nombreuses actions            #
#       login_required --> Authentification requise                                 #
#####################################################################################


@app.route("/", methods=["POST", "GET"])
@login_required
def home():
    """
    Le login est ici requis\n
    C'est une fonction qui est utilisée par flask elle accepte les méthodes POST et GET.\n
    Elle effectue du traitement ainsi que de l'affichage (le tout est condensé dans la même route, on contrôle juste la méthode).\n
    :return:
    Cette fonction retourne la page index.html avec les différentes variables.
    """
    messagered = None
    messageblue = None
    messageyellow = None
    # dans le cas où la method post est envoyé
    if request.method == "POST":
        # on utilise cette fonction request.form.get("redlight") dus aux différents formulaires pour une meilleure compatibilité et stabilité
        if request.form.get("redlight") == "ON":
            # on envoie la commande au serveur
            send("3")
            messagered = "okon"
            # on enregistre l'état dans le fichier state.json avec cette fonction
            changestate("red", "ON")
            # on enregistre l'action dans le fichier de log
            logger("[CHAUFFAGE] Le chauffage a été allumé")
        elif request.form.get("redlight") == "OFF":
            send("4")
            messagered = "okoff"
            logger("[CHAUFFAGE] Le chauffage a été éteint")
            changestate("red", "OFF")
        elif request.form.get("bluelight") == "ON":
            send("7")
            messageblue = "okon"
            logger("[FONTAINE] La fontaine a été allumée")
            changestate("blue", "ON")
        elif request.form.get("bluelight") == "OFF":
            messageblue = "okoff"
            send("8")
            changestate("blue", "OFF")
            logger("[FONTAINE] La fontaine a été éteinte")
        elif request.form.get("yellowlight") == "ON":
            messageyellow = "okon"
            send("5")
            changestate("yellow", "ON")
            logger("[LUMIERE] La lumière a été allumée")
        elif request.form.get("yellowlight") == "OFF":
            send("6")
            messageyellow = "okoff"
            changestate("yellow", "OFF")
            logger("[LUMIERE] La lumière a été éteinte")
        else:
            pass  # inconnu
    print(Fore.CYAN + "La page home a été request " + Style.RESET_ALL)
    # on récupère les données du fichier json en l'occurrence le statut des leds
    Data = jsonopen("state.json", "r")
    stateyellow = Data["yellow"]
    dateyellow = Data["yellow_date"]
    stateblue = Data["blue"]
    dateblue = Data["blue_date"]
    statered = Data["red"]
    datered = Data["red_date"]
    ip = session["ip"]
    image = session["picture"]
    # on adapte au format du return de la fonction getinfo()
    tempmes, lummes, datelum, temperature_date = getinfo()
    author, thedate, action = getlastlog()
    # on retourne la page index.html avec les différentes variables
    return render_template(
        "index.html",
        author=author,
        thedate=thedate,
        action=action,
        messageyellow=messageyellow,
        messageblue=messageblue,
        messagered=messagered,
        ip=ip,
        img=image,
        ETATr=statered,
        ETATb=stateblue,
        ETATy=stateyellow,
        blue_date=dateblue,
        red_date=dateyellow,
        yellow_date=datered,
        temp=tempmes,
        lum=lummes,
        datelum=datelum,
        datetemp=temperature_date,
    )


#######################################################
#                  Route /log                         #
#       Permet de voir les différents logs            #
#       login_required --> Authentification requise   #
#######################################################


@app.route("/log")
@login_required
def logshow():
    """
    Le login ici est requis\n
    Cette fonction est utilisée par le décorateur flask\n
    Elle a pour objectif de montrer les derniers logs
    :return:
    Cette fonction renvoie une page html en l'occurrence log.html avec les différentes variables
    """
    table = []
    # on souhaite afficher les 15 derniers logs
    for i in range(0, 15):
        # on récupère les données du fichier log
        Dat = jsonopen("log.json", "r")
        for data in Dat:
            for x in Dat[data]:
                # on prend l'id du log de manière decroissante
                if x["id"] == (int(getidlog()) - i):
                    # on récupère les valeurs
                    idof = x["id"]
                    author = x["actionneur"]
                    date = x["date"]
                    action = x["action"]
                    # on ajoute les données dans une liste
                    table.append(
                        {"id": idof, "author": author, "date": date, "action": action}
                    )
    ip = session["ip"]
    image = session["picture"]
    # on retourne la page log.html avec les différentes variables
    return render_template("log.html", ip=ip, img=image, dtlist=table)


##########################################################
#                  Route /logtaks                        #
#       Permet de voir les différents logs des tâches    #
#       login_required --> Authentification requise      #
##########################################################


@app.route("/logtask")
@login_required
def tasklog():
    """
    Le login ici est requis\n
    Cette fonction est utilisée par le décorateur flask\n
    Elle a pour objectif de montrer les derniers logs des actions programmées
    :return:
    Cette fonction renvoie une page html en l'occurrence log-task.html avec les différentes variables
    """

    def left_append(table, element):
        """
        Cette fonction permet d'ajouter un élément au début d'une liste
        :param table: La liste
        :param element: L'élément à ajouter (peut-être un dictionnaire, une liste, un tuple, etc...)
        :return: Ne renvoie rien, mais modifie la liste (table)
        """
        table.insert(0, element)

    table = []
    counter = 0
    Dat = jsonopen("actions.json", "r")
    for data in Dat:
        for x in Dat[data]:
            # on souhaite afficher les 15 derniers logs
            if counter <= 15:
                counter += 1
                name = x["name"]
                date = x["date"]
                action = x["command"]
                state = x["dejaexecute"]
                # on ajoute les données dans une liste en ajoutant par la gauche
                left_append(
                    table,
                    {"name": name, "date": date, "action": action, "state": state},
                )
    ip = session["ip"]
    image = session["picture"]
    # on retourne la page log-task.html avec les différentes variables
    return render_template("log-task.html", ip=ip, img=image, dtlist=table)


#######################################################
#                  Route /logout                      #
#       Permet de voir les différents logs            #
#       login_required --> Authentification requise   #
#######################################################


@app.route("/logout")
@login_required
def logo():
    """
    Cette fonction est utilisée par le décorateur flask et nécessite d'être connecté.\n
    Elle a pour but de déconnecter l'utilisateur en effaçant sa session (en l'occurrence toutes les clés de session)
    :return:
    Cette fonction retourne un redirect de flask sur la route /login
    """
    [session.pop(key) for key in list(session.keys())]
    return redirect("/login")


############################################################
#                      Route /task                         #
#       Permet d'actionner des actions programmé ou pas    #
#       login_required --> Authentification requise        #
############################################################


@app.route("/task", methods=["POST", "GET"])
@login_required
def tasktoshow():
    """
    Cette fonction nécessite la connexion de plus cette fonction est utilisée, appelée par le décorateur flask @app.route\n
    Elle a pour objectif de montrer une page avec les tâches à exécuter et à programmer.
    :return:
    Cette fonction retourne tout simplement la page task.html avec les différentes variables
    """
    # ici, le script sera exécuté si la methode est post
    if request.method == "POST":
        # on récupère les données du formulaire
        if request.form.get("valp") != None:
            Dat = jsonopen("task.json", "r")
            Dat["lum"] = request.form.get("valp")
            jsonwritter("w", Dat, "task.json")
        # on vérifie si le formulaire est bien rempli
        elif request.form.get("tempval") != None:
            Data = jsonopen("task.json", "r")
            Data["temp"] = request.form.get("tempval")
            jsonwritter("w", Data, "task.json")
        # ici, le formulaire est celui des actions programmées
        elif request.form.get("chooseoption") != None:
            choosen = request.form.get("chooseoption")
            if choosen == "onchauff":
                # ici, on enregistre une action tout en l'ayant créé (dans le fichier actions.json)
                save_action(
                    create_action(
                        request.form.get("chooseoption"),
                        "3",
                        datetime.strptime(request.form.get("date"), "%Y-%m-%dT%H:%M"),
                    )
                )
            elif choosen == "offchauff":
                save_action(
                    create_action(
                        request.form.get("chooseoption"),
                        "4",
                        datetime.strptime(request.form.get("date"), "%Y-%m-%dT%H:%M"),
                    )
                )
            elif choosen == "onfontaine":
                save_action(
                    create_action(
                        request.form.get("chooseoption"),
                        "7",
                        datetime.strptime(request.form.get("date"), "%Y-%m-%dT%H:%M"),
                    )
                )
            elif choosen == "offfontaine":
                save_action(
                    create_action(
                        request.form.get("chooseoption"),
                        "8",
                        datetime.strptime(request.form.get("date"), "%Y-%m-%dT%H:%M"),
                    )
                )
            elif choosen == "onlumiere":
                save_action(
                    create_action(
                        request.form.get("chooseoption"),
                        "5",
                        datetime.strptime(request.form.get("date"), "%Y-%m-%dT%H:%M"),
                    )
                )
            elif choosen == "offlumiere":
                save_action(
                    create_action(
                        request.form.get("chooseoption"),
                        "6",
                        datetime.strptime(request.form.get("date"), "%Y-%m-%dT%H:%M"),
                    )
                )
    else:
        pass  # inconnu
    ip = session["ip"]
    image = session["picture"]
    return render_template("task.html", ip=ip, img=image)


#########################################
#     Section pour lancer le serveur    #
#########################################

if __name__ == "__main__":
    activate_job()
    text = "Serveur flask en ligne\n"
    asciitext = """
    ________           __  
   / ____/ /___ ______/ /__
  / /_  / / __ `/ ___/ //_/
 / __/ / / /_/ (__  ) ,<   
/_/   /_/\__,_/____/_/|_|                                      
    """
    print(
        Fore.GREEN
        + Style.BRIGHT
        + text
        + Style.RESET_ALL
        + Fore.BLUE
        + "\n"
        + asciitext
        + Style.RESET_ALL
    )
    app.run("0.0.0.0", port=25526)
    ###############################
    # Serveur en mode production
    # from waitress import serve
    # app.debug = False
    # on lance notre serveur (sous flask mais avec waitress)
    # serve(app, host="0.0.0.0", port=25526, _quiet=True)

atexit.register(lambda: sched.shutdown())
