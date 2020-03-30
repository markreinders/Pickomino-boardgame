import sys
import pygame
import random

from game_menu import *
from pygame.locals import *
from collections import OrderedDict
from PyQt5.QtWidgets import QApplication

# Initiate pygame environment
pygame.init()


class Die:
    def __init__(self, pos):
        """
        Initializes a Die object

        pos: position/coordinate of the Die object on the pygame window
        """
        super(Die, self).__init__()
        path = PATH + "/images/"
        self.dies = {path + "dobbel_1.png": 1, path + "dobbel_2.png": 2, path + "dobbel_3.png": 3,
                     path + "dobbel_4.png": 4, path + "dobbel_5.png": 5, path + "dobbel_w1.png": 'worm'}
        init_die = random.choice(list(self.dies.keys()))
        self.die_value = self.dies[init_die]
        self.surf = pygame.image.load(init_die).convert()
        self.rect = self.surf.get_rect(center=pos)

    def roll(self):
        """:returns an updated image surface when a die gets a new value after rolling it"""
        update_die = random.choice(list(self.dies.keys()))
        self.die_value = self.dies[update_die]
        self.surf = pygame.image.load(update_die).convert()
        return self.surf

    def get_value(self):
        """:returns the value of a die"""
        return self.die_value

    def set_zero(self):
        """sets the value of a die to zero to indicate these have been selected"""
        self.die_value = 0

    def get_position(self):
        """:returns the x,y coordinates of a Die object surface"""
        return self.rect.x, self.rect.y


class Throw:
    def __init__(self):
        """Initializes a Throw of Dies object, consisting of 8 new dice on the screen"""
        super(Throw, self).__init__()
        self.throw = {}
        self.init_throw()

        # clear parked dice from previous player
        erase = pygame.Surface([950, 200])
        erase.fill(BG)
        screen.blit(erase, (400, 400))

    def init_throw(self):
        """initialize 8 die objects on the screen"""
        x_midscreen = SCREEN_WIDTH/2
        for i in range(1, 9):
            if i < 5:
                self.throw[f'die{i}'] = Die((x_midscreen - (i*100) + 25, 350))
            else:
                self.throw[f'die{i}'] = Die((x_midscreen + ((i-5)*100) + 25, 350))
        for k in self.throw.keys():
            screen.blit(self.throw[k].surf, self.throw[k].rect)

    @property
    def get_throw(self):
        """:returns the dictionary containing the die objects"""
        return self.throw

    def check_throw(self):
        """:method used to create a list of dice allowed to chose for the next throw"""
        options = []
        for k in self.throw.keys():
            options.append(self.throw[k].get_value())
        return options

    def calculate_score(self, die):
        """
        :arg die is the selected die by the current player after a throw

        :returns the total score of the throw based on the selected die
        """
        same_dice = []
        val = self.throw[die].get_value()
        for k in self.throw.keys():
            if self.throw[k].get_value() == val:
                same_dice.append(k)
                erase_dies = pygame.Surface([90, 90])
                erase_dies.fill(BG)
                screen.blit(erase_dies, self.throw[k].get_position())
                newpos = self.throw[k].rect.move(0, 110)
                screen.blit(self.throw[k].surf, newpos)  # Move the selected die
        for k in same_dice:
            self.throw[k].set_zero()
        if val == 'worm':
            return 5 * len(same_dice)
        else:
            return val * len(same_dice)


