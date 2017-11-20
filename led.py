#!/usr/python
# -*- coding: utf-8-*-

from neopixel import *
import numpy as np

def compute_gradient_descent(elevation):
    max = 10
    min = -10

    if elevation > max:
        return 0
    elif elevation < min:
        return 1
    else:
        return 1 - (elevation + max) / (max - min)

class led(object):

    DARK_BLUE = np.array((0,0,120))
    BLUE = np.array((0,150,255))

    YELLOW = np.array((255,255,160))
    ORANGE = np.array((255,120,0))

    """docstring for ."""
    def __init__(self, x, y,strip, strip_addr):
        self.x = x
        self.y = y
        self.strip = strip
        self.strip_addr = strip_addr
        self.color = Color(255,255,255)

        self.blue_delta = self.BLUE - self.DARK_BLUE
        self.yellow_delta = self.YELLOW - self.ORANGE


    def computeColor(self, elevation, sun_gradient_matrix):

        #print "\nid : ", self.strip_addr," x : ", self.x, " y : ",self.y
        # Calcule la valeur de bleue et de jaune en fonction de l'elevation
        gradient_descent = compute_gradient_descent(elevation)

        sky_color = (self.BLUE - self.blue_delta * gradient_descent).astype(int)
        sun_color = (self.YELLOW - self.yellow_delta * gradient_descent).astype(int)
        #print "gradient_coeff : ",gradient_descent, " Elevation : ",elevation, " - sky : ", sky_color, " - sun : ", sun_color
        # Calcule du dégradé entre le jaune et le bleu précédent

        delta_sun_sky = sky_color - sun_color
        led_color = sky_color - delta_sun_sky * sun_gradient_matrix[self.y][self.x]
        #print "Delta : ",delta_sun_sky," - sun : ", sun_gradient_matrix[self.y][self.y]," - color : ",led_color

        self.color = led_color
        return;

    def applyColorToMatrix(self, matrix):
        matrix[self.y][self.x] = self.color

    def applyColorToStrip(self):
        rgb_color=self.color
        self.strip.setPixelColor(self.strip.numPixels(self.strip_addr), Color(int(rgb_color[0]),int(rgb_color[1]),int(rgb_color[2])))
        return;
