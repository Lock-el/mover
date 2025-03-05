import pygame as py
import physic

class Entity(py.sprite.Sprite):
    def __init__(self, screen: py.Surface, image, start_pos, mass):
        super().__init__()

        self.screen = screen

        # Configuration de la hitbox
        self.image = image
        self.rect = self.image.get_rect(topleft=start_pos)

        # Physique
        self.MASS = mass
        self.GRAVITY = 9.81  # Force de gravité
        self.AIR_RESISTANCE = 0.3  # Coefficient de résistance de l'air
        self.GROUND_RESISTANCE = 5
        self.velocity = py.math.Vector2(0, 0)
        self.sum_acceleration = py.math.Vector2(0, 0)

        self.on_ground = False  # État pour savoir si l'entité est au sol


    def apply_force(self, force):   # Force en newton
        self.sum_acceleration += physic.get_acceleration(force, self.MASS)

    def update(self, delta_time):
        # Applique la gravité
        self.sum_acceleration.y += self.GRAVITY

        # Applique la résistance de l'air
        air_resistance_force = -self.velocity * self.AIR_RESISTANCE
        self.sum_acceleration += air_resistance_force

        if self.on_ground:
            ground_resistance_force = -self.velocity * self.GROUND_RESISTANCE
            self.sum_acceleration += ground_resistance_force

        # Mise à jour de la vitesse et de la position.
        self.velocity += self.sum_acceleration * delta_time    # Acceleration en m/s^2
        self.rect.topleft += self.velocity * delta_time * 100    # Vitesse en m/s

        # Gestion des collisions avec les bords de l'écran
        physic.bord_collision(self.screen, self.rect, self.velocity)
        self.on_ground = self.rect.bottom>= self.screen.get_height()

        # Réinitialise l'accélération
        self.sum_acceleration = py.math.Vector2(0, 0)

class Player(Entity):
    def __init__(self, screen, joystick=None, start_pos=(50,20), mass=50, walk_force=500):
        super().__init__(screen, py.image.load("assets/player.png"), start_pos, mass)
        self.joystick = joystick

        self.mass = mass

        self.WALK_FORCE = walk_force    # En N
        self.JUMP_FORCE = 10000            # En N
        self.MAX_BOOST_AMOUNT = 100
        self.BOOST_POWER = 1.5          # En N

        self.boost_amount = self.MAX_BOOST_AMOUNT

    def update(self, dt):
        self.apply_force(self.get_input_vector()*self.WALK_FORCE)
        self.handle_input()
        if self.on_ground and self.boost_amount < self.MAX_BOOST_AMOUNT: self.boost_amount += dt * 10

        super().update(dt)


    def handle_input(self):
        if self.joystick:
            if self.joystick.get_button(1): self.boost()
        else:
            keys = py.key.get_pressed()
            if keys[py.K_LSHIFT]: self.boost()
        

    def get_input_vector(self):
        input_vector=py.Vector2(0,0)

        if self.joystick:
            input_vector.x = self.joystick.get_axis(0)  # Axe horizontal
            input_vector.y = self.joystick.get_axis(1)  # Axe vertical
        else:
            keys = py.key.get_pressed()
            if keys[py.K_q]: input_vector.x = -1
            if keys[py.K_d]: input_vector.x = 1
            if keys[py.K_z]: input_vector.y = -1
            if keys[py.K_s]: input_vector.y = 1
            if input_vector.length_squared() > 0: input_vector.normalize_ip()
        
        return input_vector

    def jump(self):
        # Le joueur saute uniquement s'il est au sol
        if self.on_ground:
            self.apply_force(py.math.Vector2(0, -self.JUMP_FORCE))
            self.on_ground = False
    
    def boost(self):
        if self.boost_amount > 0:
            self.apply_force(py.math.Vector2(0, -self.BOOST_POWER))
            self.boost_amount -= 0.5




class OtherPlayer(py.sprite.Sprite):
    def __init__(self, adress, name, start_pos, mass):
        super().__init__()
        self.image = py.image.load("assets/player.png")
        self.rect = self.image.get_rect()
        self.rect.topleft = start_pos


        # Constantes
        self.adress = adress
        self.name = name
        self.mass = mass

        # Variables
        self.velocity = py.Vector2(1,1)
