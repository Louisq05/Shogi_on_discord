import discord
import random
from discord.ext import commands
import pandas as pd # pandas pour l'affichage du game_state en tableau

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)

games = {} # stockage des partie

# Création des variables___________________


game_state = starting_game = [ #Board rangée (FR)
    ["L", "C", "A", "O", "R", "O", "A", "C", "L"],
    ["☐", "T", "☐", "☐", "☐", "☐", "☐", "F", "☐"],
    ["P", "P", "P", "P", "P", "P", "P", "P", "P"],
    ["☐", "☐", "☐", "☐", "☐", "☐", "☐", "☐", "☐"],
    ["☐", "☐", "☐", "☐", "☐", "☐", "☐", "☐", "☐"],
    ["☐", "☐", "☐", "☐", "☐", "☐", "☐", "☐", "☐"],
    ["p", "p", "p", "p", "p", "p", "p", "p", "p"],
    ["☐", "f", "☐", "☐", "☐", "☐", "☐", "t", "☐"],
    ["l", "c", "a", "o", "j", "o", "a", "c", "l"]
]


player_pieces = "plcaojft" #Pièces du joueur
player_reserve = []
opponent_pieces =  "PLCAORFT"#Pièces de l'opposant 
opponent_reserve = []

# Placeholder pour les parties en cours
games = {}

# Fonction de formatage du plateau
def format_board(board):
    return "\n".join(" ".join(row) for row in board)


@bot.command()
async def test(context):
    await context.send("hello")

# Initialisation d'une partie
@bot.command(name="shogi")
async def shogi(ctx):
    if ctx.channel.id in games:
        await ctx.send("Une partie est déjà en cours dans ce canal !")
    else:
        starting_game = [ 
            ["L", "C", "A", "O", "R", "O", "A", "C", "L"],
            ["☐", "T", "☐", "☐", "☐", "☐", "☐", "F", "☐"],
            ["P", "P", "P", "P", "P", "P", "P", "P", "P"],
            ["☐", "☐", "☐", "☐", "☐", "☐", "☐", "☐", "☐"],
            ["☐", "☐", "☐", "☐", "☐", "☐", "☐", "☐", "☐"],
            ["☐", "☐", "☐", "☐", "☐", "☐", "☐", "☐", "☐"],
            ["p", "p", "p", "p", "p", "p", "p", "p", "p"],
            ["☐", "f", "☐", "☐", "☐", "☐", "☐", "t", "☐"],
            ["l", "c", "a", "o", "j", "o", "a", "c", "l"]
        ]

        games[ctx.channel.id] = {"board": starting_game, "turn": "player1"}
        await ctx.send("Partie de shogi démarrée ! À Player1 de jouer.")
        await ctx.send(format_board(starting_game))

# Fonctions du jeu_________________________
def format_board(game_state):
    board_str = "\n".join([" ".join(row) for row in game_state])
    board_str = board_str + f"\n{player_reserve}\n{opponent_reserve}"
    return f"```{board_str}```"

def same_team(game_state, starting_x, starting_y, ending_x, ending_y, player_pieces, opponent_pieces): #Vérifie si les deux pièces appartiennent au même joueur (soit au joueur, soit à l'adversaire).

    start_piece = game_state[starting_y][starting_x] #Pièce de départ
    end_piece = game_state[ending_y][ending_x] #Pièces d'arrivé
    
    # Vérifie si les deux pièces appartiennent au joueur ou à l'adversaire
    if (start_piece in player_pieces and end_piece in player_pieces) or \
       (start_piece in opponent_pieces and end_piece in opponent_pieces):
        return True
    return False

def empty_column (game_state, starting_x, starting_y, ending_y) :
    print(starting_y)
    print(game_state[8][8])
    if game_state[starting_y][starting_x] in player_pieces :
        for i in range(ending_y-starting_y) :
            if game_state[i][starting_x] != "☐" :
                return False
    if game_state[starting_y][starting_x] in opponent_pieces: 
        for i in range(starting_y-ending_y) :
            if game_state[i][starting_x] != "☐" :
                return False
    return True

