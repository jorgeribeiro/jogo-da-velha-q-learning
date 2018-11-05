import numpy as np
import tkinter as tk
import copy
import pickle as pickle

from q_jogo_da_velha import Game, HumanPlayer, QPlayer


Q = pickle.load(open("aprendizado_q_200000.p", "rb"))

root = tk.Tk()
player1 = HumanPlayer(mark="X")
player2 = QPlayer(mark="O", epsilon=0)

game = Game(root, player1, player2, Q=Q)

game.play()
root.mainloop()
