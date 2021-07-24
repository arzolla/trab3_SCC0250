#!/usr/bin/env python3
#########################################
##### SCC0250 - Computação Gráfica ######
####### Trabalho 3 - Iluminação #########
#########################################
#### Aluno: Victor de Mattos Arzolla ####
#### NUSP: 9039312 ######################
#########################################


# Importando dependências
import glfw
from OpenGL.GL import *
#import OpenGL.GL.shaders
import numpy as np
import math
import glm
from PIL import Image
import sys, os
sys.path.append(os.path.join(sys.path[0],'sources'))

# Importa módulo com os codigos referentes aos shaders e buffer
import shader_buffer as sb
# Importa módulo com os codigos referentes aos comandos de teclado
import commands as cmd
# Importa módulo com os codigos referentes aos objetos
import objects as obj

# inicializa o GLFW
if  glfw.init():
    print("GLFW Inicializado")
else:
    print("Erro na inicialização do GLFW")

# Declarando a janela
glfw.init()
glfw.window_hint(glfw.VISIBLE, glfw.FALSE);
largura = 1280
altura = 720
window = glfw.create_window(largura, altura, "Trabalho 2 - Cenário 3D", None, None)
glfw.make_context_current(window)


##############################################
##############################################

# Função para rodar shaders, retorna variavel programa principal
program = sb.run_shader()

# Configura suporte a texturas
glEnable(GL_TEXTURE_2D)
qtd_texturas = 30
textures = glGenTextures(qtd_texturas)

##############################################
################### OBJETOS ##################

# Declaração dos objetos a partir de modelo e texturas 

# obj.declare_obj('chao.obj',['grass.jpg'])

obj.declare_obj('hut.obj',['body.jpg','frame.jpg','roof_floor.jpg'])

obj.declare_obj('pine_forest.obj',['pines.png','ground.jpeg'])

obj.declare_obj('mountain.obj',['rocks.jpg'])

obj.declare_obj('tree.obj',['folhas.jpg','tronco.jpg'])

obj.declare_obj('skydome.obj',['milkyway.jpg'])

obj.declare_obj('spaceship.obj',['spaceship.jpg'])

obj.declare_obj('mothership.obj',['ms1.jpg','ms2.jpg','ms3.jpg','ms4.jpg','ms5.jpg'])

obj.declare_obj('remains.obj',['limb.jpg','body.jpg','skull.jpg','stones.jpg','sticks.jpg'])

obj.declare_obj('alien.obj',['blaster.jpg','alien.jpg'])

obj.declare_obj('stove.obj',['stove.jpeg'])

# Envia variável de programa para módulo objects.py
obj.program = program


##############################################
################### BUFFERS ##################

# Declara buffers da GPU e envia para módulo shader_buffer.py
sb.buffer = glGenBuffers(3)

# Declara variável para armazenar lista de vértices
vertices = np.zeros(len(obj.vertices_list), [("position", np.float32, 3)])
# Obtém lista de vértices do módulo objetcs.py
vertices['position'] = obj.vertices_list
# Envia lista de vértices para buffer da GPU
sb.vertex_buffer(vertices)

# Decwwwwwwwwwwwwwwwwwwwlara variável para armazenar lista de coordenadas de textura
textures = np.zeros(len(obj.textures_coord_list), [("position", np.float32, 2)]) # duas coordenadas
# Obtém lista de coordenadas de textura do módulo objetcs.py
textures['position'] = obj.textures_coord_list
# Envia lista de coordenadas de texturas para buffer da GPU
sb.texture_buffer(textures)

# Declara variável para armazenar lista de vetores normais
normals = np.zeros(len(obj.normals_list), [("position", np.float32, 3)]) # três coordenadas
# Obtém lista de vetores normais do módulo objetcs.py
normals['position'] = obj.normals_list
# Envia lista de vetores normais para buffer da GPU
sb.normals_buffer(normals)

##############################################
################## COMANDOS ##################

# Envia variáveis de janela para modulo commands.py
cmd.altura = altura
cmd.largura = largura
# Envia variável de janela para modulo commands.py
cmd.window = window
# Ativa os comandos de teclado e mouse
cmd.commands()

##############################################
################ CONFIGURAÇÕES ###############

# Mostra a janela
glfw.show_window(window)
glfw.set_cursor_pos(window, cmd.lastX, cmd.lastY)

# Configurações do OpenGL
glEnable(GL_BLEND)
glEnable(GL_DEPTH_TEST) ### importante para 3D

##############################################
################## VARIÁVEIS #################

# Variáveis para laço principal
move_inc = 0

# Laço principal
while not glfw.window_should_close(window):

    glfw.poll_events() 
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glClearColor(1.0, 1.0, 1.0, 1.0)
    
    # Ativa ou desativa modo poligonal
    if cmd.polygonal_mode==True:
        glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
    if cmd.polygonal_mode==False:
        glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)
    
    # ativar modo de luz colorida
    # recuperando localizacao do flag light_mode
    loc_light_mode = glGetUniformLocation(program, "light_mode") 
    glUniform1f(loc_light_mode, cmd.light_mode) ### envia modo pra gpu

    # intensidade da luz 2
    intensity2 = np.random.normal(0.3,0.1) # distribuiçao normal da intensidade
    # recuperando localizacao do multiplicador de intensidade
    loc_intensity2 = glGetUniformLocation(program, "intensity2") 
    glUniform1f(loc_intensity2, intensity2) ### envia intensidade pra gpu


    # Insere o céu
    obj.draw_sky(move_inc)

    # Insere as naves espaciais
    obj.draw_spaceships(5*move_inc,cmd.ka_mult)

    # Insere a cena estática
    obj.draw_forest(cmd.ka_mult)
    obj.draw_stove(cmd.ka_mult)
    obj.draw_static(cmd.ka_mult)


    # Incremento do movimento
    move_inc += 0.1
 
    # Roda matriz view
    mat_view = cmd.view()
    loc_view = glGetUniformLocation(program, "view")
    glUniformMatrix4fv(loc_view, 1, GL_FALSE, mat_view)

    # Roda matriz projection
    mat_projection = cmd.projection()
    loc_projection = glGetUniformLocation(program, "projection")
    glUniformMatrix4fv(loc_projection, 1, GL_FALSE, mat_projection)   

    
    glfw.swap_buffers(window)

glfw.terminate()