def is_valid_diagonal( starting_x, starting_y, ending_x, ending_y):
        """Vérifie si le déplacement est sur une diagonale."""
        return abs(ending_x - starting_x) == abs(ending_y - starting_y)

def is_path_clear( game_state, starting_x, starting_y, ending_x, ending_y):
        """
        Vérifie si le chemin est dégagé entre le point de départ et le point d'arrivée.
        Retourne True si dégagé, sinon False.
        """
        step_x = 1 if ending_x > starting_x else -1
        step_y = 1 if ending_y > starting_y else -1

        x, y = starting_x + step_x, starting_y + step_y
        while (x, y) != (ending_x, ending_y):
            if game_state[y][x] != "☐":  # Case non vide
                return False
            x += step_x
            y += step_y
        return True

def move_a_piece(game_state, starting_x, starting_y, ending_x, ending_y): #Déplace une pièce

    if game_state[starting_y][starting_x] == "☐":  # Case vide de départ
        raise ValueError("La case de départ est vide.")
    
    if game_state[ending_y][ending_x] != "☐":  # Case de destination déjà occupée
        if same_team(game_state, starting_x, starting_y, ending_x, ending_y, player_pieces, opponent_pieces): #Case de déstination occupéé par un teammate
            raise ValueError("Vous ne pouvez pas déplacer une pièce sur une case occupée par une autre pièce de votre équipe.")
        else :
            if game_state[ending_y][ending_x] in player_pieces :
                opponent_reserve.append(game_state[ending_y][ending_x])
            elif game_state[ending_y][ending_x] in opponent_pieces :
                player_reserve.append(game_state[ending_y][ending_x])

    
    
    game_state[starting_y][starting_x], game_state[ending_y][ending_x] =  "☐", game_state[starting_y][starting_x] # Effectuer le déplacement

    return game_state

#Zone classes des pièces__________

class Pion () :
    def __init__(self,starting_x,starting_y) : #Self, coordonnées de départ du pion 
        self.starting_x = starting_x # x de départ
        self.starting_y = starting_y # y de départ
    def Deplacement_x(self,starting_x) : # Déplacement en x
        return starting_x # le x ne change pas (pion)
    def Deplacement_y(self,starting_y, starting_x) : # déplacement en y
        if game_state[starting_y][starting_x] in opponent_pieces:
            return (starting_y + 1) # déplacement de +1 (descend de 1)
        else :
            return (starting_y - 1) # déplacement de -1 (monte de 1)
    def Deplacement_Pion(self, starting_x, starting_y, gs) : # réel déplacement du pion (move_a_piece)
        ending_xp = Pion.Deplacement_x(self, starting_x) # Utilisation de DeplacementX
        ending_yp = Pion.Deplacement_y(self, starting_y, starting_x) # Utilisation de DeplacementY
        return move_a_piece(gs,starting_x,starting_y,ending_xp, ending_yp) # Utilisation de move_a_piece

class Cavalier () :
    def __init__(self,starting_x, starting_y, ending_x, ending_y) :
        self.starting_x = starting_x # x de départ
        self.starting_y = starting_y # y de départ
        self.ending_x = ending_x # x d'arrivé
        self.ending_y = ending_y # y d'arrivé

    def Deplacement_cavalier (self, starting_x, starting_y, ending_x, ending_y, gs) :
        if ending_x not in [starting_x+1, starting_x-1] :
            raise ValueError("Le déplacement du cavalier est interdit.")
        elif game_state[starting_y][starting_x] in opponent_pieces :
            if ending_y != starting_y+2 :
                raise ValueError("Le déplacement du cavalier est interdit.")
            else :
               return move_a_piece(gs,starting_x, starting_y, ending_x, ending_y) 
        elif game_state[starting_y][starting_x] in player_pieces :
            if ending_y != starting_y-2 :
                raise ValueError("Le déplacement du cavalier est interdit.")
            else :
                return move_a_piece(gs,starting_x, starting_y, ending_x, ending_y)
                
        else :
            return move_a_piece(gs,starting_x, starting_y, ending_x, ending_y)

