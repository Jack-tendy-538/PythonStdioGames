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
    # 初始化牌堆和玩家手牌
    deck = ["J"] * 4 + ["Q"] * 4 + ["K"] * 4 + ["A"] * 4 + ["O"] * 4
    random.shuffle(deck)
    remains = {player: [deck.pop() for _ in range(5)] for player in players}
    
    index = 0
    while True:
        name = players[index]
        
        # 检查当前玩家是否有牌，如果没有则重新洗牌
        if not remains[name]:
            # 重新洗牌并给所有玩家发牌
            deck = ["J"] * 4 + ["Q"] * 4 + ["K"] * 4 + ["A"] * 4 + ["O"] * 4
            random.shuffle(deck)
            for player in players:
                if remains[player]:  # 如果玩家还有牌，保留他们的牌
                    # 只给没有牌的玩家发牌
                    if not remains[player]:
                        remains[player] = [deck.pop() for _ in range(5)]
        
        feedback = yield name, remains
        if feedback is None:
            continue
            
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
            
            # 检查是否需要重新洗牌（任何玩家手牌为空）
            if any(not cards for cards in remains.values()):
                # 重新洗牌并给所有玩家发牌
                deck = ["J"] * 4 + ["Q"] * 4 + ["K"] * 4 + ["A"] * 4 + ["O"] * 4
                random.shuffle(deck)
                for player in players:
                    if not remains[player]:  # 只给没有牌的玩家发牌
                        remains[player] = [deck.pop() for _ in range(5)]
        
        index = (index + 1) % len(players)


def get_players_name():
    """Get player names from input."""
    players = []
    for i in range(4):
        name = input(f"Enter name for Player {i+1} (or press Enter for default 'Player{i+1}'): \n")
        if not name.strip():
            name = f"Player{i+1}"
        players.append(name)
    return players

def main():
    """主函数，运行骗子酒馆游戏"""
    global target, last_played_cards
    print("Welcome to Liars Pub!")
    # 显示游戏说明
    show_instructions()
    
    # 初始化玩家
    players = ["Player1", "Player2", "Player3", "Player4"]
    # 初始化游戏状态生成器
    game = gen_pub(players)
    # 初始化左轮手枪生成器
    gun = gen_gun()
    
    # 随机选择目标牌
    global target
    target = random.choice(["J", "Q", "K", "A"])
    print(f"\n本局游戏的目标牌是: {target}")
    
    # 获取初始游戏状态
    current_player, remains = next(game)
    last_player = None
    last_action = None
    last_played_cards = []
    
    # 游戏主循环
    while True:
        print(f"\n===== {current_player}'s turn =====")
        
        # 显示当前玩家手牌
        print(f"Your cards: {', '.join(remains[current_player])}")
        
        # 检查玩家是否有牌可出
        if not remains[current_player]:
            print(f"{current_player} has no cards to play! Refilling...")
            # 发送一个空操作以触发重新洗牌
            result = game.send(("pass", None))
            if result and result[0] == "win":
                print(f"\n🎉 Game Over! {result[1]} wins! 🎉")
                break
            else:
                current_player, remains = result
            continue
            
        # 玩家选择出牌数量 (简化: 随机出1-2张)
        num_to_play = random.randint(1, min(2, len(remains[current_player])))
        cards_to_play = random.sample(remains[current_player], num_to_play)
        last_played_cards = cards_to_play.copy()
        
        # 玩家声明出牌 (总是声明为目标牌)
        print(f"{current_player} plays {num_to_play} card(s) and declares: 'These are all {target}s!'")
        
        # 记录最后动作
        last_action = f"declared {num_to_play} {target}(s)"
        last_player = current_player
        
        # 只有下家可以挑战
        next_player_index = (players.index(current_player) + 1) % len(players)
        next_player = players[next_player_index]
        
        # 检查下家是否还在游戏中
        if remains.get(next_player):  # 使用get方法避免KeyError
            # 下家决定是否挑战 (简化: 有一定概率挑战)
            will_challenge = random.random() < 0.4  # 40%概率挑战
            
            if will_challenge:
                print(f"{next_player} challenges the declaration!")
                
                # 验证声明
                is_truthful = not _is_false_declaration()
                
                if is_truthful:
                    print("The declaration was truthful!")
                    loser = next_player
                else:
                    print("The declaration was a lie!")
                    loser = current_player
                
                # 执行枪击
                print(f"\nShooting at {loser}...")
                time.sleep(1)  # 增加 suspense
                
                is_dead = next(gun)
                shoot_at(loser, is_dead)
                
                # 更新游戏状态
                result = game.send(("shoot", is_dead))
                
                if result and result[0] == "win":
                    print(f"\n🎉 Game Over! {result[1]} wins! 🎉")
                    break
            else:
                print(f"{next_player} does not challenge.")
                # 正常出牌，更新游戏状态
                result = game.send(("put", num_to_play, cards_to_play, target))
        else:
            print(f"{next_player} is out, no one to challenge.")
            # 正常出牌，更新游戏状态
            result = game.send(("put", num_to_play, cards_to_play, target))
        
        # 显示当前游戏状态
        print("\nCurrent game status:")
        show_remains(remains, last_player, last_action)
        
        # 获取下一个玩家
        if result and result[0] == "win":
            print(f"\n🎉 Game Over! {result[1]} wins! 🎉")
            break
        else:
            current_player, remains = result

if __name__ == "__main__":
    main()