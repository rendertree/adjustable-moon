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

class CameraControls:
    TURN_LEFT       = 0
    TURN_RIGHT      = 1
    TURN_UP         = 2
    TURN_DOWN       = 3

class CameraTP:
    def __init__(self, fovy, pos):
        self.controls_keys  = [KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN, KEY_LEFT_SHIFT]
        self.turn_speed     = Vector2(90, 90)
        self.minimum_view_y = -89.0
        self.maximum_view_y = 0.0
        self.focused        = is_window_focused()
        self.view_angles    = Vector2(0, 0)
        self.fov            = Vector2(0, 0)
        self.view_camera    = Camera3D()
        self.view_forward   = Vector3(0, 0, 0)
        self.near_plane     = 0.01
        self.far_plane      = 1000.0

        self.fov.y = fovy
        self.pos = pos

        self.view_camera.fovy = fovy
        self.view_camera.projection = CAMERA_PERSPECTIVE
        self.camera_pullback_distance = 5
        
        self.view_camera.target = pos
        self.view_camera.pos    = vector3_add(pos, Vector3(0, 0, self.camera_pullback_distance))
        self.view_camera.up     = Vector3(0.0, 1.0, 0.0)
        self.view_angles.x      = -180 * DEG2RAD
        self.view_angles.y      = -15 * DEG2RAD
        self.resize_tp_orbit_camera_view()

        self.mouse_sensitivity = 800.0

        self.is_free_mode = False

    def resize_tp_orbit_camera_view(self):
        width = get_screen_width()
        height = get_screen_height()
        self.fov.y = self.view_camera.fovy
        if height != 0:
            self.fov.x = self.fov.y * (width / height)

    def update(self, target_pos, is_free_mode, is_view_moon_mode, lock_mouse):
        self.is_free_mode = is_free_mode
        if self.is_free_mode:
            if is_mouse_button_down(MOUSE_BUTTON_RIGHT):
                    update_camera(self.view_camera, CAMERA_FREE)
        else:
            self.pos.y = 3.0

            if is_view_moon_mode:
                self.maximum_view_y = 89.0
                self.camera_pullback_distance = 3.0
            else:
                self.maximum_view_y = 0.0

            if is_window_resized():
                self.resize_tp_orbit_camera_view()
            if is_window_focused() != self.focused and not show_cursor:
                self.focused = is_window_focused()
                if self.focused:
                    disable_cursor()
                else:
                    enable_cursor()
            
            mouse_delta_pos = get_mouse_delta()
            use_mouse = is_mouse_button_down(MOUSE_BUTTON_LEFT) and not lock_mouse

            turn_rotation = self.get_speed_for_axis(CameraControls.TURN_RIGHT, self.turn_speed.x) - \
                        self.get_speed_for_axis(CameraControls.TURN_LEFT, self.turn_speed.x)

            tilt_rotation = self.get_speed_for_axis(CameraControls.TURN_UP, self.turn_speed.y) - \
                        self.get_speed_for_axis(CameraControls.TURN_DOWN, self.turn_speed.y)

            if turn_rotation != 0:
                self.view_angles.x -= turn_rotation * DEG2RAD
            elif use_mouse and self.focused:
                self.view_angles.x -= (mouse_delta_pos.x / self.mouse_sensitivity)

            if tilt_rotation:
                self.view_angles.y += tilt_rotation * DEG2RAD
            elif use_mouse and self.focused:
                self.view_angles.y += (mouse_delta_pos.y / -self.mouse_sensitivity)

            if self.view_angles.y < self.minimum_view_y * DEG2RAD:
                self.view_angles.y = self.minimum_view_y * DEG2RAD
            elif self.view_angles.y > self.maximum_view_y * DEG2RAD:
                self.view_angles.y = self.maximum_view_y * DEG2RAD
            
            if (self.camera_pullback_distance > 3 and get_mouse_wheel_move() < 0.0):
                self.camera_pullback_distance -= 0.1
            if (self.camera_pullback_distance < 6 and get_mouse_wheel_move() > 0.0):
                self.camera_pullback_distance += 0.1

            cam_pos = Vector3(0, 0, self.camera_pullback_distance)
            tilt_mat = matrix_rotate_x(self.view_angles.y)
            rot_mat = matrix_rotate_y(self.view_angles.x)
            mat = matrix_multiply(tilt_mat, rot_mat)
            cam_pos = vector3_transform(cam_pos, mat)
            self.view_camera.target = Vector3(target_pos.x, self.pos.y, target_pos.z)
            self.view_camera.pos = vector3_add(Vector3(target_pos.x, self.pos.y, target_pos.z), cam_pos)

    def get_speed_for_axis(self, axis, speed):
        key = self.controls_keys[axis]
        if key == -1:
            return 0
        factor = 1.0
        if is_key_down(key):
            return speed * get_frame_time() * factor
        return 0

    def setup_camera(self, aspect):
        rl_matrix_mode(RL_PROJECTION)
        rl_push_matrix()
        rl_load_identity()
        top = RL_CULL_DISTANCE_NEAR * tan(self.view_camera.fovy * 0.5 * DEG2RAD)
        right = top * aspect
        rl_frustum(-right, right, -top, top, self.near_plane, self.far_plane)
        rl_matrix_mode(RL_MODELVIEW)
        rl_load_identity()
        mat_view = matrix_look_at(self.view_camera.pos, self.view_camera.target, self.view_camera.up)
        rl_mult_matrixf(matrix_to_float_v(mat_view).v)
        rl_enable_depth_test()

    def begin_mode_3d(self):
        if self.is_free_mode:
            begin_mode3d(self.view_camera)
        else:
            aspect = get_screen_width() / get_screen_height()
            self.setup_camera(aspect)

    def end_mode_3d(self):
        end_mode3d()