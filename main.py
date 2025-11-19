import pygame
import math
import random
import io
import sys

# try/except imports are common when sharing scripts just in case
try:
    import requests
except ImportError:
    print("You need the requests lib! (pip install requests)")
    sys.exit()

# Config
W, H = 800, 600
FPS = 60
CENTER = (W // 2, H // 2)
IMG_URL = "https://pngimg.com/d/thermos_PNG41.png"

# Quick palette
c_bg = (10, 10, 10)
c_white = (240, 240, 240)
c_green = (50, 200, 50)
c_btn_hover = (80, 220, 80)

def get_image(url):
    # Quick and dirty image downloader
    print(f"Fetching {url}...")
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        r.raise_for_status()
        img_data = io.BytesIO(r.content)
        surf = pygame.image.load(img_data)
        
        # scale it down to fit reasonably
        scale = 300 / surf.get_height()
        new_size = (int(surf.get_width() * scale), 300)
        return pygame.transform.smoothscale(surf, new_size)
        
    except Exception as e:
        print(f"Failed to grab image: {e}")
        # Just return a red placeholder square if it fails
        surf = pygame.Surface((200, 200))
        surf.fill((200, 50, 50))
        return surf

class Orb:
    def __init__(self, idx, total):
        self.angle = (idx / total) * (math.pi * 2)
        self.dist = 100
        self.base_r = random.randint(3, 6)
        self.r = self.base_r
        self.speed = 0.05
        
    def update(self, mode='spin'):
        if mode == 'spin':
            self.angle += self.speed
            # Add a little pulse effect
            pulse = math.sin(pygame.time.get_ticks() * 0.01 + self.angle)
            self.r = max(1, self.base_r + (pulse * 2))
            
        elif mode == 'implode':
            self.angle += self.speed * 3
            self.dist -= 3 # pull in
            if self.dist < 0: self.dist = 0

    def draw(self, screen):
        x = CENTER[0] + math.cos(self.angle) * self.dist
        y = CENTER[1] + math.sin(self.angle) * self.dist
        pygame.draw.circle(screen, c_white, (int(x), int(y)), int(self.r))

class Spark:
    def __init__(self):
        self.x, self.y = CENTER
        ang = random.uniform(0, 6.28)
        spd = random.uniform(2, 9)
        self.vel = [math.cos(ang) * spd, math.sin(ang) * spd]
        self.life = 255
        self.color = random.choice([(255, 255, 255), (255, 200, 50), (255, 100, 0)])
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vel[0]
        self.y += self.vel[1]
        self.life -= 6 # fade speed

    def draw(self, screen):
        if self.life <= 0: return
        
        # Making a new surface for alpha is slow, but fine for small particle counts
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, self.life), (self.size, self.size), self.size)
        screen.blit(s, (int(self.x)-self.size, int(self.y)-self.size))

def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    # Updated the caption per request
    pygame.display.set_caption("Zinate Mard")
    
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 28, bold=True)

    # Load assets upfront
    final_img = get_image(IMG_URL)
    img_rect = final_img.get_rect(center=CENTER)

    # Setup animation vars
    state = 'menu' # menu, spin, implode, explode, show
    
    # Button setup
    btn_rect = pygame.Rect(0, 0, 180, 50)
    btn_rect.center = CENTER
    
    orbs = []
    sparks = []
    spin_timer = 0

    running = True
    while running:
        dt = clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state == 'menu' and btn_rect.collidepoint((mx, my)):
                    state = 'spin'
                    spin_timer = pygame.time.get_ticks()
                    # Init orbs
                    orbs = [Orb(i, 12) for i in range(12)]

        # --- Draw & Update ---
        screen.fill(c_bg)

        if state == 'menu':
            # Draw button
            col = c_btn_hover if btn_rect.collidepoint((mx, my)) else c_green
            pygame.draw.rect(screen, col, btn_rect, border_radius=8)
            
            # Add the text above the button
            title_lbl = font.render("Zinate Mard Chist?", True, c_white)
            # Position it 40 pixels above the button top
            title_rect = title_lbl.get_rect(center=(CENTER[0], btn_rect.top - 40))
            screen.blit(title_lbl, title_rect)

            # Button Label (Changed from Run Demo to Start)
            lbl = font.render("Start", True, c_white)
            screen.blit(lbl, lbl.get_rect(center=btn_rect.center))

        elif state == 'spin':
            for o in orbs:
                o.update('spin')
                o.draw(screen)
            
            if pygame.time.get_ticks() - spin_timer > 2500: # 2.5s wait
                state = 'implode'

        elif state == 'implode':
            center_hit = True
            for o in orbs:
                o.update('implode')
                o.draw(screen)
                if o.dist > 2: center_hit = False
            
            if center_hit:
                state = 'explode'
                # Boom!
                sparks = [Spark() for _ in range(80)]
                screen.fill((255, 255, 255)) # flash frame

        elif state == 'explode':
            # Filter out dead sparks
            sparks = [s for s in sparks if s.life > 0]
            
            for s in sparks:
                s.update()
                s.draw(screen)
                
            if not sparks:
                state = 'show'

        elif state == 'show':
            screen.blit(final_img, img_rect)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
