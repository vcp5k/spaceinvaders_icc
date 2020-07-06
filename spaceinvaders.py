
# Space Invaders (version 1.15 - depende de pygame)
from pygame import *
import sys
from os.path import abspath, dirname
from random import choice

RUTABASE = abspath(dirname(__file__))
RUTAFUENTES = RUTABASE + "/fuentes/"
RUTAIMAGENES = RUTABASE + "/imagenes/"
RUTASONIDOS = RUTABASE + "/sonidos/"

# Colores en RGB (R, G, B)
BLANCO = (255, 255, 255)        # Texto normal
VERDE = (78, 255, 87)           # Score
AMARILLO = (241, 255, 0)        # Bonus Boss

SCREEN = display.set_mode((800, ))
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
        self.velocidad = 5
        self.rect = self.imagen.get_rect(topleft=(375, 540))

    def update(self, tecla, *args):
        if tecla[K_RIGHT] and self.rect.x < 745:     # K_RIGHT == Tecla Derecha
            self.rect.x += self.velocidad
        if tecla[K_LEFT] and self.rect.x > 15:       # K_LEFT == Tecla Izquierda
            self.rect.x -= self.velocidad
        game.screen.blit(self.imagen, self.rect)


class Laser(sprite.Sprite):
    def __init__(self, x, y, direccion, velocidad, archivo, lado):
        sprite.Sprite.__init__(self)
        self.imagen = IMAGENES[archivo]
        self.rect = self.imagen.get_rect(topleft=(x, y))
        self.velocidad = velocidad
        self.lado = lado
        self.direccion = direccion
        self.archivo = archivo


    def update(self, tecla, *args):
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
        if self.index >= len(self.imagenes):        # si hay mas index que imagenes (filas de enemigos) resetea el contador
            self.index = 0
        self.imagen = self.imagenes[self.index]

    def update(self, *args):
        game.screen.blit(self.imagen, self.rect)

    def cargar_imagenes(self):
        imagenes = {0: ['1_2', '1_1'], 1: ['2_2', '2_1'], 2: ['2_2', '2_1'], 3: ['3_1', '3_2'], 4: ['3_1', '3_2']}
        img1, img2 = (IMAGENES['enemigo{}'.format(NUMIMAGENES)] for NUMIMAGENES in imagenes[self.linea])
        self.imagenes.append(transform.scale(img1, (35, 35)))       # Tamaño enemigos 35px por 35 px
        self.imagenes.append(transform.scale(img2, (35, 35)))       # disfraces 1 y 2