class Fou:
    def __init__(self, starting_x, starting_y, ending_x, ending_y):
        self.starting_x = starting_x
        self.starting_y = starting_y
        self.ending_x = ending_x
        self.ending_y = ending_y



    def Deplacement_Fou(self, starting_x, starting_y, ending_x, ending_y, gs):
        """
        Gère le déplacement du fou sur l'échiquier.
        """
        if not is_valid_diagonal(starting_x, starting_y, ending_x, ending_y):
            raise ValueError("Le fou ne peut se déplacer que sur des diagonales.")

        if not is_path_clear(game_state, starting_x, starting_y, ending_x, ending_y):
            raise ValueError("Le chemin du fou est bloqué par une autre pièce.")
        
        target = game_state[ending_y][ending_x]

        if game_state[starting_y][starting_x] in player_pieces:
            if target in player_pieces:
                raise ValueError("Le fou ne peut pas terminer sur une case occupée par une pièce alliée.")
        # Si capture, vérifiez qu'il n'y a qu'une pièce ennemie
            if target in opponent_pieces:
                print("Capture effectuée!")
                
        if game_state[starting_y][starting_x] in opponent_pieces:
            if target in opponent_pieces:
                raise ValueError("Le fou ne peut pas terminer sur une case occupée par une pièce alliée.")
        # Si capture, vérifiez qu'il n'y a qu'une pièce ennemie
            if target in player_pieces:
                print("Capture effectuée!")

        # Déplacement effectif
        return move_a_piece(gs,starting_x, starting_y, ending_x, ending_y)



class Lancier:
    def __init__(self, starting_x, starting_y, ending_y):
        self.starting_x = starting_x
        self.starting_y = starting_y
        self.ending_y = ending_y

    def Deplacement_y(game_state, starting_x, starting_y, ending_y):
        # Check if the column is empty
        if empty_column(game_state, starting_x, starting_y, ending_y) == False:
            raise ValueError("Déplacement interdit, le lancier ne peut pas sauter par dessus une autre pièce.")
        
        # Validate direction of movement
        if game_state[starting_y][starting_x] in opponent_pieces:
            if ending_y < starting_y:
                raise ValueError("Coup interdit, le lancier ne peut pas reculer")
        elif game_state[starting_y][starting_x] in player_pieces:
            if ending_y > starting_y:
                raise ValueError("Coup interdit, le lancier ne peut pas reculer")
        
        return ending_y

    def Deplacement_Lancier(self, starting_x, starting_y, ending_x, ending_y,gs):
        ending_y = Lancier.Deplacement_y(game_state, starting_x, starting_y, ending_y)
        return move_a_piece(gs,starting_x, starting_y, ending_x, ending_y) 


class Tour:
    def __init__(self,starting_x : int, starting_y : int, ending_x : int, ending_y : int) :
        self.starting_x = starting_x
        self.starting_y = starting_y
        self.ending_x = ending_x
        self.ending_y = ending_y

    def Deplacement_x(self, starting_x : int, starting_y : int, ending_x : int) :
        if starting_x < ending_x :
            for i in range(1, abs(ending_x-starting_x)) :
                if game_state[starting_y][starting_x+i] != "☐" :
                    raise ValueError("Coup interdit, la tour ne peut pas survoler de pièce(s)")
        else :
            for i in range(1, abs(ending_x-starting_x)+1) :
                if game_state[starting_y][starting_x-i] != "☐" :
                    raise ValueError("Coup interdit, la tour ne peut pas survoler de pièce(s)")
        return ending_x
    
    def Deplacement_y(self, starting_x : int, starting_y : int, ending_y : int) :
        if starting_y > ending_y :
            for i in range(1, abs(ending_y-starting_y)) :
                if game_state[starting_y-i][starting_x] != "☐" :
                    raise ValueError("Coup interdit, la tour ne peut pas survoler de pièce(s)")
        else :
            for i in range(1, abs(ending_y-starting_y)) :
                if game_state[starting_y+i][starting_x] != "☐" :
                    raise ValueError("Coup interdit, la tour ne peut pas survoler de pièce(s)")
        return ending_y
    
    def Deplacement_Tour(self, starting_x : int, starting_y : int, ending_x : int, ending_y : int, gs) :
        if starting_x != ending_x and starting_y != ending_y :
            raise ValueError("Coup interdit : la tour bouge horizontalement ou verticalement")
        else :
            x = Tour.Deplacement_x(self, starting_x, starting_y, ending_x)
            y = Tour.Deplacement_y(self, starting_x, starting_y, ending_y)
            return move_a_piece(gs,starting_x, starting_y, x, y) 

