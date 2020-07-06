
# Space Invaders (beta 9 - depende de pygame)
import pygame
import sys
from os.path import abspath, dirname
from random import choice

RUTABASE = abspath(dirname(__file__))
RUTAFUENTES = RUTABASE + "/fuentes/"
RUTAIMAGENES = RUTABASE + "/imagenes/"
RUTASONIDOS = RUTABASE + "/sonidos/"

# Colores en RGB (R, G, B)
BLANCO = (255, 255, 255)
VERDE = (78, 255, 87)
AMARILLO = (241, 255, 0)
AZUL = (80, 255, 239)
MORADO = (203, 0, 255)

SCREEN = display.set_mode((800, 600))
FUENTE = RUTAFUENTES + 'space_invaders.ttf'
NOMIMAGENES= ['nave', 'jefe', 'enemigo1_1', 'enemigo1_2', 'enemigo2_1', 'enemigo2_2', 'enemigo3_1', 'enemigo3_2', 'explosionazul', 'explosionverde', 'explosionmorada', 'laser', 'laserenemigo']
IMAGENES = {nombre: image.load(RUTAIMAGENES + '{}.png'.format(nombre)).convert_alpha() for nombre in NOMIMAGENES}

POSICION_PROTECTORES = 450     # Valor para posicion de protecciones
POSICION_INICIAL_ENEMIGO = 65  # Valor inicial para nueva partida
MOVIMIENTO_VERTICAL_ENEMIGOS = 35    # Valor de movimiento hacia abajo


