from math import sin, cos, atan2, sqrt, acos, asin, pi
from random import random, randint

class Missile():
    """ class for missile object
    """
    def __init__(self, x, y, vx, vy, turn_speed, burn_duration, burn_acc, fps, guidance_mode=1):
        """ everything is in px and s
        plane_pos is needed to determine a init position close to the plane
        burn_duration in ticks
        turn_speed in deg/tick
        """
        self.x = x
        self.y = y
        self.v =[vx, vy]
        self.burn_duration = burn_duration
        self.burn_acc = burn_acc
        self.burned = 0
        self.omega = turn_speed      # deg/s
        self.turn_drag = -70        # px /s/s, max drag
        self.guidance_mode = guidance_mode
        self.fps = fps
        self.dt = 1.0/fps
        self.alive = True
        self.hit = False
        self.p_last = []
        self.m_last = []


    def pure_guidance(self, plane):
        """ (Plane) -> void
        worst way to guide a missile, aka
        points the missile directly at the plane
        *** + omega is clockwise    - is ct clockwise
        """
        x, y, vx, vy = plane.missile_tracking()
        vec_target = [x-self.x, y-self.y]           # displacement vector
        vec_missile = [self.v[0], self.v[1]]        # velocity vector
        dot_prod = vec_target[0] * vec_missile[0] + vec_target[1] * vec_missile[1]
        mag_prod = sqrt(vec_target[0]**2 + vec_target[1]**2) * sqrt(vec_missile[0]**2 + vec_missile[1]**2)
        cross_prod_k = vec_target[0] * vec_missile[1] - vec_missile[0] * vec_target[1]
        try:
            omega = acos(dot_prod/mag_prod)
        except ValueError:
            # due to floating point math, dot product can be > magnitude when they're perfectly aligned...
            omega = 0
        # this gets how much omega can be done and how much v will be bled
        turn_command, decel = self.calc_angle_drag(omega)
        # fixing omega using cross product..
        if cross_prod_k > 0:
            turn_command *= -1
        # steers missile
        self.turn(turn_command, decel)
        self.x += self.v[0] * self.dt
        self.y += self.v[1] * self.dt

    
    def proportional_guidance(self, plane):
        ''' the real beast of an algorithm
        normal accel = N * LOS rate * closing V
        accel is proportional to LOS rate and closing velocity
        N = navigational gain (3-5 according to wiki)
        '''
        if len(self.p_last) == 0 or len(self.m_last) == 0:
            # upon initialization
            self.p_last = [plane.x, plane.y]
            self.m_last = [self.x, self.y]
            self.pure_guidance(plane)
        else:
            x, y, vx, vy = plane.missile_tracking()
            # both vectors are of velocity
            V0 = [self.p_last[0]-self.m_last[0], self.p_last[1], self.m_last[1]]
            V1 = [x - self.x, y - self.y]
            self.p_last[0] = x
            self.p_last[1] = y
            self.m_last[0] = self.x
            self.m_last[1] = self.y
            dot_prod = V0[0] * V1[0] + V0[1] * V1[1]
            mag_prod = sqrt(V0[0]**2 + V0[1]**2) * sqrt(V1[0]**2 + V1[1]**2)
            cross_prod_k = V0[0] * V1[1] - V1[0] * V0[1]
            try:
                omega = acos(dot_prod/mag_prod)
            except ValueError:
                # due to floating point math, dot product can be > magnitude when they're perfectly aligned...
                omega = 0
             # fixing omega using cross product..
            if cross_prod_k > 0:
                omega *= -1
            rate_LOS = omega * self.dt
            print(rate_LOS)
    

    def calc_angle_drag(self, desired_omega):
        """ (float) -> float, float
        determines how much turn is possible according to what's desired
        and how much speed is kept after bleed(as a fraction of v)
        """
        max_omega = (self.omega/180) * pi * self.dt
        if abs(desired_omega) >= max_omega:
            # missile cant turn fast enough, max omega commanded
            turn_commanded = max_omega
            decel = self.turn_drag
        else:
            # missile doesn't need max omega
            turn_commanded = desired_omega
            decel = (desired_omega/max_omega) * self.turn_drag
        return turn_commanded, decel


    def turn(self, turn, drag):
        """ (float, float) -> void
        actually steers the missile according to what's commanded
        DOES NOT move the missile
        ** also bleeds speed off the missile
        """
        theta = atan2(self.v[1], self.v[0])
        self.v[0] += drag * cos(theta) * self.dt
        self.v[1] += drag * sin(theta) * self.dt
        vx = self.v[0]
        vy = self.v[1]
        # rotation matrix
        self.v[0] = vx * cos(turn) - vy * sin(turn)
        self.v[1] = vx * sin(turn) + vy * cos(turn)
        

    def move(self, plane):
        """ (Plane) -> void
        moves the missile forward according to a specific guidance
        does NOT return new coordinates
        """
        if self.guidance_mode == 1:
            # -> pure guidance
            self.pure_guidance(plane)
            # self.proportional_guidance(plane)
        elif self.guidance_mode == 2:
            # TODO
            pass
        

    def pos(self):
        """ () -> tuple(int, int) 
        this one will return the current position
        """
        return (int(round(self.x)), int(round(self.y)))


    def get_angle(self):
        '''() -> float
        returns the angle to rotate the missile img
        '''
        ang = atan2(self.v[0], self.v[1])
        return ang * 180 / pi + 180


    def shift(self, shift_x, shift_y):
        """ (float, float) -> void
        same as in Plane class
        """
        self.x += shift_x
        self.y += shift_y