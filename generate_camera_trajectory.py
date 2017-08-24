
YMIN = -4000.0
YMAX = 4800.0
X = -700.0
Z = 410.0

NB = 20


# faire un linspace

str = '[ \n'
x = X
y = YMIN
z = Z
for idx in range(NB):
    str += '[{'
    str += '"x":{x}, "y":{y}, "z":{y}'.format(x=x, y=y, z=z)
    str += '},'
    str += '{"yaw":0.0, "pitch":0.0, "roll":0.0}]'
    if idx < NB-1:
        str += ','
    str += '\n'

    y += (YMAX-YMIN)/NB
str += ']'

print(str)