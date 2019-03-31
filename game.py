from tkinter import *
from PIL import Image, ImageTk
from os import listdir
from time import strftime, gmtime
import pickle


position_x1, position_y1 = 0, 0  # position du joueur 1 
position_x2, position_y2 = 0, 0  # position du joueur 2
bomb_timer = 3                   # début du compte a rebours des bombes
vie_player1 = 5                  # nombre de vies de départ 
vie_player2 = 5
is_dead1 = False                 # attribut qui sera donné au joueur lorsqu'il n'a plus de vie
is_dead2 = False                 
nbr_bomb1 = 10                   # nombre de bombes de départ
nbr_bomb2 = 10
door_x, door_y = 0, 0            # coordonnées de la porte (=objectif)
murs = []                        #creations de listes qui contiendront plus tard les position des murs et des bombes
murs_cassable = []
bombs = []
level = "01"                     # définit le niveau de départ
taille_x = 0                     # definit la longueur des axes: x = horizontal
taille_y = 0                     #                               y = vertical
colour_player1 = "black"         # attribue des couleurs pour les différents elements
colour_player2 = "green"
colour_mur = "brown"
colour_mur_cassable= "light grey"
colour_vide = "white"
canvas_life1 = None              # crée des variables vides qui contiendront les infos au dessus du jeu
canvas_bombs1 = None
canvas_mur_cassable = None
canvas_level = None
canvas_life2 = None
canvas_bombs2 = None
sauvgardes_list = None
cote = 24                        # definit le coté d'un carré : 24 pixels
player1, player2 = None, None
already_started = False          # conditions à verifier par après pour 'dire' au code si le jeu à démarré
already_in_menu = False          #                                                     si on est dans le menu
finished = False                 #                                                     si le jeu est terminé
start_button= None               # boutons start
save_button = None               #         save
close_button = None              #         exit


fenetre = Tk()                   # ouvre la fenetre
fenetre.title("Bomberman")       # intitule la fenetre 'Bomberman'

bomb_img = ImageTk.PhotoImage(Image.open("images/bomb.png"))
door_img = ImageTk.PhotoImage(Image.open("images/door.png"))
canvas = Canvas(fenetre, height=720, width=720)
exploded_regions = []


def update_infos():
    #met a jour les infos au dessus du jeu(=supprime et remplace par la nouvelle valeur)
    global canvas_life1, canvas_bombs1, canvas_life2, canvas_bombs2, canvas_level, canvas_mur_cassable
    canvas.delete(canvas_life1)
    canvas.delete(canvas_bombs1)
    canvas.delete(canvas_mur_cassable)
    canvas.delete(canvas_level)
    canvas.delete(canvas_life2)
    canvas.delete(canvas_bombs2)
    if vie_player1 == 0:
        vp1 = "Dead"
    else:
        vp1 = str(vie_player1)  # "str" permet d'afficher le nombre de vie sur le canvas

    if vie_player2 == 0:
        vp2 = "Dead"
    else:
        vp2 = str(vie_player2)
    canvas_life1 = canvas.create_text(50, 20, text="Lifes : " + vp1)
    canvas_bombs1 = canvas.create_text(58, 40, text="Bombs: " + str(nbr_bomb1))
    canvas_mur_cassable = canvas.create_text(350, 20, text="Walls : " + str(len(murs_cassable)))
    canvas_level = canvas.create_text(350, 40, text="Level: " + str(level))
    canvas_life2 = canvas.create_text(650, 20, text="Lifes : " + vp2)
    canvas_bombs2 = canvas.create_text(658, 40, text="Bombs: " + str(nbr_bomb2))



def kill_player(player_nb):
    #fait perdre une vie au joueur touché par une bombe. Supprime le joueur s'il n'a plus de vie
    global vie_player1, vie_player2, position_x1, position_y1, position_x2, position_y2
    global is_dead1, is_dead2
    if player_nb == 1:                          #pour le joueur 1
        vie_player1 -= 1                        #fait perdre une vie
        if vie_player1 <= 0:                    #si les vie arivent a 0
            canvas.delete(player1)              #supprime le carré du joueur du canvas
            position_x1,position_y1 = -1, -1    #déplace le joueur hors de l'écran
            is_dead1 = True                     
    else:
        vie_player2 -= 1
        if vie_player2 <= 0:
            canvas.delete(player2)
            is_dead2 = True
            position_x2,position_y2 = -1, -1