class GeneralOr() :
    def init(self,starting_x, starting_y) :
            self.starting_x = starting_x
            self.starting_y = starting_y

    def Deplacement_GeneralOr(self, starting_x,starting_y,ending_xr, ending_yr,gs) :
        if self != 'o' and self != 'O'  :
            raise LookupError("Mauvaise commande utilisé")
        diff_x = starting_x - ending_xr
        diff_y = starting_y - ending_yr
        if abs(diff_x) > 1 :
            raise ValueError("Coup Interdit, le général d'or ne peut pas se déplacer de plus d'une colone")
        if abs(diff_y) > 1 :
            raise ValueError("Coup Interdit, le général d'or ne peut pas se déplacer de plus d'une ligne")
        if game_state[starting_y][starting_x] in opponent_pieces :
            if diff_x == 1 and diff_y == 1 :
                raise ValueError("Coup Interdit, le général d'or ne peux pas se déplacer sur cette case")
            if diff_x == -1 and diff_y == 1 :
                raise ValueError("Coup Interdit, le général d'or ne peux pas se déplacer sur cette case")
            else :
                move_a_piece(game_state,starting_x,starting_y,ending_xr,ending_yr)
        else :
            if diff_x == -1 and diff_y == -1 :
                raise ValueError("Coup Interdit, le général d'or ne peux pas se déplacer sur cette case")
            if diff_x == 1 and diff_y == -1 :
                raise ValueError("Coup Interdit, le général d'or ne peux pas se déplacer sur cette case")
            else :
                move_a_piece(gs,starting_x,starting_y,ending_xr,ending_yr)

class GeneralArgent() :
    
    def __init__(self,starting_x, starting_y) :
            self.starting_x = starting_x
            self.starting_y = starting_y
    def Promotion_General(self,starting_x,starting_y) :
        if game_state[starting_y][starting_x] in player_pieces :
            if starting_y == 0 or starting_y == 1 or starting_y == 2 :
                if game_state[starting_y][starting_x] == "A" :
                    conf = str(input("Voulez vous promouvoir en général d'or ? (Oui : promotion, Non/autre : rien)"))
                    if conf.lower() == "oui" :
                        game_state[starting_y][starting_x] = "O"
        else :
            if starting_y == 6 or starting_y == 7 or starting_y == 8 :
                if game_state[starting_y][starting_x] == "a" :
                    conf = str(input("Voulez vous promouvoir en général d'or ? (Oui : promotion, Non/autre : rien)"))
                    if conf.lower() == "oui" :
                        game_state[starting_y][starting_x] = "o"

    def Deplacement_GeneralArgent(self, starting_x,starting_y,ending_xr, ending_yr, gs) :
        diff_x = starting_x - ending_xr
        diff_y = starting_y - ending_yr
        if abs(diff_x) > 1 :
            raise ValueError("Coup Interdit, le général d'argent ne peut pas se déplacer de plus d'une colone")
        if abs(diff_y) > 1 :
            raise ValueError("Coup Interdit, le général d'argent ne peut pas se déplacer de plus d'une ligne")

        if game_state[starting_y][starting_x] in player_pieces :
            if diff_x == -1 and diff_y == 0 :
                raise ValueError("Coup Interdit, le général d'argent ne peux pas se déplacer sur cette case")
            if diff_x == 1 and diff_y == 0:
                raise ValueError("Coup Interdit, le général d'argent ne peux pas se déplacer sur cette case")
            if diff_y == -1 and diff_x == 0  :
                raise ValueError("Coup Interdit, le général d'argent ne peux pas se déplacer sur cette case")

        if game_state[starting_y][starting_x] in opponent_pieces :
            if diff_x == -1 and diff_y == 0 :
                raise ValueError("Coup Interdit, le général d'argent ne peux pas se déplacer sur cette case")
            if diff_x == 1 and diff_y == 0:
                raise ValueError("Coup Interdit, le général d'argent ne peux pas se déplacer sur cette case")
            if diff_y == 1 and diff_x == 0  :
                raise ValueError("Coup Interdit, le général d'argent ne peux pas se déplacer sur cette case")
        
        move_a_piece(gs,starting_x,starting_y,ending_xr,ending_yr)

