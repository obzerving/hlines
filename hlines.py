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
import math
import copy

from inkex import PathElement, Style
from inkex.paths import Move, Line, ZoneClose, Path

class HLines(inkex.EffectExtension):

    #draw SVG line segment(s) between the given (raw) points
    def drawline(self, dstr, name, parent, sstr=None):
        line_style   = {'stroke':'#000000','stroke-width':'1','fill':'none'}
        if sstr == None:
            stylestr = str(Style(line_style))
        else:
            stylestr = sstr
        el = parent.add(PathElement())
        el.path = dstr
        el.style = stylestr
        el.label = name
        
    def effect(self):
        path_num = 0
        elems = []
        npaths = []
        sstr = None
        for selem in self.svg.selection.filter(PathElement):
            elems.append(copy.deepcopy(selem))
        if len(elems) == 0:
            raise inkex.AbortExtension("Nothing selected")
        for elem in elems:
            escale = 1.0
            npaths.clear()
            #inkex.utils.debug(elem.attrib)
            if 'style' in elem.attrib:
                sstr = elem.attrib['style']
            if 'transform' in elem.attrib:
                transforms = elem.attrib['transform'].split()
                for tf in transforms:
                    if tf.startswith('scale'):
                        escale = float(tf.split('(')[1].split(')')[0])
                if sstr != None:
                    lsstr = sstr.split(';')
                    for stoken in range(len(lsstr)):
                        if lsstr[stoken].startswith('stroke-width'):
                            swt = lsstr[stoken].split(':')[1]
                            swf = str(float(swt)*escale)
                            lsstr[stoken] = lsstr[stoken].replace(swt, swf)
                        if lsstr[stoken].startswith('stroke-miterlimit'):
                            swt = lsstr[stoken].split(':')[1]
                            swf = str(float(swt)*escale)
                            lsstr[stoken] = lsstr[stoken].replace(swt, swf)
                    sstr = ";".join(lsstr)
                else:
                    sstr = None
                elem.apply_transform()
            xbound,ybound = elem.bounding_box() # Get bounds of this element
            xmin,xmax = xbound
            ymin,ymax = ybound
            ntotal = len(elem.path)
            nodecnt = 0
            startx = 0
            starty = ymax + 10*escale
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
            for ptoken in elem.path: # For each point in the path
                startx = xmin + xoffset
                if ptoken.letter == 'M': # Starting a new line
                    orig_sx = ptoken.x
                    orig_sy = ptoken.y
                    cd = Path()
                    cd.append(Move(startx,starty))
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
                        cd.append(Line(endx,endy))
                    elif ptoken.letter == 'H':
                        orig_ey = ptoken.Horz.to_line().y
                        orig_length = abs(orig_sx - ptoken.x)
                        orig_ex = ptoken.x
                        endx = startx + orig_length
                        cd.append(Line(endx,endy))
                    elif ptoken.letter == 'V':
                        orig_ex = ptoken.Vert.to_line().x
                        orig_length = abs(orig_sy - ptoken.y)
                        orig_ey = ptoken.y
                        endx = startx + orig_length
                        cd.append(Line(endx,endy))
                    elif ptoken.letter == 'Z':
                        orig_ex = sx1
                        orig_ey = sy1
                        orig_length = math.sqrt((orig_sx-orig_ex)**2 + (orig_sy-orig_ey)**2)
                        endx = startx + orig_length
                        cd.append(Line(endx,endy))
                    else:
                        raise inkex.AbortExtension("Unknown letter - {0}".format(ptoken.letter))
                nodecnt = nodecnt + 1
                if ptoken.letter != 'M':
                    if nodecnt == ntotal:
                        self.drawline(str(cd),"hline{0}".format(path_num),self.svg.get_current_layer(),sstr)
                        path_num = path_num + 1
                    xoffset = xoffset + orig_length
                last_letter = ptoken.letter

if __name__ == '__main__':
    HLines().run()
