import random
from .collision_funcs import *
from .collision_handling import CollisionNoHandler, CollisionRubHandler


# -------------------------------------------------------------------------------------------------------------------
# This file contains an implementation of a 2D grid for detecting potential collisions in 2D space to speed up
# collision detection in large game worlds. It is built using the collision shapes, detection functions and
# handler functions implemented elsewhere in this collision library.
# -------------------------------------------------------------------------------------------------------------------
# TODO: optimisation pass to weed out any crufty old code tucked away in here.


class GridSquare:
    def __init__(self):
        self.index_of_first_shape_in_square = -1
        self.index_of_first_static_shape_in_square = -1


class CollisionGrid:

    def __init__(self, grid_size, grid_pixel_size):
        self.grid_square_pixel_size = grid_pixel_size
        self.grid_size = grid_size
        self.grid = []
        self.all_dynamic_collision_shapes = []  # shapes that move around

        # special case shapes that fit in a single grid square and stay there
        # no need to move these around grid or test them against
        # other shapes - moving shapes will test against them
        self.static_grid_aligned_collision_shapes = []

        self.shapes_collided_this_frame = []
        self.shapes_collided_this_loop = []

        self.rub_handler = CollisionRubHandler()
        self.no_handler = CollisionNoHandler()

        # fill empty grid
        for x_axis in range(0, self.grid_size[0]):
            column = []
            for y_axis in range(0, self.grid_size[1]):
                column.append(GridSquare())
            self.grid.append(column)

    def check_collisions(self):
        for shape in self.shapes_collided_this_frame:
            shape.clear_frame_collided_shapes()
        self.shapes_collided_this_frame[:] = []

        for shape in self.shapes_collided_this_loop:
            shape.clear_loop_collided_shapes()
        self.shapes_collided_this_loop[:] = []

        collided_shapes_for_handler = []
        for shape in self.all_dynamic_collision_shapes:
            if shape.moved_since_last_collision_test:
                self.shape_collision_test(shape, collided_shapes_for_handler)

        # handle detected collisions

        # This is the amount of times per frame we will attempt to resolve collisions/handle shapes to clear collisions
        max_handling_per_frame = 15
        handling_this_frame = 0
        while len(collided_shapes_for_handler) > 0 and handling_this_frame < max_handling_per_frame:
            # sort collided shapes so the ones with the least amount of collisions are first. The idea being that this
            # will make it easier to resolve messy multi-object collisions by moving the shapes on the outside edge of
            # pile-ups first, thereby giving room for the ones in the centre. This principle should be the same on any
            # kind of resistant collision handling
            # We also randomise the order of the list of shapes first to stop the same shapes being moved each time a
            # collision occurs in cases where both shapes in a collision could move.

            random.shuffle(collided_shapes_for_handler)
            sorted(collided_shapes_for_handler, key=lambda x: len(x.collided_shapes_this_loop))

            # Back to trying to resolve all collisions every frame as long as neither shape in a collision has moved
            # ready since the last test. Should make unhandled collisions resolve quickly and still deal with complex
            # resolutions (I hope)
            for shape in collided_shapes_for_handler:
                if len(shape.collided_shapes_this_loop) > 0:
                    # this shuffle ensures we don't fall into bad pattern of consistently bouncing between two objects
                    # while ignoring a third when trying to resolve collisions
                    random.shuffle(shape.collided_shapes_this_loop)
                    for colliding_shape in shape.collided_shapes_this_loop:
                        if shape.moved_since_last_collision_test or colliding_shape.moved_since_last_collision_test:
                            pass
                        else:
                            # only allow each shape to move once in a resolve loop
                            # in case move solves multiple collisions
                            shape.get_handler(colliding_shape.game_type).handle(shape, colliding_shape)

            # this just makes sure we don't double compare collided shapes in the inner collision test
            for shape in self.shapes_collided_this_loop:
                shape.clear_loop_collided_shapes()
            self.shapes_collided_this_loop[:] = []

            collided_shapes_for_handler[:] = []
            for shape in self.all_dynamic_collision_shapes:
                if shape.moved_since_last_collision_test:
                    self.shape_collision_test(shape, collided_shapes_for_handler)

            handling_this_frame += 1

    def shape_collision_test(self, shape, collided_shapes_for_handler):
        shape.moved_since_last_collision_test = False
        for grid_x in range(shape.nearby_grid_range_x[0], shape.nearby_grid_range_x[1] + 1):
            for grid_y in range(shape.nearby_grid_range_y[0], shape.nearby_grid_range_y[1] + 1):

                # dynamic shapes collision
                shape_index_in_square = self.grid[grid_x][grid_y].index_of_first_shape_in_square
                while shape_index_in_square != -1:
                    shape_to_test = self.all_dynamic_collision_shapes[shape_index_in_square]
                    self.inner_collision_test(shape, shape_to_test, collided_shapes_for_handler)
                    shape_index_in_square = shape_to_test.next_shape_in_grid_square_index

                # static shapes collision
                static_shape_index_in_square = self.grid[grid_x][grid_y].index_of_first_static_shape_in_square
                while static_shape_index_in_square != -1:
                    shape_to_test = self.static_grid_aligned_collision_shapes[static_shape_index_in_square]
                    self.inner_collision_test(shape, shape_to_test, collided_shapes_for_handler)
                    static_shape_index_in_square = shape_to_test.next_shape_in_grid_square_index

    def inner_collision_test(self, shape, shape_to_test, collided_shapes_for_handler):
        # Do some quick tests to see if we should collide these two shapes
        should_collide_from_game_type = self.check_should_collide_from_game_type(shape, shape_to_test)
        if should_collide_from_game_type:
            if shape.aabb_rect.colliderect(shape_to_test.aabb_rect):  # aabb test
                already_collided = self.check_already_collided_this_loop(shape, shape_to_test)
                if already_collided:
                    if shape.get_mtv_vector(shape_to_test) is not None:
                        shape.get_handler(shape_to_test.game_type).record_shape_for_handling(
                            collided_shapes_for_handler, shape, shape_to_test)
                else:
                    # Check they are not the same shape
                    if shape_to_test != shape:
                        collided = False
                        if shape_to_test.type == BaseCollisionShape.CIRCLE and shape.type == BaseCollisionShape.RECT:
                            if collide_circle_with_rotated_rectangle(shape_to_test, shape):
                                collided = True
                        elif shape_to_test.type == BaseCollisionShape.RECT and shape.type == BaseCollisionShape.CIRCLE:
                            if collide_circle_with_rotated_rectangle(shape, shape_to_test):
                                collided = True
                        elif shape_to_test.type == BaseCollisionShape.RECT and shape.type == BaseCollisionShape.RECT:
                            if collide_polygon_with_polygon(shape, shape_to_test):
                                collided = True
                        elif shape_to_test.type == BaseCollisionShape.CIRCLE and \
                                shape.type == BaseCollisionShape.CIRCLE:
                            if collide_circle_with_circle(shape, shape_to_test):
                                collided = True
                        elif shape_to_test.type == BaseCollisionShape.COMPOSITE:
                            if self.composite_single_shape_collision_test(shape, shape_to_test):
                                collided = True
                        elif shape.type == BaseCollisionShape.COMPOSITE:
                            if self.composite_single_shape_collision_test(shape_to_test, shape):
                                collided = True

                        if collided:
                            needs_resolving = shape.get_mtv_vector(shape_to_test) is not None
                            self.record_colliding_shapes(shape, shape_to_test, needs_resolving)
                            if needs_resolving:
                                shape.get_handler(shape_to_test.game_type).record_shape_for_handling(
                                    collided_shapes_for_handler, shape, shape_to_test)

    @staticmethod
    def composite_single_shape_collision_test(shape, composite_shape):
        collided = False
        for sub_shape in composite_shape.collision_shapes:
            if sub_shape.type == BaseCollisionShape.CIRCLE and shape.type == BaseCollisionShape.RECT:
                if collide_circle_with_rotated_rectangle(sub_shape, shape):
                    collided = True
            elif sub_shape.type == BaseCollisionShape.RECT and shape.type == BaseCollisionShape.CIRCLE:
                if collide_circle_with_rotated_rectangle(shape, sub_shape):
                    collided = True
            elif sub_shape.type == BaseCollisionShape.RECT and shape.type == BaseCollisionShape.RECT:
                if collide_polygon_with_polygon(shape, sub_shape):
                    collided = True
            elif sub_shape.type == BaseCollisionShape.CIRCLE and shape.type == BaseCollisionShape.CIRCLE:
                if collide_circle_with_circle(shape, sub_shape):
                    collided = True
        return collided

    @staticmethod
    def check_already_collided_this_loop(shape_a, shape_b):
        for collision in shape_a.collided_shapes_this_loop:
            if collision == shape_b:
                return True
        return False

    @staticmethod
    def check_should_collide_from_game_type(shape_a, shape_b):
        for game_type in shape_a.game_types_to_collide:
            if game_type == shape_b.game_type:
                return True
        return False

    def record_colliding_shapes(self, shape_a, shape_b, needs_resolving=True):
        shape_a.add_frame_collided_shape(shape_b)
        shape_b.add_frame_collided_shape(shape_a)
        self.shapes_collided_this_frame.append(shape_a)
        self.shapes_collided_this_frame.append(shape_b)

        if needs_resolving:
            shape_a.add_loop_collided_shape(shape_b)
            shape_b.add_loop_collided_shape(shape_a)
            self.shapes_collided_this_loop.append(shape_a)
            self.shapes_collided_this_loop.append(shape_b)

    def update_shape_grid_positions(self):
        index = 0

        for shape in self.all_dynamic_collision_shapes:
            new_grid_pos = [max(0, min(self.grid_size[0] - 1,
                                       int(shape.x / self.grid_square_pixel_size))),
                            max(0, min(self.grid_size[1] - 1,
                                       int(shape.y / self.grid_square_pixel_size)))]
            if shape.current_grid_pos[0] == new_grid_pos[0] and shape.current_grid_pos[1] == new_grid_pos[1]:
                pass
            else:
                self.remove_shape_from_old_grid_pos_by_index(index, shape.current_grid_pos)
                self.add_shape_to_new_grid_pos_by_index(index, new_grid_pos)
                shape.set_new_grid_pos(new_grid_pos, self.grid_size)

            index += 1

    # shape must fit entirely inside single grid square
    def add_static_grid_aligned_shape_to_grid(self, shape):
        new_static_shape_index = len(self.static_grid_aligned_collision_shapes)
        self.static_grid_aligned_collision_shapes.append(shape)
        new_grid_pos = [max(0, min(self.grid_size[0] - 1,
                                   int(shape.x / self.grid_square_pixel_size))),
                        max(0, min(self.grid_size[1] - 1,
                                   int(shape.y / self.grid_square_pixel_size)))]
        shape.set_new_grid_pos(new_grid_pos, self.grid_size)
        self.add_static_shape_to_new_grid_pos_by_index(new_static_shape_index, new_grid_pos)
        shape.moved_since_last_collision_test = False  # static shapes never move so we default this to false

    def add_static_shape_to_new_grid_pos_by_index(self, shape_index, grid_pos):
        # check if grid square empty of shapes, if so add our shape
        self.static_grid_aligned_collision_shapes[shape_index].next_shape_in_grid_square_index = -1
        if self.grid[grid_pos[0]][grid_pos[1]].index_of_first_static_shape_in_square == -1:
            self.grid[grid_pos[0]][grid_pos[1]].index_of_first_static_shape_in_square = shape_index
        else:
            current_index = self.grid[grid_pos[0]][grid_pos[1]].index_of_first_static_shape_in_square
            next_index = self.static_grid_aligned_collision_shapes[current_index].next_shape_in_grid_square_index
            # zip to the end of our list
            while current_index != -1 and next_index != -1:
                current_index = self.static_grid_aligned_collision_shapes[current_index].next_shape_in_grid_square_index
                next_index = self.static_grid_aligned_collision_shapes[next_index].next_shape_in_grid_square_index

            self.static_grid_aligned_collision_shapes[current_index].next_shape_in_grid_square_index = shape_index

    def add_new_shape_to_grid(self, shape):
        new_shape_index = len(self.all_dynamic_collision_shapes)
        self.all_dynamic_collision_shapes.append(shape)
        new_grid_pos = [max(0, min(self.grid_size[0] - 1,
                                   int(shape.x / self.grid_square_pixel_size))),
                        max(0, min(self.grid_size[1] - 1,
                                   int(shape.y / self.grid_square_pixel_size)))]
        shape.set_grid_search_radius(self.grid_square_pixel_size)
        shape.set_new_grid_pos(new_grid_pos, self.grid_size)
        self.add_shape_to_new_grid_pos_by_index(new_shape_index, new_grid_pos)

    def remove_shape_from_grid(self, shape):
        removal_index = self.all_dynamic_collision_shapes.index(shape)
        self.remove_shape_from_old_grid_pos_by_index(removal_index, shape.current_grid_pos)
        self.all_dynamic_collision_shapes.remove(shape)

        for shape in self.all_dynamic_collision_shapes:
            if shape.next_shape_in_grid_square_index > removal_index:
                shape.next_shape_in_grid_square_index -= 1

        for col in self.grid:
            for square in col:
                if square.index_of_first_shape_in_square > removal_index:
                    square.index_of_first_shape_in_square -= 1

    def add_shape_to_new_grid_pos_by_index(self, shape_index, grid_pos):
        # check if grid square empty of shapes, if so add our shape
        self.all_dynamic_collision_shapes[shape_index].next_shape_in_grid_square_index = -1
        if self.grid[grid_pos[0]][grid_pos[1]].index_of_first_shape_in_square == -1:
            self.grid[grid_pos[0]][grid_pos[1]].index_of_first_shape_in_square = shape_index
        else:
            current_index = self.grid[grid_pos[0]][grid_pos[1]].index_of_first_shape_in_square
            next_index = self.all_dynamic_collision_shapes[current_index].next_shape_in_grid_square_index
            # zip to the end of our list
            while current_index != -1 and next_index != -1:
                current_index = self.all_dynamic_collision_shapes[current_index].next_shape_in_grid_square_index
                next_index = self.all_dynamic_collision_shapes[next_index].next_shape_in_grid_square_index

            self.all_dynamic_collision_shapes[current_index].next_shape_in_grid_square_index = shape_index

    def remove_shape_from_old_grid_pos_by_index(self, shape_index, grid_pos):
        start_index = self.grid[grid_pos[0]][grid_pos[1]].index_of_first_shape_in_square
        if start_index == shape_index:
            self.grid[grid_pos[0]][grid_pos[1]].index_of_first_shape_in_square = \
                self.all_dynamic_collision_shapes[start_index].next_shape_in_grid_square_index
        else:
            # need to find shape in list
            current_index = self.grid[grid_pos[0]][grid_pos[1]].index_of_first_shape_in_square
            while current_index != -1:
                next_index = self.all_dynamic_collision_shapes[current_index].next_shape_in_grid_square_index

                if (next_index != -1) and next_index == shape_index:
                    self.all_dynamic_collision_shapes[current_index].next_shape_in_grid_square_index = \
                        self.all_dynamic_collision_shapes[next_index].next_shape_in_grid_square_index

                current_index = next_index
