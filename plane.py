import numpy as np
from math import sin, cos, pi, sqrt, atan2

class Plane():
    """class for Plane object
    ** initailly, all the speed is +J
    """

    def __init__(self, x, y, vx, vy, turn_speed, fps):
        """ x, y in px      vx, vy in px/s  (positive is down)
        turn_speed in deg/s (will be converted int rad/s)
        """
        self.x = x          # x and y are in px
        self.y = y
        self.v = np.array([[vx], [vy]])      # in px/s
        omega_per_s = turn_speed/180*pi      # converts to rad/s
        self.omega = omega_per_s/fps         # rad/tick
        self.fps = fps
        self.right_rot = np.array([[cos(self.omega), -1*sin(self.omega)],\
        [sin(self.omega), cos(self.omega)]])    # per tick!!!

        self.left_rot = np.array([[cos(-1*self.omega), -1*sin(-1*self.omega)],\
        [sin(-1*self.omega), cos(-1*self.omega)]])

        self.turn_drag = 0.9
        self.dt = 1.0/fps
        self.alive = True


    def move(self, turn=0):
        """ (int) -> void
        CALCULATES the next position of the plane taking turning
        into account (default = no turn)
        """
        if turn == 0:
            self.x += self.v[0][0] * self.dt
            self.y += self.v[1][0] * self.dt
        elif turn == 1:
            # counter clockwise
            self.v[0][0] *= self.turn_drag        # decreases the speed for the turn
            self.v[1][0] *= self.turn_drag
            self.v = np.dot(self.right_rot, self.v)
            self.x += self.v[0][0] * self.dt
            self.y += self.v[1][0] * self.dt
            self.v = self.v / self.turn_drag    # reset speed afterwards
        else:
            # clockwise
            self.v[0][0] *= self.turn_drag
            self.v[1][0] *= self.turn_drag
            self.v = np.dot(self.left_rot, self.v)
            self.x += self.v[0][0] * self.dt
            self.y += self.v[1][0] * self.dt
            self.v = self.v / self.turn_drag


    def pos(self):
        """ () -> tuple(int, int) 
        this one will return the current position
        """
        return(int(round(self.x)), int(round(self.y)))
    

    def get_angle(self):
        """ -> float
        returns angle of the plane in DEG for displaying
        """
        # arctant(x/y) turns out to work in this case
        new_angle = atan2(self.v[0][0], self.v[1][0])
        return new_angle * 180 / pi + 180


    def is_alive(self, missiles, radius):
        """ () -> bool
        hit detection
        """
        for m in missiles:
            hypot = sqrt((m.x-self.x)**2 + (m.y-self.y)**2)
            if hypot < radius:
                self.alive = False
                return False


    def shift(self, x_shift, y_shift):
        """ (float, float) -> void
        adds the shift values to its position
        """
        self.x += x_shift
        self.y += y_shift


    def missile_tracking(self):
        """ () -> tuple(float x, float y, float vx, float vy)
        Returns relevant info for the missile guidance
        """
        return (self.x, self.y, self.v[0][0], self.v[1][0])