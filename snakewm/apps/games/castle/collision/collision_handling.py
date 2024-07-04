# ------------------------------------------------------------------------------------------------------------------
# These handler functions modify the positions and movement of shapes that are colliding, also known as overlapping.
# They are intended to allow for multiple different types of behaviour when two colliding shapes are detected; from
# doing nothing at all (NoHandler), to pushing the shapes just outside of one another (RubHandler) to bouncing off
# one another (BounceHandler).
# ------------------------------------------------------------------------------------------------------------------
# TODO: Create BounceHandler class


class BaseCollisionHandler:
    def __init__(self):
        pass

    def handle(self, shape_to_handle, collision_shape):
        pass

    def record_shape_for_handling(self, shape_list, shape, shape_to_test):
        pass


class CollisionRubHandler(BaseCollisionHandler):
    def __init__(self):
        super().__init__()

    def record_shape_for_handling(self, shape_list, shape, shape_to_test):
        mtv_vector = shape.get_mtv_vector(shape_to_test)
        if mtv_vector is not None:
            shape_list.append(shape)

    def handle(self, shape_to_handle, collision_shape):
        # check for MTV
        mtv_vector = shape_to_handle.get_mtv_vector(collision_shape)
        shape_to_handle.set_position([shape_to_handle.x + mtv_vector[0], shape_to_handle.y + mtv_vector[1]])
        may_need_further_handling = True
        return may_need_further_handling


class CollisionNoHandler(BaseCollisionHandler):
    def __init__(self):
        super().__init__()

    def handle(self, shape_to_handle, collision_shape):
        may_need_further_handling = False
        return may_need_further_handling