class GrupoEnemigos(sprite.Group):                                  # Logica en cuaderno
    def __init__(self, columnas, lineas):
        sprite.Group.__init__(self)
        self.enemigos = [[0] * columnas for _ in range(lineas)]
        self.columnas = columnas
        self.lineas = lineas
        self.agregarmovizq = 0
        self.agregarmovder = 0
        self.tiempomovtot = 600
        self.direccion = 1
        self.movsder = 30
        self.movsizq = 30
        self.nmov = 15
        self.timer = time.get_ticks()
        self.liminf = game.PosicionEnemigo + ((lineas - 1) * 45) + 35
        self._Columnasv = list(range(columnas))
        self._Columnavizq = 0
        self._Columnavider = columnas - 1

    def update(self, tiempo_actual):
        if tiempo_actual - self.timer > self.tiempomovtot:
            if self.direccion == 1:
                mov_max = self.movsder + self.agregarmovder
            else:
                mov_max = self.movsizq + self.agregarmovizq

            if self.nmov >= mov_max:
                self.movsizq = 30 + self.agregarmovder
                self.movsder = 30 + self.agregarmovizq
                self.direccion *= -1
                self.nmov = 0
                self.liminf = 0
                for enemigo in self:
                    enemigo.rect.y += MOVIMIENTO_VERTICAL_ENEMIGOS
                    enemigo.cambiar_imagen()
                    if self.liminf < enemigo.rect.y + 35:
                        self.liminf = enemigo.rect.y + 35
            else:
                rapidez = 10 if self.direccion == 1 else -10
                for enemigo in self:
                    enemigo.rect.x += rapidez
                    enemigo.cambiar_imagen()
                self.nmov += 1

            self.timer += self.tiempomovtot

    def add_internal(self, *sprites):                           # Permite matar enemigos dentro del grupo
        super(GrupoEnemigos, self).add_internal(*sprites)       # agregando o quitando los internals respectivos
        for s in sprites:
            self.enemigos[s.linea][s.columna] = s

    def remove_internal(self, *sprites):
        super(GrupoEnemigos, self).remove_internal(*sprites)
        for s in sprites:
            self.kill(s)
        self.update_velocidad()

    def columna_muerta(self, columna):
        return not any(self.enemigos[linea][columna]
                       for linea in range(self.lineas))

    def limrandom (self):
        col = choice(self._Columnasv)
        col_enemigos = (self.enemigos[linea - 1][col] for linea in range(self.lineas, 0, -1))
        return next((en for en in col_enemigos if en is not None), None)

    def update_velocidad(self):
        if len(self) == 1:
            self.tiempomovtot = 200
        elif len(self) <= 10:
            self.tiempomovtot = 400

    def kill(self, enemigo):
        self.enemigos[enemigo.linea][enemigo.columna] = None
        columna_muerta = self.columna_muerta(enemigo.columna)
        if columna_muerta:
            self._Columnasv.remove(enemigo.columna)

        if enemigo.columna == self._Columnavider:
            while self._Columnavider > 0 and columna_muerta:
                self._Columnavider -= 1
                self.agregarmovder += 5
                columna_muerta = self.columna_muerta(self._Columnavider)

        elif enemigo.columna == self._Columnavizq:
            while self._Columnavizq < self.columnas and columna_muerta:
                self._Columnavizq += 1
                self.agregarmovizq += 5
                columna_muerta = self.columna_muerta(self._Columnavizq)


class Protector(sprite.Sprite):
    def __init__(self, tamano, color, linea, columna):
        sprite.Sprite.__init__(self)
        self.altura = tamano
        self.anchura = tamano
        self.color = color
        self.imagen = Surface((self.anchura, self.altura))      # x, y == anchura, altura
        self.imagen.fill(self.color)
        self.rect = self.imagen.get_rect()
        self.linea = linea
        self.columna = columna

    def update(self, tecla, *args):
        game.screen.blit(self.imagen, self.rect)


