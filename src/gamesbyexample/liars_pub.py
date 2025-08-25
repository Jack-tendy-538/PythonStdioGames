import random
import time

# 全局变量
target = None  # 目标牌
gun_chamber = []  # 左轮手枪弹巢
gun_index = 0  # 当前子弹位置
players = []  # 玩家列表
active_players = []  # 活跃玩家列表（未被淘汰的玩家）
player_hands = {}  # 玩家手牌
current_player_index = 0  # 当前玩家索引
deck = []  # 牌堆

def reset_deck():
    """重置并洗牌"""
    global deck
    deck = ["J"] * 4 + ["Q"] * 4 + ["K"] * 4 + ["A"] * 4 + ["O"] * 4
    random.shuffle(deck)

def deal_cards():
    """发牌给所有活跃玩家"""
    global player_hands, deck
    
    # 如果牌堆不够，重新洗牌
    if len(deck) < len(active_players) * 5:
        reset_deck()
    
    # 给每个活跃玩家发5张牌
    for player in active_players:
        if len(player_hands[player]) == 0:  # 只给没有牌的玩家发牌
            player_hands[player] = [deck.pop() for _ in range(min(5, len(deck)))]

def init_gun():
    """初始化左轮手枪"""
    global gun_chamber, gun_index
    gun_chamber = [False, False, False, False, False, True]
    random.shuffle(gun_chamber)
    gun_index = 0

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


def shoot():
    """开枪，返回是否击中"""
    global gun_index, gun_chamber
    
    is_hit = gun_chamber[gun_index]
    gun_index = (gun_index + 1) % 6
    
    # 如果已经用完所有子弹，重新装填
    if gun_index == 0:
        random.shuffle(gun_chamber)
    
    return is_hit

def is_false_declaration(played_cards):
    """检查声明是否虚假"""
    global target
    for card in played_cards:
        if card != target and card != "O":  # 如果不是目标牌也不是Joker
            return True
    return False

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

def get_next_player():
    """获取下一个活跃玩家"""
    global current_player_index, active_players
    
    if len(active_players) <= 1:
        return current_player_index
    
    # 找到下一个活跃玩家
    next_index = (current_player_index + 1) % len(active_players)
    return next_index

def check_win_condition():
    """检查是否满足胜利条件"""
    return len(active_players) == 1, active_players[0] if len(active_players) == 1 else None

def get_player_input(player, hand):
    """获取玩家输入"""
    print(f"\n{player}'s turn. Your cards: {', '.join(hand)}")
    
    # 获取出牌数量
    while True:
        try:
            num_to_play = int(input("How many cards do you want to play? (1-2): "))
            if 1 <= num_to_play <= 2 and num_to_play <= len(hand):
                break
            else:
                print("Invalid input. Please enter 1 or 2, and make sure you have enough cards.")
        except ValueError:
            print("Please enter a valid number.")
    
    # 获取要出的牌
    print("Select cards to play (enter the card letters, separated by spaces):")
    print("Available cards:", ", ".join(hand))
    
    while True:
        try:
            selected_cards = input().strip().upper().split()
            # 验证输入
            if len(selected_cards) != num_to_play:
                print(f"Please select exactly {num_to_play} card(s).")
                continue
            
            # 检查所选牌是否在手牌中
            valid_selection = True
            temp_hand = hand.copy()
            for card in selected_cards:
                if card in temp_hand:
                    temp_hand.remove(card)
                else:
                    print(f"Card {card} is not in your hand or has already been selected.")
                    valid_selection = False
                    break
            
            if valid_selection:
                return selected_cards
        except Exception as e:
            print("Invalid input. Please try again.")

def main():
    """主函数，运行骗子酒馆游戏"""
    global target, players, active_players, player_hands, current_player_index, deck
    
    # 显示游戏说明
    show_instructions()
    
    # 初始化玩家
    players = ["Player1", "Player2", "Player3", "Player4"]
    active_players = players.copy()
    player_hands = {player: [] for player in players}
    
    # 初始化牌堆和发牌
    reset_deck()
    deal_cards()
    
    # 初始化左轮手枪
    init_gun()
    
    # 随机选择目标牌
    target = random.choice(["J", "Q", "K", "A"])
    print(f"\n本局游戏的目标牌是: {target}")
    
    # 游戏主循环
    game_over = False
    winner = None
    last_player = None
    last_action = None
    
    while not game_over:
        current_player = active_players[current_player_index]
        
        # 如果当前玩家没有牌，重新发牌
        if len(player_hands[current_player]) == 0:
            deal_cards()
            # 如果重新发牌后仍然没有牌，可能是牌堆空了
            if len(player_hands[current_player]) == 0:
                print(f"{current_player} has no cards to play! Skipping turn.")
                current_player_index = get_next_player()
                continue
        
        # 获取玩家输入
        cards_to_play = get_player_input(current_player, player_hands[current_player])
        num_to_play = len(cards_to_play)
        
        # 从手牌中移除这些牌
        for card in cards_to_play:
            player_hands[current_player].remove(card)
        
        # 玩家声明出牌 (总是声明为目标牌)
        print(f"{current_player} plays {num_to_play} card(s) and declares: 'These are all {target}s!'")
        
        # 记录最后动作
        last_action = f"declared {num_to_play} {target}(s)"
        last_player = current_player
        
        # 只有下家可以挑战
        next_player_index = get_next_player()
        next_player = active_players[next_player_index]
        
        # 下家决定是否挑战
        challenge = input(f"{next_player}, do you challenge? (y/n): ").strip().lower()
        will_challenge = challenge == 'y'
        
        if will_challenge:
            print(f"{next_player} challenges the declaration!")
            
            # 验证声明
            declaration_false = is_false_declaration(cards_to_play)
            
            if not declaration_false:
                print("The declaration was truthful!")
                loser = next_player
            else:
                print("The declaration was a lie!")
                loser = current_player
            
            # 执行枪击
            print(f"\nShooting at {loser}...")
            time.sleep(1)  # 增加 suspense
            
            is_dead = shoot()
            shoot_at(loser, is_dead)
            
            # 如果被击中，移除该玩家
            if is_dead:
                print(f"{loser} is eliminated from the game!")
                active_players.remove(loser)
                player_hands[loser] = []
                
                # 检查游戏是否结束
                game_over, winner = check_win_condition()
                if game_over:
                    break
        else:
            print(f"{next_player} does not challenge.")
        
        # 显示当前游戏状态
        print("\nCurrent game status:")
        show_remains(player_hands, last_player, last_action)
        
        # 移动到下一个玩家
        current_player_index = get_next_player()
    
    # 游戏结束
    print(f"\n🎉 Game Over! {winner} wins! 🎉")

if __name__ == "__main__":
    main()
