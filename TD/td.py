import pygame
import random
import sys

# Pygame initialisieren
pygame.init()
pygame.font.init()
font = pygame.font.Font(None, 50)

WIDTH = 1280
HEIGHT = 780
WINDOW_TITLE = "Tower Defense"
FPS = 60

TOWER_STATS = {
    1: {"radius": 100, "damage": 1, "cooldown": 30, "upgrade_cost": 150},
    2: {"radius": 120, "damage": 2, "cooldown": 25, "upgrade_cost": 250},
    3: {"radius": 140, "damage": 3, "cooldown": 20, "upgrade_cost": None},  # Max level
}
tower_levels = []

def upgrade_tower(index):
    level = tower_levels[index]
    if level < 3:
        cost = TOWER_STATS[level]["upgrade_cost"]
        if money >= cost:
            tower_levels[index] += 1
            return cost
    return 0

BLOON_TILES = {
    "green": {"tile": (15, 10), "health": 3},
    "blue": {"tile": (16, 10), "health": 5},
    "red": {"tile": (17, 10), "health": 7},
    "air": {"tile": (18, 10), "health": 10},  # New air bloon
}

# Spielfenster erstellen
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)
pygame.display.set_caption(WINDOW_TITLE)

# Clock für FPS-Begrenzung
clock = pygame.time.Clock()

delay = 0
health_icon = pygame.image.load("health.png").convert_alpha()
money_icon = pygame.image.load("money_icon.png").convert_alpha()
tilesheet = pygame.image.load("towerDefense_tilesheet.png").convert_alpha()
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
money = 1000
wave = 1
    

AirTowers = []
air_tower_cooldowns = []

def get_tile(col, row):
    """Gibt ein Surface mit dem Tile in Spalte col, Zeile row zurück."""
    rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    image.blit(tilesheet, (0, 0), rect)
    return image

DEBUG = True
checkpoints = [ [525, HEIGHT/2-80], [525, HEIGHT/2-170], [835, HEIGHT/2-170], [835, HEIGHT/2-80], [1280, HEIGHT/2-80] ]
def RenderPath():
    if DEBUG == True:
        for checkpoint in checkpoints:
            pygame.draw.rect(screen, "cyan", pygame.Rect(checkpoint[0], checkpoint[1], 50, 50), 5, 5)

BloonsData = []  # [x, y, checkpoint, alive]
movingspeed = 1
bloondistance = 100
spawnedStatus = False

waveData = [
    [],
    ["blue", "green", "green", "blue"],
    ["green", "blue", "green", "blue", "green", "blue", "green", "blue", "green", "blue"],
    ["red", "red", "red", "red", "red", "red", "red", "red"],
    ["air", "air", "air", "air", "air", "air"],
    ["air", "red", "air", "red", "air", "red", "air", "red", "air",  "red", "air"],
    ["red", "red", "red", "red", "red", "red", "red", "red", "red", "red", "red", "red", "red", "red", "red", "red", "red", "red", "red", "red", "red", "red", "red", "red"],
    ["air", "red", "air", "red", "air", "red", "air", "red", "air",  "red", "air", "air", "red", "air", "red", "air", "red", "air", "red", "air",  "red", "air", "air", "red", "air", "red", "air", "red", "air", "red", "air",  "red", "air"],
    ]

def SpawnBloons():
    global BloonsData, bloonCounter, bloondistance, spawnedStatus, movingspeed, wave
    if not spawnedStatus:
        for bloon in range(len(waveData[wave])):
            # btype for the current bloon
            
            btype = waveData[wave][bloon]
            
            tile_col, tile_row = BLOON_TILES[btype]["tile"]  # Get tile position
            hp = int(BLOON_TILES[btype]["health"])
            BloonsData.append([0-(bloon*bloondistance), HEIGHT/2-80, 1, True, btype, hp])
        spawnedStatus = True

tower_cooldowns = []  # One cooldown per tower
tower_pop_delay = 30  # Frames between pops