class Roi() :
    def init(self,starting_x, starting_y) :
        self.starting_x = starting_x
        self.starting_y = starting_y
    def Deplacement_Roi(self, starting_x,starting_y,ending_xr, ending_yr, gs) :
        diff_x = starting_x - ending_xr
        diff_y = starting_y - ending_yr
        if abs(diff_x) > 1 :
            raise ValueError("Coup Interdit, le roi ne peut pas se déplacer de plus d'une colone")
        if abs(diff_y) > 1 :
            raise ValueError("Coup Interdit, le roi ne peut pas se déplacer de plus d'une ligne")
        else :
            move_a_piece(gs,starting_x,starting_y,ending_xr,ending_yr)


# Zone de "l'IA" qui joue seule 

def coups_possibles(game_state: list, starting_x: int, starting_y: int):
    coups_possibles = []
    piece = game_state[starting_y][starting_x]

    # Fonction utilitaire pour vérifier si une position est valide
    def est_valide(x, y):
        return 0 <= x < 9 and 0 <= y < 9

    # Pion
    if piece == 'P':
        if est_valide(starting_x, starting_y + 1):
            coups_possibles.append([starting_x, starting_y + 1])
        return coups_possibles

    # Cavalier
    elif piece == 'C':
        if est_valide(starting_x + 1, starting_y + 2):
            coups_possibles.append([starting_x + 1, starting_y + 2])
        if est_valide(starting_x - 1, starting_y + 2):
            coups_possibles.append([starting_x - 1, starting_y + 2])
        return coups_possibles

    # Fou
    elif piece == 'F':
        for i in range(1, 9):
            if est_valide(starting_x + i, starting_y + i):
                coups_possibles.append([starting_x + i, starting_y + i])  # Diagonale en bas à droite
            if est_valide(starting_x - i, starting_y + i):
                coups_possibles.append([starting_x - i, starting_y + i])  # Diagonale en bas à gauche
            if est_valide(starting_x + i, starting_y - i):
                coups_possibles.append([starting_x + i, starting_y - i])  # Diagonale en haut à droite
            if est_valide(starting_x - i, starting_y - i):
                coups_possibles.append([starting_x - i, starting_y - i])  # Diagonale en haut à gauche
        return coups_possibles

    # Lancier
    elif piece == 'L':
        for i in range(1, 9):
            if est_valide(starting_x, starting_y + i):
                coups_possibles.append([starting_x, starting_y + i])  # Ligne verticale vers le bas
        return coups_possibles

    # Tour
    elif piece == 'T':
        for i in range(1, 9):
            if est_valide(starting_x + i, starting_y):
                coups_possibles.append([starting_x + i, starting_y])  # Horizontal à droite
            if est_valide(starting_x - i, starting_y):
                coups_possibles.append([starting_x - i, starting_y])  # Horizontal à gauche
            if est_valide(starting_x, starting_y + i):
                coups_possibles.append([starting_x, starting_y + i])  # Vertical vers le bas
            if est_valide(starting_x, starting_y - i):
                coups_possibles.append([starting_x, starting_y - i])  # Vertical vers le haut
        return coups_possibles

    # Général d'or
    elif piece == 'O':
        directions = [
            (1, 1), (1, 0), (-1, 1), (-1, 0),
            (0, 1), (0, -1)
        ]
        for dx, dy in directions:
            if est_valide(starting_x + dx, starting_y + dy):
                coups_possibles.append([starting_x + dx, starting_y + dy])
        return coups_possibles

    # Général d'argent
    elif piece == 'A':
        directions = [
            (1, 1), (1, -1), (0, 1), 
            (-1, 1), (-1, -1)
        ]
        for dx, dy in directions:
            if est_valide(starting_x + dx, starting_y + dy):
                coups_possibles.append([starting_x + dx, starting_y + dy])
        return coups_possibles

    # Roi
    elif piece == 'R':
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:  # Exclure la case centrale (pas de mouvement nul)
                    if est_valide(starting_x + dx, starting_y + dy):
                        coups_possibles.append([starting_x + dx, starting_y + dy])
        return coups_possibles

    return coups_possibles
