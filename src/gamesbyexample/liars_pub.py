"""
This file isn't part of the Jack Tendy project.
This is a game that was created by a user named Jack Tendy.
This file is part of the Liars Pub game, which is a simple text-based game

All the code should be styled according to Al Sweigart's style guide.
"""
import random, sys, time
# Python 2 compatibility for input (remove if only supporting Python 3)
if sys.version_info[0] < 3:
    try:
        input = raw_input
    except NameError:
        pass

# cards
card_img = {
    "J": [r"|--------|",
          r"|    |   |",
          r"|    |   |",
          r"|  __|   |",
          r"|________|"],
    "Q": [r"|--------|",
          r"|   __   |",
          r"|  |__|  |",
          r"|     \  |",
          r"|________|"],
    "K": [r"|--------|",
          r"|  | /   |",
          r"|  |<    |",
          r"|  | \   |",
          r"|________|"],
    "A": [r"|--------|",
          r"|   /\   |",
          r"|  /--\  |",
          r"| |    | |",
          r"|________|"],
    "JOKER": [r"|--------|",  # JOKER can be represented as O
              r"|  O  |JO|",
              r"| /|\ |KE|",
              r"| / \ |R`|",
              r"|________|"]
}

CARD_GAP = "  "
def display_cards(cards):
    """Display the cards in a list of cards."""
    rows = [""] * 5
    for card in cards:
        for i in range(5):
            rows[i] += card_img[card][i] + CARD_GAP
    for row in rows:
        print(row)

def shoot_at(player, is_killed):
    """ Draw a gun and shoot at the player. 
    If is_killed is True, the player is killed.
    """
    print("~    |\ ____________  _",flush=True)
    print("~   / |_____________||",end="",flush=True)
    if is_killed:
        print("■> "+player+" is killed! > x <",flush=True)
    else:
        print(" > "+player+" is safe! ^ _ ^",flush=True)
    print("~  /  |______________|ˉˉ",flush=True)
    print('~ /  /',flush=True)
    print("~|_|_|",flush=True)

def show_remains(remain_dict,last_player,last_action):
    """Show the remaining players and their num of cards, one per row.
      remain_dict is a dict of {player_name: num_of_cards}.
      output should be like:
        Player1: o o o o o
        Player2: o o o  <- if last_player is Player2 and last_action is "put out 2 cards"
        Player3: (out)
    if last_player and last_action are not None,
      show the last action at his row of the output(Who has put out how many cards).
    """
    for player, num in remain_dict.items():
        print("# ",end="")  # to flush the output buffer
        if isinstance(num, list):
            card_count = len(num)
        else:
            card_count = num
        if card_count > 0:
            cards = "o " * card_count
            if player == last_player and last_action is not None:
                print(f"{player}: {cards} <- {last_player} {last_action}")
            else:
                print(f"{player}: {cards}")
        else:
            print(f"{player}: (out)")

def _is_false_declaration():
    global last_played_cards, target
    """Check if the last declaration is false."""
    for card in last_played_cards:
        if card != target and card != "O":
            return True
    return False

def show_instructions():
    """Display the instructions for the game."""
    print('''Liars Pub, by Jack Tendy.
A simple card game for 4 players.
The goal is to live the last.
Rules:
- Each player is dealt 5 cards.
- Players take turns playing cards face down and declaring their rank (J, Q, K, A, O).
- Other players can challenge the declaration.
- If the declaration is true, the challenger gets the gun shoot.
- If the declaration is false, the declarer gets the gun shoot.
- When one player has no cards left, refill their hand from the deck.
- The gun has 6 bullets, 1 full and 5 empty..
- When the gun is shot, if it's a full bullet, the player is out.
- The last player remaining wins the game.
- Press Enter to continue...''')
    input()

# the following code uses generators to manage the game flow, and coroutines to handle player actions.
def gen_gun():
    """A generator that yields True for a full bullet and False for an empty bullet.
    """
    while True:
        bullet_chamber = [False, False, False, False, False, True]
        random.shuffle(bullet_chamber)
        for chamber in bullet_chamber:
            yield chamber

def reset_deck(players):
    """Reset and shuffle the deck, return a list of cards."""
    deck = ["J"] * 4 + ["Q"] * 4 + ["K"] * 4 + ["A"] * 4 + ["O"] * 4
    random.shuffle(deck)
    return {player: [deck.pop() for _ in range(5)] for player in players}

