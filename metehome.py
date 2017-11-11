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

from PIL import Image

from led import led


###
if __name__ == '__main__':

    np.set_printoptions(linewidth=200)

    # Ci-dessous les paramètres nécessaires au fonctionement du programme.
    ############################################################################
    # Azimut de la piece, et position GPS de la maison => à déterminer sur place
    azimut_maison = 0
    lat_maison = 41
    long_maison = 0

    # Dimensions en nombres de leds
    longueur_maison = 75
    largeur_maison  = 75

    diffusion_soleil = 6

    gradient_upscaling = 1.04

    ############################ Constantes ####################################
    # Lorsque l'orientation du soleil passe en dessous de cette limite,
    # c'est le debut de la nuit noire
    # Cette valeur sert à créer un dégradé pour la tombée de la nuit
    LIMITE_COUCHER_DE_SOLEIL = 20
    VALEUR_DE_NORMALISATION_DE_LA_MATRICE = 255

    ############################ Traitement ####################################

    steps = 0

    leds = []
    # Simulutation d'une piece carrée


    ### Generation des leds
    for x in range(largeur_maison):
        led_x = x + int(largeur_maison*(gradient_upscaling-1)/2)

        led_y_1 = int(longueur_maison*(gradient_upscaling-1)/2)
        led_y_2 = longueur_maison + int(longueur_maison*(gradient_upscaling-1)/2)
        led_y_3 = int(longueur_maison*(gradient_upscaling)/2)

        leds.append(led(led_x,led_y_1,"","TODO"))
        leds.append(led(led_x,led_y_2,"","TODO"))
        leds.append(led(led_x,led_y_3,"","TODO"))


    for y in range(longueur_maison):
        led_y = y + int(longueur_maison*(gradient_upscaling-1)/2)

        led_x_1 = int(largeur_maison*(gradient_upscaling-1)/2)
        led_x_2 = largeur_maison + int(largeur_maison*(gradient_upscaling-1)/2)
        led_x_3 = int(largeur_maison*(gradient_upscaling)/2)

        leds.append(led(led_x_1,led_y,"","TODO"))
        leds.append(led(led_x_2,led_y,"","TODO"))
        leds.append(led(led_x_3,led_y,"","TODO"))

    #####
    size_y, size_x = (int(largeur_maison*gradient_upscaling),int(longueur_maison*gradient_upscaling))
    print "Dimensions matrix_grad : (", size_y,",",size_x,")"

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
            l.applyColorToMatrix(data)
        img = Image.fromarray(data,'RGB')

        img.save('imgs/s%05d.png' % (steps))

        steps += 5
        #time.sleep(0.09)