def armée(game_state) :
    armée = []
    for i in range(len(game_state)) :
        for j in range(len(game_state[i])) :
            if game_state[i][j] in "PLCAORFT" :
                armée.append([j, i])
    return armée
from random import randrange
def choix_piece(game_state) :
    soldats = armée(game_state)
    choix = soldats[randrange(0,len(soldats))]
    return choix
def choix_move(game_state) :
    sortie = []
    piece = choix_piece(game_state)
    sortie.append(piece)
    coups = coups_possibles(game_state, piece[0], piece[1])
    choix = coups[randrange(0,len(coups))]
    sortie.append(choix)
    return sortie
def random_move(game_state):
    while True:  # Boucle infinie qui essaie un nouveau coup jusqu'à ce qu'il réussisse
        choix = choix_move(game_state)  # Choisit un mouvement aléatoire
        coups = coups_possibles(game_state, choix[0][0], choix[0][1])  # Trouve les coups possibles pour la pièce choisie
        
        if coups:  # Si des coups possibles existent
            try:
                # Essaie de déplacer la pièce
                move_a_piece(game_state, choix[0][0], choix[0][1], choix[1][0], choix[1][1])
                break  # Si le coup réussit, on sort de la boucle
            except Exception as e:
                print(f"Erreur dans le coup {choix}: {e}. Réessayer...")
                # Si une exception est levée (coup invalide), la boucle continue et un nouveau coup est tenté
                continue

@bot.command(name="ia")
async def ia(ctx):
    if ctx.channel.id not in games:
        await ctx.send("Il n'y a pas de partie en cours dans ce canal.")
        return
    game = games[ctx.channel.id]
    game_state = game["board"]
    choix = choix_move(game_state)
    move_a_piece(game_state, choix[0][0], choix[0][1], choix[1][0], choix[1][1])

    # Changer le tour
    game["turn"] = "player2"

    # Envoyer le plateau mis à jour
    await ctx.send("L'IA a joué, à votre tour !")
    await ctx.send(format_board(game_state))
    
    # Exemple de mouvement aléatoire
    def random_move(board):
        possible_moves = []
        for y, row in enumerate(board):
            for x, cell in enumerate(row):
                if cell.isupper():  # Pièces de l'IA
                    possible_moves.append((x, y))
        if not possible_moves:
            return board  # Aucun mouvement possible
        start_x, start_y = random.choice(possible_moves)
        board[start_y][start_x] = "☐"
        board[start_y + 1][start_x] = "p"  # Exemple de nouveau positionnement
        return board

    game_state = random_move(game_state)

    # Changer le tour
    turn = game["turn"]
    game["turn"] = "player2" if turn == "player1" else "player1"

    # Envoyer le plateau mis à jour
    await ctx.send("L'IA a joué, à votre tour !")


# Mouvement des pièces
@bot.command(name="move")
async def move(ctx, x1, y1, x2, y2):
    if ctx.channel.id not in games:
        await ctx.send("Il n'y a pas de partie en cours dans ce canal.")
        return

    game = games[ctx.channel.id]
    game_state = game["board"]
    turn = game["turn"]

    # Convertir les indices en entiers
    starting_x, starting_y = int(x1), int(y1)
    ending_x, ending_y = int(x2), int(y2)

    # Validation du mouvement
    if starting_x not in range(9) or starting_y not in range(9) or ending_x not in range(9) or ending_y not in range(9):
        await ctx.send("Les coordonnées sont hors du plateau.")
        return

    piece = game_state[starting_y][starting_x]
    if piece == "☐":
        await ctx.send("La case de départ est vide.")
    if (turn == "player2" and piece.islower()) or (turn == "player1" and piece.isupper()):
        await ctx.send("Ce n'est pas votre tour.")

    
