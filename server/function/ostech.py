from sys import platform
import os
def findos():
    """
    Cette fonction à pour but de renvoyer le type du système
    :return:
    Renvoi unix ou windows
    """
    if platform not in ('win32', 'cygwin'):
        return 'unix'
    else:
        return 'windows'

def clearScreen(os):
    """
    Cette procédure à pour but de supprimer les anciens messages dans la console
    :param os:
    Prend en compte le système (l'os de l'ordinateur)
    :return:
    Cette procédure ne renvoi rien elle efface la console.
    """
    from subprocess import call
    if os == 'unix':
        command = 'clear'
    else:
        command = 'cls'
    call(command, shell=True)

def smoothstop():
    """
    Permet de stopper le script en cas d'erreur contrôlé  de manière contrôlé et surtout ne pour que l'on puisse voir l'erreur avant que la console se ferme
    :return:
    La procédure ne renvoi rien comme indiqué dans le nom procédure
    """
    print("Press Enter to exit ...")
    input()
    os._exit(0)
