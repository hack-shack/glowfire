import pygame
import math

from .collision_handling import CollisionNoHandler


# -------------------------------------------------------------------------------------------------------------------
# This file contains 2D shape classes with functions and data designed to assist in collision detection and handling.
# Currently it supports only circles, rotatable rectangles and composite shapes made of those two primitives.
# -------------------------------------------------------------------------------------------------------------------
# TODO: Add a polygon shape
# TODO: Better testing of composite shape. Does it really still work with handlers?


class Normal:
    def __init__(self, name, value, should_skip=False):
        self.name = name
        self.value = value
        self.should_skip = should_skip


class Edge:
    def __init__(self, name, value, length):
        self.name = name
        self.value = value
        self.length = length


class BaseCollisionShape:
    CIRCLE = 0
    RECT = 1
    AABB_RECT = 2
    COMPOSITE = 3

    def __init__(self, x, y, shape_type, aabb_rect, handlers_by_colliding_game_type=None,
                 game_type=None, game_types_to_collide=None):
        if game_types_to_collide is None:
            game_types_to_collide = []
        if handlers_by_colliding_game_type is None:
            handlers_by_colliding_game_type = {None: CollisionNoHandler()}
        self.next_shape_in_grid_square_index = -1

        self.text_id = ""
        self.x = float(x)
        self.y = float(y)
        self.type = shape_type

        self.current_grid_pos = [0, 0]
        self.nearby_grid_range_x = [0, 0]
        self.nearby_grid_range_y = [0, 0]

        self.collided_shapes_this_frame = []  # Intended so games can tell if two objects collided in the last frame
        self.collided_shapes_this_loop = []  # Used by collision handlers to check if they should to keep iterating
        self.loop_mtv_vectors_by_shape = {}
        self.frame_mtv_vectors_by_shape = {}

        self.owner = None
        self.game_types_to_collide = game_types_to_collide
        self.game_type = game_type

        self.handlers_by_colliding_game_type = handlers_by_colliding_game_type

        self.num_squares_to_search_around_grid_pos = 1

        self.aabb_rect = aabb_rect
        # overridden by base classes, this is essentially
        # the smallest size of height/width for an axis aligned square that will
        # fit this shape
        self.longest_aab_square_dimension = 0

        # this is the shortest distance between the centre of the shape and any edge/corner
        # helpful when assessing the maximum distance we can safely move a colliding shape in one frame.
        self.shortest_centre_to_edge = 0

        self.moved_since_last_collision_test = True

    # use this to get a handle on whatever entity in your game
    # is using this shape for collision
    def set_id(self, text_id):
        self.text_id = text_id

    def set_owner(self, owner):
        self.owner = owner

    def set_handler(self, handler, game_type):
        self.handlers_by_colliding_game_type[game_type] = handler

    def get_handler(self, game_type):
        return self.handlers_by_colliding_game_type[game_type]

    def set_grid_search_radius(self, grid_square_pixel_size):
        self.num_squares_to_search_around_grid_pos = int(math.ceil(self.longest_aab_square_dimension /
                                                                   grid_square_pixel_size))

    def set_new_grid_pos(self, new_grid_pos, grid_size):
        self.current_grid_pos = new_grid_pos

        start_x_grid_pos = max(0, self.current_grid_pos[0] - self.num_squares_to_search_around_grid_pos)
        end_x_grid_pos = min(grid_size[0] - 1, self.current_grid_pos[0] + self.num_squares_to_search_around_grid_pos)
        self.nearby_grid_range_x = [start_x_grid_pos, end_x_grid_pos]

        start_y_grid_pos = max(0, self.current_grid_pos[1] - self.num_squares_to_search_around_grid_pos)
        end_y_grid_pos = min(grid_size[1] - 1, self.current_grid_pos[1] + self.num_squares_to_search_around_grid_pos)
        self.nearby_grid_range_y = [start_y_grid_pos, end_y_grid_pos]

    def set_position(self, pos):
        pass

    def get_closest_active_collision_normal(self, collision_shape):
        pass

    def clear_frame_collided_shapes(self):
        self.collided_shapes_this_frame[:] = []
        self.frame_mtv_vectors_by_shape = {}

    def clear_loop_collided_shapes(self):
        self.collided_shapes_this_loop[:] = []
        self.loop_mtv_vectors_by_shape = {}

    def add_frame_collided_shape(self, shape):
        if shape not in self.collided_shapes_this_frame:
            self.collided_shapes_this_frame.append(shape)

    def add_loop_collided_shape(self, shape):
        if shape not in self.collided_shapes_this_loop:
            self.collided_shapes_this_loop.append(shape)

    def set_loop_mtv_vector(self, shape, vector):
        if shape not in self.collided_shapes_this_loop:
            self.loop_mtv_vectors_by_shape[shape] = vector

        if shape in self.frame_mtv_vectors_by_shape:
            old_vec = self.frame_mtv_vectors_by_shape[shape]
            if (vector[0] ** 2 + vector[1] ** 2) > (old_vec[0] ** 2 + old_vec[1] ** 2):
                self.frame_mtv_vectors_by_shape[shape] = vector
        else:
            self.frame_mtv_vectors_by_shape[shape] = vector

    def get_mtv_vector(self, shape):
        if shape in self.loop_mtv_vectors_by_shape:
            return self.loop_mtv_vectors_by_shape[shape]
        elif shape.type == BaseCollisionShape.COMPOSITE:
            for sub_shape in shape.collision_shapes:
                if sub_shape in self.loop_mtv_vectors_by_shape:
                    return self.loop_mtv_vectors_by_shape[sub_shape]
        else:
            return None

    def get_frame_mtv_vector(self, shape):
        if shape in self.frame_mtv_vectors_by_shape:
            return self.frame_mtv_vectors_by_shape[shape]
        elif shape.type == BaseCollisionShape.COMPOSITE:
            for sub_shape in shape.collision_shapes:
                if sub_shape in self.frame_mtv_vectors_by_shape:
                    return self.frame_mtv_vectors_by_shape[sub_shape]
        else:
            return None


