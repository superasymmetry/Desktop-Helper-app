import pyautogui, sys


print('Press Ctrl-C to quit.')
try:
    while True:
        x, y = pyautogui.position()
        positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
        print(positionStr, end='')
        print('\b' * len(positionStr), end='', flush=True)
except KeyboardInterrupt:
    print('\n')

# pyautogui.moveTo(100, 200)
# pyautogui.dragTo(100, 200, button='left')
# pyautogui.moveTo(800,800, 2, pyautogui.easeInQuad)
