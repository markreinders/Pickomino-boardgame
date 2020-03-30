import os

from PyQt5.QtWidgets import QWidget, QAbstractButton, QDialog
from PyQt5.QtWidgets import QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QMessageBox
from PyQt5.QtGui import QFont, QColor, QPixmap, QPainter
from PyQt5.QtCore import QSize

# get current working directory
PATH = os.getcwd()


class PicButton(QAbstractButton):
    def __init__(self, pixmap, pixmap_hover, pixmap_pressed, parent=None):
        """
        :arg pixmap: image file of the image button
        :arg pixmap_hover: image file button for hoover event
        :arg pixmap_pressed: images files

        Initializes a PicButton object is created to generate an image changes properties when the mouse is hovering
        and creates a clickable image
        """
        super(PicButton, self).__init__(parent)
        self.pixmap = pixmap
        self.pixmap_hover = pixmap_hover
        self.pixmap_pressed = pixmap_pressed

    def paintEvent(self, event):
        """Method detects mouse actions and changes appearance of the pixmap / image buttons"""
        pix = self.pixmap_hover if self.underMouse() else self.pixmap
        if self.isDown():
            pix = self.pixmap_pressed
            self.rules_window()

        painter = QPainter(self)
        painter.drawPixmap(event.rect(), pix)

    def sizeHint(self):
        """Method controls the size of the pixmap / image button"""
        return QSize(232, 309)

    def rules_window(self):
        """method creates an instance of a Dialogue object, in this case a window that appears to explaining the game"""
        dialog = Dialog()
        dialog.exec_()


class StartMenu(QWidget):
    def __init__(self, play_game):
        """
        :arg play_game: the main game loop function

        Initializes a PyQt5 UI window that contains a number of QLineEdit objects that are used to let the user
        specify the names of the players for a new game. The amount of player names provided is used to start the
        game with correct number of players.
        """

        super().__init__()
        path = PATH + '/images'  # Location of the image files used in the UI window
        self.game = play_game

        self.lbl_title = QLabel()
        self.lbl_title.setPixmap(QPixmap(path + '/titel_regenwormen.png'))

        self.lbl_worm = QLabel()
        self.lbl_worm.setPixmap(QPixmap(path + '/worm3.png'))
        self.lbl = []
        self.le = []
        self.lbl_0 = QLabel('Vul de namen van de spelers in:')
        self.lbl_0.setFont(QFont("Arial", 16))
        self.lbl_0.setFixedHeight(18)
        self.max_players = 6
        for i in range(self.max_players):
            self.lbl.append(QLabel(f'Speler {i + 1}: '))
            self.lbl[i].setFont(QFont("Arial", 16))
            self.le.append(QLineEdit())
            self.le[i].setFont(QFont("Arial", 16))
        self.btn = QPushButton('START GAME!')
        self.btn.setFont(QFont("Arial", 18))

        self.btn2 = PicButton(QPixmap(path + '/worm3.png'), QPixmap(path + '/worm3_hover.png'),
                              QPixmap(path + '/worm3_hover.png'))

        self.init_ui()  # Initialize the UI window

    def init_ui(self):
        """Create the main window and define the lay-out of the user interface"""
        v_layout1 = QVBoxLayout()
        h_layout1 = QHBoxLayout()
        g_layout1 = QGridLayout()

        v_layout1.addWidget(self.lbl_title)
        g_layout1.addWidget(self.lbl_0, 0, 0, 1, 2)
        for i in range(self.max_players):
            g_layout1.addWidget(self.lbl[i], i + 1, 0)
            g_layout1.addWidget(self.le[i], i + 1, 1)

        h_layout1.addLayout(g_layout1)
        h_layout1.addWidget(self.btn2)
        v_layout1.addLayout(h_layout1)
        v_layout1.addWidget(self.btn)

        self.setLayout(v_layout1)

        self.setWindowTitle('Regenwormen Start Menu')
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(122, 139, 139))
        self.setPalette(p)

        # button to eimt signal to start_game function
        self.btn.clicked.connect(self.start_game)

        self.resize(500, 650)

    def start_game(self):
        """
        This method is called from the init_ui signal send from the start_game button. Only allows the game to start
        with a minimum of 1 player
        """
        players = []
        for i in range(len(self.lbl)):
            if self.le[i].text() is not '':
                players.append(self.le[i].text())
        # Check whether at least one player name is provided, otherwise send notification using a QMessageBox object
        if len(players) != 0:
            self.close()
            self.game(players, game=True)
        else:
            msg = QMessageBox()
            msg.setWindowTitle('input required')
            msg.setText('Je moet minimaal 1 naam invullen')
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            # return False, players