class Player:

    number = 1

    def __init__(self, name, dominos, textboard):
        """
        Initializes a Player object

        :arg name: name of each player instance
        :arg dominos: a Dominos object containing a dictionary of all the dominos on the table
        :arg textboard: a Textboard object for explaining the player result at the end of the turn on the messageboard
        """
        self.name = name
        self.dominos = OrderedDict()    # dictionary to store in order the dominos each player possesses
        self.parked = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 'worm': 0}
        self.stenen = dominos           # dictionary of the current dominos available at the table
        self.number = Player.number
        self.board = textboard
        Player.number += 1

    def get_score(self):
        """:returns the total number of points from the parked dice of the player so far in a turn"""
        score = sum(self.parked.values())
        return score

    def get_worms(self):
        """
        :returns the total score of a player at a certain moment based on the stock of dominos the player possesses
        """
        worms = sum(self.dominos.values())
        return worms

    def dice_chosen(self):
        """":returns a list of the dice chosen/parked so far"""
        selected_dice = [k for k in self.parked.keys() if self.parked[k] != 0]
        return selected_dice

    def add_domino(self, score, upper_dominos, count, areas):
        """
        this method adds the domino to the stack of the current player. In case the domino that matches the turn
        score is not available anymore, a recursive call to this function is made until a lower available domino
        is found, which will then instead be added

        :arg score is the score at the end of the turn, on the basis of which a domino can be obtained
        :arg upper_dominos is a list of the upper dominos of the other players
        :arg count is used to for recursive call in case the domino is not available but a lower valued domino is
        :arg areas needs to be passed in to the .take_domino method from the Dominos object and indicates the
            screen area as coordinates (x,y) of the current player, from a Scoreboard Object

        :returns: None if s domino from the table is added to the players stock,
        :returns: domino number / score in case the domino number
        """
        try:
            self.dominos[score] = self.stenen.take_domino(score, areas)
            text = self.name + ' krijgt domino ' + str(score) + ' met waarde ' + str(self.dominos[score])
            self.board.message(text)

        except KeyError:
            dominos = [u for u in upper_dominos if u is not None]
            if count == 0:
                count += 1
                for d in dominos:
                    if d[0] == score:
                        self.dominos[score] = d[1]
                        return d[0]
            # recursive call to function to find next available domino
            self.add_domino(score-1, upper_dominos, count, areas)

    def get_upper_domino(self):
        """:returns the upper domino of the stock of dominos of a player, if no upper domino available returns None"""
        try:
            upper_domino = list(self.dominos.items())[-1]
            steen = upper_domino[0]
            value = upper_domino[1]
            return steen, value
        except IndexError:
            return

    def put_back_domino(self, areas):
        """
        :arg areas indicates the screen area as coordinates (x,y) of the current player, from a Scoreboard Object

        This method returns the upper domino of a player, if he possesses dominos back to the table and updates all
        screen locations: 1) domino returned on the table, 2) new upper_domino, or blank at the player Scoreboard
        """
        try:
            domino, value = self.get_upper_domino()
            text3 = self.name + ' heeft domino ' + str(domino) + ' teruggelegd'
            self.board.message(text3)                   # output turn action to messageboard
            self.stenen.return_domino(domino, value)    # move upper domino to start position
            self.dominos.__delitem__(domino)            # delete upper domino from self.dominos
            if not self.dominos:
                # If there is no domino below, then restore the BG surface color
                redraw = pygame.Surface([100, 200])
                redraw.fill(BG)
                screen.blit(redraw, areas)
            else:
                domino, value = self.get_upper_domino()
                screen.blit(self.stenen.surf[domino], areas)
        except TypeError:
            pass

    def lost_upper_domino(self, lost_domino, areas):
        """
        :arg lost_domino: is a domino number (int), e.g 24
        :arg areas: indicates the screen area as coordinates (x,y) of the current player, from a Scoreboard Object

        This method updates a player stack of domino's in case the current player can steal a domino from a player
        """
        try:
            # delete the domino a player just lost from it's stack of dominos
            self.dominos.__delitem__(lost_domino)
            # update the screen with the new upper domino of the player stack
            if self.get_upper_domino() is not None:
                domino, value = self.get_upper_domino()
                screen.blit(self.stenen.surf[domino], areas)
            else:
                # If there is no domino below, then restore the BG surface color
                redraw = pygame.Surface([100, 200])
                redraw.fill(BG)
                screen.blit(redraw, areas)
            self.get_worms()
            return self.name
        except KeyError:
            pass

    def reset_turn(self):
        """reset a players parked dice at the end of a turn"""
        self.parked = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 'worm': 0}


