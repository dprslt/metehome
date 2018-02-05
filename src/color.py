# -*- coding: utf-8-*-

import numpy as np

DARK_BLUE = np.array((0,0,120))
BLUE = np.array((0,150,255))

YELLOW = np.array((255,255,0))
ORANGE = np.array((255,120,0))

blue_delta = BLUE - DARK_BLUE
yellow_delta = YELLOW - ORANGE

def compute_gradient_descent(elevation):
    max = 10
    min = -10

    if elevation > max:
        return 0
    elif elevation < min:
        return 1
    else:
        return 1 - (elevation + max) / (max - min)

"""
Cete fonction calcule la couleur du soleil avec un dégradé en fonction de l'heure de la journée.
Le soleil est représenté par la couleur jaune à midi et orange en debut et fin de journée.
Le ciel passe de bleu clair à bleu nuit.

Le gradient calculé préccédement est utilisé pour calculer le dégradé de couleur.
"""
def computeColor(elevation, sun_gradient_matrix):

    # Calcule la valeur de bleue et de jaune en fonction de l'elevation
    gradient_descent = compute_gradient_descent(elevation)

    sky_color = (BLUE - blue_delta * gradient_descent).astype(int)
    sun_color = (YELLOW - yellow_delta * gradient_descent).astype(int)

    delta_sun_sky = sky_color - sun_color

    transformed_matrix = sun_gradient_matrix.reshape(sun_gradient_matrix.size)
    upscaled_colors = np.zeros((transformed_matrix.size,3), dtype=np.uint8)

    for i in range(0,transformed_matrix.size):
        upscaled_colors[i] = sky_color - delta_sun_sky * transformed_matrix[i]

    upscaled_colors = upscaled_colors.reshape((sun_gradient_matrix.shape[0], sun_gradient_matrix.shape[1], 3))

    return upscaled_colors.astype(int)


"""
Cette fonction diffuse une valeur sur un plan.
Elle est utilisée pour simuler l'éclairage du soleil sur le plan

arr : La matrice sur laqu'elle la diffusion doit être faite.
"""
def diffusion(arr):
    coeff = 0.10

    # Cette partie du code est un peu complexe, elle fait appel
    # a une fonction de numpy pour calculer la moyenne des pixels avoisinant
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
