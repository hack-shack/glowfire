from .collision_shapes import *

# -------------------------------------------------------------------------------------------------------
# The collision functions in this file are intended to detect collision, or overlaps, between two shapes.
# They currently just return True, in the case of an overlap, or False, in the case of no overlap.
# The polygon polygon function also stores a MTV (minimum translation vector) which should be the minimum
# vector to translate either shape by to undo the collision.
# -------------------------------------------------------------------------------------------------------
# TODO: create better, MTV-like, calculations for other collision functions


def get_distance(from_x, from_y, to_x, to_y):
    dx = from_x - to_x
    dy = from_y - to_y
    return math.sqrt((dx * dx) + (dy * dy))


def collide_circle_with_circle(a, b):
    x_dist = a.x - b.x
    y_dist = a.y - b.y
    squared_dist = x_dist ** 2 + y_dist ** 2
    radius_sum = (a.radius + b.radius)
    if squared_dist <= radius_sum ** 2:
        dist = math.sqrt(squared_dist)
        if dist > 0.0:
            overlap_normal = [x_dist/dist, y_dist/dist]
        else:
            overlap_normal = [0.0, 1.0]
        overlap_dist = radius_sum - dist
        overlap_vector = [overlap_normal[0] * overlap_dist, overlap_normal[1] * overlap_dist]
        if abs(overlap_vector[0]) > 0.0 or abs(overlap_vector[1]) > 0.0:
            a.set_loop_mtv_vector(b, overlap_vector)
            b.set_loop_mtv_vector(a, [-overlap_vector[0], -overlap_vector[1]])
        return True

    return False


def collide_circle_with_rotated_rectangle(circle, rect):
    rect_center_x = rect.x
    rect_center_y = rect.y

    rect_x = rect_center_x - rect.width / 2
    rect_y = rect_center_y - rect.height / 2

    rect_reference_x = rect_x
    rect_reference_y = rect_y

    # Rotate circle's center point back
    sin_rot = math.sin(rect.rotation)
    cos_rot = math.cos(rect.rotation)
    un_rotated_circle_x = cos_rot * (circle.x - rect_center_x) - sin_rot * (circle.y - rect_center_y) + rect_center_x
    un_rotated_circle_y = sin_rot * (circle.x - rect_center_x) + cos_rot * (circle.y - rect_center_y) + rect_center_y

    # Closest point in the rectangle to the center of circle rotated backwards(un-rotated)
    closest_x = un_rotated_circle_x
    closest_y = un_rotated_circle_y

    # Find the un-rotated closest x point from center of un-rotated circle
    if un_rotated_circle_x < rect_reference_x:
        closest_x = rect_reference_x
    elif un_rotated_circle_x > rect_reference_x + rect.width:
        closest_x = rect_reference_x + rect.width

    # Find the un-rotated closest y point from center of un-rotated circle
    if un_rotated_circle_y < rect_reference_y:
        closest_y = rect_reference_y
    elif un_rotated_circle_y > rect_reference_y + rect.height:
        closest_y = rect_reference_y + rect.height

    # Determine collision
    distance = get_distance(un_rotated_circle_x, un_rotated_circle_y, closest_x, closest_y)

    if distance < circle.radius:
        if distance > 0.0:
            x_dist = circle.x - rect_center_x
            y_dist = circle.y - rect_center_y
            overlap_normal = [x_dist / distance, y_dist / distance]
            overlap_dist = circle.radius - distance
        else:
            overlap_normal = [0.0, -1.0]
            overlap_dist = 1.0

        overlap_vector = [overlap_normal[0] * overlap_dist, overlap_normal[1] * overlap_dist]
        if abs(overlap_vector[0]) > 0.0 or abs(overlap_vector[1]) > 0.0:
            circle.set_loop_mtv_vector(rect, overlap_vector)
            rect.set_loop_mtv_vector(circle, [-overlap_vector[0], -overlap_vector[1]])
        return True

    return False


def collide_polygon_with_polygon(a, b):
    polygons = [a, b]
    smallest_overlap = 1000000000.0
    overlap_vector = [0.0, 0.0]
    for i in range(0, len(polygons)):
        # for each polygon, look at each edge of the polygon, and determine if it separates
        # the two shapes
        polygon = polygons[i]
        for name, edge in polygon.edges.items():
            # find the line perpendicular to this edge
            normal = [edge.value[1][1] - edge.value[0][1], edge.value[0][0] - edge.value[1][0]]

            min_a = None
            max_a = None
            # for each vertex in the first shape, project it onto the line perpendicular to the edge
            # and keep track of the min and max of these values
            for j in range(0, len(a.verts)):
                projected = (normal[0] * a.verts[j][0]) + (normal[1] * a.verts[j][1])
                if (min_a is None) or (projected < min_a):
                    min_a = projected

                if (max_a is None) or (projected > max_a):
                    max_a = projected

            # for each vertex in the second shape, project it onto the line perpendicular to the edge
            # and keep track of the min and max of these values
            min_b = None
            max_b = None
            for j in range(0, len(b.verts)):
                projected = (normal[0] * b.verts[j][0]) + (normal[1] * b.verts[j][1])
                if (min_b is None) or (projected < min_b):
                    min_b = projected

                if (max_b is None) or (projected > max_b):
                    max_b = projected

            # if there is no overlap between the projects, the edge we are looking at separates the two
            # polygons, and we know there is no overlap
            if (max_a < min_b) or (max_b < min_a):
                return False
            else:
                normalised_normal = polygon.normals[name].value

                if max_a > max_b:
                    overall_projection_length = max_a - min_b
                    direction = 1
                else:
                    overall_projection_length = max_b - min_a
                    direction = -1

                # test if we need to ignore collision reactions along this normal
                skip_normal = False
                for normal_test_polygon in polygons:
                    for normal_to_test in normal_test_polygon.normals.values():
                        if is_approx_equal(normalised_normal, normal_to_test.value):
                            if normal_to_test.should_skip:
                                skip_normal = True

                if not skip_normal:
                    combined_length_of_both_shapes = max_a - min_a + max_b - min_b
                    overlap_depth = (combined_length_of_both_shapes - overall_projection_length) / edge.length
                    if overlap_depth < smallest_overlap:
                        smallest_overlap = overlap_depth
                        overlap_vector[0] = direction * (normalised_normal[0] * overlap_depth)
                        overlap_vector[1] = direction * (normalised_normal[1] * overlap_depth)

    if abs(overlap_vector[0]) > 0.0 or abs(overlap_vector[1]) > 0.0:
        a.set_loop_mtv_vector(b, overlap_vector)
        b.set_loop_mtv_vector(a, [-overlap_vector[0], -overlap_vector[1]])
    return True


def is_approx_equal(normal_1, normal_2):
    if abs(normal_1[0] - normal_2[0]) < 0.05:
        if abs(normal_1[1] - normal_2[1]) < 0.05:
            return True
    return False