class Dialog(QDialog):
    def __init__(self):
        """
        Initializes a Dialog object that explains how the game works and what controls are available to the
        players to play the games
        """

        super().__init__()
        path = PATH + '/images'  # Location of the image files used in the window
        self.lbl_title = QLabel()
        self.lbl_title.setPixmap(QPixmap(path + '/titel_regenwormen_large.png'))

        self.lbl_rules = QLabel('Spelregels')
        self.lbl_rules.setFont(QFont('arial', 20, QFont.Bold))
        self.lbl_explanation = QLabel('Het doel van het spel is om zoveel mogelijk wormen te verzamelen, dit doe je '
                                      'door domninos te pakken.\n\n Aan het begin van je beurt gooi je 8 dobbelstenen '
                                      'en selecteert dan de dobbelstenen die je opzij wil leggen om punten te '
                                      'verzamelen. Je kan na iedere worp, besluiten om \nte stoppen, of om opnieuw te '
                                      'gooien met de overgebleven dobbelstenen. Als je stopt moet je minimaal 1 worm '
                                      'in je bezit hebben en het aantal punten moet minimaal gelijk zijn \naan de '
                                      'waarde van de laagste dobbelsteen. Als je verder gooit, kun je score verder '
                                      'verhogen, je mag echter de dobbelsteen die je al opzij gelegd hebt niet meer '
                                      'kiezen \nuit je nieuwe worp. Op het moment dat je geen keuzes meer hebt na een '
                                      'nieuwe worp ben je af en moet je je bovenste dominosteen terugleggen op het '
                                      'bord en word tevens de \nhoogste beschikbare domino omgedraaid.\n\n Verder '
                                      'krijg je als bv 28 punten hebt gegooid en domino 28 niet meer beschikbaar is de '
                                      'eerstvolgende lagere domino. Als je score gelijk is aan een domino die niet op '
                                      '\ntafel ligt, maar bovenop de stapel van 1 van je tegenstanders, kun je deze '
                                      'afpakken!\n\n\n')
        self.lbl_explanation.setFont(QFont('arial', 12))
        self.lbl_controls = QLabel('Besturing')
        self.lbl_controls.setFont(QFont('arial', 20, QFont.Bold))
        self.lbl_explanation2 = QLabel('Optie 1: gebruik de buttons om te werpen en te stoppen\n'
                                       'Optie 2: gebruik "spatie" om te werpen en druk op "S" om je beurt te stoppen\n'
                                       'Na een worp, dobbelstenen selecteren kan met de muis \n'
                                       'Gebruik "escape" om tijdens het spel te stoppen\n\n'
                                       'De witte balk onderaan het scherm, laat het resultaat van de vorige beurt zien'
                                       '\nBV: "Speler 1 krijgt domino 27 met waarde 2" of\n'
                                       '"Speler 3 heeft domino 22 van Speler 2 afgepakt!"')
        self.lbl_explanation2.setFont(QFont('arial', 12))

        self.init_ui()  # Initializes the UI window

    def init_ui(self):
        """Create the main window and define the lay-out of the window"""
        v_layout1 = QVBoxLayout()

        v_layout1.addWidget(self.lbl_title)
        v_layout1.addWidget(self.lbl_rules)
        v_layout1.addWidget(self.lbl_explanation)
        v_layout1.addWidget(self.lbl_controls)
        v_layout1.addWidget(self.lbl_explanation2)

        self.setLayout(v_layout1)

        self.setWindowTitle('Spelregels en Besturing')
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(122, 139, 139))
        self.setPalette(p)

        self.resize(1200, 650)
        self.show()