def draw_rectangle(canvas, colour, x, y):
    #dessine un carré 
    return canvas.create_rectangle(x * cote + 22, y * cote + 70, (x + 1) * cote + 22, (y + 1) * cote + 70, fill=colour)

def draw_bomb(x, y):
    #affiche une bombe (bomb.png)
    return canvas.create_image(x*cote+34,y*cote+83, image=bomb_img)

def draw_door(x, y):
    #affiche une porte (door.png)
    return canvas.create_image(x*cote+34,y*cote+83, image=door_img)


def get_bomb_text_position(x, y):
    #renvoie la position de la bombe pour centrer le compte a rebours dessus
    return x * cote + 34, y * cote + 82


def clear_exploded_regions():
    #supprime les zones explosées (jaunes) du canvas et de la liste des zones explosées tant qu'il y a au moins 1 éléments dans la liste exploded_regions
    global exploded_regions
    while len(exploded_regions) != 0:
        for reg in exploded_regions:
            canvas.delete(reg[2])
            exploded_regions.remove(reg)


def explode(bx, by):
    #colore en jaune la zone (d'explosion) autour de la bombe pendant 1 sec,stoppée par les murs, fait perdre une vie aux joueurs dans la zone, et détruit les murs cassables. 
    cordinates = []
    x, y = 1, 1
    i = -1
    while i <= y:
        pos = (bx,(by+i)%taille_y)
        if pos not in murs:
            cordinates.append(pos)
        i+=1

    j = -1
    while j <= x:
        pos = ((bx+j)%taille_x,by)
        if pos not in murs:
            cordinates.append(pos)
        j+=1
    for cord in cordinates:
        x,y = cord
        p = draw_rectangle(canvas, "yellow", x, y)
        exploded_regions.append([x,y,p])
    canvas.lift(player1)
    canvas.lift(player2)
    fenetre.after(1000, clear_exploded_regions)
    k = 0
    while k < len(murs_cassable):
        mur = murs_cassable[k]
        position = (mur[0], mur[1])
        if position in cordinates:
            canvas.delete(mur[2])
            del murs_cassable[k]
        k += 1
    pos_player1 = (position_x1, position_y1)
    pos_player2 = (position_x2, position_y2)
    if pos_player1 in cordinates:
        kill_player(1)
    if pos_player2 in cordinates:
        kill_player(2)
    update_infos()

def update_bomb_timer():
    #affiche un compte a rebours sur la bombe (démarre a 3 secondes)
    global bombs
    i = 0
    while i < len(bombs):
        bomb = bombs[i]
        bx, by =  get_bomb_text_position(bomb[0], bomb[1])
        timer = bomb[2]
        timer -= 1
        bomb_canvas = bomb[3]
        canvas.delete(bomb_canvas)
        if timer != 0:
            bomb_canvas = canvas.create_text(bx, by, text=str(timer), fill="white")
            bombs[i][3] = bomb_canvas
            bombs[i][2] = timer
        else:
            explode(bomb[0], bomb[1])
            canvas.delete(bombs[i][4])
            del bombs[i]
        i+= 1
    fenetre.after(1000, update_bomb_timer)


def move(event):
    #gère le mouvement des joueurs: assigne une touche a chaque direction (Haut-bas-gauche-droite) et (z-s-q-d) et deplace le carré du joueur dans cette direction
    global position_x1, position_y1, direction,player1, player2,  position_x2, position_y2
    keysym = event.keysym
    new_x1, new_y1 = position_x1, position_y1
    new_x2, new_y2 = position_x2, position_y2
    if keysym == "Up":
        new_y1 -= 1
    if keysym == "Down":
        new_y1 += 1
    if keysym == "Left":
        new_x1 -= 1
    if keysym == "Right":
        new_x1 += 1
    if keysym == "z":
        new_y2 -= 1
    if keysym == "s":
        new_y2 += 1
    if keysym == "q":
        new_x2 -= 1
    if keysym == "d":
        new_x2 += 1
    if already_started and not finished:                        #empeche le joueur de bouger dans les menus
        new_x1, new_y1 = new_x1%taille_x, new_y1%taille_y        # new_x1%taille_x  new_y1%taille_y permet le retour au debut de la ligne/colonne une fois au bout
        new_x2, new_y2 = new_x2%taille_x, new_y2%taille_y
        if new_x1 != position_x1 or new_y1 != position_y1:
            if is_possible_to_move(new_x1, new_y1, 1):
                canvas.move(player1,(new_x1-position_x1)*cote,(new_y1-position_y1)*cote)
                position_x1 = new_x1
                position_y1 = new_y1
                if is_in_door(position_x1, position_y1):
                    load_next_level()
        if new_x2 != position_x2 or new_y2 != position_y2:
            if is_possible_to_move(new_x2, new_y2, 2):
                canvas.move(player2,(new_x2-position_x2)*cote,(new_y2-position_y2)*cote)
                position_x2 = new_x2
                position_y2 = new_y2
                if is_in_door(position_x2, position_y2):
                    load_next_level()

