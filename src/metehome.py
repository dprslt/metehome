#!/usr/python
# -*- coding: utf-8-*-
"""
Cette fonction calcul la projection du soleil sur un plan horizontal dans les
dimensions indiquées.
Les coordonées sont données par rapport au coin supérieur gauche du plan.

Les paramètres d'entrées proviennent de la librairie sunpos2

elevation : Elevation du soleil en degres
azimut : azimut du soleil en degres
size_x et size_y : dimensions de la matrice
"""
def project_sun(elevation, azimut, size_x, size_y):
    mid_x = size_x/2
    mid_y = size_y/2

    distance_from_center = math.cos(math.radians(elevation)) * mid_x

    y = mid_y - math.cos(math.radians(azimut)) * distance_from_center
    x = mid_x + math.sin(math.radians(azimut)) * distance_from_center

    return (int(x),int(y))

def render_image(upscaled_colors):
    upscaled_colors[largeur_upscaling,longueur_upscaling:-longueur_upscaling] = (255,0,0)
    upscaled_colors[-largeur_upscaling-1,longueur_upscaling:-longueur_upscaling] = (255,0,0)
    upscaled_colors[largeur_upscaling:-largeur_upscaling, longueur_upscaling] = (255,0,0)
    upscaled_colors[largeur_upscaling:-largeur_upscaling, -longueur_upscaling-1] = (255,0,0)
    img = Image.fromarray(np.uint8(upscaled_colors),'RGB')
    img.save('imgs/s.png')

from datetime import datetime

def get_hours_minutes():
    t = datetime.now().strftime("%H%M")
    return t[0:2], t[2:4]

import numpy as np
import sunpos2 as sunpos
import math
import time
import os.path
from PIL import Image

import color
import options

import sys

import fastopc

###
if __name__ == '__main__':

    np.set_printoptions(linewidth=200)

    ############################ Traitement ####################################

    (options,args) = options.read_options()

    # Ci-dessous les paramètres nécessaires au fonctionement du programme.
    ############################################################################
    # Azimut de la piece, et position GPS de la maison => à déterminer sur place
    print('Options : ')
    azimut_maison = int(options.azimut_maison)
    print "\tazimut_maison : ", azimut_maison

    lat_maison = float(options.lat_maison)
    print "\tlat_maison : ", lat_maison

    long_maison = float(options.long_maison)
    print "\tlong_maison : ", long_maison

    diffusion_soleil = int(options.diffusion_soleil)
    print "\tdiffusion_soleil : ",diffusion_soleil

    matrix_upscaling = float(options.matrix_upscaling)
    print "\tmatrix_upscaling : ", matrix_upscaling

    user_luminosity = float(options.luminosity)
    print "\luminosité utilisateur : ", user_luminosity

    ############################ Constantes ####################################
    # Lorsque l'orientation du soleil passe en dessous de cette limite,
    # c'est le debut de la nuit noire
    # Cette valeur sert à créer un dégradé pour la tombée de la nuit
    LIMITE_COUCHER_DE_SOLEIL = int(options.limite_coucher_de_soleil)
    print "\tLIMITE_COUCHER_DE_SOLEIL : ", LIMITE_COUCHER_DE_SOLEIL

    # Dimensions en nombres de leds
    longueur_maison = int(options.longueur_maison)
    print "\tlongueur_maison : ", longueur_maison

    largeur_maison  = int(options.largeur_maison)
    print "\tlargeur_maison : ",largeur_maison

    print

    longueur_upscaling = int(longueur_maison*(matrix_upscaling-1)/2)
    largeur_upscaling = int(largeur_maison*(matrix_upscaling-1)/2)

    print "Longueur upscaling : ", longueur_upscaling, " Largeur upscaling : ", largeur_upscaling

    largeur = largeur_maison + largeur_upscaling * 2
    longueur = longueur_maison + longueur_upscaling * 2

    print "Taille totale : ", largeur,", ", longueur


    ############# Boucle de traitement #############

    OPC_server = fastopc.FastOPC()


    VALEUR_DE_NORMALISATION_DE_LA_MATRICE = 255
    SECURITY_LUMINOSITY=0.7

    steps = 0
    while(True):

        upscaled_matrix = np.zeros((largeur, longueur), dtype=float)

        # On calcul l'azimut et l'élévation du soleil en fonction de la date et
        # du lieu.
        azimut_soleil, elevation = sunpos.sun_position(2017,07,10,hour=(steps / 60)%24, minute=steps%60, lat=lat_maison, longitude=long_maison)
        # Projection de la position du solein sur un plan
        x, y = project_sun(elevation, azimut_soleil - azimut_maison, largeur, longueur)

        print steps," : ",(steps/60)%24,"h ", steps%60,"m  elevation : ",int(elevation)

        # Placement du soleil sur le plan
        print "x : " ,x, " y : ",y
        upscaled_matrix[y,x] = 1.

        # Diffusion de l'aura du soleil sur la matrice
        # Le facteur de 3.5 régule la force de la diffusion,
        # On l'a déterminé empiriquement
        # TODO Cette méthode de calcule est trés complexe, On doit pouvoir trouver
        # une approche plus efficace.
        for i in range(int(max(largeur, longueur) * 3.5)):
            color.diffusion(upscaled_matrix)
        # Normalisation des valeurs car l'algo de diffusion peut faire
        # augmenter des valeurs au dessus de 1
        upscaled_matrix = (upscaled_matrix/upscaled_matrix.max())

        # Si le soleil est couché, on met en place une descende graduelle de la luminosité
        # pour éviter un coucher et un levé trop brusque
        if elevation < 0 :
            degrade = (LIMITE_COUCHER_DE_SOLEIL - min(-elevation, LIMITE_COUCHER_DE_SOLEIL)) / LIMITE_COUCHER_DE_SOLEIL
            upscaled_matrix = (upscaled_matrix * degrade)


        # Calcul de la couleur à partir de la position du soleil
        upscaled_colors = color.computeColor(elevation, upscaled_matrix)

        # Sélection de la zone à afficher en excluant les bordures
        # On ne peut pas utiliser largeur_upscaling:-largeur_upscaling car l'upscaling
        # peut être égale à 0
        colors = upscaled_colors[largeur_upscaling:largeur - largeur_upscaling, longueur_upscaling:longueur-longueur_upscaling]
        #Transformation de la matrice en un tableau de pixel à une dimention
        colors = colors.reshape((largeur_maison * longueur_maison, 3))

        # Application du coefficient de correction pour limiter la luminosité des leds
        colors = colors * user_luminosity * SECURITY_LUMINOSITY

        # On utilise le client OPC pour envoyer les pixels à afficher à la matrice
        OPC_server.putPixels(0,colors)


        # Rendu de l'image de prévisualisation
        render_image(upscaled_colors)

        steps += 10
        time.sleep(0.09)
