import glm
import glfw
import math
import numpy as np


# Variáveis de janela 
altura = 0
largura = 0
window = 0

##############################################
############# FUNÇÕES DE MATRIZES ############
##############################################

# Matriz Projection
fov = 45
near = 0.1 
far = 1000.0


def view():
    global cameraPos, cameraFront, cameraUp
    mat_view = glm.lookAt(cameraPos, cameraPos + cameraFront, cameraUp);
    mat_view = np.array(mat_view)
    return mat_view

def projection():
    global altura, largura
    global fov
    # perspective parameters: fovy, aspect, near, far
    mat_projection = glm.perspective(glm.radians(fov), largura/altura, near, far)
    mat_projection = np.array(mat_projection)    
    return mat_projection

##############################################
############## COMANDOS DE INPUT #############
##############################################

# Modo poligonal
polygonal_mode = False

# Variáveis de mouse
firstMouse = True
yaw = -90.0 
pitch = 0.0
lastX =  largura/2
lastY =  altura/2

# Variaveis de câmera
cameraPos   = glm.vec3(0.0,  0.0,  1.0);
cameraFront = glm.vec3(0.0,  0.0, -1.0);
cameraUp    = glm.vec3(0.0,  1.0,  0.0);
cameraPos_antes = glm.vec3(0.0,  1.0,  0.0);

# Iluminação
light_mode = 0
ka_mult = 1
tx = 1
tz = 1

def commands():

    # Define eventos do teclado
    def key_event(window,key,scancode,action,mods):
        
        global cameraPos, cameraFront, cameraUp
        global cameraPos_antes

        # Movimento da camera
        cameraSpeed = 0.2
        if key == 87 and (action==1 or action==2): # tecla W
            cameraPos += cameraSpeed * cameraFront
        
        if key == 83 and (action==1 or action==2): # tecla S
            cameraPos -= cameraSpeed * cameraFront
        
        if key == 65 and (action==1 or action==2): # tecla A
            cameraPos -= .7*glm.normalize(glm.cross(cameraFront, cameraUp)) * cameraSpeed
            
        if key == 68 and (action==1 or action==2): # tecla D
            cameraPos += .7*glm.normalize(glm.cross(cameraFront, cameraUp)) * cameraSpeed
            
        # limitando altura da camera dentro do cenário
        # if cameraPos[1] <= -0.092 : cameraPos[1] = -0.092
        # if cameraPos[1] >= 17 : cameraPos[1] = 17
        
        # Raio máximo do movimento no plano
        r_max = 20
        # Raio atual da posição da câmera
        r_atual = ((cameraPos[0]**2) + (cameraPos[2]**2))**(1/2)

        # Se raio atual for menor q raio maximo
        # if r_atual <= r_max:
        #     # Salva posição atual
        #     cameraPos_antes[0] = cameraPos[0]
        #     cameraPos_antes[2] = cameraPos[2]
        # else: # Se raio atual for maior q raio maximo
        #     # Mantém a posição anterior
        #     cameraPos[0] = cameraPos_antes[0]
        #     cameraPos[2] = cameraPos_antes[2]

        global light_mode, ka_mult, tx, tz

        # Tecla L para ativar/desativar luz colorida 
        if key == 76 and action==1:
            light_mode = not(light_mode)
            print('Luzes coloridas:', light_mode)
        # Tecla P para aumentar luz ambiente
        if key == 80 and (action==1 or action==2): # tecla P
            ka_mult += 0.2
            print('Luz ambiente:', ka_mult)
        # Tecla U para diminuir luz ambiente
        if key == 85 and (action==1 or action==2): # tecla U
            ka_mult -= 0.2
            print('Luz ambiente:', ka_mult)


        # if key == 263 and (action==1 or action==2): # direita
        #     tx += 0.1

        # if key == 262 and (action==1 or action==2): # esquerda
        #     tx -= 0.1
        # print('tx tz',tx,tz)

        # if key == 265 and (action==1 or action==2): # cima
        #     tz += 0.1
        # if key == 264 and (action==1 or action==2): # baixo
        #     tz -= 0.1

        # print('tx tz',tx,tz)

        # print('tecla',key,scancode,action,mods)
                     
    # Define eventos do mouse
    def mouse_event(window, xpos, ypos):
        
        global firstMouse, cameraFront, yaw, pitch, lastX, lastY

        if firstMouse:
            lastX = xpos
            lastY = ypos
            firstMouse = False

        xoffset = xpos - lastX
        yoffset = lastY - ypos
        lastX = xpos
        lastY = ypos

        sensitivity = 0.3 
        xoffset *= sensitivity
        yoffset *= sensitivity

        yaw += xoffset;
        pitch += yoffset;

        # CAMERA BUGA SE ANGULO DO PITCH FOR
        # >= 90   OU   <= -90
        if pitch >= 89.99: pitch = 89.99
        if pitch <= -89.99: pitch = -89.99

        front = glm.vec3()

        front.x = math.cos(glm.radians(yaw)) * math.cos(glm.radians(pitch))
        front.y = math.sin(glm.radians(pitch))
        front.z = math.sin(glm.radians(yaw)) * math.cos(glm.radians(pitch))
        cameraFront = glm.normalize(front)

    glfw.set_key_callback(window, key_event)
    glfw.set_cursor_pos_callback(window, mouse_event)


