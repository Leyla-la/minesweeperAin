import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):
        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """
        # Initialize count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Skip the cell itself
                if (i, j) == cell:
                    continue

                # Increment count if cell is within bounds and contains a mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """

        # If count of mines is equal to number of cells (and > 0), all cells are mines:
        if len(self.cells) == self.count and self.count != 0:
            print('Mine Identified! - ', self.cells)
            return self.cells
        else:
            return set()


    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        return self.cells if self.count == 0 else set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count = max(0, self.count - 1)  # Safety check to prevent negative count

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        self.cells.discard(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):
        # Set initial height and width
        self.height = height
        self.width = width

        # Track cells that have been clicked on
        self.moves_made = set()

        # Track cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of known sentences about the game
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
            based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
            if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
            if they can be inferred from existing knowledge
        """

        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) mark the cell as safe
        self.mark_safe(cell)

        # Create set to store undecided cells for KB:
        new_sentence_cells = set()

        # 3) Loop over all cells within one row and column
        #    and add them to the knowledge base sentence
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # If cells are already safe, ignore them:
                if (i, j) in self.safes:
                    continue

                # If cells are known to be mines, reduce count by 1 and ignore them:
                if (i, j) in self.mines:
                    count = count - 1
                    continue

                # Otherwise add them to sentence if they are in the game board:
                if 0 <= i < self.height and 0 <= j < self.width:
                    new_sentence_cells.add((i, j))

        # 3) Add the new sentence to the AI's Knowledge Base:
        print(f'Move on cell: {cell} has added sentence to knowledge {new_sentence_cells} = {count}' )
        self.knowledge.append(Sentence(new_sentence_cells, count))

        # 4) Iteratively mark guaranteed mines and safes, and infer new knowledge:
        knowledge_changed = True

        while knowledge_changed:
            knowledge_changed = False

            safes = set()
            mines = set()

            # Get set of safe spaces and mines from KB
            for sentence in self.knowledge:
                safes = safes.union(sentence.known_safes())
                mines = mines.union(sentence.known_mines())

            # Mark any safe spaces or mines:
            if safes:
                knowledge_changed = True
                for safe in safes:
                    self.mark_safe(safe)
            if mines:
                knowledge_changed = True
                for mine in mines:
                    self.mark_mine(mine)

            # Remove any empty sentences from knowledge base:
            empty = Sentence(set(), 0)

            self.knowledge[:] = [x for x in self.knowledge if x != empty]

            # 5) Try to infer new sentences from the current ones:
            for sentence_1 in self.knowledge:
                for sentence_2 in self.knowledge:

                    # Ignore when sentences are identical
                    if sentence_1.cells == sentence_2.cells:
                        continue

                    if sentence_1.cells == set() and sentence_1.count > 0:
                        print('Error - sentence with no cells and count created')
                        raise ValueError

                    # Create a new sentence if 1 is subset of 2, and not in KB:
                    if sentence_1.cells.issubset(sentence_2.cells):
                        new_sentence_cells = sentence_2.cells - sentence_1.cells
                        new_sentence_count = sentence_2.count - sentence_1.count

                        new_sentence = Sentence(new_sentence_cells, new_sentence_count)

                        # Add to knowledge if not already in KB:
                        if new_sentence not in self.knowledge:
                            knowledge_changed = True
                            print('New Inferred Knowledge: ', new_sentence,
                                  'from', sentence_1, ' and ', sentence_2)
                            self.knowledge.append(new_sentence)

        # Print out AI current knowledge to terminal:
        print('Current AI Knowledge Base length: ', len(self.knowledge))
        print('Known Mines: ', self.mines)
        print('Safe Moves Remaining: ', self.safes - self.moves_made)
        print('====================================================')


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.
        """
        safe_moves = self.safes - self.moves_made
        if safe_moves:
            print('Making a Safe Move! Safe moves available: ', len(safe_moves))
            return next(iter(safe_moves))
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # Find all cells that are possible moves (not yet chosen and not mines)
        remaining = {
            (i, j)
            for i in range(self.height)
            for j in range(self.width)
        } - self.moves_made - self.mines

        # If there are no remaining moves, return None
        if not remaining:
            print("No remaining moves are possible.")
            return None

        # Calculate basic probability of a remaining cell being a mine
        remaining_mines = 8 - len(self.mines)
        base_probability = remaining_mines / len(remaining)
        print("Basic mine probability for each cell without knowledge:", base_probability)

        # Track risk (mine probability) for each remaining cell
        cell_risks = {}
        for cell in remaining:
            # Start with the base probability
            max_risk = base_probability
            # Adjust probability if we have knowledge about neighboring mines
            for sentence in self.knowledge:
                if cell in sentence.cells:
                    cell_risk = sentence.count / len(sentence.cells)
                    max_risk = max(max_risk, cell_risk)
            cell_risks[cell] = max_risk

        # Find the minimum risk level among all possible moves
        min_risk = min(cell_risks.values())
        safest_moves = [cell for cell, risk in cell_risks.items() if risk == min_risk]

        # Choose a random move from those with the lowest mine probability
        move = random.choice(safest_moves)
        if not self.knowledge:
            print("AI selecting random move with basic probability:", move)
        else:
            print("AI selecting random move with lowest mine probability using Knowledge Base:", move)

        return move
