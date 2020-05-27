import pygame
from astar_algo import astar
import random

pygame.init()

screen_width = 800
screen_height = 400
win = pygame.display.set_mode([screen_width,screen_height])

score=0
difficulty_level=1
fps=18

pygame.display.set_caption(("Peter Pew Pew"))

clock=pygame.time.Clock()

walkUp=[pygame.image.load('img/sprite1-1.tiff'), pygame.image.load('img/sprite1-2.tiff'), pygame.image.load('img/sprite1-3.tiff')]
walkRight=[pygame.image.load('img/sprite2-1.tiff'),pygame.image.load('img/sprite2-2.tiff'),pygame.image.load('img/sprite2-3.tiff')]
walkLeft=[pygame.image.load('img/sprite3-1.tiff'),pygame.image.load('img/sprite3-2.tiff'),pygame.image.load('img/sprite3-3.tiff')]
walkDown=[pygame.image.load('img/sprite4-1.tiff'),pygame.image.load('img/sprite4-2.tiff'),pygame.image.load('img/sprite4-3.tiff')]

class player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image=pygame.image.load('img/sprite1-1.tiff').convert()
        self.rect=self.image.get_rect()
        self.vel=0
        self.left=False
        self.right=False
        self.up=False
        self.down=False
        self.moveCount=0
        self.mask=None

    def draw(self,win):
        if self.moveCount+1>=9:
            self.moveCount=0

        if self.left:
            win.blit(walkLeft[self.moveCount//3],(self.rect.x,self.rect.y))
            self.image=walkLeft[self.moveCount//3]
            self.moveCount+=1
        elif self.right:
            win.blit(walkRight[self.moveCount//3],(self.rect.x,self.rect.y))
            self.image=walkRight[self.moveCount//3]
            self.moveCount+=1
        elif self.up:
            win.blit(walkUp[self.moveCount//3],(self.rect.x,self.rect.y))
            self.image=walkUp[self.moveCount//3]
            self.moveCount+=1
        elif self.down:
            win.blit(walkDown[self.moveCount//3],(self.rect.x,self.rect.y))
            self.image=walkDown[self.moveCount//3]
            self.moveCount+=1
        else:
            pass

eWalkRight=[pygame.image.load('img/enemy1-1.tiff'),pygame.image.load('img/enemy1-2.tiff'),pygame.image.load('img/enemy1-3.tiff')]
eWalkLeft=[pygame.image.load('img/enemy2-1.tiff'),pygame.image.load('img/enemy2-2.tiff'),pygame.image.load('img/enemy2-3.tiff')]

class enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('img/enemy1-1.tiff').convert()
        self.vel=0
        self.rect=self.image.get_rect()
        self.goal_node=[0,0]
        self.gridloc=[0,0]
        self.mask=None
        self.alive=True
        self.health=3
        self.hitbox=(self.rect.x+7,self.rect.y+2,10,30)
        self.right=False
        self.left=False
        self.up=False
        self.down=False
        self.last_move='none'
        self.moveCount=0

    def update(self):
        """updates new posiiton of sprite"""
        if self.right:
            self.rect.x += self.vel
            self.last_move='right'
        elif self.left:
            self.rect.x -= self.vel
            self.last_move='left'
        elif self.up:
            self.rect.y -= self.vel
            self.last_move='up'
        elif self.down:
            self.rect.y += self.vel
            self.last_move='down'
        else:
            pass

        self.gridloc = [self.rect.x//50,self.rect.y//50]
        self.goal_node=[pac.rect.x//50,pac.rect.y//50]

    def draw(self, win):
        """drawing the new position of the sprite and its healthbar"""
        if self.alive:
            #win.blit(self.image, [self.rect.x, self.rect.y])
            if self.moveCount+1>=9:
                self.moveCount=0

            if self.gridloc[0]>=self.goal_node[0]:
                win.blit(eWalkLeft[self.moveCount//3],(self.rect.x,self.rect.y))
                self.image=eWalkLeft[self.moveCount//3]
                self.moveCount+=1
            elif self.gridloc[0]<=self.goal_node[0]:
                win.blit(eWalkRight[self.moveCount//3],(self.rect.x,self.rect.y))
                self.image=eWalkRight[self.moveCount//3]
                self.moveCount+=1
            else:
                pass

            #draw healthbar
            pygame.draw.rect(win,(255,0,0),(self.hitbox[0],self.hitbox[1]-20,30,10))
            pygame.draw.rect(win,(0,255,0),(self.hitbox[0],self.hitbox[1]-20,30-(10*(3-self.health)),10))
            self.hitbox=(self.rect.x+7,self.rect.y+2,10,30)

    def hit(self):
        """"reducing the health of sprite if hit by bullet and checks if it is still alive after being hit"""
        if self.health>0:
            self.health-=1
        else:
            global score
            self.alive=False
            score+=1

max_bullets=6
class projectiles():
    """bullets that will come out of the player sprite"""
    def __init__(self,x,y,left,right,up,down,back):
        self.colour=(0,255,0)
        self.x=x
        self.y=y
        self.radius=6
        self.left=left
        self.right=right
        self.up=up
        self.down=down
        self.rect=None
        self.vel=8
        self.back=back

        if self.left or self.up:
            self.vel*=-1
        elif self.right or self.down:
            self.vel*=1

    def draw(self,win):
        self.rect=pygame.draw.circle(win,self.colour,(self.x,self.y),self.radius)


def collision(surface_1,surface_2):
    """checks for collision between two surfaces. if there is rectangular collision, then checks for mask collision

    surface_1 (surface), surface_2 (surface) --> (bool)
    """
    #check if there is rectangular collision
    if surface_1.rect.colliderect(surface_2):
        #check if there is mask collision
        surface_1.mask=pygame.mask.from_surface(surface_1.image)
        surface_2.mask=pygame.mask.from_surface(surface_2.image)
        if pygame.sprite.spritecollide(surface_1,[surface_2],False,pygame.sprite.collide_mask):
            return True
    else:
        return False


def astar_ghost(pac,ghost):
    """uses the astar pathfinding algorithm to determine the goal node of the enemy sprite, then assigns
    booleans to each direction that the sprite can take. checks for collision as well. if there is collision
    between the enemy and player, the game variable will be False and the game would be over

    pac (player), ghost(enemy) --> (bool)
    """
    maze=astar.create_maze(screen_width,screen_height)

    start=(ghost.gridloc[0],ghost.gridloc[1])
    end=(ghost.goal_node[0],ghost.goal_node[1])
    goal_node=astar.astar(maze,start,end)

    if goal_node==None:
        pass
    else:
        ghost.goal_node=goal_node

    game=True

    if ghost.goal_node[0]<ghost.gridloc[0]:#left
        game=collision(pac,ghost)
        ghost.left=True
        ghost.right=False
        ghost.up=False
        ghost.down=False

    elif ghost.goal_node[0]>ghost.gridloc[0]:#right
        game=collision(pac,ghost)
        ghost.left=False
        ghost.right=True
        ghost.up=False
        ghost.down=False

    elif ghost.goal_node[1]<ghost.gridloc[1]:#up
        game=collision(pac,ghost)
        ghost.left=False
        ghost.right=False
        ghost.up=True
        ghost.down=False

    elif ghost.goal_node[1]>ghost.gridloc[1]:#down
        game=collision(pac,ghost)
        ghost.left=False
        ghost.right=False
        ghost.up=False
        ghost.down=True

    else:
        pass
    return game


font_name = pygame.font.match_font('arial')
def draw_text(surface,text,size,x,y):
    """drawing texts"""
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, (200,200,100))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x,y)
    win.blit(text_surface, text_rect)
    return

def show_gameover_screen():
    """show game over screen"""
    draw_text(win,'Game Over!',32,screen_width//2,screen_height//2)
    draw_text(win,'Press any key to play again',24,screen_width//2,screen_height//4*3)
    pygame.display.flip()
    pygame.time.wait(50)

    waiting=True
    while waiting:
        clock.tick(9)
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
            elif event.type==pygame.KEYUP:
                waiting=False
    return

def redrawGameWindow():
    """redraw everything for new frame"""
    win.fill((0,0,0))
    for ghost in ghost_list:
        ghost.draw(win)
    for bullet in bullets:
        bullet.draw(win)
    pac.draw(win)
    draw_text(win,'Score: '+str(score),40,screen_width*0.9,screen_height*0.9)
    pygame.display.flip()
    return

"""creating player"""
pac=player()
pac.rect.x=8*50
pac.rect.y=4*50
pac.vel=6

"""creating starting enemies"""
ghost1=enemy()
ghost1.rect.x=15*50
ghost1.rect.y=4*50
ghost1.goal_node=[(pac.rect.x//50),(pac.rect.y//50)]
ghost1.gridloc=[15,4]
ghost1.vel=2

ghost2=enemy()
ghost2.rect.x=1*50
ghost2.rect.y=4*50
ghost2.goal_node=[(pac.rect.x//50),(pac.rect.y//50)]
ghost2.gridloc=[1,4]
ghost2.vel=1

"""creating arrays to store objects"""
#Ghost list
ghost_list=[]
ghost_list.append(ghost1)
ghost_list.append(ghost2)

"""Bullets List"""
bullets=[]

"""shootLoop is prevent bullets from sticking too close to each other"""
shootLoop=0

"""for ghost respawns"""
len_ghost_list=len(ghost_list)

#MAIN LOOP
run=True
game_over=False
while run:
    if not game_over:
        clock.tick(fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            else:
                continue

        """determining difficulty level"""
        if score<100:
            difficulty_level=score//10
        else:
            pass

        """moving bullets"""
        if shootLoop>0:
            shootLoop+=1
        if shootLoop>3:
            shootLoop=0

        for bullet in bullets:
            for ghost in ghost_list:
                if pygame.sprite.collide_circle(bullet,ghost):
                    ghost.hit()
                    try:
                        bullets.pop(bullets.index(bullet))
                    except:
                        continue


            if bullet.x<screen_width and bullet.x>0 and bullet.right:
                if bullet.back:
                    bullet.x-=bullet.vel
                else:
                    bullet.x+=bullet.vel

            elif bullet.x<screen_width and bullet.x>0 and bullet.left:
                if bullet.back:
                    bullet.x-=bullet.vel
                else:
                    bullet.x+=bullet.vel

            elif bullet.y<screen_height and bullet.y>0 and bullet.down:
                if bullet.back:
                    bullet.y-=bullet.vel
                else:
                    bullet.y+=bullet.vel

            elif bullet.y<screen_height and bullet.y>0 and bullet.up:
                if bullet.back:
                    bullet.y-=bullet.vel
                else:
                    bullet.y+=bullet.vel
            else:
                bullets.pop(bullets.index(bullet))

        keys=pygame.key.get_pressed()


        if keys[pygame.K_SPACE] and shootLoop==0:
            if len(bullets)<max_bullets:
                if pac.left:
                    left=True
                    right=False
                    up=False
                    down=False
                elif pac.right:
                    left=False
                    right=True
                    up=False
                    down=False
                elif pac.up:
                    left=False
                    right=False
                    up=True
                    down=False
                elif pac.down:
                    left=False
                    right=False
                    up=False
                    down=True

                if score>40:
                    max_bullets=12
                    bullets.append(projectiles(round(pac.rect.x+pac.rect.width//2),round(pac.rect.y+pac.rect.height//2),left,right,up,down,True))
                    back_bullet=projectiles(round(pac.rect.x+pac.rect.width//2),round(pac.rect.y+pac.rect.height//2),left,right,up,down,False)
                    bullets.append(back_bullet)

                else:
                    bullets.append(projectiles(round(pac.rect.x+pac.rect.width//2),round(pac.rect.y+pac.rect.height//2),left,right,up,down,False))

                shootLoop=1

        """moving player"""
        if keys[pygame.K_LEFT] and pac.rect.x > pac.vel:
            pac.rect.x -= pac.vel
            pac.left=True
            pac.right=False
            pac.up=False
            pac.down=False

        elif keys[pygame.K_RIGHT] and pac.rect.x<screen_width-pac.rect.width-pac.vel:
            pac.rect.x += pac.vel
            pac.right=True
            pac.left=False
            pac.up=False
            pac.down=False

        elif keys[pygame.K_UP] and pac.rect.y>pac.vel:
            pac.rect.y -= pac.vel
            pac.up=True
            pac.down=False
            pac.left=False
            pac.right=False

        elif keys[pygame.K_DOWN] and pac.rect.y<screen_height-pac.rect.height-pac.vel:
            pac.rect.y += pac.vel
            pac.up=False
            pac.down=True
            pac.left=False
            pac.right=False

        else:
            pac.moveCount=0

        """creating new ghost if one died"""
        if len(ghost_list)<len_ghost_list:
            for i in range(len_ghost_list-len(ghost_list)):
                inhabited_x_space=[pac.rect.x//50,pac.rect.x//50+1,pac.rect.x//50-1,pac.rect.x//50+2,pac.rect.x//50-2]
                inhabited_y_space=[pac.rect.y//50,pac.rect.y//50+1,pac.rect.y//50-1,pac.rect.y//50+2,pac.rect.y//50-2]
                new_ghost=enemy()
                new_ghost.rect.x=random.choice([i for i in range(0,16) if i not in inhabited_x_space])*50
                new_ghost.rect.y=random.choice([i for i in range(0,8) if i not in inhabited_y_space])*50
                new_ghost.goal_node=[(pac.rect.x//50),(pac.rect.y//50)]
                new_ghost.gridloc=[new_ghost.rect.x//50,new_ghost.rect.y//50]
                new_ghost.vel=random.randint(2,4)
                ghost_list.append(new_ghost)

                if score>10:
                    if random.randint(1,12-difficulty_level)==2:
                        new_ghost2=enemy()
                        new_ghost2.rect.x=random.choice([i for i in range(0,16) if i not in [pac.rect.x//50]])*50
                        new_ghost2.rect.y=random.choice([i for i in range(0,8) if i not in [pac.rect.y//50]])*50
                        new_ghost2.goal_node=[(pac.rect.x//50),(pac.rect.y//50)]
                        new_ghost2.gridloc=[new_ghost2.rect.x//50,new_ghost2.rect.y//50]
                        new_ghost2.vel=random.randint(2,4)
                        ghost_list.append(new_ghost2)

        len_ghost_list=len(ghost_list)

        """checking if ghost is dead"""
        for ghost in ghost_list:
            if ghost.health==0:
                ghost_list.pop(ghost_list.index(ghost))
                score+=1
                continue
            game_over=astar_ghost(pac,ghost)
            if game_over:
                break
            ghost.update()

        """redrawing entire window"""
        redrawGameWindow()

    else:
        """Game is over"""
        show_gameover_screen()
        game_over=False
        win.fill((0,0,0))
        #Pac man
        pac=player()
        pac.rect.x=8*50
        pac.rect.y=4*50
        pac.vel=5

        # Ghost1
        ghost1=enemy()
        ghost1.rect.x=15*50
        ghost1.rect.y=4*50
        ghost1.goal_node=[(pac.rect.x//50),(pac.rect.y//50)]
        ghost1.gridloc=[15,4]
        ghost1.vel=1

        #Ghost2
        ghost2=enemy()
        ghost2.rect.x=1*50
        ghost2.rect.y=4*50
        ghost2.goal_node=[(pac.rect.x//50),(pac.rect.y//50)]
        ghost2.gridloc=[1,4]
        ghost2.vel=2

        #Ghost list
        ghost_list=[]
        ghost_list.append(ghost1)
        ghost_list.append(ghost2)
        bullets=[]
        len_ghost_list=len(ghost_list)

        #reset score
        score=0

pygame.quit()