class CollisionCircle(BaseCollisionShape):
    def __init__(self, x, y, radius, handlers_by_colliding_game_type=None, game_type=None, game_types_to_collide=None):
        if game_types_to_collide is None:
            game_types_to_collide = []
        aabb_rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        super().__init__(x, y, BaseCollisionShape.CIRCLE, aabb_rect,
                         handlers_by_colliding_game_type, game_type, game_types_to_collide)

        self.radius = radius

        self.longest_aab_square_dimension = self.radius * 2

        self.shortest_centre_to_edge = self.radius

        self.collision_normal = [0.0, -1.0]

    def set_position(self, pos):
        self.x = float(pos[0])
        self.y = float(pos[1])
        self.aabb_rect.center = [int(self.x), int(self.y)]
        self.moved_since_last_collision_test = True

    def is_inside(self, point):
        is_inside = False
        x_dist = self.x - point[0]
        y_dist = self.y - point[1]

        length = math.sqrt(x_dist ** 2 + y_dist ** 2)
        if length < self.radius:
            is_inside = True
        return is_inside

    def set_radius(self, radius):
        self.radius = radius
        self.longest_aab_square_dimension = self.radius * 2
        self.shortest_centre_to_edge = self.radius
        self.aabb_rect = pygame.Rect(self.x - radius, self.y - radius,
                                     radius * 2, radius * 2)

    def get_closest_active_collision_normal(self, collision_shape):
        x_dist = collision_shape.x - self.x
        y_dist = collision_shape.y - self.y
        dist = math.sqrt(x_dist ** 2 + y_dist ** 2)
        self.collision_normal = [x_dist / dist, y_dist / dist]
        return self.collision_normal


