#!/usr/python
# -*- coding: utf-8-*-

from neopixel import *
import numpy as np



# LED strip configuration:
# LED_COUNT      = 16      # Number of LED pixels.
# LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
# #LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
# LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
# LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
# LED_BRIGHTNESS = 100     # Set to 0 for darkest and 255 for brightest
# LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
# LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
# LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering


def strip_init(LED_COUNT = 16, LED_PIN = 18, LED_FREQ_HZ = 800000, LED_DMA = 5,
        LED_BRIGHTNESS = 100, LED_INVERT = False, LED_CHANNEL = 0, LED_STRIP = ws.WS2811_STRIP_GRB):

    return Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)


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

    YELLOW = np.array((255,255,0))
    ORANGE = np.array((255,120,0))

    """docstring for ."""
    def __init__(self, x, y,strip, strip_addr, color = (255,255,255)):
        self.x = x
        self.y = y
        self.strip = strip
        self.strip_addr = strip_addr
        self.color = color

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
        self.strip.setPixelColor(self.strip_addr, Color(int(rgb_color[0]),int(rgb_color[1]),int(rgb_color[2])))
        return;
