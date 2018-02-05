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
