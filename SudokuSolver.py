from operator import attrgetter


class Solver:
    def checkvalidpuzzle(self, arr):
        subsquarestartingpoints = [[0, 0], [0, 3], [0, 6], [3, 0], [3, 3], [3, 6], [6, 0], [6, 3], [6, 6]]
        # Checking row validity of every row
        for row in range(9):
            has = set()
            for col in range(9):
                if arr[row][col] == 0:
                    continue
                if arr[row][col] in has:
                    return False
                has.add(arr[row][col])
        # Checking column validity of every column
        for col in range(9):
            has = set()
            for row in range(9):
                if arr[row][col] == 0:
                    continue
                if arr[row][col] in has:
                    return False
                has.add(arr[row][col])
        # Checking box validity
        for pointrow, pointcol in subsquarestartingpoints:
            has = set()
            for row in range(3):
                for col in range(3):
                    if arr[pointrow+row][pointcol+col] == 0:
                        continue
                    if arr[pointrow+row][pointcol+col] in has:
                        return False
                    has.add(arr[pointrow+row][pointcol+col])
        return True

    def print_board(self, arr):
        for i in range(9):
            for j in range(9):
                if arr[i][j]==0:
                    print("_", end=" ")
                else:
                    print(arr[i][j], end=" ")
            print("")

    @staticmethod
    def solve_sudoku(arr):
        """
        Create a binary matrix to convert to an exact cover problem.

        Choices: 729
        Each cell can have any value from 1 to 9.

        Constraints: 324
        1. Each row must have all the values from 1 to 9, total: 81
        2. Each column must have all the values from 1 to 9, total: 81
        3. Each block must have all the values from 1 to 9, total: 81
        4. Each cell must be filled, total: 81

        Choices are ordered by row > col > value
        Constraints are ordered as above.
        """
        # Represent the binary matrix as sparse matrix (has < 729 * 4 ones in a matrix of 729 * 342)
        positions = []

        def add_position(ch, r, c, x):
            positions.append([ch, [
                9 * r + x,  # Row constraint
                81 + 9 * c + x,  # Col constraint
                162 + 9 * ((r // 3) * 3 + (c // 3)) + x,  # Block constraint
                243 + 9 * r + c  # Cell constraint
            ]])

        choice_row = 0
        for i in range(9):  # Row
            for j in range(9):  # Column
                if arr[i][j] == 0:
                    for k in range(9):  # Value
                        add_position(choice_row, i, j, k)
                        choice_row += 1
                else:
                    k = arr[i][j] - 1
                    add_position(choice_row + k, i, j, k)
                    choice_row += 9
        alg_x = AlgorithmX(324, positions)
        if not alg_x.solve():
            return False
        rows = alg_x.solution
        if len(rows) != 81:
            return False
        for row in rows:
            i, row = divmod(row, 81)
            j, value = divmod(row, 9)
            arr[i][j] = value + 1  # value is 0-8
        return True


class AlgorithmXNode:
    def __init__(self, value=0):
        """
        Create a node with self links.
        :param value: Serves multiple purposes:
            - nothing for root node
            - the number of cells in column for all header nodes
            - the row id in all other nodes
        """
        self.value = value
        self.left = self.right = self.up = self.down = self.top = self

    def insert_h(self):
        """
        Insert this node in the row, using left and right links.
        """
        self.left.right = self.right.left = self

    def insert_v(self, update_top=True):
        """
        Insert this node in the column.
        :param update_top: If true, update the counter in the header.
        """
        self.up.down = self.down.up = self
        if update_top:
            self.top.value += 1

    def insert_above(self, node):
        """
        Insert this node above the given node, in the column, updating the top.
        """
        self.top = node.top
        self.up = node.up
        self.down = node
        self.insert_v()

    def insert_after(self, node):
        """
        Insert this node to the right the given node.
        """
        self.right = node.right
        self.left = node
        self.insert_h()

    def remove_h(self):
        """
        Remove this node from the row. Inverse of insert_h.
        """
        self.left.right = self.right
        self.right.left = self.left

    def remove_v(self, update_top=True):
        """
        Remove this node from the column. Inverse of insert_v.
        :param update_top: If true, update the counter in the header.
        """
        self.up.down = self.down
        self.down.up = self.up
        if update_top:
            self.top.value -= 1

    def cover(self):
        self.top.remove_h()
        for row in self.top.loop('down'):
            for node in row.loop('right'):
                node.remove_v()

    def uncover(self):
        for row in self.top.loop('up'):
            for node in row.loop('left'):
                node.insert_v()
        self.top.insert_h()

    def loop(self, direction):
        """
        Yield each node from self to self, following the direction, excluding self.
        :param direction: One of 'left', 'right', 'up', 'down'.
        :return: Nodes from self to self (both exclusive), one at a time.
        """
        if direction not in {'left', 'right', 'up', 'down'}:
            raise ValueError(f"Direction must be one of 'left', 'right', 'up', 'down', got {direction}")
        next_node = attrgetter(direction)
        node = next_node(self)
        while node != self:
            yield node
            node = next_node(node)


class AlgorithmX:
    """
    Use Algorithm X with dancing links to solve a constraint satisfaction problem
    represented in the form of Exact Cover.

    Refer to https://en.wikipedia.org/wiki/Dancing_Links and
    https://en.wikipedia.org/wiki/Algorithm_X for the algorithm.
    """

    def __init__(self, constraint_count, matrix):
        matrix.sort()
        headers = [AlgorithmXNode() for _ in range(constraint_count)]
        for row, cols in matrix:
            first = None  # first node in row
            for col in cols:
                node = AlgorithmXNode(row)
                # Insert in column
                node.insert_above(headers[col])
                # Insert in row
                if first is None:
                    first = node
                else:
                    node.insert_after(first)
        # Header row
        self.root = AlgorithmXNode()
        last = self.root
        for header in headers:
            header.insert_after(last)
            last = header
        self.solution = []

    def solve(self):
        if self.root.right == self.root:
            # All constraints have been satisfied
            return True
        # Find column with least number of nodes
        header = min(self.root.loop('right'), key=attrgetter('value'))
        if header.value == 0:
            # No valid solution exists
            return False
        header.cover()
        for row in header.loop('down'):
            for node in row.loop('right'):
                node.cover()
            if self.solve():
                # Add row to solution
                self.solution.append(row.value)
                return True
            # Try a different value
            for node in row.loop('left'):
                node.uncover()
        header.uncover()
        # Backtrack
        return False
