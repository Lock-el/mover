from pygame import Vector2

def resolve_collision(player1, player2):  
        # Calcul de la direction de la collision
        collision_vector = Vector2(player2.rect.center) - Vector2(player1.rect.center)
        collision_vector.normalize_ip()  # Normaliser la direction de la collision
        
        # Répartition de l'énergie cinétique après collision (en simplifiant)
        velocity1 = collision_vector * (get_kinetic_energy(player1.mass, player1.velocity) / (player1.mass + player2.mass))
        velocity2 = -collision_vector * (get_kinetic_energy(player2.mass, player2.velocity) / (player1.mass + player2.mass))
        
        return velocity1, velocity2


def get_kinetic_energy(mass, velocity):
    return 0.5 * mass * velocity.length_squared()