def TowerRadius():
    global Towers, AirTowers, tower_size, screen, Bloons, tower_cooldowns, air_tower_cooldowns
    surf = pygame.Surface((TILE_SIZE*2, TILE_SIZE*2), pygame.SRCALPHA)

    # Regular towers
    mouse_x, mouse_y = pygame.mouse.get_pos()
    for i, tower in enumerate(Towers):
        tower_cx = tower[0] + tower_size/2
        tower_cy = tower[1] + tower_size/2
        level = tower_levels[i]
        stats = TOWER_STATS[level]
        radius = stats["radius"]

        blit_pos = (tower_cx - radius, tower_cy - radius)
        surf.fill((0, 0, 0, 0))
        tower_x, tower_y = tower
        tower_rect = pygame.Rect(tower_x, tower_y, tower_size, tower_size)
        if tower_rect.collidepoint(mouse_x, mouse_y):
            tower_cx = tower_x + tower_size // 2
            tower_cy = tower_y + tower_size // 2
            level = tower_levels[i]
            radius = TOWER_STATS[level]["radius"]

            # Erzeuge eine transparente Oberfläche
            radius_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                radius_surf,
                (100, 100, 100, 100),  # Transparenter Grauton
                (radius, radius),
                radius
            )
            screen.blit(radius_surf, (tower_cx - radius, tower_cy - radius))
        screen.blit(surf, blit_pos)

        if tower_cooldowns[i] == 0:
            for bloonRect, bloonData in Bloons:
                if not bloonData[3]:
                    continue
                if bloonData[4] == "air":
                    continue
                closest_x = max(bloonRect.x, min(tower_cx, bloonRect.x + bloonRect.width))
                closest_y = max(bloonRect.y, min(tower_cy, bloonRect.y + bloonRect.height))
                dx = tower_cx - closest_x
                dy = tower_cy - closest_y
                if dx*dx + dy*dy <= radius*radius:
                    bloonData[5] -= stats["damage"]
                    if bloonData[5] <= 0:
                        bloonData[3] = False
                    tower_cooldowns[i] = stats["cooldown"]
                    break

    # Air towers
    for i, tower in enumerate(AirTowers):
        tower_cx = tower[0] + tower_size/2
        tower_cy = tower[1] + tower_size/2
        radius = TOWER_STATS[1]["radius"]  # Assuming air towers always have fixed radius
        blit_pos = (tower_cx - radius, tower_cy - radius)
        surf.fill((0, 0, 0, 0))
        pygame.draw.circle(
            surf,
            (20, 20, 20, 20),
            (radius, radius),
            radius
        )
        screen.blit(surf, blit_pos)

        if air_tower_cooldowns[i] == 0:
            for bloonRect, bloonData in Bloons:
                if not bloonData[3]:
                    continue
                if bloonData[4] != "air":
                    continue
                closest_x = max(bloonRect.x, min(tower_cx, bloonRect.x + bloonRect.width))
                closest_y = max(bloonRect.y, min(tower_cy, bloonRect.y + bloonRect.height))
                dx = tower_cx - closest_x
                dy = tower_cy - closest_y
                if dx*dx + dy*dy <= radius*radius:
                    bloonData[5] -= 1
                    if bloonData[5] <= 0:
                        bloonData[3] = False
                    air_tower_cooldowns[i] = tower_pop_delay
                    break

    for j in range(len(tower_cooldowns)):
        if tower_cooldowns[j] > 0:
            tower_cooldowns[j] -= 1
    for j in range(len(air_tower_cooldowns)):
        if air_tower_cooldowns[j] > 0:
            air_tower_cooldowns[j] -= 1


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

            bloonRect = pygame.Rect(bloon[0], bloon[1], TILE_SIZE, TILE_SIZE)
            bloon_type = bloon[4]
            tile_col, tile_row = BLOON_TILES[bloon_type]["tile"]  # Get tile position
            bloon_tile = get_tile(tile_col, tile_row)
            screen.blit(bloon_tile, (bloon[0], bloon[1]))

            # Display health above the bloon if DEBUG is True
            if DEBUG:
                health_text = font.render(str(bloon[5]), True, "white")
                screen.blit(health_text, (bloon[0] + TILE_SIZE // 4, bloon[1] - 20))



            Bloons.append((bloonRect, bloon))  # Store both rect and data ref

def place_tiles(tile, x_start, x_end, y_start, y_end, step_x=TILE_SIZE, step_y=TILE_SIZE):
    """
    Draws the given tile in a rectangle from (x_start, y_start) to (x_end, y_end).
    """
    for x in range(x_start, x_end, step_x):
        for y in range(y_start, y_end, step_y):
            screen.blit(tile, (x, y))

def get_number_tile(digit):
    return get_tile(digit, 11)

def drawMoney():
    global money_icon
    money_icon = pygame.transform.scale(money_icon, (50, 30))
    screen.blit(money_icon, (10, 10))
    ModeText = font.render(f'{money}', True, "black")
    screen.blit(ModeText, (80, 10))
    drawHealth()
    
def drawHealth():
    global health_icon
    health_icon = pygame.transform.scale(health_icon, (50, 50))
    screen.blit(health_icon, (10, 70))
    ModeText = font.render(f'{health}', True, "black")
    screen.blit(ModeText, (80, 70))


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
SIDEBAR_WIDTH = 200
sidebar_rect = pygame.Rect(WIDTH - SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, HEIGHT)
tower_icon_rect = pygame.Rect(WIDTH - SIDEBAR_WIDTH + 50, 100, 64, 64)  # Example position for tower icon
air_tower_icon_rect = pygame.Rect(WIDTH - SIDEBAR_WIDTH + 50, 200, 64, 64)  # Position for air tower icon

dragging_tower = False
drag_offset = (0, 0)
dragged_tower_pos = (0, 0)
dragging_air_tower = False  # Initialize dragging_air_tower

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
                        tower_cooldowns.append(0)
                        tower_levels.append(1)
                        tower_cooldowns.append(0)  # Add cooldown for new tower
                        print("Positions Changed!", Towers)
                        money -= 200
                    else:
                        print("No money to buy the tower! Current Money:",money)
            elif event.key == pygame.K_t:  # Press 'T' to place an air tower
                if money >= 300:  # Air towers cost more
                    AirTowers.append([player_x, player_y])
                    air_tower_cooldowns.append(0)  # Add cooldown for new air tower
                    money -= 300
                    print("Air tower placed!")
                else:
                    print("Not enough money for air tower!")
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if tower_icon_rect.collidepoint(mx, my):
                dragging_tower = True
                drag_offset = (mx - tower_icon_rect.x, my - tower_icon_rect.y)
                dragged_tower_pos = (mx - drag_offset[0], my - drag_offset[1])
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # Right-click to upgrade
                mx, my = pygame.mouse.get_pos()
                for i, tower in enumerate(Towers):
                    tx, ty = tower
                    if tx < mx < tx + tower_size and ty < my < ty + tower_size:
                        cost = upgrade_tower(i)
                        if cost > 0:
                            money -= cost
                            print(f"Tower {i} upgraded to level {tower_levels[i]}")
                        else:
                            print("Upgrade failed or max level reached")
        if event.type == pygame.MOUSEBUTTONUP:
            if dragging_tower:
                mx, my = pygame.mouse.get_pos()
                if mx < WIDTH - SIDEBAR_WIDTH and money >= (300 if dragging_air_tower else 200):
                    if dragging_air_tower:
                        AirTowers.append([mx - tower_size // 2, my - tower_size // 2])
                        air_tower_cooldowns.append(0)
                        money -= 300
                        print("Air tower placed!")
                    else:
                        Towers.append([mx - tower_size // 2, my - tower_size // 2])
                        tower_cooldowns.append(0)
                        tower_levels.append(1)  # <- WICHTIGER FIX
                        money -= 200
                        print("Regular tower placed!")
                dragging_tower = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if tower_icon_rect.collidepoint(mx, my):  # Regular tower icon
                dragging_tower = True
                drag_offset = (mx - tower_icon_rect.x, my - tower_icon_rect.y)
                dragged_tower_pos = (mx - drag_offset[0], my - drag_offset[1])
                dragging_air_tower = False
            elif air_tower_icon_rect.collidepoint(mx, my):  # Air tower icon
                dragging_tower = True
                drag_offset = (mx - air_tower_icon_rect.x, my - air_tower_icon_rect.y)
                dragged_tower_pos = (mx - drag_offset[0], my - drag_offset[1])
                dragging_air_tower = True

        if event.type == pygame.MOUSEBUTTONUP:
            if dragging_tower:
                mx, my = pygame.mouse.get_pos()
                if mx < WIDTH - SIDEBAR_WIDTH and money >= (300 if dragging_air_tower else 200):  # Check money for air or regular tower
                    if dragging_air_tower:
                        AirTowers.append([mx - tower_size // 2, my - tower_size // 2])
                        air_tower_cooldowns.append(0)
                        money -= 300
                        print("Air tower placed!")
                    else:
                        Towers.append([mx - tower_size // 2, my - tower_size // 2])
                        tower_cooldowns.append(0)
                        money -= 200
                        print("Regular tower placed!")
                dragging_tower = False
        if event.type == pygame.MOUSEMOTION:
            if dragging_tower:
                mx, my = pygame.mouse.get_pos()
                dragged_tower_pos = (mx - drag_offset[0], my - drag_offset[1])
                
    screen.fill("black")

    bg_tile = get_tile(19, 6)
    place_tiles(bg_tile, 0, WIDTH, 0, HEIGHT)

    road_tile = get_tile(21, 6)
    place_tiles(road_tile, 0, 300, 295, 360)
    place_tiles(road_tile, 208, 465, 420, 520)
    place_tiles(road_tile, 400, 465, 100, 370)
    place_tiles(road_tile, 400, 1040, 100, 200)
    place_tiles(road_tile, 915, WIDTH, 295, 360)
    place_tiles(road_tile, 915, 1000, 200, 360)

    plant_tile = get_tile(15, 5)
    place_tiles(plant_tile, 100, 150, 100, 150)

    rock_tile = get_tile(22, 5)
    place_tiles(rock_tile, 300, 350, 100, 150)
        
    RenderPath()
    bloonsMoving()
    TowerRadius()
    checkBloonStatus()
    drawMoney()

    # Draw sidebar
    pygame.draw.rect(screen, (40, 40, 40), sidebar_rect)

    # Regular tower icon
    pygame.draw.rect(screen, (100, 100, 100), tower_icon_rect)
    tower_icon_img = get_tile(19, 10)
    screen.blit(tower_icon_img, tower_icon_rect.topleft)

    # Air tower icon
    pygame.draw.rect(screen, (100, 100, 100), air_tower_icon_rect)
    air_tower_icon_img = get_tile(22, 8)  # Example tile for air tower
    screen.blit(air_tower_icon_img, air_tower_icon_rect.topleft)

    # Draw dragging tower
    if dragging_tower:
        if dragging_air_tower:
            screen.blit(air_tower_icon_img, dragged_tower_pos)
        else:
            screen.blit(tower_icon_img, dragged_tower_pos)

    # Draw towers (skip if dragging, so it doesn't overlap)
    for tower in Towers:
        tower_tile = get_tile(19, 10)
        screen.blit(tower_tile, (tower[0], tower[1]))

    for tower in AirTowers:
        air_tower_tile = get_tile(22, 8)  # Example tile for air tower
        screen.blit(air_tower_tile, (tower[0], tower[1]))

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
