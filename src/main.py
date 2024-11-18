from src.game import Game

import sys
import traceback

def main():
    try:
        game = Game()
        game.run()
    except Exception as e:
        with open('error_log.txt', 'w') as f:
            f.write(f"Error: {str(e)}\n")
            f.write(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()