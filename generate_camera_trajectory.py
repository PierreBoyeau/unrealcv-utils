import numpy as np

# CONSTANTS : PLEASE ADAPT TO YOUR UE_SCENE!
Y_MIN = -1250.0
Y_MAX = -30.0
X = 200.0
Z = 120.0
DX = 50.0
DZ = 40.0
NB = 50


D_ROT = 5.0
D_ROLL = 30.0

# Arrays definition
x = X + 2*DX*(np.random.random(NB) - 0.5)
y = np.linspace(start=Y_MIN, stop=Y_MAX, num=NB)
z = Z + 2*DZ*(np.random.random(NB) - 0.5)

yaw = 2*D_ROT*(np.random.random(NB) - 0.5)
pitch = 2*D_ROT*(np.random.random(NB) - 0.5)
roll = 2*D_ROLL*(np.random.random(NB) - 0.5)

result = '[ \n'

for idx in range(NB):
    result += '[{'
    result += '"x":{x}, "y":{y}, "z":{z}'.format(x=x[idx],
                                                 y=y[idx],
                                                 z=z[idx])
    result += '},'
    result += '{'
    result += '"yaw":{yaw}, "pitch":{pitch}, "roll":{yaw}'.format(yaw=yaw[idx],
                                                                  pitch=pitch[idx],
                                                                  roll=roll[idx])
    result += '}]'
    if idx < NB-1:
        result += ','
    result += '\n'
result += ']'

print(result)

with open("camera_trajectory.json", "w") as f:
    f.write(result)

print("camera_trajectory.json updated")