def is_in_door(x, y):
    #indique que le joueur est arrivé a destination(sur la porte)
    return x == door_x and y == door_y


def load_next_level():
    #passe en niveau suivant s'il y en a, sinon termine le jeu
    global level
    level = str(level).replace("0", "")
    level = int(level) + 1
    if level <= len(listdir("./levels/")):
        level = "0" + str(level)
        load_level(level)
    else:
        load_winner_msg()


def load_winner_msg():
    #termine le jeu
    global finished, level
    canvas.delete("all")
    canvas.create_text(365,280, font=("Arial", 20), text="Finish")
    finished = True
    level = "01"

def is_possible_to_move(x,y, player_nb = 0):
    #definit les collisions: empeche le joueur de passer sur un obstacle(murs, murs cassables, bombes, autre joueur)
    position = (x,y)
    possible_to_move = True
    if position in murs:
        possible_to_move = False
    for mur in murs_cassable:
        mx,my = mur[0], mur[1]
        if mx == x and my == y:
            possible_to_move = False
            break
    if position in murs_cassable:
        possible_to_move = False
    for bomb in bombs:
        bx,by = bomb[0], bomb[1]
        if bx == x and by == y:
            possible_to_move = False
            break
    if player_nb == 1:
        if x == position_x2 and y == position_y2:
            possible_to_move = False
    elif player_nb == 2:
        if x == position_x1 and y == position_y1:
            possible_to_move = False
    return possible_to_move

def pose_bomb(event):
    #pose une bombe sur la position du joueur, a l'aide d'un raccourci clavier (espace=> joueur 1; H => joueur 2)
    global bombs, canvas, nbr_bomb1, nbr_bomb2
    keysym = event.keysym
    if not finished and already_started:
            if keysym == "space":
                new_x, new_y = position_x1, position_y1
                if is_possible_to_move(new_x, new_y) and nbr_bomb1 != 0 and not is_dead1:
                    bomb = draw_bomb(new_x, new_y)
                    canvas.lift(player1)
                    bx, by = get_bomb_text_position(new_x, new_y)
                    bomb_canvas = canvas.create_text(bx, by, text=str(bomb_timer), fill="white")
                    canvas.lift(bomb_canvas)
                    bombs.append([new_x, new_y, bomb_timer, bomb_canvas, bomb])
                    nbr_bomb1 -= 1
                    update_infos()
            else:
                new_x, new_y = position_x2, position_y2
                if is_possible_to_move(new_x, new_y) and nbr_bomb2 != 0 and not is_dead2:
                    bomb = draw_bomb(new_x, new_y)
                    canvas.lift(player2)
                    bx, by = get_bomb_text_position(new_x, new_y)
                    bomb_canvas = canvas.create_text(bx, by, text=str(bomb_timer), fill="white")
                    canvas.lift(bomb_canvas)
                    bombs.append([new_x, new_y, bomb_timer, bomb_canvas, bomb])
                    nbr_bomb2 -= 1
                    update_infos()


