import keyboard
import os
import re
import sys
from time import sleep

X = "X"
O = "O"

# Get width of terminal
TERMINAL_COLUMNS = os.get_terminal_size().columns


def main():
    """Configure tic-tac-toe gamemode"""

    # Play mode
    mode = None

    # Computer difficulty
    computerMode = None

    # Print start screen
    displayStartScreen()

    # Check for player's choice of gamemode
    while not mode:
        if keyboard.is_pressed("escape"):
            sys.exit()
        # Display instructions
        elif keyboard.is_pressed("i"):
            displayInstructions()
            while not keyboard.is_pressed("backspace"):
                continue

            # Cross-platform terminal clearing taken from
            # https://stackoverflow.com/a/2084628
            os.system("cls" if os.name == "nt" else "clear")
            displayStartScreen()
        # Enable player vs player mode
        elif keyboard.is_pressed("p"):
            mode = "P"
        # Enable player vs computer mode
        elif keyboard.is_pressed("c"):
            mode = "C"

    # Prompt user for computer opponent difficulty
    if mode == "C":
        print("\n\n")
        print("SELECT DIFFICULTY\n".center(TERMINAL_COLUMNS))
        print("{0}{3}{1}{3}{2}".format(
            "[E] EASY", "[M] MEDIUM", "[H] HARD", " " * 5).center(
                TERMINAL_COLUMNS))

        while not computerMode:
            if keyboard.is_pressed("e"):
                computerMode = 3
            elif keyboard.is_pressed("m"):
                computerMode = 5
            elif keyboard.is_pressed("h"):
                computerMode = 9

    if mode == "P":
        playerVsPlayer()
    if mode == "C":
        playerVsComputer(computerMode)


def playerVsPlayer():
    """Start player vs player mode"""

    # Initiate and display tic-tac-toe grid
    gameGrid = startGrid()
    displaygameGrid(gameGrid)

    while not gameEnd(gameGrid):
        gameGrid = playerMove(gameGrid)

    # Display end-of-game message
    winMessage(winner(gameGrid))

    # Prompt for user to play again
    if playAgain():
        main()


def playerVsComputer(mode):
    """Start player vs computer mode"""

    firstPlayer = None

    menu = (
        "\n",
        "CHOOSE A PLAYER\n",
        "[X] PLAYER X",
        "[O] PLAYER O")

    # Display and center each line of the menu
    for line in menu:
        print(line.center(TERMINAL_COLUMNS))

    # Prompt user for choice of player
    while not firstPlayer:
        if keyboard.is_pressed("x"):
            firstPlayer = X
        elif keyboard.is_pressed("o"):
            firstPlayer = O

    # Initiate and display tic-tac-toe grid
    gameGrid = startGrid()
    displaygameGrid(gameGrid)

    # Prompt user or algorithm for turn depending on first player
    if firstPlayer == X:
        while not gameEnd(gameGrid):
            gameGrid = playerMove(gameGrid)
            gameGrid = computerMove(gameGrid, mode)
    else:
        while not gameEnd(gameGrid):
            gameGrid = computerMove(gameGrid, mode)
            gameGrid = playerMove(gameGrid)

    # Display end-of-game message
    winMessage(winner(gameGrid))

    # Prompt for user to play again
    if playAgain():
        main()


def playerMove(grid):
    """Prompt user for move

    Args:
        grid (list): 3x3 2D list representing tic-tac-toe grid

    Returns:
        list: Updated grid if move has been made
    """

    # No moves possible
    if gameEnd(grid):
        return grid

    # Prompt player for move
    player = nextPlayer(grid)
    move = alphanumericToCoordinate(
        input(f"Player {player}'s move: ").strip())

    while not validateMove(grid, move):
        # Indicate move in invalid to user
        print("Please enter a valid move: [LETTER A-C][NUMBER 1-3]")
        print("Possible moves: ", end="")

        # Display all possible moves in alphabetical order
        moves = possibleMoves(grid)
        playerMoves = sorted([coordinateToAlphanumeric(moves[i])
                             for i in range(len(moves))])

        for i in playerMoves:
            print(f"{i}", end=(", " if i != playerMoves[-1] else "\n\n"))

        # Re-prompt user for move
        move = alphanumericToCoordinate(
            input(f"Player {player}'s move: ").strip())

    # Update tic-tac-toe grid with move
    newGrid = moveResult(grid, move)
    displaygameGrid(newGrid)
    return newGrid


