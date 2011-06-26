# -*- coding: utf-8 -*-
#!/usr/bin/env python
'''
SVG.py - Construct/display SVG scenes.

The following code is a lightweight wrapper around SVG files. The metaphor
is to construct a scene, add objects to it, and then write it to a file
to display it. [Based on: http://code.activestate.com/recipes/325823/]
'''

import codecs
import StringIO

__author__ = "Mac Ryan"
__copyright__ = "Copyright 2011, Mac Ryan"
__license__ = "GPL v3"
__maintainer__ = "Mac Ryan"
__email__ = "quasipedia@gmail.com"
__status__ = "Development"


class Scene:
    def __init__(self, name="svg", height=400, width=400):
        self.name = name
        self.items = []
        self.height = height
        self.width = width
        return

    def add(self, item): 
        self.items.append(item)

    def remove(self, item):
        try:
            self.items.remove(item)
        except (AttributeError, ValueError):
            pass

    def strarray(self):
        var = ['<?xml version="1.0" encoding="utf-8"?>',
               '<svg height="%d" width="%d">' % (self.height, self.width),
               '  <g style="fill-opacity:1.0; stroke:black; stroke-width:1;">']
        for item in self.items: 
            var.append(item.strarray())            
        var += ["</g>", "</svg>"]
        var = [v + '\n' for v in var]
        return var
    
    def get_xml(self):
        buffer = StringIO.StringIO()
        buffer.writelines(self.strarray())
        return buffer

    def write_svg_file(self, filename=None):
        if filename:
            self.svgname = filename
        else:
            self.svgname = self.name + ".svg"
        file = codecs.open(self.svgname, "w", "utf-8")
        file.writelines(self.strarray())
        file.close()
        return


class Line:
    def __init__(self, start, end):
        self.start = start #xy tuple
        self.end = end     #xy tuple
        return

    def strarray(self):
        return '  <line x1="%d" y1="%d" x2="%d" y2="%d" />' %\
               (self.start[0], self.start[1], self.end[0], self.end[1])


class Circle:
    def __init__(self, center, radius, color):
        self.center = center #xy tuple
        self.radius = radius #xy tuple
        self.color = color   #rgb tuple in range(0,256)
        return

    def strarray(self):
        return ['  <circle cx="%d" cy="%d" r="%d" style="fill:%s;"/>' %\
                (self.center[0], self.center[1], self.radius, 
                 colorstr(self.color))]

class Rectangle:
    def __init__(self, origin, height, width, color):
        self.origin = origin
        self.height = height
        self.width = width
        self.color = color
        return

    def strarray(self):
        return [('  <rect x="%d" y="%d" height="%d" ' +\
                'width="%d" style="fill:%s;"/>') %\
                (self.origin[0], self.origin[1], self.height, self.width, colorstr(self.color))]

class Text:
    def __init__(self, origin, text, size=24, font='monospace'):
        self.origin = origin
        self.text = text
        self.size = size
        self.font = font
        return

    def strarray(self):
        return ['  <text x="%d" y="%d" font-size="%d" font-family="%s">' %\
                (self.origin[0], self.origin[1], self.size, self.font),
                "%s" % self.text,  "</text>"]

def colorstr(rgb): 
    return "#%x%x%x" % (rgb[0]/16, rgb[1]/16, rgb[2]/16)

def test():
    scene = Scene('test')
    scene.add(Rectangle((100,100),200,200,(0,255,255)))
    scene.add(Line((200,200),(200,300)))
    scene.add(Line((200,200),(300,200)))
    scene.add(Line((200,200),(100,200)))
    scene.add(Line((200,200),(200,100)))
    scene.add(Circle((200,200),30,(0,0,255)))
    scene.add(Circle((200,300),30,(0,255,0)))
    scene.add(Circle((300,200),30,(255,0,0)))
    scene.add(Circle((100,200),30,(255,255,0)))
    scene.add(Circle((200,100),30,(255,0,255)))
    scene.add(Text((50,50),"Testing SVG"))
    scene.write_svg_file()
    scene.display()
    return

if __name__ == '__main__': 
    test()