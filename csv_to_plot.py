import matplotlib.pyplot as plt
import pandas as pd

FILENAME = 'data/Test4.data'
NAME_LIST = ['Top-Left', 'Top-Middle', 'Top-Right',
             'Bottom-Left', 'Bottom-Middle', 'Bottom-Right',
             'Left Intensity', 'Middle Intensity', 'Right Intensity']
START = 0
END = 1000
MIN_VAL = 0
MAX_VAL = 100
sperpoll = 1/0.94
LINES = [6.45*sperpoll, 15.54*sperpoll, 22.35*sperpoll, 29.57*sperpoll, 36.95*sperpoll]
LINE_LABELS = ['Object 1 Enters', 'Object 2 Enters', 'Object 3 Enters', 'Object 4 Enters', 'Object 5 Enters']
TITLE = 'Graph showing vibration intensity as an object is moved from top to bottom\n'
X_LABEL = 'Polls'
Y_LABEL = 'Vibration Intensity'
# Y_LABEL = 'Distance (cm)'
LABEL_HEIGHT = 90

data = pd.read_csv(FILENAME, header=None, names=NAME_LIST)
data = data.iloc[:, 6:]
data = data[START:END]
data = data.clip(MIN_VAL, MAX_VAL)

for col in data:
    data[col] = data[col].rolling(1).mean()

plt.figure()
data.plot()
plt.vlines(LINES, MIN_VAL, MAX_VAL, linestyle='--', color='grey')
plt.title(TITLE)
plt.xlabel(X_LABEL)
plt.ylabel(Y_LABEL)
plt.ylim(MIN_VAL, MAX_VAL)
for i, line in enumerate(LINES):
    plt.text(line + .1, LABEL_HEIGHT, LINE_LABELS[i], rotation=270)
plt.show()