def computerMove(grid, mode):
    """Determine best move

    Args:
        grid (list): 3x3 2D list representing tic-tac-toe grid
        mode (int): Computer difficulty; depth value for minimax()

    Returns:
        list: Updated grid if move has been made
    """

    # No moves possible
    if gameEnd(grid):
        return grid

    # Determine best move
    player = nextPlayer(grid)
    move = optimalMove(grid, player, mode)

    # Naturalize computer's determination of best move by inducing
    # delay
    sleep(1)

    print(f"Computer's move: {coordinateToAlphanumeric(move)}")

    # Update tic-tac-toe grid with move
    newGrid = moveResult(grid, move)
    displaygameGrid(newGrid)

    return newGrid


def minimax(grid, alpha, beta, depth, player):
    """Determine all heuristic values of current possible tic-tac-toe 
    games, employ alpha-beta pruning for computation speed

    Args:
        grid (list): 3x3 2D list representing tic-tac-toe grid
        alpha (int): Certain maximum heuristic value of maximizing player
        beta (int): Certain minimum heuristic value of minimizing player
        depth (int): Maximum considerations of moves when exploring 
        possible moves
        player (string): "X" or "O"

    Returns:
        int: Maximum or minimum heuristic value of a grid 

    Minimax algorithm references https://en.wikipedia.org/wiki/Minimax
    """

    # Base case
    if depth == 0 or gameEnd(grid):
        return gridHeuristic(grid)

    if player == X:
        # Worst value for maximizing player
        value = -2

        # Explore all possible moves from current grid
        for move in possibleMoves(grid):
            # Recursive call
            value = max(value, minimax(moveResult(
                grid, move), alpha, beta, depth-1, O))

            # Skip exploration of set of moves that evaluate to the
            # same or less than current heuristic value
            if value >= beta:
                break

            # Update alpha to reflect maximum value
            alpha = value
        return value
    else:
        # Worst value for minimizing player
        value = 2

        # Explore all possible moves from current grid
        for move in possibleMoves(grid):
            value = min(value, minimax(moveResult(
                grid, move), alpha, beta, depth-1, X))

            # Skip exploration of set of moves that evaluate to the
            # same or more than current heuristic value
            if value <= alpha:
                break

            # Update beta to reflect minimum value
            beta = value
        return value


def optimalMove(grid, player, mode):
    """Determine optimal move for current player

    Args:
        grid (list): 3x3 2D list representing tic-tac-toe grid
        player (string): "X" or "O"
        mode (int): Computer gamemode that specifies depth argument of
        minimax algorithm

    Returns:
        tuple: Two indices for a move on the current grid
    """

    # Indicate no possible moves are available for current grid
    if gameEnd(grid):
        return None

    # Maximizing player
    if player == X:
        bestMove = None

        # Worst value for maximizing player
        maxValue = -2

        # Determine values for all possible tic-tac-toe games
        for move in possibleMoves(grid):
            value = minimax(moveResult(grid, move), float(
                "-inf"), float("inf"), mode, O)

            # Check if value is current maximum value
            if value > maxValue:
                maxValue = value
                bestMove = move
        return bestMove

    # Minimizing player
    else:
        bestMove = None

        # Worst value for minimizing player
        minValue = 2

        # Determine values for all possible tic-tac-toe games
        for move in possibleMoves(grid):
            value = minimax(moveResult(grid, move), float(
                "-inf"), float("inf"), mode, X)

            # Check if value is current minimum value
            if value < minValue:
                minValue = value
                bestMove = move
        return bestMove


def gridHeuristic(grid):
    """Calculate heuristic value of a tic-tac-toe grid

    Args:
        grid (list): 3x3 2D list representing tic-tac-toe grid

    Returns:
        int: Return 1 if X wins, -1 for O and 0 for draws or no win
    """

    winMark = winner(grid)
    if winMark == X:
        return 1
    elif winMark == O:
        return -1
    return 0


def startGrid():
    """Initial tic-tac-toe grid

    Returns:
        list: 3x3 2D list representing tic-tac-toe grid
    """

    return [[None, None, None],
            [None, None, None],
            [None, None, None]]