# Effectuer le mouvement
    try:
        if piece in ("p", "P"):
            game_state = Pion.Deplacement_Pion(game_state[starting_y][starting_x],starting_x,starting_y, game_state)
        if piece in ("c", "C"):
            Cavalier.Deplacement_cavalier(game_state[starting_y][starting_x],starting_x, starting_y, ending_x, ending_y, game_state)
        if piece in ("l", "L"):
            Lancier.Deplacement_Lancier(game_state[starting_y][starting_x],starting_x, starting_y, ending_x, ending_y, game_state)  
        if piece in ( "t","T"):
            Tour.Deplacement_Tour(game_state[starting_y][starting_x],starting_x, starting_y, ending_x, ending_y, game_state)
        if piece in ("f", "F"):
            Fou.Deplacement_Fou(game_state[starting_y][starting_x],starting_x, starting_y, ending_x, ending_y, game_state)
        if piece in ("o", "O"):
            GeneralOr.Deplacement_GeneralOr(game_state[starting_y][starting_x],starting_x, starting_y, ending_x, ending_y, game_state)
        if piece in ("a", "A"):
            GeneralArgent.Deplacement_GeneralArgent(game_state[starting_y][starting_x],starting_x, starting_y, ending_x, ending_y, game_state) 
        if piece in ("j", "R"):
            Roi.Deplacement_Roi(game_state[starting_y][starting_x],starting_x, starting_y, ending_x, ending_y, game_state)  
    except:
        game["turn"] = "player1" if turn == "player2" else "player2"

    # Changer le tour
    game["turn"] = "player2" if turn == "player1" else "player1"

    if "R" in player_reserve :
        await ctx.send( "Victoire du joueur 1 !!!!!!")
    elif "j" in opponent_reserve :
        game_state =  "Victoire du joueur 2 !!!!!!"
    # Envoyer le plateau mis à jour
    await ctx.send(f"Mouvement effectué de ({x1}, {y1}) à ({x2}, {y2}). C'est au tour de {game['turn']}.")
    await ctx.send(format_board(game_state))


@bot.command(name="helps")
async def helps(ctx):
    help_message = (
        "Aide au jeu : Interactions avec le bot\n"
        "======================================\n\n"
        "🎮 **Lancer le jeu :**\n\n"
        "Commande : /shogi\n"
        "Description : Cette commande démarre une nouvelle partie de Shogi dans le canal Discord. \n"
        " Vous êtes prêt à jouer !\n\n"
        "--------------------------------------\n\n"
        "♟️ **Déplacer une pièce :**\n\n"
        "Commande : /move x_départ y_départ x_arrivée y_arrivée\n"
        "Description : Effectue un déplacement en prenant la pièce située en [x_départ, y_départ] \n"
        " et en la plaçant en [x_arrivée, y_arrivée].  par Exemple /move 4 6 4 5\n"
        "⚠️ Attention : Assurez-vous que le coup est valide selon les règles du Shogi, \n"
        " sinon il sera refusé !\n\n"
        "--------------------------------------\n\n"
        "🤖 **Jouer contre l'IA :**\n\n"
        "Commande : /ia\n"
        "Description : L'IA effectue son coup automatiquement. À vous de jouer ensuite !\n\n"
        "--------------------------------------\n\n"
        "🛑 **Arrêter la partie :**\n\n"
        "Commande : /end\n"
        "Description : Termine la partie en cours. Vous pouvez ensuite relancer une nouvelle partie.\n\n"
        "======================================"
    )
    await ctx.send(help_message)

# Fin de la partie
@bot.command(name="end")
async def end_game(ctx):
    if ctx.channel.id in games:
        del games[ctx.channel.id]
        game_state=starting_game
        await ctx.send("La partie a été terminée.")
    else:
        await ctx.send("Aucune partie en cours à terminer.")


if __name__ == '__main__':
    bot.run(token="MTMxMDYyMzE0OTI3MjA3MjIwMw.G8jCO9.ybOGxl3j3HL-0gC9LCCv6FcQJA7JN1mjqAbt-Y")