# -----------------------------------------
# This is a rotatable collision rectangle
# as such it won't fit neatly into a grid
# square the same dimensions
# as it's width and height
# -----------------------------------------
class CollisionRect(BaseCollisionShape):
    def __init__(self, py_rect, rotation, handlers_by_colliding_game_type=None,
                 game_type=None, game_types_to_collide=None):
        if game_types_to_collide is None:
            game_types_to_collide = []
        self.py_rect = py_rect
        aabb_dimension = math.sqrt(py_rect.width ** 2 + py_rect.height ** 2)
        aab_rect = pygame.Rect(py_rect.centerx - (aabb_dimension / 2),
                               py_rect.centery - (aabb_dimension / 2),
                               aabb_dimension,
                               aabb_dimension)
        super().__init__(py_rect.centerx,
                         py_rect.centery,
                         BaseCollisionShape.RECT,
                         aab_rect,
                         handlers_by_colliding_game_type,
                         game_type,
                         game_types_to_collide)
        self.width = py_rect.width
        self.height = py_rect.height
        self.rotation = rotation

        self.longest_aab_square_dimension = aabb_dimension

        self.shortest_centre_to_edge = min(self.height / 2, self.width / 2)

        self.edges = {}
        self.normals = {"top": Normal("top", [0.0]),
                        "bottom": Normal("bottom", [0.0]),
                        "left": Normal("left", [0.0]),
                        "right": Normal("right", [0.0])}
        self.verts = []
        self.update_real_bounds()

    def rotate(self, rotation):
        self.rotation += rotation
        self.update_real_bounds()
        self.moved_since_last_collision_test = True

    def set_rotation(self, rotation):
        self.rotation = rotation
        self.update_real_bounds()
        self.moved_since_last_collision_test = True

    def set_position(self, pos):
        self.x = pos[0]
        self.y = pos[1]
        self.py_rect.centerx = pos[0]
        self.py_rect.centery = pos[1]
        self.update_real_bounds()
        self.aabb_rect.center = [int(self.x), int(self.y)]
        self.moved_since_last_collision_test = True

    def set_dimensions(self, width, height):
        self.width = width
        self.height = height
        self.py_rect.width = width
        self.py_rect.height = height
        aabb_dimension = math.sqrt(width ** 2 + height ** 2)
        self.aabb_rect = pygame.Rect(self.x - (aabb_dimension / 2),
                                     self.y - (aabb_dimension / 2),
                                     aabb_dimension,
                                     aabb_dimension)
        self.longest_aab_square_dimension = aabb_dimension
        self.shortest_centre_to_edge = min(self.height / 2, self.width / 2)
        self.update_real_bounds()
        self.moved_since_last_collision_test = True

    def is_inside(self, point):
        is_inside = False
        if (point[0] > self.py_rect.x) and (point[0] < (self.py_rect.x + self.width)):
            if (point[1] > self.py_rect.y) and (point[1] < (self.py_rect.y + self.height)):
                is_inside = True
        return is_inside

    def update_real_bounds(self):
        cos_rotation = math.cos(-self.rotation)
        sin_rotation = math.sin(-self.rotation)
        half_width = self.width / 2
        half_height = self.height / 2

        top_left = [0.0, 0.0]
        top_left[0] = self.x + ((-half_width * cos_rotation) - (-half_height * sin_rotation))
        top_left[1] = self.y + ((-half_width * sin_rotation) + (-half_height * cos_rotation))

        top_right = [0.0, 0.0]
        top_right[0] = self.x + ((half_width * cos_rotation) - (-half_height * sin_rotation))
        top_right[1] = self.y + ((half_width * sin_rotation) + (-half_height * cos_rotation))

        bottom_left = [0.0, 0.0]
        bottom_left[0] = self.x + ((-half_width * cos_rotation) - (half_height * sin_rotation))
        bottom_left[1] = self.y + ((-half_width * sin_rotation) + (half_height * cos_rotation))

        bottom_right = [0.0, 0.0]
        bottom_right[0] = self.x + ((half_width * cos_rotation) - (half_height * sin_rotation))
        bottom_right[1] = self.y + ((half_width * sin_rotation) + (half_height * cos_rotation))

        self.verts[:] = []
        self.verts.append(top_left)
        self.verts.append(top_right)
        self.verts.append(bottom_left)
        self.verts.append(bottom_right)

        # the edge ids will only be 'accurate' when the collision shape is not rotated
        self.edges = {"top": Edge("top", [top_left, top_right], length=self.width),
                      "left": Edge("left", [bottom_left, top_left], length=self.width),
                      "right": Edge("right", [top_right, bottom_right], length=self.width),
                      "bottom": Edge("bottom", [bottom_right, bottom_left], length=self.width)}

        old_normals = self.normals.copy()

        top_normal = [(self.edges["top"].value[1][1] - self.edges["top"].value[0][1]) / self.height,
                      (self.edges["top"].value[0][0] - self.edges["top"].value[1][0]) / self.width]

        left_normal = [(self.edges["left"].value[1][1] - self.edges["left"].value[0][1]) / self.height,
                       (self.edges["left"].value[0][0] - self.edges["left"].value[1][0]) / self.width]

        bottom_normal = [(self.edges["bottom"].value[1][1] - self.edges["bottom"].value[0][1]) / self.height,
                         (self.edges["bottom"].value[0][0] - self.edges["bottom"].value[1][0]) / self.width]

        right_normal = [(self.edges["right"].value[1][1] - self.edges["right"].value[0][1]) / self.height,
                        (self.edges["right"].value[0][0] - self.edges["right"].value[1][0]) / self.width]

        self.normals = {"top": Normal("top", top_normal, old_normals["top"].should_skip),
                        "left": Normal("left", left_normal, old_normals["left"].should_skip),
                        "bottom": Normal("bottom", bottom_normal, old_normals["bottom"].should_skip),
                        "right": Normal("right", right_normal, old_normals["right"].should_skip)}

    def get_closest_active_collision_normal(self, collision_shape):
        closest_edge_id = None
        closest_distance = 1000000000.0
        for name, normal in self.normals.items():
            if not normal.should_skip:
                distance = self.dist_between_point_and_line(collision_shape.x,
                                                            collision_shape.y,
                                                            self.edges[name].value[0][0],
                                                            self.edges[name].value[0][1],
                                                            self.edges[name].value[1][0],
                                                            self.edges[name].value[1][1])
                if distance < closest_distance:
                    closest_distance = distance
                    closest_edge_id = name
        closest_edge_normal = [0.0, -1.0]
        if closest_edge_id is not None:
            closest_edge_normal = self.normals[closest_edge_id].value
        return closest_edge_normal

    @staticmethod
    def dist_between_point_and_line(x, y, x1, y1, x2, y2):
        a = x - x1
        b = y - y1
        c = x2 - x1
        d = y2 - y1

        dot = a * c + b * d
        len_sq = c * c + d * d
        param = -1
        if len_sq != 0:  # in case of 0 length line
            param = dot / len_sq

        if param < 0:
            xx = x1
            yy = y1
        elif param > 1:
            xx = x2
            yy = y2
        else:
            xx = x1 + param * c
            yy = y1 + param * d

        dx = x - xx
        dy = y - yy
        return math.sqrt(dx * dx + dy * dy)


