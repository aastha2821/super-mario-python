import json
from tkinter import font
import pygame

from classes.Sprites import Sprites
from classes.Tile import Tile
from entities.Coin import Coin
from entities.CoinBrick import CoinBrick
from entities.Goomba import Goomba
from entities.Mushroom import RedMushroom
from entities.Koopa import Koopa
from entities.CoinBox import CoinBox
from entities.RandomBox import RandomBox


class Level:
    def __init__(self, screen, sound, dashboard):
        self.sprites = Sprites()
        self.dashboard = dashboard
        self.sound = sound
        self.screen = screen
        self.level = None
        self.levelLength = 0
        self.entityList = []
        self.show_quiz = False
        self.quiz_question = None
        self.option_rects = []
        self.quiz_timer = 0
        self.quiz_interval = 5 * 60  # 5 seconds at 60 FPS
        self.quiz_font = pygame.font.Font(None, 28)  # Cache font to avoid recreating every frame
        self.last_quiz_question = None  # Cache last quiz to avoid re-rendering

    def loadLevel(self, levelname):
        with open("./levels/{}.json".format(levelname)) as jsonData:
            data = json.load(jsonData)
            self.loadLayers(data)
            self.loadObjects(data)
            self.loadEntities(data)
            self.levelLength = data["length"]

    def loadEntities(self, data):
        try:
            [self.addCoinBox(x, y) for x, y in data["level"]["entities"]["CoinBox"]]
            [self.addGoomba(x, y) for x, y in data["level"]["entities"]["Goomba"]]
            [self.addKoopa(x, y) for x, y in data["level"]["entities"]["Koopa"]]
            [self.addCoin(x, y) for x, y in data["level"]["entities"]["coin"]]
            [self.addCoinBrick(x, y) for x, y in data["level"]["entities"]["coinBrick"]]
            [self.addRandomBox(x, y, item) for x, y, item in data["level"]["entities"]["RandomBox"]]
        except:
            # if no entities in Level
            pass

    def loadLayers(self, data):
        layers = []
        for x in range(*data["level"]["layers"]["sky"]["x"]):
            layers.append(
                (
                        [
                            Tile(self.sprites.spriteCollection.get("sky"), None)
                            for y in range(*data["level"]["layers"]["sky"]["y"])
                        ]
                        + [
                            Tile(
                                self.sprites.spriteCollection.get("ground"),
                                pygame.Rect(x * 32, (y - 1) * 32, 32, 32),
                            )
                            for y in range(*data["level"]["layers"]["ground"]["y"])
                        ]
                )
            )
        self.level = list(map(list, zip(*layers)))

    def loadObjects(self, data):
        for x, y in data["level"]["objects"]["bush"]:
            self.addBushSprite(x, y)
        for x, y in data["level"]["objects"]["cloud"]:
            self.addCloudSprite(x, y)
        for x, y, z in data["level"]["objects"]["pipe"]:
            self.addPipeSprite(x, y, z)
        for x, y in data["level"]["objects"]["sky"]:
            self.level[y][x] = Tile(self.sprites.spriteCollection.get("sky"), None)
        for x, y in data["level"]["objects"]["ground"]:
            self.level[y][x] = Tile(
                self.sprites.spriteCollection.get("ground"),
                pygame.Rect(x * 32, y * 32, 32, 32),
            )

    def updateEntities(self, cam):
        # Create a copy of the list to avoid modifying while iterating
        entities_to_remove = []
        for entity in self.entityList:
            entity.update(cam)
            if entity.alive is None:
                entities_to_remove.append(entity)
        
        # Remove dead entities after iteration
        for entity in entities_to_remove:
            self.entityList.remove(entity)

    def drawLevel(self, camera):
        try:
            for y in range(0, 15):
                for x in range(0 - int(camera.pos.x + 1), 20 - int(camera.pos.x - 1)):
                    if self.level[y][x].sprite is not None:
                        if self.level[y][x].sprite.redrawBackground:
                            self.screen.blit(
                                self.sprites.spriteCollection.get("sky").image,
                                ((x + camera.pos.x) * 32, y * 32),
                            )
                        self.level[y][x].sprite.drawSprite(
                            x + camera.pos.x, y, self.screen
                        )
            self.updateEntities(camera)
            
            # Update quiz timer
            if not self.show_quiz:
                self.quiz_timer += 1
                if self.quiz_timer >= self.quiz_interval:
                    # Import main only when needed
                    try:
                        import main
                        if main.current_question < len(main.questions):
                            self.show_quiz = True
                            self.quiz_question = main.questions[main.current_question]
                            self.quiz_timer = 0
                    except (ImportError, AttributeError):
                        pass
            
            if self.show_quiz and self.quiz_question is not None:
                self.drawQuiz(self.quiz_question)
        

        except IndexError:
            return
        

    def addCloudSprite(self, x, y):
        try:
            for yOff in range(0, 2):
                for xOff in range(0, 3):
                    self.level[y + yOff][x + xOff] = Tile(
                        self.sprites.spriteCollection.get("cloud{}_{}".format(yOff + 1, xOff + 1)), None, )
        except IndexError:
            return

    def addPipeSprite(self, x, y, length=2):
        try:
            # add pipe head
            self.level[y][x] = Tile(
                self.sprites.spriteCollection.get("pipeL"),
                pygame.Rect(x * 32, y * 32, 32, 32),
            )
            self.level[y][x + 1] = Tile(
                self.sprites.spriteCollection.get("pipeR"),
                pygame.Rect((x + 1) * 32, y * 32, 32, 32),
            )
            # add pipe body
            for i in range(1, length + 20):
                self.level[y + i][x] = Tile(
                    self.sprites.spriteCollection.get("pipe2L"),
                    pygame.Rect(x * 32, (y + i) * 32, 32, 32),
                )
                self.level[y + i][x + 1] = Tile(
                    self.sprites.spriteCollection.get("pipe2R"),
                    pygame.Rect((x + 1) * 32, (y + i) * 32, 32, 32),
                )
        except IndexError:
            return

    def addBushSprite(self, x, y):
        try:
            self.level[y][x] = Tile(self.sprites.spriteCollection.get("bush_1"), None)
            self.level[y][x + 1] = Tile(
                self.sprites.spriteCollection.get("bush_2"), None
            )
            self.level[y][x + 2] = Tile(
                self.sprites.spriteCollection.get("bush_3"), None
            )
        except IndexError:
            return

    def addCoinBox(self, x, y):
        self.level[y][x] = Tile(None, pygame.Rect(x * 32, y * 32 - 1, 32, 32))
        self.entityList.append(
            CoinBox(
                self.screen,
                self.sprites.spriteCollection,
                x,
                y,
                self.sound,
                self.dashboard,
            )
        )

    def addRandomBox(self, x, y, item):
        self.level[y][x] = Tile(None, pygame.Rect(x * 32, y * 32 - 1, 32, 32))
        self.entityList.append(
            RandomBox(
                self.screen,
                self.sprites.spriteCollection,
                x,
                y,
                item,
                self.sound,
                self.dashboard,
                self
            )
        )


            
    


    def addCoin(self, x, y):
        self.entityList.append(Coin(self.screen, self.sprites.spriteCollection, x, y))

    def addCoinBrick(self, x, y):
        self.level[y][x] = Tile(None, pygame.Rect(x * 32, y * 32 - 1, 32, 32))
        self.entityList.append(
            CoinBrick(
                self.screen,
                self.sprites.spriteCollection,
                x,
                y,
                self.sound,
                self.dashboard
            )
        )

    def addGoomba(self, x, y):
        self.entityList.append(
            Goomba(self.screen, self.sprites.spriteCollection, x, y, self, self.sound)
        )

    def addKoopa(self, x, y):
        self.entityList.append(
            Koopa(self.screen, self.sprites.spriteCollection, x, y, self, self.sound)
        )

    def addRedMushroom(self, x, y):
        self.entityList.append(
            RedMushroom(self.screen, self.sprites.spriteCollection, x, y, self, self.sound)
        )
    def drawQuiz(self, quiz):
        # Only rebuild option_rects if quiz changed
        if quiz != self.last_quiz_question:
            self.last_quiz_question = quiz
            box = pygame.Rect(40, 50, 560, 240)
            pygame.draw.rect(self.screen, (0, 0, 0), box)
            pygame.draw.rect(self.screen, (255, 255, 255), box, 3)

            q = self.quiz_font.render(quiz["question"], True, (255, 255, 255))
            self.screen.blit(q, (55, 65))

            self.option_rects = []
            for idx, option in enumerate(quiz["options"]):
                r = pygame.Rect(60, 110 + idx * 40, 520, 30)
                pygame.draw.rect(self.screen, (60, 60, 60), r)
                t = self.quiz_font.render(option, True, (255, 255, 255))
                self.screen.blit(t, (70, 115 + idx * 40))
                self.option_rects.append(r)
        else:
            # If same quiz, just redraw without rebuilding
            box = pygame.Rect(40, 50, 560, 240)
            pygame.draw.rect(self.screen, (0, 0, 0), box)
            pygame.draw.rect(self.screen, (255, 255, 255), box, 3)

            q = self.quiz_font.render(quiz["question"], True, (255, 255, 255))
            self.screen.blit(q, (55, 65))

            for idx, option in enumerate(quiz["options"]):
                r = pygame.Rect(60, 110 + idx * 40, 520, 30)
                pygame.draw.rect(self.screen, (60, 60, 60), r)
                t = self.quiz_font.render(option, True, (255, 255, 255))
                self.screen.blit(t, (70, 115 + idx * 40))
    
