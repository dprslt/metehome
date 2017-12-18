#!/usr/python
# -*- coding: utf-8-*-
"""
Cette fonction calcul la projection du soleil sur un plan horizontal dans les
dimensions indiquées.
Les coordonées sont données par rapport au coin supérieur gauche du plan.
"""
def project_sun(elevation, azimut, size_x, size_y):
    mid_x = size_x/2
    mid_y = size_y/2

    distance_from_center = math.cos(math.radians(elevation)) * mid_x

    y = mid_y - math.cos(math.radians(azimut)) * distance_from_center
    x = mid_x + math.sin(math.radians(azimut)) * distance_from_center

    return (int(x),int(y))

"""
Cette fonction diffuse une valeur sur un plan.
Elle est utilisée pour simuler l'éclairage du soleil sur le plan
"""
def diffusion(arr):
    coeff = 0.10

    right_roll = np.roll(arr,shift=1,axis=1) # right
    right_roll[:,0] = arr[:,0]

    left_roll = np.roll(arr,shift=-1,axis=1) # left
    left_roll[:,-1] = arr[:,-1]

    down_roll = np.roll(arr,shift=1,axis=0) # down
    down_roll[0,:] = arr[0,:]

    up_roll = np.roll(arr,shift=-1,axis=0) # up
    up_roll[-1,:] = arr[-1,:]

    # On stocke les valeurs avant de les appliquer pour éviter les effets
    # de trainées
    arr+=coeff*right_roll
    arr+=coeff*left_roll
    arr+=coeff*down_roll
    arr+=coeff*up_roll

    return arr


import numpy as np
import sunpos2 as sunpos
import math
import time
import os.path

from neopixel import *

from PIL import Image

from led import led

from optparse import OptionParser

import sys

reload(sys)
sys.setdefaultencoding('utf8')
        
# LED strip configuration:
LED_COUNT      = 480      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 60     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering


###
if __name__ == '__main__':

    np.set_printoptions(linewidth=200)

        ############################ Traitement ####################################

    steps = 0

    leds = []

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
    # Intialize the library (must be called once before other functions).
    strip.begin()

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
                        default=1.3,
                        help="[Avancé] Taux d'agrandissement de la matrice de visualisation du soleil")
    parser.add_option("-l", "--limite",
                        action="store",
                        dest="limite_coucher_de_soleil",
                        default=20,
                        help="[Avancé] Limite d'azimut permettant de débuter le coucher du soleil afin de permettre un dégradé")
    parser.add_option("-f", "--file",
                        action="store",
                        dest="mode_matrix_file",
                        help="Fichier de matrice correspondant au placement des leds")
    parser.add_option("-r", "--rectangle",
                        action="store_true",
                        dest="mode_rectangle",
                        help="Génère un rectangle comme matrice. Rend -x et -y obligatoire")
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
    azimut_maison = int(options.azimut_maison)
    print("azimut_maison : ", azimut_maison)

    lat_maison = float(options.lat_maison)
    print("lat_maison : ", lat_maison)

    long_maison = float(options.long_maison)
    print("long_maison : ", long_maison)

    diffusion_soleil = int(options.diffusion_soleil)
    print("diffusion_soleil : ",diffusion_soleil)

    matrix_upscaling = float(options.matrix_upscaling)
    print("matrix_upscaling : ", matrix_upscaling)

    ############################ Constantes ####################################
    # Lorsque l'orientation du soleil passe en dessous de cette limite,
    # c'est le debut de la nuit noire
    # Cette valeur sert à créer un dégradé pour la tombée de la nuit
    LIMITE_COUCHER_DE_SOLEIL = int(options.limite_coucher_de_soleil)
    print("LIMITE_COUCHER_DE_SOLEIL : ", LIMITE_COUCHER_DE_SOLEIL)

    VALEUR_DE_NORMALISATION_DE_LA_MATRICE = 255

    if options.mode_rectangle is not None:
        # Simulutation d'une piece rectangulaire
        print("Simulation d'une pièce rectangulaire")
        # Dimensions en nombres de leds
        longueur_maison = int(options.longueur_maison)
        print("longueur_maison : ", longueur_maison)

        largeur_maison  = int(options.largeur_maison)
        print("largeur_maison : ",largeur_maison)

        ### Generation des leds

        longueur_upscaling = int(longueur_maison*(matrix_upscaling-1)/2)
        largeur_upscaling = int(largeur_maison*(matrix_upscaling-1)/2)
        print("Longueur upscaling : ", longueur_upscaling, " Largeur upscaling : ", largeur_upscaling)

        for x in range(longueur_maison):
            led_x = x+1 + longueur_upscaling 
            led_y = 0 +largeur_upscaling 
            led_x2 = x+1 + longueur_upscaling 
            led_y2 = largeur_maison+2 + largeur_upscaling 
            leds.append(led(led_x, led_y, strip, x, (255,0,0)))
            leds.append(led(led_x2, led_y2, strip, 2*longueur_maison+largeur_maison-x-1 , (0,255,0)))

        for y in range(largeur_maison):
            led_x = longueur_maison+2 + longueur_upscaling 
            led_y = y+1 + largeur_upscaling 
            led_x2 = 0 + longueur_upscaling 
            led_y2 = y+1 + largeur_upscaling 
            leds.append(led(led_x, led_y, strip, y+longueur_maison, (255,255,0)))
            leds.append(led(led_x2, led_y2, strip, 2*largeur_maison+2*longueur_maison-y-1, (0,0,255)))

    elif options.mode_matrix_file is not None:
        print("Lecture d'une matrice par fichier")
        if os.path.isfile(options.mode_matrix_file):
            print("Lecture du fichier ", options.mode_matrix_file, "...")
            matrix_file = np.loadtxt(options.mode_matrix_file)
            print("Matrice de taille :", matrix_file.shape)
    
            # Dimensions en nombres de leds
            longueur_maison = matrix_file.shape[0] 
            print("longueur_maison : ", longueur_maison)

            largeur_maison  = matrix_file.shape[1]
            print("largeur_maison : ",largeur_maison)

            ### Generation des leds

            longueur_upscaling = int(longueur_maison*(matrix_upscaling-1)/2)
            largeur_upscaling = int(largeur_maison*(matrix_upscaling-1)/2)
            print("Longueur upscaling : ", longueur_upscaling, " Largeur upscaling : ", largeur_upscaling)

            for i_line, line in enumerate(matrix_file):
                for i_col, col in enumerate(line):
                    if int(col) != 0:
                        leds.append(led(i_line, i_col, strip, int(col), (0,0,0,0)))
        else:
            print("Fichier ", options.mode_matrix_file, "introuvable")
            exit()
    else:
        print("Attention ! [-r -x [VALUE] -y [VALUE]] ou [-f [FILE]] obligatoire !")
        exit()

    for l in leds:
        print('Addresse : ',l.strip_addr, " color : ", l.color, " x : ", l.x, " y : ", l.y)
        l.applyColorToStrip()

    strip.show()
    print "Displaying sides"

    time.sleep(2)

    

    #####
    size_y, size_x = (int(largeur_maison*matrix_upscaling),int(longueur_maison*matrix_upscaling))
    print "Dimensions matrix_grad : (", size_y,",",size_x,")"

    steps = 180
    while(True):
        # On calcul l'azimut et l'élévation du soleil en fonction de la date et
        # du lieu.
        azimut_soleil, elevation = sunpos.sun_position(2017,07,10,hour=(steps / 60)%24, minute=steps%60, lat=lat_maison, longitude=long_maison)
        # Initialisation de la matrice de portée du soleil
        matrix_grad = np.zeros((size_y,size_x))
        # Projection d" la position du solein sur un plan
        x, y = project_sun(elevation, azimut_soleil - azimut_maison, size_x,size_y)

        # Placement du soleil sur le plan
        matrix_grad[y,x] = 1

        print steps," : ",(steps/60)%24,"h ", steps%60,"m  elevation : ",int(elevation)

        # Diffusion de l'aura du soleil
        # Le facteur de 3.5 régule la force de la diffusion,
        # On l'a déterminé empiriquement
        for i in range(int(max(size_x,size_y)*diffusion_soleil)):
            matrix_grad = diffusion(matrix_grad)

        # Normalisation des valeurs
        matrix_grad = (matrix_grad/matrix_grad.max())

        # Si le soleil est couché, on met en place une descende graduelle de la luminosité
        if elevation < 0 :
            degrade = (LIMITE_COUCHER_DE_SOLEIL - min(-elevation, LIMITE_COUCHER_DE_SOLEIL)) / LIMITE_COUCHER_DE_SOLEIL
            matrix_grad = (matrix_grad * degrade).astype(int)

        #exit()

        #print "", (matrix_grad*255).astype(int)


        data = np.zeros((size_y,size_x,3), dtype=np.uint8)
        for l in leds:
            l.computeColor(elevation,matrix_grad)
            #l.applyColorToMatrix(data)
            l.applyColorToStrip()

        strip.show()
        # img = Image.fromarray(data,'RGB')
        # img.save('imgs/s%05d.png' % (steps))

        steps += 10
        #time.sleep(0.09)