class Nave(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.imagen = IMAGENES['nave']
        self.rect = self.imagen.get_rect(topleft=(375, 540))
        self.velocidad = 5

    def update(self, keys, *args):
        if keys[K_RIGHT] and self.rect.x < 745:     #K_RIGHT == Tecla Derecha
            self.rect.x += self.velocidad
        if keys[K_LEFT] and self.rect.x > 15:       #K_LEFT == Tecla Izquierda
            self.rect.x -= self.velocidad
        game.screen.blit(self.imagen, self.rect)


class Laser(sprite.Sprite):
    def __init__(self, x, y, direccion, velocidad, archivo, lado):
        sprite.Sprite.__init__(self)
        self.imagen = IMAGENES[archivo]
        self.rect = self.imagen.get_rect(topleft=(x, y))
        self.velocidad = velocidad
        self.direccion = direccion
        self.lado = lado
        self.filename = archivo

    def update(self, keys, *args):
        game.screen.blit(self.imagen, self.rect)
        self.rect.y += self.velocidad * self.direccion
        if self.rect.y < 15 or self.rect.y > 600:
            self.kill()


class Enemigo(sprite.Sprite):
    def __init__(self, linea, columna):
        sprite.Sprite.__init__(self)
        self.linea = linea
        self.columna = columna
        self.imagenes = []
        self.cargar_imagenes()
        self.index = 0                              # Orden de Python 0, 1, 2 ,3...
        self.imagen = self.imagenes[self.index]     # carga imagenes de acuerdo al index
        self.rect = self.imagen.get_rect()

    def cambiar_imagen(self):
        self.index += 1                             # aumenta contador de index hasta el largo de lista de imagenes
        if self.index >= len(self.imagens):         # si hay mas index que imagenes (filas de enemigos) resetea el contador
            self.index = 0
        self.imagen = self.imagenes[self.index]

    def update(self, *args):
        game.screen.blit(self.imagen, self.rect)

    def cargar_imagenes(self):
        imagenes = {0: ['1_2', '1_1'], 1: ['2_2', '2_1'], 2: ['2_2', '2_1'], 3: ['3_1', '3_2'], 4: ['3_1', '3_2'] }
        img1, img2 = (IMAGENES['enemigo{}'.format(NUMIMAGENES)] for NUMIMAGENES in
                      imagenes[self.linea])
        self.imagenes.append(transform.scale(img1, (35, 35)))       # Tamaño enemigos 35px por 35 px
        self.imagenes.append(transform.scale(img2, (35, 35)))


class GrupoEnemigos(sprite.Group):
    def __init__(self, columnas, lineas):
        sprite.Group.__init__(self)
        self.enemies = [[None] * columnas for _ in range(lineas)]
        self.columnas = columnas
        self.lineas = lineas
        self.leftAddMove = 0
        self.rightAddMove = 0
        self.moveTime = 600
        self.direccion = 1
        self.rightMoves = 30
        self.leftMoves = 30
        self.moveNumber = 15
        self.timer = time.get_ticks()
        self.bottom = game.enemyPosition + ((lineas - 1) * 45) + 35
        self._aliveColumnas = list(range(columnas))
        self._leftAliveColumna = 0
        self._rightAliveColumna = columnas - 1

    def update(self, tiempo_actual):
        if tiempo_actual - self.timer > self.moveTime:
            if self.direccion == 1:
                mov_max = self.rightMoves + self.rightAddMove
            else:
                mov_max = self.leftMoves + self.leftAddMove

            if self.moveNumber >= mov_max:
                self.leftMoves = 30 + self.rightAddMove
                self.rightMoves = 30 + self.leftAddMove
                self.direccion *= -1
                self.moveNumber = 0
                self.bottom = 0
                for enemigo in self:
                    enemigo.rect.y += MOVIMIENTO_VERTICAL_ENEMIGOS
                    enemigo.cambiar_imagen()
                    if self.bottom < enemigo.rect.y + 35:
                        self.bottom = enemigo.rect.y + 35
            else:
                velocity = 10 if self.direccion == 1 else -10
                for enemy in self:
                    enemy.rect.x += velocity
                    enemy.cambiar_imagen()
                self.moveNumber += 1

            self.timer += self.moveTime

    def add_internal(self, *sprites):
        super(GrupoEnemigos, self).add_internal(*sprites)
        for s in sprites:
            self.enemies[s.linea][s.columna] = s

    def remove_internal(self, *sprites):
        super(GrupoEnemigos, self).remove_internal(*sprites)
        for s in sprites:
            self.kill(s)
        self.update_velocidad()

    def columna_muerta(self, columna):
        return not any(self.enemies[linea][columna]
                       for linea in range(self.lineas))

    def random_bottom(self):
        col = choice(self._aliveColumnas)
        col_enemigos = (self.enemies[linea - 1][col] for linea in range(self.lineas, 0, -1))
        return next((en for en in col_enemigos if en is not None), None)

    def update_velocidad(self):
        if len(self) == 1:
            self.moveTime = 200
        elif len(self) <= 10:
            self.moveTime = 400

    def kill(self, enemigo):
        self.enemies[enemigo.linea][enemigo.columna] = None
        columna_muerta = self.columna_muerta(enemigo.columna)
        if columna_muerta:
            self._aliveColumnas.remove(enemigo.columna)

        if enemigo.columna == self._rightAliveColumna:
            while self._rightAliveColumna > 0 and columna_muerta:
                self._rightAliveColumna -= 1
                self.rightAddMove += 5
                columna_muerta = self.columna_muerta(self._rightAliveColumna)

        elif enemigo.columna == self._leftAliveColumna:
            while self._leftAliveColumna < self.columnas and columna_muerta:
                self._leftAliveColumna += 1
                self.leftAddMove += 5
                columna_muerta = self.columna_muerta(self._leftAliveColumna)


class Protector(sprite.Sprite):
    def __init__(self, tamano, color, linea, columna):
        sprite.Sprite.__init__(self)
        self.height = tamano
        self.width = tamano
        self.color = color
        self.imagen = Surface((self.width, self.height))
        self.imagen.fill(self.color)
        self.rect = self.imagen.get_rect()
        self.linea = linea
        self.columna = columna

    def update(self, keys, *args):
        game.screen.blit(self.imagen, self.rect)


class Jefe(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.imagen = IMAGENES['jefe']
        self.imagen = transform.scale(self.imagen, (75, 35))
        self.rect = self.imagen.get_rect(topleft=(-80, 45))
        self.linea = 5
        self.moveTime = 25000
        self.direccion = 1
        self.timer = time.get_ticks()
        self.EntradaBoss = mixer.Sound(SOUND_PATH + 'entradajefe.wav')
        self.EntradaBoss.set_volume(0.3)
        self.playSound = True

    def update(self, keys, TiempoActual, *args):
        resettimer = False
        transcurrido = TiempoActual - self.timer
        if transcurrido > self.moveTime:
            if (self.rect.x < 0 or self.rect.x > 800) and self.playSound:
                self.EntradaBoss.play()
                self.playSound = False
            if self.rect.x < 840 and self.direccion == 1:
                self.EntradaBoss.fadeout(4000)
                self.rect.x += 2
                game.screen.blit(self.imagen, self.rect)
            if self.rect.x > -100 and self.direccion == -1:
                self.EntradaBoss.fadeout(4000)
                self.rect.x -= 2
                game.screen.blit(self.imagen, self.rect)

        if self.rect.x > 830:
            self.playSound = True
            self.direccion = -1
            resettimer = True
        if self.rect.x < -90:
            self.playSound = True
            self.direccion = 1
            resettimer = True
        if transcurrido > self.moveTime and resettimer:
            self.timer = TiempoActual


class ExplosionEnemiga(sprite.Sprite):
    def __init__(self, enemy, *groups):
        super(ExplosionEnemiga, self).__init__(*groups)
        self.imagen = transform.scale(self.obtener_imagen(enemy.linea), (35, 35))
        self.imagen2 = transform.scale(self.obtener_imagen(enemy.linea), (50, 45))
        self.rect = self.imagen.get_rect(topleft=(enemy.rect.x, enemy.rect.y))
        self.timer = time.get_ticks()

    @staticmethod  # Metodo estatico (solucion bug colores: hay 2 lineas pero parametro es 1)
    def obtener_imagen(linea):
        COLIMAGENES = ['morada', 'azul', 'azul', 'verde', 'verde']      # 2 veces azul y verde por dif. disfraces
        return IMAGENES['explosion{}'.format(COLIMAGENES[linea])]

    def update(self, tiempo_actual, *args):
        transcurrido = tiempo_actual - self.timer
        if transcurrido <= 100:
            game.screen.blit(self.imagen, self.rect)
        elif transcurrido <= 200:
            game.screen.blit(self.imagen2, (self.rect.x - 6, self.rect.y - 6))
        elif 400 < transcurrido:
            self.kill()


class ExplosionJefe(sprite.Sprite):
    def __init__(self, jefe, puntaje, *groups):
        super(ExplosionJefe, self).__init__(*groups)
        self.text = Text(FUENTE, 20, str(puntaje), BLANCO,
                         jefe.rect.x + 20, jefe.rect.y + 6)
        self.timer = time.get_ticks()

    def update(self, tiempo_actual, *args):
        transcurrido = tiempo_actual - self.timer
        if transcurrido <= 200 or 400 < transcurrido <= 600:
            self.text.draw(game.screen)
        elif 600 < transcurrido:
            self.kill()


class ExplosionUsuario(sprite.Sprite):
    def __init__(self, ship, *groups):
        super(ExplosionUsuario, self).__init__(*groups)
        self.imagen = IMAGENES['nave']
        self.rect = self.imagen.get_rect(topleft=(ship.rect.x, ship.rect.y))
        self.timer = time.get_ticks()

    def update(self, tiempo_actual, *args):
        transcurrido = tiempo_actual - self.timer
        if 300 < transcurrido <= 600:
            game.screen.blit(self.imagen, self.rect)
        elif 900 < transcurrido:
            self.kill()


class Vida(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.imagen = IMAGENES['nave']
        self.imagen = transform.scale(self.imagen, (23, 23))
        self.rect = self.imagen.get_rect(topleft=(x, y))

    def update(self, *args):
        game.screen.blit(self.imagen, self.rect)


class Text(object):
    def __init__(self, textFont, tamano, mensaje, color, x, y):
        self.font = font.Font(textFont, tamano)
        self.surface = self.font.render(mensaje, True, color)
        self.rect = self.surface.get_rect(topleft=(x, y))

    def draw(self, surface):
        surface.blit(self.surface, self.rect)


class SpaceInvaders(object):
    def __init__(self):
        mixer.pre_init(44100, -16, 1, 4096)
        init()
        self.clock = time.Clock()
        self.caption = display.set_caption('Space Invaders')
        self.screen = SCREEN
        self.background = image.load(RUTAIMAGENES + 'background.jpg').convert()
        self.startGame = False
        self.mainScreen = True
        self.gameOver = False
        # Si pasa de ronda, posicion inicial de enemigos es más abajo
        self.enemyPosition = POSICION_INICIAL_ENEMIGO
        self.titleText = Text(FUENTE, 50, 'Space Invaders', BLANCO, 164, 155)
        self.titleText2 = Text(FUENTE, 25, 'Pulsa cualquier tecla', BLANCO,
                               201, 225)
        self.titleText3 = Text(FUENTE, 15, "For ICC Lab 1.06 _ 2020-1", BLANCO,     # Ponerlo Arriba para no incomodar vista
                               201, 5)
        self.titleText4 = Text(FUENTE, 15, 'Sounds by Carbono Beats', BLANCO,        # Ponerlo arriba para no incomodar vista
                               201, 20)
        self.gameOverText = Text(FUENTE, 50, 'Game Over', BLANCO, 250, 270)     # UTF-8 sale raro, mejor "Game Over"
        self.nextRoundText = Text(FUENTE, 50, 'Siguiente Ronda', BLANCO, 150, 270)
        self.enemy1Text = Text(FUENTE, 25, '   =   10 pts', VERDE, 368, 270)
        self.enemy2Text = Text(FUENTE, 25, '   =  20 pts', AZUL, 368, 320)
        self.enemy3Text = Text(FUENTE, 25, '   =  30 pts', MORADO, 368, 370)
        self.enemy4Text = Text(FUENTE, 25, '   =  Bonus', AMARILLO, 368, 420)
        self.scoreText = Text(FUENTE, 20, 'Score', BLANCO, 5, 5)
        self.livesText = Text(FUENTE, 20, 'Vidas ', BLANCO, 640, 5)

        self.life1 = Vida(715, 3)
        self.life2 = Vida(740, 3)
        self.life3 = Vida(750, 3)
        self.livesGroup = sprite.Group(self.life1, self.life2, self.life3)

    def reset(self, score):
        self.usuario = Nave()
        self.GrupoUsuario = sprite.Group(self.usuario)
        self.explosionsGroup = sprite.Group()
        self.bullets = sprite.Group()
        self.bossShip = Jefe()
        self.bossGroup = sprite.Group(self.bossShip)
        self.enemyBullets = sprite.Group()
        self.make_enemies()
        self.allSprites = sprite.Group(self.usuario, self.enemies,
                                       self.livesGroup, self.bossShip)
        self.keys = key.get_pressed()

        self.timer = time.get_ticks()
        self.noteTimer = time.get_ticks()
        self.shipTimer = time.get_ticks()
        self.score = score
        self.create_audio()
        self.makeNewShip = False
        self.shipAlive = True

    def make_blockers(self, number):
        blockerGroup = sprite.Group()
        for linea in range(4):
            for columna in range(9):
                blocker = Protector(10, VERDE, linea, columna)
                blocker.rect.x = 50 + (200 * number) + (columna * blocker.width)
                blocker.rect.y = POSICION_PROTECTORES + (linea * blocker.height)
                blockerGroup.add(blocker)
        return blockerGroup

    def create_audio(self):
        self.sonidos = {}
        for NOMSONIDOS in ['disparo', 'disparo2', 'invadermatado', 'jefematado',
                           'explosionusuario']:
            self.sonidos[NOMSONIDOS] = mixer.Sound(
                RUTASONIDOS + '{}.wav'.format(NOMSONIDOS))
            self.sonidos[NOMSONIDOS].set_volume(0.5)

    @staticmethod
    def abandonar(evt):
        # type: (pygame.event.EventType) -> bool
        return evt.type == QUIT or (evt.type == KEYDOWN and evt.key == K_ESCAPE) # Cuando se presione ESC se sale del juego

    def check_input(self):
        self.keys = key.get_pressed()
        for e in event.get():
            if self.abandonar(e):
                sys.exit()          # Cierra sistema/Juego
            if e.type == KEYDOWN:   # KEYDOWN == APRETAR / KEYUP == SOLTAR
                if e.key == K_SPACE:
                    if len(self.bullets) == 0 and self.shipAlive:
                        if self.score < 1000:
                            bullet = Laser(self.usuario.rect.x + 23,
                                            self.usuario.rect.y + 5, -1,
                                            15, 'laser', 'center')
                            self.bullets.add(bullet)
                            self.allSprites.add(self.bullets)
                            self.sonidos['disparo'].play()
                        else:
                            leftbullet = Laser(self.usuario.rect.x + 8,
                                                self.usuario.rect.y + 5, -1,
                                                15, 'laser', 'left')
                            rightbullet = Laser(self.usuario.rect.x + 38,
                                                 self.usuario.rect.y + 5, -1,
                                                 15, 'laser', 'right')
                            self.bullets.add(leftbullet)
                            self.bullets.add(rightbullet)
                            self.allSprites.add(self.bullets)
                            self.sonidos['disparo2'].play()

    def make_enemies(self):
        enemigos = GrupoEnemigos(10, 5)
        for linea in range(5):
            for columna in range(10):
                enemy = Enemigo(linea, columna)
                enemy.rect.x = 157 + (columna * 50)
                enemy.rect.y = self.enemyPosition + (linea * 45)
                enemigos.add(enemy)

        self.enemies = enemigos

    def make_enemies_shoot(self):
        if (time.get_ticks() - self.timer) > 700 and self.enemies:
            enemy = self.enemies.random_bottom()
            self.enemyBullets.add(
                Laser(enemy.rect.x + 14, enemy.rect.y + 20, 1, 5,
                       'laserenemigo', 'center'))
            self.allSprites.add(self.enemyBullets)
            self.timer = time.get_ticks()

    def calcular_puntaje(self, linea):
        scores = {0: 30,
                  1: 20,
                  2: 20,
                  3: 10,
                  4: 10,
                  5: choice([25, 50, 100, 150, 300, 500])
                  }

        score = scores[linea]
        self.score += score
        return score

    def create_main_menu(self):
        self.enemy1 = IMAGENES['enemigo3_1']
        self.enemy1 = transform.scale(self.enemy1, (40, 40))
        self.enemy2 = IMAGENES['enemigo2_2']
        self.enemy2 = transform.scale(self.enemy2, (40, 40))
        self.enemy3 = IMAGENES['enemigo1_2']
        self.enemy3 = transform.scale(self.enemy3, (40, 40))
        self.enemy4 = IMAGENES['jefe']
        self.enemy4 = transform.scale(self.enemy4, (80, 40))
        self.screen.blit(self.enemy1, (318, 270))
        self.screen.blit(self.enemy2, (318, 320))
        self.screen.blit(self.enemy3, (318, 370))
        self.screen.blit(self.enemy4, (299, 420))

    def check_collisions(self):
        sprite.groupcollide(self.bullets, self.enemyBullets, True, True)

        for enemy in sprite.groupcollide(self.enemies, self.bullets,
                                         True, True).keys():
            self.sonidos['invadermatado'].play()
            self.calcular_puntaje(enemy.linea)
            ExplosionEnemiga(enemy, self.explosionsGroup)
            self.gameTimer = time.get_ticks()

        for boss in sprite.groupcollide(self.bossGroup, self.bullets,
                                           True, True).keys():
            boss.EntradaBoss.stop()
            self.sonidos['jefematado'].play()
            score = self.calcular_puntaje(boss.linea)
            ExplosionJefe(boss, score, self.explosionsGroup)
            newShip = Jefe()
            self.allSprites.add(newShip)
            self.bossGroup.add(newShip)

        for usuario in sprite.groupcollide(self.GrupoUsuario, self.enemyBullets,
                                          True, True).keys():
            if self.life3.alive():
                self.life3.kill()
            elif self.life2.alive():
                self.life2.kill()
            elif self.life1.alive():
                self.life1.kill()
            else:
                self.gameOver = True
                self.startGame = False
            self.sonidos['explosionusuario'].play()
            ExplosionUsuario(usuario, self.explosionsGroup)
            self.makeNewShip = True
            self.shipTimer = time.get_ticks()
            self.shipAlive = False

        if self.enemies.bottom >= 540:
            sprite.groupcollide(self.enemies, self.GrupoUsuario, True, True)
            if not self.usuario.alive() or self.enemies.bottom >= 600:
                self.gameOver = True
                self.startGame = False

        sprite.groupcollide(self.bullets, self.allBlockers, True, True)
        sprite.groupcollide(self.enemyBullets, self.allBlockers, True, True)
        if self.enemies.bottom >= POSICION_PROTECTORES:
            sprite.groupcollide(self.enemies, self.allBlockers, False, True)

    def crear_nueva_nave(self, createShip, TiempoActual):
        if createShip and (TiempoActual - self.shipTimer > 900):
            self.usuario = Nave()
            self.allSprites.add(self.usuario)
            self.GrupoUsuario.add(self.usuario)
            self.makeNewShip = False
            self.shipAlive = True

    def Game_Over(self, TiempoActual):
        self.screen.blit(self.background, (0, 0))
        transcurrido = TiempoActual - self.timer
        if transcurrido < 750:
            self.gameOverText.draw(self.screen)
        elif 750 < transcurrido < 1500:
            self.screen.blit(self.background, (0, 0))
        elif 1500 < transcurrido < 2250:
            self.gameOverText.draw(self.screen)
        elif 2250 < transcurrido < 2750:
            self.screen.blit(self.background, (0, 0))
        elif transcurrido > 3000:
            self.mainScreen = True

        for e in event.get():
            if self.should_exit(e):
                sys.exit()

    def main(self):
        while True:
            if self.mainScreen:
                self.screen.blit(self.background, (0, 0))
                self.titleText.draw(self.screen)
                self.titleText2.draw(self.screen)
                self.titleText3.draw(self.screen)
                self.titleText4.draw(self.screen)
                self.enemy1Text.draw(self.screen)
                self.enemy2Text.draw(self.screen)
                self.enemy3Text.draw(self.screen)
                self.enemy4Text.draw(self.screen)
                self.create_main_menu()
                for e in event.get():
                    if self.should_exit(e):
                        sys.exit()
                    if e.type == KEYUP:
                        # Estos protectores SOLO se crean cuando se inicia nuevo juego (bug solucionado)
                        self.allBlockers = sprite.Group(self.make_blockers(0),
                                                        self.make_blockers(1),
                                                        self.make_blockers(2),
                                                        self.make_blockers(3))
                        self.livesGroup.add(self.life1, self.life2, self.life3)
                        self.reset(0)
                        self.startGame = True
                        self.mainScreen = False

            elif self.startGame:
                if not self.enemies and not self.explosionsGroup:
                    TiempoActual = time.get_ticks()
                    if TiempoActual - self.gameTimer < 3000:
                        self.screen.blit(self.background, (0, 0))
                        self.scoreText2 = Text(FUENTE, 20, str(self.score),
                                               VERDE, 85, 5)
                        self.scoreText.draw(self.screen)
                        self.scoreText2.draw(self.screen)
                        self.titleText3.draw(self.screen)
                        self.titleText4.draw(self.screen)
                        self.nextRoundText.draw(self.screen)
                        self.livesText.draw(self.screen)
                        self.livesGroup.update()
                        self.check_input()
                    if TiempoActual - self.gameTimer > 3000:
                        # Conforme tiempo avanza enemigos se acercan al usuario
                        self.enemyPosition += MOVIMIENTO_VERTICAL_ENEMIGOS
                        self.reset(self.score)
                        self.gameTimer += 3000
                else:
                    TiempoActual = time.get_ticks()
                    self.play_main_music(TiempoActual)
                    self.screen.blit(self.background, (0, 0))
                    self.allBlockers.update(self.screen)
                    self.scoreText2 = Text(FUENTE, 20, str(self.score), VERDE,
                                           85, 5)
                    self.scoreText.draw(self.screen)
                    self.scoreText2.draw(self.screen)
                    self.titleText3.draw(self.screen)
                    self.titleText4.draw(self.screen)
                    self.livesText.draw(self.screen)
                    self.check_input()
                    self.enemies.update(TiempoActual)
                    self.allSprites.update(self.keys, TiempoActual)
                    self.explosionsGroup.update(TiempoActual)
                    self.check_collisions()
                    self.crear_nueva_nave(self.makeNewShip, TiempoActual)
                    self.make_enemies_shoot()

            elif self.gameOver:
                TiempoActual = time.get_ticks()
                # En Game Over resetear posiciones (bug solucionado)
                self.enemyPosition = POSICION_INICIAL_ENEMIGO
                self.Game_Over(TiempoActual)

            display.update()
            self.clock.tick(60)


if __name__ == '__main__':
    game = SpaceInvaders()
    game.main()
