from pygame import Vector2

def resolve_collision(player1, player2):  
        # Calcul de la direction de la collision
        collision_vector = Vector2(player2.rect.center) - Vector2(player1.rect.center)
        collision_vector.normalize_ip()  # Normaliser la direction de la collision
        
        # Répartition de l'énergie cinétique après collision (en simplifiant)
        velocity1 = collision_vector * (get_kinetic_energy(player1.mass, player1.velocity) / (player1.mass + player2.mass))
        velocity2 = -collision_vector * (get_kinetic_energy(player2.mass, player2.velocity) / (player1.mass + player2.mass))
        
        return velocity1, velocity2

def bord_collision(screen, r, v):
      # Bord collide
        if r.top<0: 
            r.top=0
            v.y=0
        elif r.bottom>screen.get_height(): 
            r.bottom=screen.get_height()
            v.y=0
        if r.left<0: 
            r.left=0
            v.x=0
        elif r.right>screen.get_width(): 
            r.right=screen.get_width()
            v.x=0

def get_acceleration(force, mass):  # F=m*a
    return force/mass

def get_kinetic_energy(mass, velocity):
    return 0.5 * mass * velocity.length_squared()