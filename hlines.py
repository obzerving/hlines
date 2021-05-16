#!/usr/bin/env python
# coding=utf-8
#
# Copyright (C) [2021] [Joseph Zakar], [observing@gmail.com]
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
"""
For each selected path element, this extension creates an additional path element
consisting of horizontal line segments which are the same size as the original
line segments.
"""

import inkex
from lxml import etree
import math

class HLines(inkex.EffectExtension):
    def add_arguments(self, pars):
        pars.add_argument("--my_option", type=inkex.Boolean,\
            help="An example option, put your options here")

    #draw an SVG line segment between the given (raw) points
    def drawline(self, dstr, name, parent):
        line_style   = {'stroke':'#000000','stroke-width':'1','fill':'none'}
        line_attribs = {'style' : str(inkex.Style(line_style)),
                    inkex.addNS('label','inkscape') : name,
                    'd' : dstr}
        line = etree.SubElement(parent, inkex.addNS('path','svg'), line_attribs )
        
    def effect(self):
        path_num = 0
        #for elem in self.svg.get_selected(): # for each selected element (Ver. 1.0)
        for elem in self.svg.selection.filter(inkex.PathElement).values(): # for each selected element (Ver. 1.02+)
            #inkex.utils.debug(type(elem))
            #inkex.utils.debug(elem.bounding_box())
            #inkex.utils.debug(elem.path)
            if elem.typename == 'PathElement': # Only process path elements
                xbound,ybound = elem.bounding_box() # Get bounds of this element
                xmin,xmax = xbound
                ymin,ymax = ybound
                ntotal = len(elem.path)
                nodecnt = 0
                startx = 0
                starty = ymax + 10
                endx = 0
                endy = starty
                xoffset = 0
                orig_sx = 0
                orig_sy = 0
                orig_ex = 0
                orig_ey = 0
                sx1 = 0
                sy1 = 0
                orig_length = 0
                last_letter = 'M'
                for ptoken in elem.path: # For each point in the path
                    #inkex.utils.debug(type(ptoken))
                    #inkex.utils.debug(ptoken)
                    startx = xmin + xoffset
                    if ptoken.letter == 'M': # Starting a new line
                        orig_sx = ptoken.x
                        orig_sy = ptoken.y
                        cd = 'M '+ str(startx) + ',' + str(starty)
                        sx1 = orig_sx
                        sy1 = orig_sy
                    else:
                        if last_letter != 'M':
                            orig_sx = orig_ex
                            orig_sy = orig_ey
                        
                        if ptoken.letter == 'L':
                            orig_ex = ptoken.x
                            orig_ey = ptoken.y
                            orig_length = math.sqrt((orig_sx-orig_ex)**2 + (orig_sy-orig_ey)**2)
                            endx = startx + orig_length
                            cd = cd + ' L ' + str(endx) + ',' + str(endy)
                        elif ptoken.letter == 'H':
                            if last_letter == 'M':
                                orig_ey = orig_sy
                            orig_length = abs(orig_sx - ptoken.x)
                            orig_ex = ptoken.x
                            endx = startx + orig_length
                            cd = cd + ' L ' + str(endx) + ',' + str(endy)
                        elif ptoken.letter == 'V':
                            if last_letter == 'M':
                                orig_ex = orig_sx
                            orig_length = abs(orig_sy - ptoken.y)
                            orig_ey = ptoken.y
                            endx = startx + orig_length
                            cd = cd + ' L ' + str(endx) + ',' + str(endy)
                        elif ptoken.letter == 'Z':
                            orig_ex = sx1
                            orig_ey = sy1
                            orig_length = math.sqrt((orig_sx-orig_ex)**2 + (orig_sy-orig_ey)**2)
                            endx = startx + orig_length
                            cd = cd + ' L ' + str(endx) + ',' + str(endy)
                        else:
                            inkex.utils.debug("Unknown letter - {0}".format(ptoken.letter))
                    nodecnt = nodecnt + 1
                    if ptoken.letter != 'M':
                        if nodecnt == ntotal:
                            self.drawline(cd,"hline{0}".format(path_num),self.svg.get_current_layer())
                            path_num = path_num + 1
                        xoffset = xoffset + orig_length
                    last_letter = ptoken.letter

if __name__ == '__main__':
    HLines().run()
