import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import random

class Board:  
    """
        Creates a random Filler board using random integer intialziation. Then fixes the board 
        to match a standard Filler board with no groups of cells with the same color.
        Optional inputs:
            - size: Tuple determining the board size
            - data: Numpy array of integers supplying the data for a specific board configuration
    """
    def __init__(self, size = (7,8), data = None):
        if data is not None:
            self.size = data.shape
            self.data = data
        else:
            self.size = size
            self.data = np.random.randint(0, high=6, size=self.size)
            self.fix_board()
        
        self.player_1_color = self.data[self.size[0]-1,0]
        self.player_2_color = self.data[0,self.size[1]-1]
        
        self.player_1_cells_captured = {(self.size[0]-1,0)}
        self.player_2_cells_captured = {(0,self.size[1]-1)}

    
    # Displays the board
    def display_board(self):
        # For displaying the board (Defining: red = 0, green = 1, yellow = 2, blue = 3, purple = 4, black = 5)
        cmap = colors.ListedColormap(['red', 'green', 'yellow', 'blue', 'purple', 'black'])
        bounds = [0,1,2,3,4,5,6]
        norm = colors.BoundaryNorm(bounds, cmap.N)

        _, ax = plt.subplots()
        ax.imshow(self.data, cmap=cmap, norm=norm)
     
    
    # Retuns the current game score. Necessary for evaluating when the game has ended (when the two scores add
    # up to the total number of celss for the given board size).
    def get_score(self):
        return (len(self.player_1_cells_captured), len(self.player_2_cells_captured))
    

    # Function that returns what percentage of the board is captured. Useful in MCTS algorithm.
    def get_percentage_done(self):
        return (len(self.player_1_cells_captured) + len(self.player_2_cells_captured)) / (self.size[0] * self.size[1])
    

    # Returns the player color for a given player. Helpful in MCTS algorithm.
    def get_color(self, player_number):
        if player_number == 1:
            return self.player_1_color
        elif player_number == 2:
            return self.player_2_color
        else:
               raise Exception("Invalid player number")


    # Returns the possible legal moves for the current board state.
    # Necessary for MCTS algorithm.
    def legal_moves(self):
        moves = [0,1,2,3,4,5]
        moves.remove(self.player_1_color)
        moves.remove(self.player_2_color)
        return moves
    
    
    # For finding which neighbors of a cell are within the bounds of the grid
    # Takes in a list of tuples giving the coordinates of the neighbors
    def valid_neighbors(self, neighbors):
        valid_neighbors = []
        for neighbor in neighbors:
            if neighbor[0] >= 0 and neighbor[0] < self.size[0] and neighbor[1] >= 0 and neighbor[1] < self.size[1]:
                valid_neighbors.append(neighbor)
        return valid_neighbors

    
    # Takes the random generated board and fixes it so that no no cells with the same color are 
    # already touching to match the filler game. 
    def fix_board(self):
        # Fixing blobs of colors
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                neighbors = self.valid_neighbors([(i+1,j), (i-1,j), (i,j+1), (i,j-1)])
                neighbor_colors = []
                for neighbor in neighbors:
                    neighbor_colors.append(self.data[neighbor[0], neighbor[1]])
                if len(np.intersect1d([self.data[i,j]], neighbor_colors)) > 0:
                    self.data[i,j] = random.choice(np.setdiff1d([0,1,2,3,4,5],neighbor_colors))
        
        # Fixing if starting colors of players are the same
        if self.data[self.size[0]-1,0] == self.data[0,self.size[1]-1]:
            self.data[0,self.size[1]-1] = random.choice(np.setdiff1d([0,1,2,3,4,5],[self.data[0,self.size[1]-1], 
                                            self.data[0,self.size[1]-2], self.data[1,self.size[1]-1]]))
        
        # Fixing to make sure a player can never start the game off with two neighbors of the same color
        if self.data[self.size[0]-2,0] == self.data[self.size[0]-1, 1]:
            cells_to_avoid = [(self.size[0]-3,0), (self.size[0]-1,0), (self.size[0]-2,1), (self.size[0]-1,1)]
            colors_to_avoid = []
            for cell in cells_to_avoid:
                colors_to_avoid.append(self.data[cell[0], cell[1]])
            self.data[self.size[0]-2,0] = random.choice(np.setdiff1d([0,1,2,3,4,5],colors_to_avoid))
        if self.data[0, self.size[1]-2] == self.data[1, self.size[1]-1]:
            cells_to_avoid = [(0,self.size[1]-3), (0,self.size[1]-1), (1,self.size[1]-2), (1,self.size[1]-1)]
            colors_to_avoid = []
            for cell in cells_to_avoid:
                colors_to_avoid.append(self.data[cell[0], cell[1]])
            self.data[0,self.size[1]-2] = random.choice(np.setdiff1d([0,1,2,3,4,5],colors_to_avoid))
       
            
    # Updates the board based on the given player and the color value.
    def update_board(self, player_number, color_value):
        if player_number == 1:
            if color_value == self.player_2_color:
                raise Exception("Trying to choose the color of the other player")
            if color_value == self.player_1_color:
                raise Exception("Trying to choose your own color")
            
            # Finding all neighboring cells with the given chosen color
            neighbors = set()
            for cell in self.player_1_cells_captured:
                neighbors.update([(cell[0]+1,cell[1]), (cell[0]-1,cell[1]), 
                                  (cell[0],cell[1]+1), (cell[0],cell[1]-1)])
                self.data[cell] = color_value
            neighbors -= self.player_1_cells_captured
            neighbors -= self.player_2_cells_captured

            # Finding valid neighbors adding to captured set if they have the same 
            # color as the chosen color
            neighbors = self.valid_neighbors(list(neighbors))  
            for neighbor in neighbors:
                if self.data[neighbor] == color_value:
                    self.player_1_cells_captured.add(neighbor)
            
            # Updating player color
            self.player_1_color = color_value
        
        elif player_number == 2:
            if color_value == self.player_1_color:
                raise Exception("Trying to choose the color of the other player")
            if color_value == self.player_1_color:
                raise Exception("Trying to choose your own color")
            
            # Finding all neighboring cells with the given chosen color
            neighbors = set()
            for cell in self.player_2_cells_captured:
                neighbors.update([(cell[0]+1,cell[1]), (cell[0]-1,cell[1]), 
                                  (cell[0],cell[1]+1), (cell[0],cell[1]-1)])
                self.data[cell] = color_value
            neighbors -= self.player_2_cells_captured
            neighbors -= self.player_1_cells_captured

            # Finding valid neighbors adding to captured set if they have the same 
            # color as the chosen color
            neighbors = self.valid_neighbors(neighbors)
            for neighbor in neighbors:
                if self.data[neighbor] == color_value:
                    self.player_2_cells_captured.add(neighbor)
            
            # Updating player color
            self.player_2_color = color_value
        
        else:
               raise Exception("Invalid player number")
                
    
    # Returns the greedy move based on maximizing the number of cells gained in the next turn
    # for a given player. Note, it returns the maximum legal move (it can't choose the other 
    # players current color).
    def greedy_move(self, player_number):
        territory_neighbors = set()
        num_colored_neighbors = np.zeros(6)        
        
        if player_number == 1:
            # Finding all neighbors and adding them to the running total of num_colored_neighbors
            for cell in self.player_1_cells_captured:
                territory_neighbors.update(self.valid_neighbors([(cell[0]+1,cell[1]), (
                    cell[0]-1,cell[1]), (cell[0],cell[1]+1), (cell[0],cell[1]-1)]))
            for neighbor in territory_neighbors:
                num_colored_neighbors[self.data[neighbor]] += 1            
            
            # Return the top color but checking to make sure we're not chossing the other player's color  
            num_colored_neighbors[self.player_2_color] = -1
            num_colored_neighbors[self.player_1_color] = -1
            return np.argmax(num_colored_neighbors)
        
        elif player_number == 2:         
            # Finding all neighbors and adding them to the running total of num_colored_neighbors
            for cell in self.player_2_cells_captured:
                territory_neighbors.update(self.valid_neighbors([(cell[0]+1,cell[1]), (
                    cell[0]-1,cell[1]), (cell[0],cell[1]+1), (cell[0],cell[1]-1)])) 
            for neighbor in territory_neighbors:
                num_colored_neighbors[self.data[neighbor]] += 1       
            
            # Return the top color but checking to make sure we're not chossing the other player's color  
            num_colored_neighbors[self.player_2_color] = -1
            num_colored_neighbors[self.player_1_color] = -1
            return np.argmax(num_colored_neighbors)      
        
        else:
               raise Exception("Invalid player number")

    
    # Helper function for the best_move_depth function
    # Note: This is recursive but not tail recursive
    def best_move_depth_helper(self, territory, opponent_territory, depth, current_depth):
        if current_depth > depth:
            return len(territory)
        else:
            best_territory = 0 # amount of territory the best sequence of moves can get
            
            for i in range(6): # Possible 6 colors
                territory_neighbors = set() # A set so that we only add neighboring cells once
                
                # Looping over all cells in the territory to find neighboring cells of color i
                neighbors = set()
                for cell in territory:
                    neighbors.update([(cell[0]+1,cell[1]),(
                        cell[0]-1,cell[1]), (cell[0],cell[1]+1), (cell[0],cell[1]-1)])
                neighbors -= opponent_territory
                neighbors -= territory

                neighbors = self.valid_neighbors(list(neighbors))   
                for neighbor in neighbors:
                    if self.data[neighbor] == i:
                        territory_neighbors.add(neighbor)

                # Finding the best territory that can be achieved by making move i up to 
                # the given depth of moves using recursion
                best_subsequent_territory = self.best_move_depth_helper(territory.union(
                    territory_neighbors), opponent_territory, depth, current_depth+1)
                
                # Saving the best move
                if best_subsequent_territory > best_territory:
                    best_territory = best_subsequent_territory

            # Returning the best territory
            return best_territory
    

    # Returns the move that has a path to gain the most territory for a given depth of moves
    # Better approach than a greedy move but still doesn't account for the other player's
    # actions during those moves.
    def best_move_depth(self, player_number, depth):
        if depth < 2:
            return self.greedy_move(player_number)
        
        best_move = -1 # the best move we're trying to find
        best_territory = 0 # amount of territory the best sequence of moves can get
        
        # Storing correct player information
        if player_number == 1:
            player_territory = self.player_1_cells_captured
            opponent_territory = self.player_2_cells_captured
        elif player_number == 2:
            player_territory = self.player_2_cells_captured
            opponent_territory = self.player_1_cells_captured
        else:
            raise Exception("Invalid player number")

        # Looping over legal moves to find the best one at a given depth
        for move in self.legal_moves():
            territory_neighbors = set()
            
            # Looping over all cells in the territory to find neighboring cells 
            # of the color of the move
            neighbors = set()
            for cell in player_territory:
                neighbors.update([(cell[0]+1,cell[1]),(
                        cell[0]-1,cell[1]), (cell[0],cell[1]+1), (cell[0],cell[1]-1)])
            neighbors -= opponent_territory
            neighbors -= player_territory            

            neighbors = self.valid_neighbors(neighbors)   
            for neighbor in neighbors:
                if self.data[neighbor] == move:
                    territory_neighbors.add(neighbor)
            
            # Calling the helper function to find the best possible territory to capture after 
            # the given depth of moves
            best_subsequent_territory = self.best_move_depth_helper(player_territory.union(
                territory_neighbors), opponent_territory, depth, 2)
            
            # Checking if this was the best move
            if best_subsequent_territory > best_territory:
                best_territory = best_subsequent_territory
                best_move = move

            #print(f"The most possible territory with move {move} is {best_subsequent_territory}")

        # Returning the best move
        return best_move
