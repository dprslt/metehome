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

import numpy as np
import sunpos2 as sunpos
import math
import time
import os.path
from PIL import Image
from optparse import OptionParser

import color

import sys

import fastopc



###
if __name__ == '__main__':

    # setting system for Option parser
    reload(sys)
    sys.setdefaultencoding('utf8')

    np.set_printoptions(linewidth=200)

    ############################ Traitement ####################################

    steps = 0

    leds = []

    parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
    parser.add_option("-a", "--azimut",
                        action="store",
                        dest="azimut_maison",
                        default=0,
                        help="Azimut de la maison")
    parser.add_option("--latitude",
                        action="store",
                        dest="lat_maison",
                        default=45.1317,
                        help="latitude de la maison")
    parser.add_option("--longitude",
                        action="store",
                        dest="long_maison",
                        default=6.1661,
                        help="longitude de la maison")
    parser.add_option("-d", "--diffusion",
                        action="store",
                        dest="diffusion_soleil",
                        default=6,
                        help="[Avancé] Coefficient de diffusion du soleil")
    parser.add_option("-u", "--upscaling",
                        action="store",
                        dest="matrix_upscaling",
                        default=1.2,
                        help="[Avancé] Taux d'agrandissement de la matrice de visualisation du soleil")
    parser.add_option("-l", "--limite",
                        action="store",
                        dest="limite_coucher_de_soleil",
                        default=5,
                        help="[Avancé] Limite d'azimut permettant de débuter le coucher du soleil afin de permettre un dégradé")
    parser.add_option("-x", "--longueur",
                        action="store",
                        dest="longueur_maison",
                        default=75,
                        help="Longueur en nombre de leds de la maison. Paramètre pris en compte lorsque -r activé")
    parser.add_option("-y", "--largeur",
                        action="store",
                        dest="largeur_maison",
                        default=75,
                        help="Largeur en nombre de leds de la maison. Paramètre pris en compte lorsque -r activé")



    (options,args) = parser.parse_args()

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

    ############################ Constantes ####################################
    # Lorsque l'orientation du soleil passe en dessous de cette limite,
    # c'est le debut de la nuit noire
    # Cette valeur sert à créer un dégradé pour la tombée de la nuit
    LIMITE_COUCHER_DE_SOLEIL = int(options.limite_coucher_de_soleil)
    print "\tLIMITE_COUCHER_DE_SOLEIL : ", LIMITE_COUCHER_DE_SOLEIL

    VALEUR_DE_NORMALISATION_DE_LA_MATRICE = 255

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

    OPC_server = fastopc.FastOPC()

    steep = 180
    while(True):

        upscaled_matrix = np.zeros((largeur, longueur), dtype=float)

        # On calcul l'azimut et l'élévation du soleil en fonction de la date et
        # du lieu.
        azimut_soleil, elevation = sunpos.sun_position(2017,07,10,hour=(steps / 60)%24, minute=steps%60, lat=lat_maison, longitude=long_maison)
        # Projection d" la position du solein sur un plan
        x, y = project_sun(elevation, azimut_soleil - azimut_maison, largeur, longueur)

        print steps," : ",(steps/60)%24,"h ", steps%60,"m  elevation : ",int(elevation)

        # Placement du soleil sur le plan
        print "x : " ,x, " y : ",y
        upscaled_matrix[y,x] = 1.

        # Diffusion de l'aura du soleil
        # Le facteur de 3.5 régule la force de la diffusion,
        # On l'a déterminé empiriquement
        for i in range(int(max(largeur, longueur) * 3.5)):
            color.diffusion(upscaled_matrix)


        # Normalisation des valeurs
        upscaled_matrix = (upscaled_matrix/upscaled_matrix.max())

        # Si le soleil est couché, on met en place une descende graduelle de la luminosité
        if elevation < 0 :
            degrade = (LIMITE_COUCHER_DE_SOLEIL - min(-elevation, LIMITE_COUCHER_DE_SOLEIL)) / LIMITE_COUCHER_DE_SOLEIL
            upscaled_matrix = (upscaled_matrix * degrade)

        upscaled_colors = color.computeColor(elevation, upscaled_matrix)


        colors = upscaled_colors[largeur_upscaling:largeur - largeur_upscaling, longueur_upscaling:longueur-longueur_upscaling]
        colors = colors.reshape((largeur_maison * longueur_maison, 3))

        colors = colors * 0.5

        OPC_server.putPixels(0,colors)


        # Rendu de l'image de prévisualisation
        upscaled_colors[largeur_upscaling,longueur_upscaling:-longueur_upscaling] = (255,0,0)
        upscaled_colors[-largeur_upscaling-1,longueur_upscaling:-longueur_upscaling] = (255,0,0)
        upscaled_colors[largeur_upscaling:-largeur_upscaling, longueur_upscaling] = (255,0,0)
        upscaled_colors[largeur_upscaling:-largeur_upscaling, -longueur_upscaling-1] = (255,0,0)
        img = Image.fromarray(np.uint8(upscaled_colors),'RGB')
        #img = Image.fromarray(upscaled_matrix,'L')
        img.save('imgs/s.png')

        steps += 10
        time.sleep(0.09)
