import pygame
import sys

# Pygame initialisieren
pygame.init()
pygame.font.init()
font = pygame.font.Font(None, 50)

# Konstanten
WIDTH = 1280
HEIGHT = 780
WINDOW_TITLE = "Mein Pygame Spiel"
FPS = 60

# Farben
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Spielfenster erstellen
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)
pygame.display.set_caption(WINDOW_TITLE)

# Clock für FPS-Begrenzung
clock = pygame.time.Clock()

delay = 0

tilesheet = pygame.image.load("TD/towerDefense_tilesheet.png").convert_alpha()
TILE_SIZE = 64  # passe das an deine Tilesheet-Größe an

# Spieler (als Beispiel)
player_x = WIDTH // 2
player_y = HEIGHT // 2
player_size = 30
tower_size = 40
player_speed = 5
menu = "Game"
Bloons = []

def get_tile(col, row):
    """Gibt ein Surface mit dem Tile in Spalte col, Zeile row zurück."""
    rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    image.blit(tilesheet, (0, 0), rect)
    return image

DEBUG = False
checkpoints = [ [525, HEIGHT/2-80], [525, HEIGHT/2-170], [835, HEIGHT/2-170], [835, HEIGHT/2-80], [1280, HEIGHT/2-80] ]
def RenderPath():
    if DEBUG == True:
        for checkpoint in checkpoints:
            pygame.draw.rect(screen, "cyan", pygame.Rect(checkpoint[0], checkpoint[1], 50, 50), 5, 5)

BloonsData = []  # Each bloon: [x, y, checkpoint, alive]
bloonCounter = 20
movingspeed = 5
bloondistance = 100
spawnedStatus = False

def SpawnBloons():
    global BloonsData, bloonCounter, bloondistance, spawnedStatus
    if not spawnedStatus:
        for bloon in range(bloonCounter):
            BloonsData.append([0-(bloon*bloondistance), HEIGHT/2-80, 1, True])
        spawnedStatus = True

# Add this near where you define Towers
tower_cooldowns = []  # One cooldown per tower
tower_pop_delay = 30  # Frames between pops

def TowerRadius():
    global Towers, tower_size, screen, Bloons, tower_cooldowns
    radius = 100
    surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)

    for i, tower in enumerate(Towers):
        tower_cx = tower[0] + tower_size/2
        tower_cy = tower[1] + tower_size/2
        blit_pos = (tower_cx - radius, tower_cy - radius)
        surf.fill((0, 0, 0, 0))
        pygame.draw.circle(
            surf,
            (128, 128, 128, 128),
            (radius, radius),
            radius
        )
        screen.blit(surf, blit_pos)

        if tower_cooldowns[i] == 0:
            for bloonRect, bloonData in Bloons:
                if not bloonData[3]:  # Already dead
                    continue
                closest_x = max(bloonRect.x, min(tower_cx, bloonRect.x + bloonRect.width))
                closest_y = max(bloonRect.y, min(tower_cy, bloonRect.y + bloonRect.height))
                dx = tower_cx - closest_x
                dy = tower_cy - closest_y
                if dx*dx + dy*dy <= radius*radius:
                    print(f"Bloon {bloonRect} popped!")
                    bloonData[3] = False  # Mark as dead
                    tower_cooldowns[i] = tower_pop_delay
                    break

    for j in range(len(tower_cooldowns)):
        if tower_cooldowns[j] > 0:
            tower_cooldowns[j] -= 1


checkpoints = []
checkpoint_movers = []

def createCheckpoint(x, y):
    checkpoints.append([x, y])
    checkpoint_movers.append(createCheckpointMover(len(checkpoints) - 1))

def createCheckpointMover(checkpoint_idx):
    """
    Gibt eine Funktion zurück, die ein Bloon zu einem bestimmten Checkpoint bewegt.
    """
    def mover(bloon, checkpoints, movingspeed):
        cx, cy = checkpoints[checkpoint_idx]
        dx = cx - bloon[0]
        dy = cy - bloon[1]
        # Nur bewegen, wenn noch nicht am Ziel
        if dx != 0:
            step = min(abs(dx), movingspeed) * (1 if dx > 0 else -1)
            bloon[0] += step
        elif dy != 0:
            step = min(abs(dy), movingspeed) * (1 if dy > 0 else -1)
            bloon[1] += step
        if bloon[0] == cx and bloon[1] == cy:
            bloon[2] += 1
    return mover

checkpoint_movers = [createCheckpointMover(i) for i in range(len(checkpoints))]

