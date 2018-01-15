#!/usr/python
# -*- coding: utf-8-*-

import sys


from optparse import OptionParser


def read_options():

    reload(sys)
    sys.setdefaultencoding('utf8')

    # setting system for Option parser

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

    return  parser.parse_args()
