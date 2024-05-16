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
from player import *
from camera import *
from car import *

class Moon(object):
    def __init__(self):
        self.pos            = Vector3(-150, 0, 0)
        self.moon_size      = 4.0
        self.orbit_radius   = 180
        self.time           = 0.0
        self.max_time       = 1000

    def update(self, speed, size, is_reverse):
        frame_time = get_frame_time()
        
        if is_reverse:
            self.time -= frame_time
        else:
            self.time += frame_time
        
        self.time %= self.max_time

        # Calculate the new position based on time
        dy = self.orbit_radius * cos(speed * self.time)  # Move up and down
        dz = self.orbit_radius * sin(speed * self.time) + 160.0  # Orbit around z-axis

        self.moon_size = size
        self.pos = Vector3(self.pos.x, dy, dz)
    
    def draw(self):
        draw_sphere(self.pos, self.moon_size, WHITE)

class ProSlider():
    def __init__(self, bounds, value_ref, min_value, max_value, slider_width):
        self.bounds         = bounds
        self.value_ref      = value_ref
        self.min_value      = min_value
        self.max_value      = max_value
        self.slider_width   = slider_width

    def draw(self):
        # Get the current mouse position and mouse button states
        mouse_pos = get_mouse_position()
        mouse_pressed = is_mouse_button_down(MOUSE_BUTTON_LEFT)

        # Calculate handle position based on the current value
        handle_pos = ((self.value_ref[0] - self.min_value) / (self.max_value - self.min_value)) * (self.bounds.width - self.slider_width)
        handle_rec = Rectangle(self.bounds.x + handle_pos, self.bounds.y, self.slider_width, self.bounds.height)

        # Check if the mouse is over the slider handle
        is_over_handle = check_collision_point_rec(mouse_pos, handle_rec)
        
        # Manage the state based on mouse interaction
        if mouse_pressed and is_over_handle:
            self.value_ref[0] = self.min_value + ((mouse_pos.x - self.bounds.x - self.slider_width / 2) / (self.bounds.width - self.slider_width)) * (self.max_value - self.min_value)
            self.value_ref[0] = clamp(self.value_ref[0], self.min_value, self.max_value)

        # Drawing the slider background and handle
        draw_rectangle_rec(self.bounds, LIGHTGRAY)  # Slider background
        draw_rectangle_rec(handle_rec, BLACK if is_over_handle and mouse_pressed else DARKGRAY)  # Slider handle

        return self.value_ref[0]

class Engine():
    def __init__(self):
        self.in_car = False
        self.is_camera_free_mode = False

        self.moon_speed = 0.2
        self.moon_speed_slider = ProSlider(Rectangle(20, 180, 100, 10), [0.2], 0.1, 2.0, 10)

        self.moon_size = 4.0
        self.moon_size_slider = ProSlider(Rectangle(20, 230, 100, 10), [4.0], 2.0, 20.0, 10)
        
        self.is_view_moon_mode = False
        self.is_show_settings = False

        self.is_reverse_moon = False

    def run(self):
        screen_width = 640
        screen_height = 480

        set_config_flags(FLAG_MSAA_4X_HINT)
        init_window(screen_width, screen_height, "")
        set_target_fps(60)

        map_model = load_model("resources/gta_2_maps.glb")
        player = Player()
        car = Car()

        map_model.transform = matrix_multiply(map_model.transform, matrix_rotate_zyx(quaternion_to_euler(quaternion_normalize(Quaternion(0.0, 7.20, 7.20, 0.0)))))

        camera = CameraTP(45, Vector3(1, 0, 1))

        moon = Moon()

        def draw_checkbox(text, rec, flag) -> bool:
            mouse_pos = get_mouse_position()
            is_mouse_over = check_collision_point_rec(mouse_pos, rec)

            if is_mouse_over:
                draw_rectangle_rec(rec, LIGHTGRAY)

            if flag:
                draw_rectangle_rec(rec, GRAY)

            draw_rectangle_lines_ex(rec, 1.2, BLACK)
            draw_text(text, rec.x + 35, rec.y + 20, 12, BLACK)

            if is_mouse_over and is_mouse_button_pressed(MOUSE_LEFT_BUTTON):
                flag = not flag

            return flag

        def draw_button(text, button_rec, is_clickable=True) -> bool:
            mouse_pos = get_mouse_position()
            is_mouse_over = check_collision_point_rec(mouse_pos, button_rec)

            text_x = button_rec.x + (button_rec.width - measure_text(text, 11)) / 2
            text_y = button_rec.y + (button_rec.height - 11) / 2

            rec_color = DARKBROWN if is_mouse_over else LIGHTGRAY
            
            text_color = BLACK
            if is_clickable:
                text_color = BLACK if is_mouse_over else DARKGRAY
            else:
                text_color = GRAY

            draw_rectangle_rec(button_rec, rec_color)
            draw_text(text, text_x, text_y, 11, text_color)

            return is_clickable and is_mouse_over and is_mouse_button_pressed(MOUSE_LEFT_BUTTON)

        def update():
            lock_mouse = True if self.is_show_settings else False
            camera.update(player.pos, self.is_camera_free_mode, self.is_view_moon_mode, lock_mouse)
            moon.update(self.moon_speed, self.moon_size, self.is_reverse_moon)

            if check_collision_boxes(player.bounding_box, car.bounding_box) and is_key_pressed(KEY_ENTER):
                self.in_car = not self.in_car
                if self.in_car:
                    print("Entering")
                else:
                    print("Exiting")

            if not self.is_camera_free_mode:
                player.update(self.in_car, car)

            car.update(player.rot_radians, player.pos, self.in_car)

        def render():
            begin_drawing()
            camera.begin_mode_3d()

            clear_background(BLACK)
            moon.draw()
            player.draw()
            car.draw()

            draw_model(map_model, Vector3(0, 0, 0), 1.0, WHITE)
            draw_grid(24, 24)

            camera.end_mode_3d()
            
            camera_target_str = str(round(camera.view_camera.pos.x)) + " " + str(round(camera.view_camera.pos.y)) + " " + str(round(camera.view_camera.pos.z))
            draw_text(camera_target_str, 10, screen_height - 50, 12, WHITE)

            if not self.is_show_settings:
                if draw_button("Settings", Rectangle(10, 20, 100, 32)):
                    self.is_show_settings = not self.is_show_settings

            if self.is_show_settings:
                draw_rectangle_rec(Rectangle(10, 20, 180, 250), RAYWHITE)

                draw_text("Moon Speed:", 20, 160, 14, BLACK)
                self.moon_speed = self.moon_speed_slider.draw()

                draw_text("Moon Size:", 20, 210, 14, BLACK)
                self.moon_size = self.moon_size_slider.draw()

                self.is_camera_free_mode = draw_checkbox("Camera Free Mode", Rectangle(20, 35, 28, 28), self.is_camera_free_mode)
                self.is_view_moon_mode = draw_checkbox("View Moon Mode", Rectangle(20, 70, 28, 28), self.is_view_moon_mode)
                self.is_reverse_moon = draw_checkbox("Reverse Moon", Rectangle(20, 105, 28, 28), self.is_reverse_moon)

                if draw_button("Hide", Rectangle(140, 280, 50, 30)):
                    self.is_show_settings = not self.is_show_settings

            end_drawing()

        while not window_should_close():
            update()
            render()

        unload_model(map_model)
        close_window()

if __name__ == '__main__':
    engine = Engine()
    engine.run()