class Dominos:
    def __init__(self):
        """
        intializes a Dominos object by creating a dictionary of all dominos called dominoVals

        :arg self.dominoVals: key, value pairs represent the domino number and value (expressed in nr of worms)
        """
        self.path = PATH + "/images/"
        self.dominoVals = {21: 1, 22: 1, 23: 1, 24: 1, 25: 2, 26: 2, 27: 2, 28: 2,
                           29: 3, 30: 3, 31: 3, 32: 3, 33: 4, 34: 4, 35: 4, 36: 4}
        # self.dominoVals = {21: 1, 22: 2}  # for testing only

        # generate pygame image objects to create dominos on the screen
        self.surf, self.rect = {}, {}
        for k in self.dominoVals.keys():
            self.surf[k] = pygame.image.load(self.path + f"{k}.png").convert()
            self.rect[k] = self.surf[k].get_rect(topleft=(50 + 100 * (k - 21), 35))
            screen.blit(self.surf[k], self.rect[k])

    def get_dominos(self):
        """:returns the dominos on the table (dictionary)"""
        return self.dominoVals

    def take_domino(self, score, areas):
        """
        :arg score: integer that is the total value of the parked dice, which corresponde to a certain domino number
        :arg areas: indicates the screen area as coordinates (x,y) of the current player, from a Scoreboard Object

        :returns the domino value (value in worms) of the taken domino, and at the same time removes the domino
            key, value pair from the self.dominosVals dictionary
        TODO:
        """
        # remove the domino image from the table
        erase_domino = pygame.Surface([100, 200])
        erase_domino.fill(BG)
        screen.blit(erase_domino, self.rect[score])
        # output the domino to the scoreboard area from the current player
        screen.blit(self.surf[score], areas)
        return self.dominoVals.pop(score)

    def return_domino(self, domino, value):
        """
        :arg domino: integer with the domino number
        :arg value: integer with the domino value in worms

        method adds a domino that a player just lost back on the table
        """
        if domino:
            self.dominoVals[domino] = value
            screen.blit(self.surf[domino], self.rect[domino])
        else:
            print('je hebt geen stenen om terug te leggen')

    def delete_domino(self):
        """method deletes the highest domino from the table and updates the screen with the backside of the domino"""
        domino = max(self.dominoVals.keys())
        backside = pygame.image.load(self.path + "backside.png").convert()
        screen.blit(backside, self.rect[domino])
        self.dominoVals.__delitem__(domino)

    def get_lowest_domino(self):
        """:returns the lowest domino value on the table"""
        return min(self.dominoVals.keys())

    def get_highest_domino(self):
        """:returns the highest domino value on the table"""
        return max(self.dominoVals.keys())

    def __len__(self):
        """sets the len method for the dominos on the table"""
        return len(self.dominoVals)

    def __str__(self):
        return 'Beschikbare Stenen: ' + str(self.dominoVals)


