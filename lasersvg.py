#!/usr/bin/env python3

from guizero import App, Box, Combo, PushButton, Text, TextBox

try:
    import untangle
except ModuleNotFoundError:
    print("No module named 'untangle'\n Run: sudo pip3 install untangle.")
    quit()

class LoadSvg:
    PWR_OFF = 0
    PWR_MAX = 100

    def __init__(self, input_file):     
        try:
            obj = untangle.parse(input_file)
            self.validfile = True
        except Exception as inst:
            self._wprint("Not a valid/recognized svg file.")
            self.validfile = False
            return

        #Get some svg parameters 
        w = obj.svg["width"]
        self._wprint("obj.svg.width   {}".format(w))
        h = obj.svg["height"]
        self._wprint("obj.svg.height  {}".format(h))
        vb = obj.svg["viewBox"]
        self._wprint("obj.svg.viewBox {}".format(vb))
        self._wprint("")

        # self.dimensions = Return this to the caller: tuple (width, height)
        self.dimensions = self._build_dimensions(w, h, vb)
        self._wprint("dimensions: ({}, {})".format(self.dimensions[0], self.dimensions[1]))

        # self.steps = Return this to the caller
        # List of (pwr(int), x(float,int), yfloat(float,int), fast(bool))
#       self.steps=[(0,0,0,True)]
        self.steps=[]
        indent = 0
        self._get_items(obj.svg, indent)
        self._wprint("-" * 60)

    def _wprint(self, text):
        print(text)

    def _build_dimensions(self, width, height, viewbox):
        def clean(value):   # Value might have "px" suffix. This will clean it off.
            if len(value) >= 3 and value[-2:] == "px":
                return value[0:-2]
            return value

        # Get values from Viewbox first
        try:
            vb = viewbox.split()
        except AttributeError:
            vb = ""
        if len(vb) == 4:   #  good, we;ll, use... not sure if we'll see funky units.
            # viewbox = <min-x> <min-y> <width> <height>
            try:
                for i, num in enumerate(vb):
                    vb[i] = int(float(num) + 0.9)       # forces a roundup
            except ValueError:
                self._wprint("Error: viewBox values not integer/float numbers.")
                quit()
            if vb[0] != 0 or vb[1] != 0:
                self._wprint("Warning: viewBox origin not (0,0).")
            return (vb[2], vb[3])
            
        # Need to use the width, height values.
        width  = clean(width)
        height = clean(height)
        try:
            width  = int(float(width) + 0.9)
            height = int(float(height) + 0.9)
        except ValueError:
            self._wprint("Error: global width/height values not integer/float numbers.")
            quit()
        return (width, height)

    def _get_lines(self, elem):
        for i, line in enumerate(elem): 
            self._wprint("{} line: {} {} {} {}".format(i, line["x1"], line["x2"], line["y1"], line["y2"]))
            self.steps.append( (self.PWR_OFF, float(line["x1"]), float(line["x2"]), True) )
            self.steps.append( (self.PWR_MAX, float(line["y1"]), float(line["y2"]), False) )
        self._wprint("")

    def _get_rects(self, elem):
        for i, rect in enumerate(elem): 
            self._wprint("{} rect: {} {} {} {}".format(i, rect["x"], rect["y"], rect["width"],
                rect["height"]))
            r_x = float(rect["x"])
            r_y = float(rect["y"])
            r_wid = float(rect["width"])
            r_hgt = float(rect["height"])
            self.steps.append( (self.PWR_OFF, r_x, r_y, True) )
            self.steps.append( (self.PWR_MAX, r_x+r_wid, r_y, False) )
            self.steps.append( (self.PWR_MAX, r_x+r_wid, r_y+r_hgt, False) )
            self.steps.append( (self.PWR_MAX, r_x, r_y+r_hgt, False) )
            self.steps.append( (self.PWR_MAX, r_x, r_y, False) )
        self._wprint("")

    def _get_texts(self, elem):
        for i, text in enumerate(elem): 
            self._wprint("{} text: {}".format(i, text.cdata))
        self._wprint("")

    def _get_circles(self, elem):
        for i, circle in enumerate(elem): 
            self._wprint("{} circle: {} {} {}".format(i, circle["cx"], circle["cy"], circle["r"]))
        self._wprint("")

    def _get_ellipses(self, elem):
        for i, ellipse in enumerate(elem): 
            self._wprint("{} ellipse: {} {} {} {}".format(i, ellipse["cx"], ellipse["cy"],
                ellipse["rx"], ellipse["ry"]))
        self._wprint("")

    def _get_paths(self, elem):
        for i, path in enumerate(elem): 
            self._wprint("{} path: {} {} {} {}".format(i, path["cx"], path["cy"], path["rx"], path["ry"]))
        self._wprint("")

    def _get_desc(self, elem, name):
    #   print(obj.svg.<name>[i].referenceFile.cdata)
    #   print(obj.svg.<name>[i].cdata)
        for i, desc in enumerate(elem): 
            if hasattr(desc, "referenceFile"):
                self._wprint("{} {}: {}".format(i, name, desc.referenceFile.cdata))
            else:
                self._wprint("{} {}: {}".format(i, name, desc.cdata))
        print()

    def _get_items(self, struct, indent):
#       for s in struct:
#           if "transform" in s:
#               self._wprint(" " * indent, "g struct: transform")

        seg_types = list(set(dir((struct))))
        self._wprint("{} set dir: {}".format(">" * indent, seg_types))
        if isinstance(struct["transform"], str):
            self._wprint("{} g struct: {}".format(" " * indent, struct["transform"]))

        if hasattr(struct, "desc"):
            self._get_desc(struct.desc, "desc")
        if hasattr(struct, "title"):
            self._get_desc(struct.title, "title")
        if hasattr(struct, "line"):
            self._get_lines(getattr(struct, "line"))
        if hasattr(struct, "rect"):
            self._get_rects(getattr(struct, "rect"))
        if hasattr(struct, "text"):
            self._get_texts(getattr(struct, "text"))
        if hasattr(struct, "circle"):
            self._get_circles(getattr(struct, "circle"))
        if hasattr(struct, "ellipse"):
            self._get_ellipses(getattr(struct, "ellipse"))
        if hasattr(struct, "path"):
            self._get_paths(getattr(struct, "path"))
        if hasattr(struct, "g"):
#           g_struct = getattr(struct, "g")
            indent += 1
            for new_struct in getattr(struct, "g"):
#               if isinstance(new_struct["transform"], str):
#                   self._wprint("{} g struct: {}".format(" " * indent, new_struct["transform"]))
                self._get_items(new_struct, indent)

#-----------------------------------------------------------------------
if __name__ == "__main__":
    import os.path

    while True:
        try:
            input_file = input("Enter filename: ")
        except KeyboardInterrupt:
            print()
            break
        if os.path.exists(input_file):
            print()
            A = LoadSvg(input_file)