def load_level(current_level, dico_sauvgarde=None):
    """affiche les infos au dessus du jeu et charge un nouveau niveau - 2 methodes:
        1.(demarrage normal): ouvre un fichier .txt du dossier levels, le lit ligne par ligne, et crée le niveau en fonction de ce qu'il lit(#=mur)(*=mur cassable)(0=espace vide)(p=porte)(1 et 2= joueurs)
           + donne 10 bombes et 5 vies a chaque joueur
        2. (bouton load): charge les données d'une partie enregistrée en allant chercher les emplacements/nombres des murs/joueurs/bombes dans un dictionnaire créé à partir des infos sauvegardées par la fonction "sauvgarde()" """
    global murs, murs_cassable, bombs, player1, player2, taille_y, taille_x, position_y2, position_y1, position_x2, position_x1, door_x, door_y
    global canvas_life1, canvas_bombs1, canvas_life2, canvas_bombs2, canvas_level, canvas_mur_cassable
    global nbr_bomb2, nbr_bomb1, vie_player1, vie_player2, finished, level
    finished = False
    level_file = "./levels/" + current_level + ".txt"
    f = open(level_file)
    lines = f.readlines()
    lines = [list(line.strip()) for line in lines]
    f.close()
    taille_y = len(lines)
    taille_x = len(lines[0])
    murs[:], murs_cassable[:], bombs[:] = [], [], []
    canvas.delete("all")
    if not dico_sauvgarde:
        is_door = False
        for y in range(taille_y):
            for x in range(taille_x):
                draw_rectangle(canvas, colour_vide, x, y)
                if lines[y][x] == "#":
                    colour = colour_mur
                    murs.append((x,y))
                elif lines[y][x] == "*":
                    colour = colour_mur_cassable
                elif lines[y][x] == "1":
                    position_x1, position_y1 = x, y
                    colour = colour_player1
                elif lines[y][x] == "2":
                    position_x2, position_y2 = x, y
                    colour = colour_player2
                elif lines[y][x] == "p":
                    door_x, door_y = x,y
                    is_door = True
                else:
                    colour = colour_vide
                p = draw_rectangle(canvas, colour, x, y)
                canvas.lift(p)

                if is_door:
                    p = draw_door(x, y)
                    canvas.lift(p)
                    is_door = False
                if lines[y][x] == "1":
                    player1 = p
                elif lines[y][x] == "2":
                    player2 = p
                elif lines[y][x] == "*":
                    murs_cassable.append([x,y,p])
                nbr_bomb1 = 10
                nbr_bomb2 = 10
                vie_player1 = 5
                vie_player2 = 5
    else:
        nbr_bomb1 = dico_sauvgarde["player1"]["bombs"]
        nbr_bomb2 = dico_sauvgarde["player2"]["bombs"]
        vie_player1 = dico_sauvgarde["player1"]["life"]
        vie_player2 = dico_sauvgarde["player2"]["life"]
        position_x1 = dico_sauvgarde["player1"]["x"]
        position_y1 = dico_sauvgarde["player1"]["y"]
        position_x2 = dico_sauvgarde["player2"]["x"]
        position_y2 = dico_sauvgarde["player2"]["y"]
        level = dico_sauvgarde["level"]
        door_x = dico_sauvgarde["door"]["x"]
        door_y = dico_sauvgarde["door"]["y"]
        player1 = draw_rectangle(canvas, colour_player1, position_x1, position_y1)
        player2 = draw_rectangle(canvas, colour_player2, position_x2, position_y2)
        draw_rectangle(canvas, colour_vide, door_x, door_y)
        p = draw_door(door_x, door_y)
        murs_cassable = dico_sauvgarde["murs_cassable"]
        for mur in murs_cassable:
            x,y = mur[0], mur[1]
            mur[2] = draw_rectangle(canvas, colour_mur_cassable, x, y)
        for y in range(taille_y):
            for x in range(taille_x):
                if is_possible_to_move(x,y):
                    draw_rectangle(canvas, colour_vide, x, y)
                if lines[y][x] == "#":
                    murs.append((x,y))
                    draw_rectangle(canvas, colour_mur, x, y)
                elif lines[y][x] == "p":
                    p = draw_door(x, y)
                    canvas.lift(p)

    canvas.lift(player1)
    canvas.lift(player2)

    canvas_life1 = canvas.create_text(50, 20, text="Lifes : " + str(vie_player1))
    canvas_bombs1 = canvas.create_text(58, 40, text="Bombs: " + str(nbr_bomb1))
    canvas_mur_cassable = canvas.create_text(350, 20, text="Walls : " + str(len(murs_cassable)))
    canvas_level = canvas.create_text(350, 40, text="Level: " + str(level))
    canvas_life2 = canvas.create_text(650, 20, text="Lifes : " + str(vie_player2))
    canvas_bombs2 = canvas.create_text(658, 40, text="Bombs: " + str(nbr_bomb2))