class Button:

    font1 = pygame.font.SysFont('cambria', 25)

    def __init__(self, color, x, y, width, height, text=''):
        """
        :arg color: pygame.Color object
        :arg x, y: integers for button rect x,y -ccordinates
        :arg width, height: integers for button rect width and height
        :arg text: a string that contains the text on the button object
        """
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, win, outline=True):
        """
        :arg win: pygame window object where the button is to be placed on
        :arg outline: boolean that defines whether or not the button has an outline or not

        Call this method to draw the button on the screen
        """
        if outline:
            pygame.draw.rect(win, BLUE, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)

        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)

        if self.text != '':
            text = Button.font1.render(self.text, True, BLACK)
            win.blit(text, (
            self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    def isOver(self, pos):
        """
        :arg Pos is the mouse position or a tuple of (x,y) coordinates

        Call this method to check if the mouse position is over the button or not
        """
        if self.x < pos[0] < self.x + self.width:
            if self.y < pos[1] < self.y + self.height:
                return True
        return False

    def get_xpos(self):
        """:returns a tuple containing the x-coordinates spanning the button"""
        x = (self.x, self.x + self.width)
        return x

    def get_ypos(self):
        """:returns a tuple containing the y-coordinates spanning the button"""
        y = (self.y, self.y + self.height)
        return y


class Scoreboard:

    font1 = pygame.font.SysFont('cambria', 35)
    font2 = pygame.font.SysFont('cambria', 72)

    def __init__(self, players):
        """
        :arg players: a list of Player objects

        Method initializes:
        - A Scoreboard instance that creates a lay-out based on the number of players in the game
        - Updates the scores and highlights the current player
        - Handles the end of game event
        """
        self.players = players
        self.coordinates = []
        self.max_score = 0
        self.current_leader = None
        self.init_board()

    def init_board(self):
        """Generates the coordinates for players and score display, stored in self.coordinates"""
        x = SCREEN_WIDTH / 2 - 80
        for i in range(len(self.players)):
            if len(self.players) % 2 == 0:
                if i < len(self.players)/2:
                    coords = ((x - (i+1) * 300), 680)
                else:
                    coords = ((x + (i+1-len(self.players)/2) * 300), 680)
            else:
                if i <= len(self.players)//2:
                    coords = ((x - (len(self.players)//2 - i) * 300), 680)
                else:
                    coords = ((x + (i - len(self.players)//2) * 300), 680)
            self.coordinates.append(coords)

    def current_player(self, j):
        """
        :arg j: integer that holds the index of the current player in the game loop

        Call this method to highlight the current player and update the players scores
        """
        erase_score = pygame.Surface([250, 55])
        erase_score.fill(BG)
        for i in range(len(self.players)):
            score = self.players[i].get_worms()

            # Highlight name and score of the current player
            if i == j:
                text = Scoreboard.font1.render(self.players[i].name + ': ' + str(score), True, BLACK, RED)
            else:
                text = Scoreboard.font1.render(self.players[i].name + ': ' + str(score), True, BLACK, BG)
            coords = (self.coordinates[i][0], self.coordinates[i][1] - 70)
            screen.blit(erase_score, coords)
            screen.blit(text, coords)

            # Keep track of the leader and the leading score for the end_of_game screen
            if score > self.max_score:
                self.max_score = score
                self.current_leader = self.players[i].name
            elif self.current_leader is None:
                self.current_leader = 'Niemand'

    def end_of_game(self):
        """
        This method is called at after all the dominos have been taken by the players and creates an end screen
        displaying the winner. It also adds a Button object that can be used to start a new game

        :returns a Button object on the end_of_game screen to start a new game
        """
        # set-up content for end of game screen
        screen.fill(BG)
        text1 = Scoreboard.font2.render(self.current_leader + " heeft gewonnen!!", True, WHITE)
        text2 = Scoreboard.font1.render("met een score van: " + str(self.max_score), True, WHITE)
        b_x, b_y = 200, 70
        button = Button(LBLUE, (SCREEN_WIDTH-b_x) / 2, 700, b_x, b_y, 'Nieuw Spel')

        # position and update the screen
        x1, x2 = text1.get_width()/2, text2.get_width()/2
        screen.blit(text1, (SCREEN_WIDTH / 2 - x1, SCREEN_HEIGHT / 2 - 100))
        screen.blit(text2, (SCREEN_WIDTH / 2 - x2, SCREEN_HEIGHT / 2))
        button.draw(screen)
        return button

    def get_coords(self):
        """:returns a list of coordinates of the scoreboard of each player"""
        return self.coordinates


class Textboard:

    font1 = pygame.font.SysFont('cambria', 25)

    def message(self, text):
        """Class to create the white TextBoard object to display game actions at the bottom of the game window"""

        # Clear textboard
        message_area = pygame.Surface([SCREEN_WIDTH, 70])
        message_area.fill(WHITE)
        screen.blit(message_area, (0, SCREEN_HEIGHT - 70))

        # Output message to textboard
        text = Textboard.font1.render(text, True, BLACK)
        loc = (SCREEN_WIDTH/2 - text.get_width()/2, SCREEN_HEIGHT - 50)
        screen.blit(text, loc)


def init_display():
    """
    This method is called from the main game loop to initialize the main pygame window. Further it defines a set of
    global variables used to draw and update the main game window and
    """

    # Define constants for the screen width and height
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen, message_area
    global BG, WHITE, BLACK, LBLUE, BLUE, RED

    # Set the vars for the window size
    SCREEN_WIDTH = 1700
    SCREEN_HEIGHT = 1000

    # colors for backgrounds
    BG = pygame.Color('lightcyan4')
    WHITE = pygame.Color('white')
    BLACK = pygame.Color('black')
    LBLUE = pygame.Color('lightcyan2')
    BLUE = pygame.Color('lightcyan3')
    RED = pygame.Color('brown1')  # FF4040

    # set the pygame main window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.fill(BG)  # Fill the background with background color
    message_area = pygame.Surface([SCREEN_WIDTH, 70])
    message_area.fill(WHITE)


def throw_dice(throw, textboard, players, dominos, i, player_areas, turn, one_round):
    """
    :arg throw: an instance of a Throw object containing the 8 Die objects
    :arg textboard: an instance of a Textboard object
    :arg players: list containing all instances of Player objects
    :arg i: integer representing index of current player
    :arg player_areas: a list of coordinates of the scoreboard screen area allocated to each player
    :arg turn: boolean to stop a turn of a player
    :arg one_round: boolean that controls the pygame loop of one turn of a player

    :returns updated turn booleans turn, dice_taken, one_round and select
    """
    dice_taken = False

    # if dices left, roll a new die
    for k in throw.get_throw.keys():
        if throw.get_throw[k].get_value() != 0:
            screen.blit(throw.get_throw[k].roll(), throw.get_throw[k].rect)

    # counter for selecting the same dice in one throw
    select = False

    # create list that stores the dice left allowed to chose for the next throw
    options_left = [d for d in throw.check_throw() if d not in players[i].dice_chosen() and d != 0]

    # check if new rolling of dices is allowed
    if len(options_left) == 0:
        text1 = 'Geen keuzes meer, je verliest je bovenste dominosteen'
        textboard.message(text1)
        highest_domino_before = dominos.get_highest_domino()
        players[i].put_back_domino(player_areas[i])
        highest_domino_after = dominos.get_highest_domino()
        if highest_domino_before == highest_domino_after:
            dominos.delete_domino()
        turn = False
        one_round = False
        players[i].reset_turn()

    return turn, dice_taken, one_round, select


def stop_turn(textboard, players, dominos, i, player_areas, steal_options, upper_dominos, min_score, turn, one_round):
    """
    :arg textboard: an instance of a Textboard object
    :arg players: list containing all instances of Player objects
    :arg dominos: an instance of a Dominos object
    :arg i: integer representing index of current player
    :arg player_areas: a list of coordinates of the scoreboard screen area allocated to each player
    :arg steal_options: list of upper_dominos numbers from the other players
    :arg upper_dominos: list of upper_dominos from the other players
    :arg min_score: integer representing the lowest domino number on the table at that moment, which gives the
        minimum turn score at that moment
    :arg turn: boolean to stop a turn of a player
    :arg one_round: boolean that controls the pygame loop of one turn of a player

    :returns updated turn booleans one_round and turn. Also :returns integer the players turn score
    """
    # Obtain players score based on dice
    score = players[i].get_score()

    # Check if score is not in steal options
    if score not in steal_options:
        # check if score is invalid: too low or no worm in throw
        if score < min_score or 'worm' not in players[i].dice_chosen():
            text1 = 'Je score: ' + str(score) + ' is of te laag, of je hebt nog geen worm gegooid'
            textboard.message(text1)
            return one_round, turn, score

    # Check if worm is part of the throw, end turn and put_back upper domino and remove highest domino on the table
    if 'worm' not in players[i].dice_chosen():
        text2 = 'Je hebt geen worm gegooid, je verliest je bovenste dominosteen'
        textboard.message(text2)
        players[i].put_back_domino(player_areas[i])
        dominos.delete_domino()
        one_round = False
        turn = False
        players[i].reset_turn()
    else:
        # add domino to the current player based on the score, returns None if domino comes from the table
        count = 0
        stolen_domino = players[i].add_domino(score, upper_dominos, count, player_areas[i])
        if stolen_domino is not None:
            for j in range(len(players)):
                if j != i:
                    name = players[j].lost_upper_domino(stolen_domino, player_areas[j])
                    if name:
                        text3 = players[i].name + ' heeft domino ' + str(score) + ' van ' + name + ' afgepakt'
            textboard.message(text3)
        one_round = False
        turn = False
        players[i].reset_turn()
    return one_round, turn, score


def play_game(names, game):
    """
    :arg names: list of strings containing the names of the players of the games. Length of the is the nr of players
    :keyword game: boolean to control the outer game loop

    This function is the main game loop using all classes and helper functions defined in this file. It is called from
    the game_menu.py file that contains PyQt5 UI's to start the game. At the end of a game, a new game can be started
    from this function by a recursive call.
    """
    # Initialize pygame window
    init_display()

    # Initialize dominos, textboard and player objects
    dominos = Dominos()
    screen.blit(message_area, (0, SCREEN_HEIGHT - 70))
    textboard = Textboard()
    players = []
    for i in range(len(names)):
        players.append(Player(names[i], dominos, textboard))

    # Create instance of player scoreboard
    scoreboard = Scoreboard(players)
    player_areas = scoreboard.get_coords()

    # Create play buttons
    throw_button = Button(LBLUE, 100, 400, 200, 70, 'Dobbelen')
    throw_button.draw(screen, outline=True)
    stop_button = Button(LBLUE, 1400, 400, 200, 70, 'Stop')
    stop_button.draw(screen, outline=True)

    # Main game loop
    while game:

        # Event loop that handles starting a new game or quit after finishing a game
        for ev in pygame.event.get():

            # Loop one round of the game over all players
            for i in range(len(players)):
                # Highlight active player
                scoreboard.current_player(i)

                # Check if there are any dominos left. If not then end the game
                try:
                    min_score = dominos.get_lowest_domino()
                except ValueError:
                    # create a new_game Button object, which will be checked after breaking out of this loop
                    new_game = scoreboard.end_of_game()
                    pygame.display.flip()
                    break

                # create a list with upper_dominos of all other players that can be stolen
                upper_dominos = [players[j].get_upper_domino() for j in range(len(players)) if j != i]
                steal_options = [ud[0] for ud in upper_dominos if ud is not None]

                # reset turn booleans to start a new turn for the current player
                turn = True  # Stops one turn of a player and determines the turn score
                dice_taken = False  # Ensures rolling new dice can only be done after selecting min of 1 die
                select = False  # Ensures that only one die is selected per throw and not more
                one_round = True # Stops one game_round and breaks out of loop to move to next player

                # Start with 8 dices in the new round
                throw = Throw()

                # Loop that plays one_round for the current player
                while one_round:
                    # check keyboard input
                    for event in pygame.event.get():

                        # check for keydown events escape to exit, space for new throw or 's' to stop turn
                        if event.type == KEYDOWN:
                            # Was it the Escape key? If so, stop the loop.
                            if event.key == K_ESCAPE:
                                game = False
                                one_round = False
                                pygame.quit()

                            # Roll dice that are not parked
                            elif event.key == K_SPACE and turn and dice_taken:
                                turn, dice_taken, one_round, select = \
                                    throw_dice(throw, textboard, players, dominos, i, player_areas, turn, one_round)

                            # user can press 's' to stop the rolling of dice and get score to select domino
                            elif event.key == K_s:
                                one_round, turn, score = stop_turn(textboard, players, dominos, i, player_areas,
                                                                   steal_options, upper_dominos, min_score,
                                                                   turn, one_round)

                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            # get the position of the mouse click
                            x, y = pygame.mouse.get_pos()

                            # get positions of play butttons
                            throw_xpos = throw_button.get_xpos()
                            throw_ypos = throw_button.get_ypos()
                            stop_xpos = stop_button.get_xpos()
                            stop_ypos = stop_button.get_ypos()

                            # check if throw_button has been clicked
                            if throw_xpos[0] < x < throw_xpos[1] and turn and dice_taken:
                                if throw_ypos[0] < y < throw_ypos[1]:
                                    # Roll dice that are not parked
                                    turn, dice_taken, one_round, select = \
                                        throw_dice(throw, textboard, players, dominos, i, player_areas, turn, one_round)

                            # check if stop_button has been clicked
                            if stop_xpos[0] < x < stop_xpos[1]:
                                if stop_ypos[0] < y < stop_ypos[1]:
                                    # take domino and stop current turn
                                    one_round, turn, score = stop_turn(textboard, players, dominos, i, player_areas,
                                                                       steal_options, upper_dominos, min_score,
                                                                       turn, one_round)

                            # check if a die has been clicked and freeze die
                            for k in throw.get_throw.keys():
                                # check if a user has clicked on a die
                                if throw.get_throw[k].rect.left < x < throw.get_throw[k].rect.right:
                                    if throw.get_throw[k].rect.top < y < throw.get_throw[k].rect.bottom:

                                        # check if selected die is allowed
                                        val = throw.get_throw[k].get_value()
                                        try:
                                            if players[i].parked[val] == 0 and not select:
                                                # get score based on the chosen dice
                                                score = throw.calculate_score(k)
                                                players[i].parked[val] = score
                                                dice_taken = True
                                                select = True
                                        except KeyError:
                                            pass

                        elif event.type == QUIT:
                            game = False

                        # Flip the display
                        pygame.display.flip()

            # Check at the end of a game, whether the players would like to play a new game
            pos = pygame.mouse.get_pos()
            if ev.type == MOUSEBUTTONDOWN:
                if new_game.isOver(pos):
                    # recursive call to play_game to restart the game
                    play_game(names, game)

            elif ev.type == QUIT:
                game = False

            # flip the display
            pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    startmenu = StartMenu(play_game)
    startmenu.show()
    sys.exit(app.exec_())