class Jefe(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.imagen = IMAGENES['jefe']
        self.imagen = transform.scale(self.imagen, (75, 35))
        self.rect = self.imagen.get_rect(topleft=(-80, 45))
        self.linea = 5
        self.tiempomovtot = 25000
        self.direccion = 1
        self.timer = time.get_ticks()
        self.EntradaBoss = mixer.Sound(RUTASONIDOS + 'entradajefe.wav')
        self.EntradaBoss.set_volume(0.3)
        self.repson = True                          # reproducir sonido jefe

    def update(self, tecla, TiempoActual, *args):
        resettimer = False
        transcurrido = TiempoActual - self.timer
        if transcurrido > self.tiempomovtot:
            if (self.rect.x < 0 or self.rect.x > 800) and self.repson:
                self.EntradaBoss.play()
                self.repson = False
            if self.rect.x < 840 and self.direccion == 1:
                self.rect.x += 2
                game.screen.blit(self.imagen, self.rect)
            if self.rect.x >= -100 and self.direccion == -1:
                self.rect.x -= 2
                game.screen.blit(self.imagen, self.rect)

        if self.rect.x < -90:
            self.repson = True
            self.direccion = 1
            resettimer = True
        if transcurrido > self.tiempomovtot and resettimer:
            self.timer = TiempoActual
        if self.rect.x > 830:
            self.repson = True
            self.direccion = -1
            resettimer = True


class ExplosionEnemiga(sprite.Sprite):
    def __init__(self, enemigo, *groups):
        super(ExplosionEnemiga, self).__init__(*groups)
        self.imagen = transform.scale(self.obtener_imagen(enemigo.linea), (35, 35))
        self.imagen2 = transform.scale(self.obtener_imagen(enemigo.linea), (50, 45))
        self.rect = self.imagen.get_rect(topleft=(enemigo.rect.x, enemigo.rect.y))
        self.timer = time.get_ticks()



    def update(self, tiempo_actual, *args):
        transcurrido = tiempo_actual - self.timer
        if transcurrido <= 100:
            game.screen.blit(self.imagen, self.rect)
        elif transcurrido <= 200:
            game.screen.blit(self.imagen2, (self.rect.x - 6, self.rect.y - 6))
        elif 400 < transcurrido:
            self.kill()

    @staticmethod  # Metodo estatico (solucion bug colores: hay 2 lineas pero parametro es 1)
    def obtener_imagen(linea):
        COLIMAGENES = ['morada', 'azul', 'azul', 'verde', 'verde']  # 2 veces azul y verde por dif. disfraces
        return IMAGENES['explosion{}'.format(COLIMAGENES[linea])]


class ExplosionJefe(sprite.Sprite):
    def __init__(self, jefe, puntaje, *groups):
        super(ExplosionJefe, self).__init__(*groups)
        self.text = Text(FUENTE, 20, str(puntaje), BLANCO,
                         jefe.rect.x + 20, jefe.rect.y + 6)
        self.timer = time.get_ticks()

    def update(self, tiempo_actual, *args):
        transcurrido = tiempo_actual - self.timer
        if transcurrido <= 200 or 400 < transcurrido <= 600:
            self.text.aparecerpantalla(game.screen)
        elif 600 < transcurrido:
            self.kill()


class ExplosionUsuario(sprite.Sprite):
    def __init__(self, nave, *groups):
        super(ExplosionUsuario, self).__init__(*groups)
        self.imagen = IMAGENES['nave']
        self.rect = self.imagen.get_rect(topleft=(nave.rect.x, nave.rect.y))
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
    def __init__(self, fuente, tamano, mensaje, color, coordx, coordy):
        self.fuente = font.Font(fuente, tamano)
        self.surface = self.fuente.render(mensaje, True, color)
        self.rect = self.surface.get_rect(topleft=(coordx, coordy))

    def aparecerpantalla(self, surface):
        surface.blit(self.surface, self.rect)


class SpaceInvaders(object):
    def __init__(self):
        mixer.pre_init(44100, -16, 1, 4096)
        init()
        self.clock = time.Clock()
        self.descripcion = display.set_caption('Space Invaders')
        self.screen = SCREEN
        self.background = image.load(RUTAIMAGENES + 'background.jpg').convert()
        self.startGame = False
        self.mainScreen = True
        self.gameOver = False
        # Si pasa de ronda, posicion inicial de enemigos es más abajo
        self.PosicionEnemigo = POSICION_INICIAL_ENEMIGO
        self.titulo = Text(FUENTE, 50, 'Space Invaders', BLANCO, 164, 155)
        self.subtitulo = Text(FUENTE, 25, 'Pulsa cualquier tecla', BLANCO,
                               215, 225)
        self.creditos1 = Text(FUENTE, 15, "For ICC Lab 1.06 _ 2020-1", BLANCO,     # Ponerlo Arriba para no incomodar vista
                               201, 5)
        self.creditos2 = Text(FUENTE, 15, 'Sounds by Carbono Beats', BLANCO,        # Ponerlo arriba para no incomodar vista
                               201, 20)
        self.finjuego = Text(FUENTE, 50, 'Game Over', BLANCO, 250, 270)     # UTF-8 sale raro, mejor "Game Over"
        self.ronda = Text(FUENTE, 50, 'Siguiente Ronda', BLANCO, 150, 270)
        self.DescrEnemigo1 = Text(FUENTE, 25, '   =   10 pts', BLANCO, 368, 270)
        self.DescrEnemigo2 = Text(FUENTE, 25, '   =  20 pts', BLANCO, 368, 320)
        self.DescrEnemigo3 = Text(FUENTE, 25, '   =  30 pts', BLANCO, 368, 370)
        self.DescrEnemigo4 = Text(FUENTE, 25, '   =  Bonus', AMARILLO, 368, 420)
        self.scorenombre = Text(FUENTE, 20, 'Score', BLANCO, 5, 5)
        self.vidasnombre = Text(FUENTE, 20, 'Vidas ', BLANCO, 640, 5)

        self.vida1 = Vida(715, 3)
        self.vida2 = Vida(741, 3)
        self.vida3 = Vida(755, 3)
        self.grupovidas = sprite.Group(self.vida1, self.vida2, self.vida3)

    def reset(self, score):
        self.usuario = Nave()
        self.GrupoUsuario = sprite.Group(self.usuario)
        self.grupoexp = sprite.Group()
        self.balas = sprite.Group()
        self.naveboss = Jefe()
        self.bossGroup = sprite.Group(self.naveboss)
        self.DisparosEnemigos = sprite.Group()
        self.crearenemigos()
        self.allSprites = sprite.Group(self.usuario, self.enemigos,
                                       self.grupovidas, self.naveboss)
        self.teclas = key.get_pressed()

        self.timer = time.get_ticks()
        self.noteTimer = time.get_ticks()
        self.Timernave = time.get_ticks()
        self.score = score
        self.create_audio()
        self.nuevanave = False
        self.naveconvida = True

    def crearprotectores(self, number):
        Grupoprotectores = sprite.Group()
        for linea in range(4):
            for columna in range(9):
                protector = Protector(10, VERDE, linea, columna)
                protector.rect.x = 50 + (200 * number) + (columna * protector.anchura)
                protector.rect.y = POSICION_PROTECTORES + (linea * protector.altura)
                Grupoprotectores.add(protector)
        return Grupoprotectores

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
        self.teclas = key.get_pressed()
        for evnt in event.get():
            if self.abandonar(evnt):
                sys.exit()          # Cierra sistema/Juego
            if evnt.type == KEYDOWN:   # KEYDOWN == APRETAR / KEYUP == SOLTAR
                if evnt.key == K_SPACE:
                    if len(self.balas) == 0 and self.naveconvida:
                        if self.score < 1000:
                            bala = Laser(self.usuario.rect.x + 23,
                                            self.usuario.rect.y + 5, -1,
                                            15, 'laser', 'center')
                            self.balas.add(bala)
                            self.allSprites.add(self.balas)
                            self.sonidos['disparo'].play()      # BALAS SIMPLES
                        else:
                            bala1 = Laser(self.usuario.rect.x + 8,
                                                self.usuario.rect.y + 5, -1,
                                                15, 'laser', 'left')
                            bala2= Laser(self.usuario.rect.x + 38,
                                                 self.usuario.rect.y + 5, -1,
                                                 15, 'laser', 'right')
                            self.balas.add(bala1)
                            self.balas.add(bala2)
                            self.allSprites.add(self.balas)
                            self.sonidos['disparo2'].play()       # BALAS DOBLES

    def crearenemigos(self):
        enemigos = GrupoEnemigos(10, 5)
        for linea in range(5):
            for columna in range(10):
                enemigo= Enemigo(linea, columna)
                enemigo.rect.x = 157 + (columna * 50)
                enemigo.rect.y = self.PosicionEnemigo + (linea * 45)
                enemigos.add(enemigo)

        self.enemigos = enemigos

    def dispararenemigos(self):
        if (time.get_ticks() - self.timer) > 700 and self.enemigos:
            enemigo = self.enemigos.limrandom()
            self.DisparosEnemigos.add(Laser(enemigo.rect.x + 14, enemigo.rect.y + 20, 1, 5, 'laserenemigo', 'center'))
            self.allSprites.add(self.DisparosEnemigos)
            self.timer = time.get_ticks()

    def calcular_puntaje(self, linea):
        scores = {0: 30, 1: 20, 2: 20, 3: 10, 4: 10, 5: choice([25, 50, 100, 150, 300, 500])}
        score = scores[linea]
        self.score += score
        return score

    def create_main_menu(self):
        self.enemigo3 = IMAGENES['enemigo3_1']
        self.enemigo3 = transform.scale(self.enemigo3, (40, 40))
        self.enemigo2 = IMAGENES['enemigo2_2']
        self.enemigo2 = transform.scale(self.enemigo2, (40, 40))
        self.enemigo1 = IMAGENES['enemigo1_2']
        self.enemigo1 = transform.scale(self.enemigo1, (40, 40))
        self.boss = IMAGENES['jefe']
        self.boss = transform.scale(self.boss, (80, 40))
        self.screen.blit(self.enemigo3, (318, 270))
        self.screen.blit(self.enemigo2, (318, 320))
        self.screen.blit(self.enemigo1, (318, 370))
        self.screen.blit(self.boss, (299, 420))

    def check_collisions(self):
        sprite.groupcollide(self.balas, self.DisparosEnemigos, True, True)

        for enemigo in sprite.groupcollide(self.enemigos, self.balas, True, True).keys():
            self.sonidos['invadermatado'].play()
            self.calcular_puntaje(enemigo.linea)
            ExplosionEnemiga(enemigo, self.grupoexp)
            self.gameTimer = time.get_ticks()

        for boss in sprite.groupcollide(self.bossGroup, self.balas, True, True).keys():
            boss.EntradaBoss.stop()
            self.sonidos['jefematado'].play()
            score = self.calcular_puntaje(boss.linea)
            ExplosionJefe(boss, score, self.grupoexp)
            nuevanave = Jefe()
            self.allSprites.add(nuevanave)
            self.bossGroup.add(nuevanave)

        for usuario in sprite.groupcollide(self.GrupoUsuario, self.DisparosEnemigos, True, True).keys():
            if self.vida3.alive():              # Vidas se pierden de derecha a izquierda
                self.vida3.kill()
            elif self.vida2.alive():
                self.vida2.kill()
            elif self.vida1.alive():
                self.vida1.kill()
            else:
                self.gameOver = True
                self.startGame = False
            self.sonidos['explosionusuario'].play()
            ExplosionUsuario(usuario, self.grupoexp)
            self.nuevanave = True
            self.Timernave = time.get_ticks()
            self.naveconvida = False

        if self.enemigos.liminf >= 550:
            sprite.groupcollide(self.enemigos, self.GrupoUsuario, True, True)
            if not self.usuario.alive() or self.enemigos.liminf >= 600:
                self.gameOver = True
                self.startGame = False

        sprite.groupcollide(self.balas, self.protectores, True, True)
        sprite.groupcollide(self.DisparosEnemigos, self.protectores, True, True)
        if self.enemigos.liminf >= POSICION_PROTECTORES:
            sprite.groupcollide(self.enemigos, self.protectores, False, True)

    def crear_nueva_nave(self, crearnave, TiempoActual):
        if crearnave and (TiempoActual - self.Timernave) > 900:
            self.usuario = Nave()
            self.allSprites.add(self.usuario)
            self.GrupoUsuario.add(self.usuario)
            self.nuevanave = False
            self.naveconvida = True

    def Game_Over(self, TiempoActual):
        self.screen.blit(self.background, (0, 0))
        transcurrido = TiempoActual - self.timer
        if transcurrido < 750:
            self.finjuego.aparecerpantalla(self.screen)
            self.puntajefinal.aparecerpantalla(self.screen)
        elif 750 < transcurrido < 1515:
            self.screen.blit(self.background, (0, 0))
        elif 1515 < transcurrido < 2500:
            self.finjuego.aparecerpantalla(self.screen)
            self.puntajefinal.aparecerpantalla(self.screen)
        elif 2500 < transcurrido < 2750:
            self.screen.blit(self.background, (0, 0))
        elif transcurrido > 3000:
            self.mainScreen = True

        for evnt in event.get():
            if self.abandonar(evnt):
                sys.exit()

    def main(self):
        while True:
            if self.mainScreen:
                self.titulo.aparecerpantalla(self.screen)
                self.subtitulo.aparecerpantalla(self.screen)
                self.creditos1.aparecerpantalla(self.screen)
                self.creditos2.aparecerpantalla(self.screen)
                self.DescrEnemigo1.aparecerpantalla(self.screen)
                self.DescrEnemigo2.aparecerpantalla(self.screen)
                self.DescrEnemigo3.aparecerpantalla(self.screen)
                self.DescrEnemigo4.aparecerpantalla(self.screen)
                self.create_main_menu()
                for evnt in event.get():
                    if self.abandonar(evnt):
                        sys.exit()
                    if evnt.type == KEYUP:
                        # Estos protectores SOLO se crean cuando se inicia nuevo juego (bug solucionado)
                        self.protectores= sprite.Group(self.crearprotectores(0), self.crearprotectores(1), self.crearprotectores(2), self.crearprotectores(3))
                        self.grupovidas.add(self.vida1, self.vida2, self.vida3)
                        self.reset(0)
                        self.startGame = True
                        self.mainScreen = False

            elif self.startGame:
                if not self.enemigos and not self.grupoexp:
                    TiempoActual = time.get_ticks()
                    if TiempoActual - self.gameTimer < 3000:
                        self.screen.blit(self.background, (0, 0))
                        self.puntajeactual = Text(FUENTE, 20, str(self.score), VERDE, 85, 5)
                        self.puntajefinal = Text(FUENTE, 30, str(self.score), VERDE, 370, 350)
                        self.scorenombre.aparecerpantalla(self.screen)
                        self.puntajeactual.aparecerpantalla(self.screen)
                        self.creditos1.aparecerpantalla(self.screen)
                        self.creditos2.aparecerpantalla(self.screen)
                        self.ronda.aparecerpantalla(self.screen)
                        self.vidasnombre.aparecerpantalla(self.screen)
                        self.grupovidas.update()
                        self.check_input()
                    if TiempoActual - self.gameTimer > 3000:
                        # Conforme tiempo avanza enemigos se acercan al usuario
                        self.PosicionEnemigo += MOVIMIENTO_VERTICAL_ENEMIGOS
                        self.reset(self.score)
                        self.gameTimer += 3000
                else:
                    TiempoActual = time.get_ticks()
                    self.screen.blit(self.background, (0, 0))
                    self.protectores.update(self.screen)
                    self.puntajeactual = Text(FUENTE, 20, str(self.score), VERDE, 85, 5)
                    self.puntajefinal = Text(FUENTE, 30, str(self.score), VERDE, 370, 350)
                    self.scorenombre.aparecerpantalla(self.screen)
                    self.puntajeactual.aparecerpantalla(self.screen)
                    self.creditos1.aparecerpantalla(self.screen)
                    self.creditos2.aparecerpantalla(self.screen)
                    self.vidasnombre.aparecerpantalla( self.screen)
                    self.enemigos.update(TiempoActual)
                    self.check_input()
                    self.allSprites.update(self.teclas, TiempoActual)
                    self.grupoexp.update(TiempoActual)
                    self.check_collisions()
                    self.crear_nueva_nave(self.nuevanave, TiempoActual)
                    self.dispararenemigos()

            elif self.gameOver:
                TiempoActual = time.get_ticks()
                # En Game Over resetear posiciones (bug solucionado)
                self.PosicionEnemigo = POSICION_INICIAL_ENEMIGO
                self.Game_Over(TiempoActual)

            display.update()
            self.clock.tick(60)


if __name__ == '__main__':
    game = SpaceInvaders()
    game.main()