def start_game():
    #lance ou reprend le jeu
    load_level(level)
    resume_game()


def sauvgarde():
    #enregistre les positions des objets dans un fichier "date_et_heure.sauvgarde" (dans le dossier sauvgarde) pour etre par-après ouvert par la fonction précédente "load_level"
    fichier = "./sauvgarde/" + strftime("%d-%m-%Y_%H-%M-%S", gmtime()) + ".sauvgarde"
    fichier_objet = open(fichier, "wb")
    pickle.dump({
        "bombs": bombs,
        "murs_cassable": murs_cassable,
        "level" : level,
        "door" : {
            "x" : door_x,
            "y" : door_y
        },
        "player1"  : {
            "life" : vie_player1,
            "bombs" : nbr_bomb1,
            "x" : position_x1,
            "y" : position_y1
        },
        "player2"  : {
            "life" : vie_player2,
            "bombs" : nbr_bomb2,
            "x" : position_x2,
            "y" : position_y2
        }
    }, fichier_objet)
    fichier_objet.close()


def start_menu(event=None):
    """gère les boutons du menu: 
        (de base) Start -- Load -- Exit
        (si le jeu a commencé) Resume -- Save -- Exit"""
    global start_button, save_button, close_button, already_in_menu
    global sauvgardes_list
    canvas.grid_forget()
    if not already_in_menu:
        already_in_menu = True
        if already_started and not finished:
            start_button = Button(fenetre, text="Resume", command=resume_game)
            start_button.grid(row=0,column=0)
        else:
            start_button = Button(fenetre, text="Start", command=start_game)
            start_button.grid(row=0,column=0)
        if already_started and not finished:
            save_button = Button(fenetre, text="Save", command=sauvgarde)
            save_button.grid(row=1,column=0)
        else:
            save_button = Button(fenetre, text="Load", command=load)
            sauvgardes_list = Listbox(fenetre, height=2, selectmode=SINGLE)
            levels = listdir("./sauvgarde/")
            if len(levels) != 0:
                save_button.grid(row=1,column=0)
                for level in levels:
                    sauvgardes_list.insert(END, level)
                sauvgardes_list.grid(row=1, column=1)

        close_button = Button(fenetre, text="Exit", command=fenetre.destroy)
        close_button.grid(row=2,column=0)
    else:
        resume_game()

def load():
    #s'il y a une sauvegarde, cherche dans le dossier "sauvgarde", ouvre le fichier avec pickle puis charge le niveau avec la fonction "load_level" définie plus haut(ligne 308) puis (re)lance le jeu
    if len(sauvgardes_list.curselection()) > 0:
        index = sauvgardes_list.curselection()[0]
        sauvgarde_file = "./sauvgarde/" + sauvgardes_list.get(index,index)[0]
        file_object = open(sauvgarde_file, "rb")
        liste = pickle.load(file_object)
        file_object.close()
        level = liste["level"]
        load_level(level, liste)
        resume_game()

def resume_game():
    #fais disparaitre les boutons du menu, et reforme la grille du jeu
    global already_started, already_in_menu
    start_button.grid_forget()
    save_button.grid_forget()
    close_button.grid_forget()
    sauvgardes_list.grid_forget()
    canvas.grid(row=0, column=0, rowspan=1)
    already_in_menu = False
    already_started = True
    
start_menu()
fenetre.minsize(width=750, height=580)  #fixe les dimensions de la fenetre
fenetre.maxsize(width=750, height=580)
fenetre.bind("<Left>", move)            #associe les raccourcis clavier aux actions des joueurs
fenetre.bind("<Right>", move)
fenetre.bind("<Escape>", start_menu)
fenetre.bind("<Up>", move)
fenetre.bind("<Down>", move)
fenetre.bind("<q>", move)
fenetre.bind("<d>", move)
fenetre.bind("<z>", move)
fenetre.bind("<s>", move)
fenetre.bind("<space>", pose_bomb)
fenetre.bind("<h>", pose_bomb)
fenetre.after(1000, update_bomb_timer)  #compte à rebours: effectue la fonction update_bomb_timer chaque seconde
fenetre.mainloop()                      #garde la fenetre ouverte
