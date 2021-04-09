import numpy as np
from random import random, choice
from math import log, sqrt
from Board import Board
from copy import deepcopy
from time import time

"""
MCTS Class: Performs a Monte Carlo Tree Search on a given board to find the best next move
Takes in the following parameters:
    - current_board: The board at the current game state
    - player: The game player it is trying to find the best next move for
    - exploration_parameter: Parameter defined in the MCTS algorithm
    - intelligence_parameter: Paramter determining with what probability the opponent will choose
        a best move instead of a random move during the "selection" step of the MCTS algorithm. 
        This helps to avoid paths that look like the AI would win most of the time but are very 
        unlikely to happen if the opponent has some level of intelligence (picks a color that blocks
        the AI from following that game path). 
"""
class MCTS: 
    def __init__(self, current_board, player, 
                 exploration_parameter = 2, intelligence_parameter = 0.5):
        self.game_board = deepcopy(current_board)
        self.search_board = deepcopy(self.game_board)
        self.player = player
        self.other_player = 1 if self.player == 2 else 2
        self.exploration_parameter = exploration_parameter
        self.intelligence_parameter = intelligence_parameter

        # Initializing the root node and its children
        self.root_node = self.Node(0) # (its color doesn't matter)
        legal_moves = self.game_board.legal_moves()
        for move in legal_moves:
            self.root_node.add_child(move)
            
            
    """
    Node Class: Used to build out the search tree. 
    Each node stores the number of times it's been visited, the color of its update to the board,
    the number of wins recorded for it and all its children's nodes, a score_value based on how high 
    an average score was achieved, a list of its children, and a pointer to its parent node.
    """
    class Node:
        def __init__(self, color, parent = None):
            self.num_visits = 1
            self.color = color
            self.num_wins = 0
            self.score_value = 0
            self.children = []
            self.parent = parent
            
        def add_child(self, color):
            child = self.__class__(color, self)
            self.children.append(child)
        
        def update(self, win_loss, score_value):
            self.num_visits += 1
            self.num_wins += win_loss
            self.score_value += score_value
     
    
    # Selection step of the MCTS algorithm.       
    def select(self):
        self.search_board = deepcopy(self.game_board)
        current_node = self.root_node
        
        # Searching till we finally select a leaf node
        while len(current_node.children) > 0:
            selected_child = None
            best_weight = 0.0
            
            # Looping over all children
            for child in current_node.children:
                # Making sure we don't select a node whose color is the same as the other player's
                if child.color != self.search_board.get_color(self.other_player):
                    weight = (child.num_wins + child.score_value) / child.num_visits + self.exploration_parameter * (
                        sqrt(log(current_node.num_visits) / child.num_visits))
                    if weight >= best_weight:
                        best_weight = weight
                        selected_child = child
            
            # Stepping down the tree to the selected child
            current_node = selected_child
            
            # Updating the search board for player and other player. Updates with a random choice
            # or a best move with probabilty based on the given intelligence_parameter
            self.search_board.update_board(self.player, current_node.color)      
            if random() > self.intelligence_parameter:
                self.search_board.update_board(self.other_player, 
                                               choice(self.search_board.legal_moves()))
            else:
                # Searching to a depth of 3 if the game is less than half done and lesser depths 
                # the further the game goes along. Helps to not fit to paths that won't even be 
                # able to happen near the end of the game
                percentage_done = self.search_board.get_percentage_done()
                if percentage_done < 0.5:
                    self.search_board.update_board(self.other_player, self.search_board.best_move_depth(
                        self.other_player, 3))
                elif percentage_done < 0.75: 
                    self.search_board.update_board(self.other_player, self.search_board.best_move_depth(
                        self.other_player, 2))
                else:
                    self.search_board.update_board(self.other_player, self.search_board.best_move_depth(
                        self.other_player, 1))
        
        # Returning the selected leaf node
        return current_node
    
    
    # Expantion step of the MCTS algorithm.    
    def expand(self, selected_node):
        colors = [0,1,2,3,4,5]
        colors.remove(self.search_board.get_color(self.player))
        for color in colors:
            selected_node.add_child(color)
    
    
    # Simulation step of the MCTS algorithm.    
    def simulate(self, board):
        board_size = board.size[0]*board.size[1]
        
        # Playing out the simulation
        while sum(board.get_score()) < board_size:
            board.update_board(self.other_player, choice(board.legal_moves()))
            board.update_board(self.player, choice(board.legal_moves()))
        
        # Returning the result
        score = board.get_score()
        if self.player == 1:
            if score[0] > score[1]:
                return (1, score[0]*2 / board_size) 
            else:
                return (0, 0)
        else:
            if score[1] > score[0]:
                return (1, score[1]*2 / board_size)
            else:
                return (0, 0)
    
    
    # Backpropagation step of the MCTS algorithm.    
    def backpropagate(self, node, win_loss, score_value):
        current_node = node
        while current_node != None:
            current_node.update(win_loss, score_value)
            current_node = current_node.parent
     

    # Returning the final best move after running the MCTS algorithm with num_iterations.     
    def select_move(self, num_iterations = 100, verbose = False):
        for _ in range(num_iterations):
            selected_node = self.select()
            self.expand(selected_node)
            
            for child in selected_node.children:
                if child.color != self.search_board.get_color(self.other_player):
                    expansion_board = deepcopy(self.search_board)
                    expansion_board.update_board(self.player, child.color)
                    simulation_results = self.simulate(expansion_board)
                    self.backpropagate(child, simulation_results[0], simulation_results[1])

        # Returning the child of the root node with the highest weight
        move_scores = np.zeros(4)
        for inx, child in enumerate(self.root_node.children):
            move_scores[inx] = (child.num_wins + child.score_value) / child.num_visits
            if verbose:
                size_scale = self.game_board.size[0] * self.game_board.size[1] / 2
                print(f"{get_color_name(child.color)} has win percentage {child.num_wins / child.num_visits}" + 
                f" with an average score of {child.score_value / child.num_visits * size_scale}")

        # Keeping algorithm from just choosing randomly once it's sure it's gonna win or lose
        if np.std(move_scores) < 0.05:
            return self.game_board.greedy_move(self.player)
        else:
            return self.root_node.children[np.argmax(move_scores)].color



# Helper function for the verbose printout
def get_color_name(color_number):
    if color_number == 0:
        return "red"
    if color_number == 1:
        return "green"
    if color_number == 2:
        return "yellow"
    if color_number == 3:
        return "blue"
    if color_number == 4:
        return "purple"
    if color_number == 5:
        return "black"