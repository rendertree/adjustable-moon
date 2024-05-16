#   Copyright (c) 2024 Wildan R Wijanarko
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in all
#   copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.

from raylibpy import *
from copy import *

class Car(object):
    def __init__(self):
        self.pos    = Vector3(-134, 1.5, 60)
        self.model  = load_model("resources/bmw_m3_e92.glb")
        self.status = True
        self.bounding_box = BoundingBox()
        self.rot_radians  = 0.0
    
    def __del__(self):
        unload_model(self.model)

    def update(self, rot_radians, pos=Vector3(0, 0, 0), status=True):
        self.status = status
        if status:
            self.pos = deepcopy(pos)
            self.rot_radians = deepcopy(rot_radians)

        # Update bounding box based on the current pos
        box_size = 1.0
        self.bounding_box.min = Vector3(self.pos.x - box_size / 2, self.pos.y - box_size / 2, self.pos.z - box_size / 2)
        self.bounding_box.max = Vector3(self.pos.x + box_size / 2, self.pos.y + box_size / 2, self.pos.z + box_size / 2)
    
    def draw(self): 
        draw_bounding_box(self.bounding_box, GREEN)
        if not self.status: draw_model(self.model, self.pos, 0.45, WHITE)