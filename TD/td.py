import pygame
import random
import sys

# Pygame initialisieren
pygame.init()
pygame.font.init()
font = pygame.font.Font(None, 50)

# Konstanten
WIDTH = 1280
HEIGHT = 780
WINDOW_TITLE = "Tower Defense"
FPS = 60

# Farben
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

BLOON_TYPES = {
    "green": ((0, 255, 0), 1),
    "blue": ((0, 0, 255), 2),
    "red": ((255, 0, 0), 3),
}

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
health = 100
money = 200
wave = 1
    

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
bloonCounter = 2
movingspeed = 6
bloondistance = 100
spawnedStatus = False

def SpawnBloons():
    global BloonsData, bloonCounter, bloondistance, spawnedStatus, movingspeed, wave
    if not spawnedStatus:
        bloonCounter *= wave
        for bloon in range(bloonCounter):
            # Alternate types for demo: green, blue, red
            if bloon % 3 == 0:
                btype = "green"
            elif bloon % 3 == 1:
                btype = "blue"
            else:
                btype = "red"
            color, hp = BLOON_TYPES[btype]
            BloonsData.append([0-(bloon*bloondistance), HEIGHT/2-80, 1, True, btype, hp])
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
            (20, 20, 20, 20),
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
                    bloonData[5] -= 1  # Reduce HP
                    if bloonData[5] <= 0:
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

def checkBloonStatus():
    global spawnedStatus, wave, money
    for bloon in BloonsData:
        if bloon[0] > 1200:
            bloon[3] = False
    
    
    counter1 = 0
    for bloon in BloonsData:
        counter1 += 1
    counter = 0
    for bloon in BloonsData:
        if bloon[3] == False:
            counter += 1
    if counter == counter1:
        spawnedStatus = False
        wave +=1
        money += 200*wave
        print("respawning Bloon")

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
            color = BLOON_TYPES[bloon[4]][0]
            pygame.draw.rect(screen, color, bloonRect)
            # Draw HP as text
            hp_text = font.render(str(bloon[5]), True, (255,255,255))
            screen.blit(hp_text, (bloon[0]+10, bloon[1]+10))
            Bloons.append((bloonRect, bloon))  # Store both rect and data ref


createCheckpoint(0, HEIGHT/2-60)
createCheckpoint(250, HEIGHT/2-60)
createCheckpoint(250, HEIGHT/2+80)
createCheckpoint(430, HEIGHT/2+80)
createCheckpoint(430, HEIGHT/2-260)
createCheckpoint(950, HEIGHT/2-260)
createCheckpoint(950, HEIGHT/2-60)
createCheckpoint(1280, HEIGHT/2-60)

def drawMoney():
    ModeText = font.render(f'$: {money}', True, "white")
    screen.blit(ModeText, (10, 10))

Towers = []
renderplacer = False
SIDEBAR_WIDTH = 200
sidebar_rect = pygame.Rect(WIDTH - SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, HEIGHT)
tower_icon_rect = pygame.Rect(WIDTH - SIDEBAR_WIDTH + 50, 100, 64, 64)  # Example position for tower icon

dragging_tower = False
drag_offset = (0, 0)
dragged_tower_pos = (0, 0)

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
                if (((player_y >= 290) and (player_y <= 390) and (player_x <= 290)) or (( player_y <= 520) and (player_y >= 420) and (player_x <= 500) and (player_x >= 210)) or ((player_y >= 100) and (player_y <= 400) and (player_x >= 400) and (player_x <= 500)) or ((player_y >= 100) and (player_y <= 200) and (player_x >= 520) and (player_x <= 1015)) or ((player_y >= 300) and (player_y <= 400) and (player_x >= 915))):
                    print("unable to place the Tower")
                else:
                    if money >= 200:
                        Towers.append([player_x, player_y])
                        tower_cooldowns.append(0)  # Add cooldown for new tower
                        print("Positions Changed!", Towers)
                        money -= 200
                    else:
                        print("No money to buy the tower! Current Money:",money)
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if tower_icon_rect.collidepoint(mx, my):
                dragging_tower = True
                drag_offset = (mx - tower_icon_rect.x, my - tower_icon_rect.y)
                dragged_tower_pos = (mx - drag_offset[0], my - drag_offset[1])
        if event.type == pygame.MOUSEBUTTONUP:
            if dragging_tower:
                mx, my = pygame.mouse.get_pos()
                # Only place if not in sidebar and enough money
                if mx < WIDTH - SIDEBAR_WIDTH and money >= 200:
                    Towers.append([mx - tower_size // 2, my - tower_size // 2])
                    tower_cooldowns.append(0)
                    money -= 200
                dragging_tower = False
        if event.type == pygame.MOUSEMOTION:
            if dragging_tower:
                mx, my = pygame.mouse.get_pos()
                dragged_tower_pos = (mx - drag_offset[0], my - drag_offset[1])

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
    
    plant_tile = get_tile(15, 5)  # Beispiel: Tile aus Spalte 1, Zeile 2
    for x in range(100, 150, TILE_SIZE):
        for y in range(100, 150, TILE_SIZE):
            screen.blit(plant_tile, (x, y))
    
    rock_tile = get_tile(22, 5)  # Beispiel: Tile aus Spalte 1, Zeile 2
    for x in range(300, 350, TILE_SIZE):
        for y in range(100, 150, TILE_SIZE):
            screen.blit(rock_tile, (x, y))
            
    RenderPath()
    bloonsMoving()
    TowerRadius()
    checkBloonStatus()
    drawMoney()

    # Draw sidebar
    pygame.draw.rect(screen, (40, 40, 40), sidebar_rect)
    pygame.draw.rect(screen, (100, 100, 100), tower_icon_rect)
    tower_icon_img = get_tile(19, 10)
    screen.blit(tower_icon_img, tower_icon_rect.topleft)

    # Draw dragging tower
    if dragging_tower:
        screen.blit(tower_icon_img, dragged_tower_pos)

    # Draw towers (skip if dragging, so it doesn't overlap)
    for tower in Towers:
        tower_tile = get_tile(19, 10)
        screen.blit(tower_tile, (tower[0], tower[1]))

    ModeText = font.render(f'Menu: {menu}', True, "white")
    screen.blit(ModeText, (WIDTH/2-100, 10))
    if delay > 0:
        delay -= 1

    if menu == "Game":
        pass
 
    for tower in Towers:
        tower_tile = get_tile(19, 10)  # Beispiel: Tile aus Spalte 1, Zeile 2
        for x in range(tower[0], tower[0]+1, TILE_SIZE):
            for y in range(tower[1], tower[1]+1, TILE_SIZE):
                screen.blit(tower_tile, (x, y))

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
