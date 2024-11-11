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
        return self.cells if len(self.cells) == self.count != 0 else set()

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
        self.moves_made.add(cell)
        self.mark_safe(cell)

        # Calculate neighboring cells
        neighbors = {
            (i, j)
            for i in range(max(0, cell[0]-1), min(self.height, cell[0]+2))
            for j in range(max(0, cell[1]-1), min(self.width, cell[1]+2))
            if (i, j) != cell
        }

        # Identify already known mines and adjust count
        mine_neighbors = neighbors & self.mines
        count -= len(mine_neighbors)
        unknown_cells = neighbors - self.safes - self.mines

        if unknown_cells:
            self.knowledge.append(Sentence(unknown_cells, count))

        while True:
            knowledge_changed = False

            for sentence in self.knowledge:
                new_mines = sentence.known_mines() - self.mines
                new_safes = sentence.known_safes() - self.safes

                if new_mines:
                    knowledge_changed = True
                    for mine in new_mines:
                        self.mark_mine(mine)

                if new_safes:
                    knowledge_changed = True
                    for safe in new_safes:
                        self.mark_safe(safe)

            # Clean up empty sentences
            self.knowledge = [s for s in self.knowledge if s.cells]

            knowledge_size = len(self.knowledge)
            for i in range(knowledge_size):
                for j in range(i + 1, knowledge_size):
                    s1, s2 = self.knowledge[i], self.knowledge[j]
                    if s1.cells and s2.cells:
                        if s1.cells < s2.cells:
                            new_cells = s2.cells - s1.cells
                            new_count = s2.count - s1.count
                            new_sentence = Sentence(new_cells, new_count)
                            if new_sentence not in self.knowledge and new_cells:
                                self.knowledge.append(new_sentence)
                                knowledge_changed = True

            if not knowledge_changed:
                break

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.
        """
        safe_moves = self.safes - self.moves_made
        if safe_moves:
            return next(iter(safe_moves))
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        remaining = {
            (i, j)
            for i in range(self.height)
            for j in range(self.width)
        } - self.moves_made - self.mines

        if not remaining:
            return None

        remaining_mines = 8 - len(self.mines)
        base_probability = remaining_mines / len(remaining)

        cell_risks = {}
        for cell in remaining:
            max_risk = base_probability
            for sentence in self.knowledge:
                if cell in sentence.cells:
                    cell_risk = sentence.count / len(sentence.cells)
                    max_risk = max(max_risk, cell_risk)
            cell_risks[cell] = max_risk

        min_risk = min(cell_risks.values())
        safest_moves = [cell for cell, risk in cell_risks.items() if risk == min_risk]

        return random.choice(safest_moves)