class CompositeCollisionShape(BaseCollisionShape):

    def __init__(self, x, y, dimensions, handlers_by_colliding_game_type=None,
                 game_type=None, game_types_to_collide=None):
        if game_types_to_collide is None:
            game_types_to_collide = []
        self.collision_shapes = []
        self.collision_shape_pos_offsets = []

        aabb_rect = pygame.Rect([x - (dimensions[0] / 2), y - (dimensions[1] / 2)], dimensions)
        super(CompositeCollisionShape, self).__init__(x,
                                                      y,
                                                      BaseCollisionShape.COMPOSITE,
                                                      aabb_rect,
                                                      handlers_by_colliding_game_type,
                                                      game_type,
                                                      game_types_to_collide)

    def add_rotatable_rect(self, py_rect, rotation):
        half_width = self.aabb_rect.width / 2
        half_height = self.aabb_rect.height / 2
        self.add_shape(CollisionRect(py_rect, rotation, self.handlers_by_colliding_game_type, self.game_type,
                                     self.game_types_to_collide),
                       [py_rect.centerx - half_width, py_rect.centery - half_height])

    def add_circle(self, x, y, radius):
        half_width = self.aabb_rect.width / 2
        half_height = self.aabb_rect.height / 2
        self.add_shape(CollisionCircle(x, y, radius, self.handlers_by_colliding_game_type, self.game_type,
                                       self.game_types_to_collide),
                       [x - half_width, y - half_height])

    def add_shape(self, shape, pos_offset):
        self.collision_shapes.append(shape)
        self.collision_shape_pos_offsets.append(pos_offset)
        self.update_sub_shape_positions()

    def set_position(self, pos):
        self.x = pos[0]
        self.y = pos[1]
        self.update_sub_shape_positions()
        self.aabb_rect.center = [int(self.x), int(self.y)]
        self.moved_since_last_collision_test = True

    def update_sub_shape_positions(self):
        for i in range(0, len(self.collision_shapes)):
            shape = self.collision_shapes[i]
            offset = self.collision_shape_pos_offsets[i]
            shape.set_position([self.x + offset[0], self.y + offset[1]])

    def is_inside(self, point):
        is_inside = False
        if (point[0] > self.aabb_rect.x) and (point[0] < (self.aabb_rect.x + self.aabb_rect.width)):
            if (point[1] > self.aabb_rect.y) and (point[1] < (self.aabb_rect.y + self.aabb_rect.height)):
                is_inside = True
        return is_inside

    def get_closest_active_collision_normal(self, collision_shape):
        closest_sub_shape = self.collision_shapes[0]
        closest_dist = 10000000000
        for sub_shape in self.collision_shapes:
            x_dist = sub_shape.x - collision_shape.x
            y_dist = sub_shape.y - collision_shape.y
            dist = math.sqrt(x_dist ** 2 + y_dist ** 2)
            if dist < closest_dist:
                closest_dist = dist
                closest_sub_shape = sub_shape

        return closest_sub_shape.get_closest_active_collision_normal(collision_shape)
