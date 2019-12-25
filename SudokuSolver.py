class Solver:

    def find_empty_location(self, arr, l):
        for row in range(9):
            for col in range(9):
                if arr[row][col] == 0:
                    l[0] = row
                    l[1] = col
                    return True
        return False

    def check_location_is_safe(self, arr, row, col, num):

        def used_in_row(arr, row, num):
            for i in range(9):
                if arr[row][i] == num:
                    return True
            return False

        def used_in_col(arr, col, num):
            for i in range(9):
                if arr[i][col] == num:
                    return True
            return False

        def used_in_box(arr, row, col, num):
            for i in range(3):
                for j in range(3):
                    if arr[i + row][j + col] == num:
                        return True
            return False
        return not used_in_row(arr, row, num) \
               and not used_in_col(arr, col, num) and \
               not used_in_box(arr, row - row % 3, col - col % 3, num)

    def solve_sudoku(self, arr):
        l = [0, 0]
        # If there is no unassigned location, we are done
        if not self.find_empty_location(arr, l):
            return True
        row = l[0]
        col = l[1]

        for num in range(1, 10):
            # If the number does not violate the constraints
            if self.check_location_is_safe(arr, row, col, num):
                arr[row][col] = num
                # Return True if Success
                if self.solve_sudoku(arr):
                    return True
                # If Fail, then assign 0 and try the next number
                arr[row][col] = 0
        return False