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
from math import *
from copy import *

class Car: pass

class Player(object):
    def __init__(self):
        self.pos                = Vector3(-151, 1.5, 58)
        self.rot                = 0.0
        self.speed              = 0.0
        self.model_scale        = 0.0
        self.entering           = False
        self.player_model       = load_model("resources/male_shirt.glb")
        self.model              = self.player_model
        self.anims_count        = 0
        self.anim_index         = 0
        self.anim_current_frame = 0
        self.bounding_box       = BoundingBox()
        self.model_anims        = load_model_animations("resources/male_shirt.glb", self.anims_count)
        self.current_transform  = Matrix()
        self.rot_radians        = 0.0

    def __del__(self):
        unload_model(self.model)
        anim: ModelAnimationPtr = self.model_anims[self.anim_index]
        unload_model_animations(self.model_anims, anim.frame_count)

    def update(self, in_car, car: Car):
        car_model = car.model
        # Constants for movement and rotation
        ROTATION_STEP = 1.0  # Degrees
        SPEED_MULTIPLIER = 0.1
        
        # Update speed based on key press
        self.speed = 0.4 if is_key_down(KEY_SPACE) else 0.2

        # Handle rotation inputs and update rotation and transformation matrix
        if is_key_down(KEY_A):
            self.rot += ROTATION_STEP
        elif is_key_down(KEY_D):
            self.rot -= ROTATION_STEP
        
        # Always update radians and forward vector based on the current rotation
        self.rot_radians = self.rot * DEG2RAD
        forward = Vector3(sin(self.rot_radians), 0.0, cos(self.rot_radians))
        
        # Update pos based on forward vector
        if is_key_down(KEY_W):
            self.pos.x += forward.x * SPEED_MULTIPLIER * self.speed
            self.pos.z += forward.z * SPEED_MULTIPLIER * self.speed

        # Apply rotation to the model's transformation matrix
        if is_key_down(KEY_A) or is_key_down(KEY_D):
            rotation_direction = ROTATION_STEP if is_key_down(KEY_A) else -ROTATION_STEP
            self.model.transform = matrix_multiply(self.model.transform, matrix_rotate_y(rotation_direction * DEG2RAD))

        # Check and handle model switching for entering or exiting the car
        if in_car and not self.entering:
            self.model = car_model
            self.model.transform = self.current_transform
            self.rot_radians = car.rot_radians
            self.rot = self.rot_radians * RAD2DEG
            self.model.transform = matrix_rotate_y(self.rot_radians)  # Apply rotation reset to transformation
            self.pos = car.pos
            self.entering = True
        elif not in_car and self.entering:
            self.model = self.player_model
            self.model.transform = self.current_transform
            self.entering = False

        # Update bounding box
        box_size = 1.0
        self.bounding_box.min = Vector3(self.pos.x - box_size / 2, self.pos.y - box_size / 2, self.pos.z - box_size / 2)
        self.bounding_box.max = Vector3(self.pos.x + box_size / 2, self.pos.y + box_size / 2, self.pos.z + box_size / 2)

        # Update animation index based on actions
        if is_key_down(KEY_W) and is_key_down(KEY_SPACE):
            self.anim_index = 6
        elif is_key_down(KEY_W):
            self.anim_index = 11
        else:
            self.anim_index = 2

        # Scale model differently based on being in car
        self.model_scale = 0.45 if in_car else 0.2

        # Store current transformation for potential model changes
        self.current_transform = deepcopy(self.model.transform)

        if in_car: return

        # Update model animations
        anim: ModelAnimationPtr = self.model_anims[self.anim_index]
        self.anim_current_frame = (self.anim_current_frame + 1) % anim.frame_count
        update_model_animation(self.model, anim, self.anim_current_frame)

    def draw(self):
        draw_bounding_box(self.bounding_box, GREEN)
        draw_model(self.model, self.pos, self.model_scale, WHITE)