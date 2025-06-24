#!/usr/bin/env python3
"""
Math Snake Game Runner
Checks for pygame installation and runs the game
"""

import sys
import subprocess

def check_pygame():
    """Check if pygame is installed"""
    try:
        import pygame
        return True
    except ImportError:
        return False

def install_pygame():
    """Install pygame using pip"""
    print("Pygame not found. Installing...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
        print("Pygame installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("Failed to install pygame. Please install it manually:")
        print("pip install pygame")
        return False

def main():
    """Main function to run the game"""
    if not check_pygame():
        if not install_pygame():
            sys.exit(1)
    
    # Import and run the game
    try:
        from math_snake_pygame import MathSnakeGame
        print("Starting Math Snake Game...")
        print("Controls:")
        print("- Arrow keys: Move snake")
        print("- P: Pause/Unpause")
        print("- ESC: Quit")
        print("- SPACE: Restart (when game over)")
        print("\n🎮 NEW ENHANCED GAMEPLAY:")
        print("🔥 LIVES SYSTEM: You have 2 lives - 2 wrong eggs = Game Over!")
        print("⏰ TIMER: Each level has a time limit!")
        print("📈 LEVELS: Math gets more complex as you progress!")
        print("   • Level 0: Simple addition/subtraction (45s)")
        print("   • Level 1: All 4 operations (42s)")
        print("   • Level 2+: Multi-step equations like 5 + 7 - 9 = 3")
        print("🥚 COLLECT: Find and eat ALL numbers from the equation")
        print("🎯 CHALLENGE: All eggs look identical - no hints!")
        print("⚡ SPEED: Snake gets faster every level")
        
        game = MathSnakeGame()
        game.run()
    except Exception as e:
        print(f"Error running game: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