def nextPlayer(grid):
    """Determines the next player in a tic-tac-toe game

    Args:
        grid (list): 3x3 2D list representing tic-tac-toe grid

    Returns:
        string, NoneType: Return X or O; None if the grid is full
    """

    noneCount = 0

    for i in grid:
        for j in i:
            if not j:
                noneCount += 1

    if not noneCount:
        return None
    else:
        return O if noneCount % 2 == 0 else X


def gameEnd(grid):
    """Check if tic-tac-toe game has ended

    Args:
        grid (list): 3x3 2D list representing tic-tac-toe grid

    Returns:
        boolean: Return True if the game has ended; otherwise, return 
        False
    """

    if winner(grid) or winner(grid) == None:
        return True
    return False


def winner(grid):
    """Check winner of tic-tac-toe game

    Args:
        grid (list): 3x3 2D list representing tic-tac-toe grid

    Returns:
        String, NoneType, boolean: Return "X"/"O", None for tie, False
        for no winner
    """

    sequences = []

    # Add rows to sequences
    for i in grid:
        sequences.append(i)

    # Add columns to sequences
    for i in range(3):
        sequences.append([grid[j][i] for j in range(3)])

    # Add diagonals to sequences
    sequences.append([grid[i][i] for i in range(3)])
    sequences.append([grid[i][2-i] for i in range(3)])

    # Check if any row, column or diagonal has all X's or O's
    empty = 0
    for sequence in sequences:
        if None in sequence:
            empty += 1
        if all([k == X for k in sequence]):
            return X
        elif all([k == O for k in sequence]):
            return O
        else:
            continue

    # Check if game gameGrid is full with no winner
    if not empty:
        return None

    return False


def possibleMoves(grid):
    """Determine possible moves from a tic-tac-toe grid

    Args:
        grid (list): 3x3 2D list representing tic-tac-toe grid

    Returns:
        list: Return list of tuples of possible moves
    """

    # No moves are possible
    if gameEnd(grid):
        return None

    moves = []
    for i in range(3):
        for j in range(3):
            if not grid[i][j]:
                moves.append((i, j))
    return moves


def moveResult(grid, move):
    """Return new grid resulting from a move

    Args:
        grid (list): 3x3 2D list representing tic-tac-toe grid
        move (tuple): Two elements that specify the indices of the grid

    Returns:
        list: New 2D list with a new move addded
    """

    # Copy grid to prevent altering the original grid; allows
    # minimax() to determine all possiblities of a tic-tac-toe game
    gridCopy = [row[:] for row in grid]

    # Add move to new grid
    gridCopy[move[0]][move[1]] = nextPlayer(grid)

    return gridCopy


def displaygameGrid(grid):
    """Print tic-tac-toe grid with inputted moves

    Args:
        grid (list): 3x3 2D list representing tic-tac-toe grid
    """

    # Print labels
    print("\n")
    print("{:>6}{:>6}{:>6}\n".format("a", "b", "c").center(
        TERMINAL_COLUMNS))
    
    # Print tic-tac-toe grid with side labels
    for row in range(3):
        # Substitute None values for spaces in order to format grid 
        # properly
        moves = [" " if not move else move for move in grid[row]]
        print("{1:>4}{0:>6}{0:>6}{1:>6}".format(
            "|", " ").center(TERMINAL_COLUMNS))
        print("{1:<3}{5:3}{2:3}{0:3}{3:3}{0:3}{4:3}{5}".format(
            "|", 3 - row, moves[0], moves[1], moves[2], " ").center(
                TERMINAL_COLUMNS))
        if row == 2:
            print("{1:>4}{0:>6}{0:>6}{1:>6}".format(
                "|", " ").center(TERMINAL_COLUMNS))
        else:
            print("{2:>4}{1}{0}{1}{0}{1}{2}".format(
                "|", "_"*5, " ").center(TERMINAL_COLUMNS))


def alphanumericToCoordinate(move):
    """Convert alphanumeric notation coresponding list indices on grid

    Args:
        move (string): Alphanumeric move on the tic-tac-toe grid

    Returns:
        tuple: Two indices (int) for a 3x3 2D list
    """

    if not re.fullmatch(r"[a-cA-C][1-3]", move):
        return False
    return (3 - int(move[1]), ord(move[0].upper()) - 65)