def bloonsMoving():
    global BloonsData, Bloons
    SpawnBloons()
    Bloons = []
    if spawnedStatus:
        for bloon in BloonsData:
            if not bloon[3]:  # Skip dead bloons
                continue
            try:
                idx = bloon[2] - 1
                if 0 <= idx < len(checkpoint_movers):
                    checkpoint_movers[idx](bloon, checkpoints, movingspeed)
            except:
                pass

            bloonRect = pygame.Rect(bloon[0], bloon[1], 50, 50)
            pygame.draw.rect(screen, "green", bloonRect)
            Bloons.append((bloonRect, bloon))  # Store both rect and data ref

createCheckpoint(0, HEIGHT/2-60)
createCheckpoint(250, HEIGHT/2-60)
createCheckpoint(250, HEIGHT/2+80)
createCheckpoint(430, HEIGHT/2+80)
createCheckpoint(430, HEIGHT/2-260)
createCheckpoint(950, HEIGHT/2-260)
createCheckpoint(950, HEIGHT/2-60)
createCheckpoint(1280, HEIGHT/2-60)



Towers = []
renderplacer = False
running = True
while running:
    # Ereignisse verarbeiten
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if (menu == "Game") and event.key == pygame.K_SPACE and (delay <= 0):
                menu = "Edit"
                renderplacer = True
                delay = 10
                print("Switched to", menu)
            elif (menu == "Edit") and event.key == pygame.K_SPACE and (delay <= 0):
                menu = "Game"
                renderplacer = False
                delay = 10
                print("Switched to", menu)
            elif (menu == "Edit") and event.key == pygame.K_RETURN and (delay <= 0):
                delay = 10
                if (((player_y >= 290) and (player_y <= 360) and (player_x <= 570)) or (( player_y <= 260) and (player_y >= 190) and (player_x <= 870) and (player_x >= 500)) or ((player_y >= 290) and (player_y <= 360) and (player_x >= 800))):
                    print("unable to place the Tower")
                else:
                    Towers.append([player_x, player_y])
                    tower_cooldowns.append(0)  # Add cooldown for new tower
                    print("Positions Changed!", Towers)


    screen.fill("black")

    bg_tile = get_tile(19, 6)  # Beispiel: Tile aus Spalte 1, Zeile 2
    for x in range(0, WIDTH, TILE_SIZE):
        for y in range(0, HEIGHT, TILE_SIZE):
            screen.blit(bg_tile, (x, y))

    road_tile = get_tile(21, 6)  # Beispiel: Tile aus Spalte 1, Zeile 2
    for x in range(0, 300, TILE_SIZE):
        for y in range(295, 360, TILE_SIZE):
            screen.blit(road_tile, (x, y))
    for x in range(208, 465, TILE_SIZE):
        for y in range(420, 520, TILE_SIZE):
            screen.blit(road_tile, (x, y))
    for x in range(400, 465, TILE_SIZE):
        for y in range(100, 370, TILE_SIZE):
            screen.blit(road_tile, (x, y))
    for x in range(400, 1040, TILE_SIZE):
        for y in range(100, 200, TILE_SIZE):
            screen.blit(road_tile, (x, y))
    for x in range(915, WIDTH, TILE_SIZE):
        for y in range(295, 360, TILE_SIZE):
            screen.blit(road_tile, (x, y))
    for x in range(915, 1000, TILE_SIZE):
        for y in range(200, 360, TILE_SIZE):
            screen.blit(road_tile, (x, y))


    RenderPath()
    bloonsMoving()
    TowerRadius()

    ModeText = font.render(f'Menu: {menu}', True, "white")
    screen.blit(ModeText, (WIDTH/2-100, 10))
    if delay > 0:
        delay -= 1

    if menu == "Game":
        pass

    for tower in Towers:
        pygame.draw.rect(screen, "blue", (tower[0], tower[1], tower_size, tower_size))

    if renderplacer == True:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            player_x -= player_speed
        if keys[pygame.K_d]:
            player_x += player_speed
        if keys[pygame.K_w]:
            player_y -= player_speed
        if keys[pygame.K_s]:
            player_y += player_speed
        if keys[pygame.K_LEFT]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_x += player_speed
        if keys[pygame.K_UP]:
            player_y -= player_speed
        if keys[pygame.K_DOWN]:
            player_y += player_speed
        
        player_x = max(0, min(player_x, WIDTH - player_size))
        player_y = max(0, min(player_y, HEIGHT - player_size))
        
        pygame.draw.rect(screen, "red", (player_x, player_y, player_size, player_size))


    pygame.display.flip()
    
    clock.tick(FPS)

pygame.quit()
sys.exit()