def gen_pub(players):
    """A generator that manages the game flow"""
    remains = reset_deck(players)
    index = 0
    while True:
        name = players[index]
        feedback = yield name, remains
        if feedback[0] == "shoot":
            # shoot at the player
            is_killed = feedback[1]
            if is_killed:
                remains[name] = []
                if sum(1 for cards in remains.values() if cards) == 1:
                    # only one player left
                    winner = [player for player, cards in remains.items() if cards][0]
                    yield "win", winner
                    return
        elif feedback[0] == "put":
            # put out cards
            num, cards, target = feedback[1], feedback[2], feedback[3]
            for card in cards:
                remains[name].remove(card)
            if not remains[name]:
                # refill if no cards left-- this redistribute all players' cards
                remains = reset_deck(players)
            index = (index + 1) % len(players)

def main():
    """
    Runs the main loop for the Liars Pub card game.
    This function initializes the game, sets up players, and manages the turn-based gameplay loop.
    Players take turns declaring and playing cards, and other players may challenge the declaration.
    If challenged, the truthfulness of the declaration is checked, and the loser faces a penalty (simulated by 'shooting').
    The game continues until a win condition is met.
    Key steps:
    - Shows instructions to the players.
    - Initializes player list and game generators for pub and gun mechanics.
    - Tracks game state variables such as last player, last action, last played cards, and current target declaration.
    - For each turn:
        - Displays current player's hand and game state.
        - Prompts the player to select cards and make a declaration.
        - Allows other players to challenge the declaration.
        - Resolves challenges and applies penalties.
        - Checks for win condition after each challenge.
        - Advances to the next player if no challenge occurs.
    Assumes existence of helper functions:
    - show_instructions()
    - gen_pub(players)
    - gen_gun()
    - show_remains(remains, last_player, last_action)
    - display_cards(cards)
    - shoot_at(player, is_killed)
    """
    """Main game function."""
    show_instructions()
    
    # Initialize players
    players = ["Player1", "Player2", "Player3", "Player4"]
    pub_gen = gen_pub(players)
    gun_gen = gen_gun()
    
    # Game state variables
    last_player = None
    last_action = None
    last_played_cards = []
    target = None
    
    # Start the game
    player, remains = next(pub_gen)
    
    while True:
        print(f"\n--- {player}'s turn ---")
        show_remains(remains, last_player, last_action)
        
        # Display player's hand
        print(f"\nYour cards: {', '.join(remains[player])}")
        
        # Get player's action
        while True:
            try:
                num_cards = int(input("How many cards do you want to play? "))
                if num_cards < 1 or num_cards > len(remains[player]):
                    print(f"Invalid number. You have {len(remains[player])} cards.")
                    continue
                    
                # Get which cards to play
                print("Your cards: ", end="")
                for i, card in enumerate(remains[player]):
                    print(f"{i+1}:{card} ", end="")
                print()
                
                card_indices = input(f"Enter the indices (1-{len(remains[player])}) of cards to play, separated by spaces: ").split()
                cards_to_play = [remains[player][int(i)-1] for i in card_indices]
                
                if len(cards_to_play) != num_cards:
                    print("Number of cards doesn't match the indices provided.")
                    continue
                    
                # Get declaration
                valid_declarations = ["J", "Q", "K", "A", "O"]
                declaration = input("What are you declaring? (J, Q, K, A, O): ").upper()
                if declaration not in valid_declarations:
                    print("Invalid declaration. Must be J, Q, K, A, or O.")
                    continue
                    
                break
            except (ValueError, IndexError):
                print("Invalid input. Please try again.")
        
        # Update game state
        last_player = player
        last_action = f"declared {num_cards} {declaration}(s)"
        last_played_cards = cards_to_play
        target = declaration
        
        # Send action to game generator
        pub_gen.send(("put", num_cards, cards_to_play, declaration))
        
        # Check for challenges
        challenger = None
        for p in players:
            if p != player and remains[p]:  # Only players still in the game can challenge
                challenge = input(f"{p}, do you want to challenge? (y/n): ").lower()
                if challenge == 'y':
                    challenger = p
                    break
        
        # Resolve challenge or continue
        if challenger:
            print(f"\n{challenger} challenges {player}'s declaration!")
            print("The played cards are: ")
            display_cards(last_played_cards)
            
            # Check if declaration was true
            is_truthful = True
            for card in last_played_cards:
                if card != target and card != "O":  # O (Joker) is wild
                    is_truthful = False
                    break
            
            if is_truthful:
                print(f"{player}'s declaration was truthful! {challenger} gets shot.")
                shoot_player = challenger
            else:
                print(f"{player} was lying! {player} gets shot.")
                shoot_player = player
            
            # Perform the shooting
            is_killed = next(gun_gen)
            shoot_at(shoot_player, is_killed)
            
            # Update game state
            pub_gen.send(("shoot", is_killed))
            
            # Check for win condition
            result = next(pub_gen)
            if result[0] == "win":
                print(f"\n🎉 {result[1]} wins the game! 🎉")
                break
        else:
            print("No one challenged. Moving to next player.")
        
        # Get next player
        player, remains = next(pub_gen)

if __name__ == "__main__":
    main()