def coordinateToAlphanumeric(move):
    """Convert coordinate notation to alphanumeric

    Args:
        move (tuple): Two indices (int) fora 3x3 2D list

    Returns:
        string: Alphanumeric move on the tic-tac-toe grid
    """

    # Convert first integer in move to ASCII; convert move to string
    # in order to be printable
    return chr(move[1] + 97) + str(3 - move[0])


def validateMove(grid, move):
    """Validate if a tic-tac-toe move is legal on the current grid

    Args:
        grid (list): 3x3 two-dimensional list that represents
        tic-tac-toe grid
        move (tuple): Planned action on grid

    Returns:
        boolean: Legality of move
    """

    try:
        return move in possibleMoves(grid)
    except:
        return False


def winMessage(winner):
    """Display end game message

    Args:
        winner (string, NoneType): Display if X or O has won or 
        indicate a draw in no one has won
    """

    if winner:
        print()
        print(f"PLAYER {winner} WINS".center(TERMINAL_COLUMNS))
        print("\n")
    else:
        print()
        print("DRAW".center(TERMINAL_COLUMNS))
        print("\n")


def displayStartScreen():
    """Print start screen of tic-tac-toe game with options"""

    # ASCII art for "TIC-TAC-TOE"
    title = (
        "\n\n",
        "████████╗██╗ ██████╗          ████████╗ █████╗  ██████╗          ████████╗ ██████╗ ███████╗",
        "╚══██╔══╝██║██╔════╝          ╚══██╔══╝██╔══██╗██╔════╝          ╚══██╔══╝██╔═══██╗██╔════╝",
        "   ██║   ██║██║       █████╗     ██║   ███████║██║       █████╗     ██║   ██║   ██║█████╗  ",
        "   ██║   ██║██║       ╚════╝     ██║   ██╔══██║██║       ╚════╝     ██║   ██║   ██║██╔══╝  ",
        "   ██║   ██║╚██████╗             ██║   ██║  ██║╚██████╗             ██║   ╚██████╔╝███████╗",
        "   ╚═╝   ╚═╝ ╚═════╝             ╚═╝   ╚═╝  ╚═╝ ╚═════╝             ╚═╝    ╚═════╝ ╚══════╝\n")

    menu = (
        "PRESS KEY TO PLAY",
        "",
        "[P] PLAYER VS PLAYER",
        "[C] PLAYER VS COMPUTER",
        "",
        "[I] INSTRUCTIONS",
        "[ESC] EXIT")

    # Display and center each line of the title
    for line in title:
        print(line.center(TERMINAL_COLUMNS))

    # Display instructions to user
    for line in menu:
        print(line.center(TERMINAL_COLUMNS))


def displayInstructions():
    """Display instructions of tic-tac-toe"""

    instructions = (
        "\n\n",
        "HOW TO PLAY",
        "",
        "Take turns with a player or computer marking a grid with an X "
        "or an O.",
        "Win by placing three (3) X's or three (3) O's in a horizontal,"
        " diagonal or vertical line.",
        "\n",
        "USING THE ALPHANUMERIC GRID",
        "",
        "To input a move, use a combination of a letter (a-c) and a "
        "number (1-3) to indicate the position",
        "in which the X or O will be inserted on the grid.",
        "",
        "EXAMPLE: \"a3\" inputs X in the top right corner on player X's "
        "turn:\n",
        "      a     b     c\n",
        "         |     |     ",
        "3     X  |     |     ",
        "    _____|_____|_____",
        "         |     |     ",
        "2        |     |     ",
        "    _____|_____|_____",
        "         |     |     ",
        "1        |     |     ",
        "         |     |     \n",
        "[BACKSPACE] EXIT INSTRUCTIONS")

    # Display each line of instructions
    for line in instructions:
        print(line.center(TERMINAL_COLUMNS))


def playAgain():
    """Check if user wants to play another tic-tac-toe game

    Returns:
        boolean: Return True if player wants to play again; False if
        not
    """

    menu = (
        "PLAY AGAIN?",
        "\n",
        "[Y] YES",
        "[ESC] END GAME"
    )

    # Print each line of menu
    for line in menu:
        print(line.center(TERMINAL_COLUMNS))

    # Wait for player to input response
    while not keyboard.is_pressed("y"):
        if keyboard.is_pressed("escape"):
            # clear screen
            return False
    return True


if __name__ == "__main__":
    main()
