import random
import time

def genWindow():
    notification = input("What notification would you like to see? ")
    while len(notification) > 87:
        print("Notification too long! Please keep it under 87 characters.")
        notification = input("What notification would you like to see? ")
    msg_length= max(30, len(notification))+4
    window = [
        '+' + '-' * (msg_length - 2) + '+',
        '|' + ' ' * (msg_length - 2) + '|',
        '| ' + notification.ljust(msg_length - 2) + ' |',
        "|" + '[ Close Ctrl+C ]'.rjust(msg_length - 2) + " |",
        '+' + '-' * (msg_length - 2) + '+'
        ]
    return window, msg_length

def genRandomBg(width, height):
    material = ['.','*','-']+[' ']*97
    bg = []
    for i in range(height):
        line = ''.join(random.choice(material) for _ in range(width))
        bg.append(line)
    return bg

def placeWindow(x ,y, window):
    global pattern
    for i, line in enumerate(window):
        pattern[y+i] = pattern[y+i][:x] + line + pattern[y+i][x+len(line):]

# constants
pause = 0.1
HEIGHT = 30
WIDTH = 93
window, windowWidth = genWindow()
windowHeight = len(window)
go_down, go_right = True, True
x, y = 0, 0
while True:
    pattern = genRandomBg(WIDTH, HEIGHT)
    placeWindow(x, y, window)
    print('\n'.join(pattern),flush=True)
    time.sleep(pause)
    if go_right:
        x += 1
    else:
        x -= 1
    if go_down:
        y += 1
    else:
        y -= 1
    if x + windowWidth >= WIDTH:
        go_right = False
    if x <= 0:
        go_right = True
    if y + windowHeight >= HEIGHT:
        go_down = False
    if y <= 0:
        go_down = True