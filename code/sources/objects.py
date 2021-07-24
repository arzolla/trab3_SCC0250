from OpenGL.GL import *
import numpy as np
import math
import glm
from PIL import Image
import sys, os


##############################################
############# FUNÇÕES DE ARQUIVO #############
##############################################

# Função para carregar modelo a partir de arquivo .obj
def load_model_from_file(filename):
    """Loads a Wavefront OBJ file. """
    objects = {}
    vertices = []
    normals = []
    texture_coords = []
    faces = []

    material = None

    # abre o arquivo obj para leitura
    for line in open(filename, "r"): ## para cada linha do arquivo .obj
        if line.startswith('#'): continue ## ignora comentarios
        values = line.split() # quebra a linha por espaço
        if not values: continue


        ### recuperando vertices
        if values[0] == 'v':
            vertices.append(values[1:4])

        ### recuperando vertices
        if values[0] == 'vn':
            normals.append(values[1:4])

        ### recuperando coordenadas de textura
        elif values[0] == 'vt':
            texture_coords.append(values[1:3])

        ### recuperando faces 
        elif values[0] in ('usemtl', 'usemat'):
            material = values[1]
        elif values[0] == 'f':
            face = []
            face_texture = []
            face_normals = []
            for v in values[1:]:
                w = v.split('/')
                face.append(int(w[0]))
                face_normals.append(int(w[2]))
                if len(w) >= 2 and len(w[1]) > 0:
                    face_texture.append(int(w[1]))
                else:
                    face_texture.append(0)

            faces.append((face, face_texture, face_normals, material))

    model = {}
    model['vertices'] = vertices
    model['texture'] = texture_coords
    model['faces'] = faces
    model['normals'] = normals

    return model

# Função para carregar a textura a partir de arquivo de imagem
def load_texture_from_file(texture_id, img_textura):
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    img = Image.open(img_textura)
    img_width = img.size[0]
    img_height = img.size[1]
    image_data = img.convert("RGBA").tobytes("raw", "RGBA", 0, -1)
    #image_data = img.tobytes("raw", "RGB", 0, -1)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img_width, img_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
    #glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img_width, img_height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_data)

# Acesso ao path de modelos
def model_path(obj):
    return os.path.join(sys.path[0],'models',obj)

# Acesso ao path de texturas
def tex_path(mod,tex):
    return os.path.join(sys.path[0],'textures',mod,tex)

##############################################
############# FUNÇÕES DE OBJETOS #############
##############################################

# Lista de vertices e coordenadas da textura
vertices_list = []    
textures_coord_list = []
normals_list = []  

# contador absoluto de texturas inseridas
texture_counter = 0

# Dicionário para armazenar o indice das texturas 
texture_index = {
    # 'modelo' : [id_textura1, id_textura2, ...]
}

# Dicionário para armazenar inicio dos vértices e 
# fim dos vértices de cada material interno no arquivo
vertex_index = {
    # 'modelo' : [vertice_inicial, vertice_final1, vertice_final2, ...]]
}
### Para facilidade, as chaves de ambos são o nome do modelo


# Função para declarar os objetos, entrada é o modelo .obj 
# e vetor com texturas usadas neste modelo
def declare_obj(model, textures):
    
    global vertex_index, texture_index
    modelo = load_model_from_file(model_path(model))

    ### inserindo vertices do modelo no vetor de vertices
    print('_____________________________________________________')
    print('Processando modelo',model,'. Materiais:')
    faces_visited = []
    vertex_index[model] = []
    for face in modelo['faces']:
        if face[3] not in faces_visited:
            print("{:27} {} {:5}".format(face[3],'- Vertice inicial:', len(vertices_list)))
            vertex_index[model].append(len(vertices_list))
            faces_visited.append(face[3])
        for vertice_id in face[0]:
            vertices_list.append( modelo['vertices'][vertice_id-1] )
        for texture_id in face[1]:
            textures_coord_list.append( modelo['texture'][texture_id-1] )
        for normal_id in face[2]:
            normals_list.append( modelo['normals'][normal_id-1] )
    print("{} {:20} {} {:1}".format('Fim de',model,'- Vertice final  :', len(vertices_list)))  
    vertex_index[model].append(len(vertices_list))

    
    ### inserindo coordenadas de textura do modelo no vetor de texturas
    texture_index[model] = []
    # Loop repete para cada arquivo de textura inserido para este objeto
    for i in range(len(textures)):
        global texture_counter
        ### carregando textura equivalente e definindo um id (buffer)
        print("{} {:15} {} {:1}".format('Índice da textura',textures[i],':',texture_counter))
        texture_index[model].append(texture_counter)
        load_texture_from_file(texture_counter,tex_path(model,textures[i]))
        texture_counter = texture_counter +1


# Variável instanciada para armazenar programa principal
program = []

def draw_obj(modelo, mat_model):

    loc_model = glGetUniformLocation(program, "model")
    glUniformMatrix4fv(loc_model, 1, GL_TRUE, mat_model)
       
    # Insere os modelos de acordo com o número de indices de vértice
    # Caso haja por exemplo três índices, isso significa q há dois 
    # objetos a serem inseridos
    for i in range(len(vertex_index[modelo])-1):
        #define id da textura do modelo
        glBindTexture(GL_TEXTURE_2D, texture_index[modelo][i])

        # desenha o modelo
        glDrawArrays(GL_TRIANGLES, vertex_index[modelo][i],vertex_index[modelo][1+i]-vertex_index[modelo][i] ) ## renderizando


def set_light(ka, kd, ks, ns):
    
    loc_ka = glGetUniformLocation(program, "ka") # recuperando localizacao da variavel ka na GPU
    glUniform1f(loc_ka, ka) ### envia ka pra gpu
    
    loc_kd = glGetUniformLocation(program, "kd") # recuperando localizacao da variavel kd na GPU
    glUniform1f(loc_kd, kd) ### envia kd pra gpu    
    
    loc_ks = glGetUniformLocation(program, "ks") # recuperando localizacao da variavel ks na GPU
    glUniform1f(loc_ks, ks) ### envia ns pra gpu        
    
    loc_ns = glGetUniformLocation(program, "ns") # recuperando localizacao da variavel ns na GPU
    glUniform1f(loc_ns, ns) ### envia ns pra gpu            
    



# Matriz model
def model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z):
    
    angle = math.radians(angle)
    
    matrix_transform = glm.mat4(1.0) # instanciando uma matriz identidade

    # aplicando translacao
    matrix_transform = glm.translate(matrix_transform, glm.vec3(t_x, t_y, t_z))    
    
    # aplicando rotacao
    matrix_transform = glm.rotate(matrix_transform, angle, glm.vec3(r_x, r_y, r_z))
    
    # aplicando escala
    matrix_transform = glm.scale(matrix_transform, glm.vec3(s_x, s_y, s_z))
    
    matrix_transform = np.array(matrix_transform).T # pegando a transposta da matriz (glm trabalha com ela invertida)
    
    return matrix_transform



##############################################
################### OBJETOS ##################
##############################################

# Função para desenhar o céu
def draw_sky(rotacao_inc):
    # rotacao
    angle = 90 +rotacao_inc/10;
    r_x = 1.0; r_y = -1.0; r_z = 0.0;
    # translacao
    t_x = 0.0; t_y = -1.0; t_z = 0.0;
    # escala
    s_x = 800.0; s_y = 800.0; s_z = 800.0;

    mat_model = model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z)


    #### define parametros de ilumincao do modelo
    ka = 0.7 # coeficiente de reflexao ambiente do modelo
    kd = 0 # coeficiente de reflexao difusa do modelo
    ks = 0 # coeficiente de reflexao especular do modelo
    ns = 1 # expoente de reflexao especular
    
    set_light(ka, kd, ks, ns)
    draw_obj('skydome.obj', mat_model)

# Função para desenhar as naves espaciais
def draw_spaceships(inc):
    # rotacaowwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
    angle = -math.degrees(inc/50) 
    r_x = 0.0; r_y = 1.0; r_z = 0.0;
    # translacao
    t_x = 10*math.cos(inc/50) ; t_y = 10.0; t_z = 10*math.sin(inc/50);
    # escala
    s_x = 1.0; s_y = 1.0; s_z = 1.0;

    mat_model = model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z)
    
    #### define parametros de ilumincao do modelo
    ka = 0.5 # coeficiente de reflexao ambiente do modelo
    kd = 1 # coeficiente de reflexao difusa do modelo
    ks = 0.3 # coeficiente de reflexao especular do modelo
    ns = 2.0 # expoente de reflexao especular
    
    set_light(ka, kd, ks, ns)
    
    draw_obj('spaceship.obj', mat_model)

    loc_light_pos = glGetUniformLocation(program, "lightPos2") # recuperando localizacao da variavel lightPos na GPU
    glUniform3f(loc_light_pos, t_x, t_y-0.3, t_z) ### posicao da fonte de luz



    # rotacao
    angle = 0.0;
    r_x = 0.0; r_y = 0.0; r_z = 1.0;
    # translacao
    t_x = 300 ; t_y = 300.0; t_z = +200 -inc/10;
    # escala
    s_x = 5.0; s_y = 5.0; s_z = 5.0;
    
    #### define parametros de ilumincao do modelo
    ka = 0.5 # coeficiente de reflexao ambiente do modelo
    kd = 1 # coeficiente de reflexao difusa do modelo
    ks = 0.3 # coeficiente de reflexao especular do modelo
    ns = 2.0 # expoente de reflexao especular
    
    set_light(ka, kd, ks, ns)

    
    mat_model = model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z)
    draw_obj('mothership.obj', mat_model)

    loc_light_pos = glGetUniformLocation(program, "lightPos1") # recuperando localizacao da variavel lightPos na GPU
    glUniform3f(loc_light_pos, t_x, t_y, t_z) ### posicao da fonte de luz

# Função para desenhar a cena estática
def draw_static():
    # rotacao
    angle = 0.0;
    r_x = 0.0; r_y = 0.0; r_z = 1.0;
    # escala
    s_x = 1.0; s_y = 1.0; s_z = 1.0;
    # translacao
    t_x = 0.4 ; t_y = -2.3; t_z = 0.0;
    # insere arvore interna
    mat_model = model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z)


    #### define parametros de ilumincao do modelo
    ka = 0.1 # coeficiente de reflexao ambiente do modelo
    kd = 1 # coeficiente de reflexao difusa do modelo
    ks = 0.3 # coeficiente de reflexao especular do modelo
    ns = 4.0 # expoente de reflexao especular
    
    set_light(ka, kd, ks, ns)
     
    draw_obj('tree.obj', mat_model)

    # translacao
    t_x = 5.5 ; t_y = -2 ; t_z = 2.2;
    # insere cabana
    mat_model = model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z)
    draw_obj('hut.obj', mat_model)


    #### define parametros de ilumincao do modelo
    ka = 0.1 # coeficiente de reflexao ambiente do modelo
    kd = 1 # coeficiente de reflexao difusa do modelo
    ks = 0.7 # coeficiente de reflexao especular do modelo
    ns = 8.0 # expoente de reflexao especular
    
    set_light(ka, kd, ks, ns)

    # translacao
    t_x = 0.0 ; t_y = -2.0; t_z = 0.0;
    # escala
    s_x = 0.4; s_y = 0.4; s_z = 0.4;
    # insere esqueleto
    mat_model = model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z)
    draw_obj('remains.obj', mat_model)


    #### define parametros de ilumincao do modelo
    ka = 0.1 # coeficiente de reflexao ambiente do modelo
    kd = 1 # coeficiente de reflexao difusa do modelo
    ks = 1 # coeficiente de reflexao especular do modelo
    ns = 32 # expoente de reflexao especular
    
    set_light(ka, kd, ks, ns)

    # rotacao
    angle = -180.0;
    r_x = 0.0; r_y = 1.0; r_z = 0.0;
    # translacao
    t_x = 1 ; t_y = -1.95 ; t_z = 8;
    # escala
    s_x = 0.1; s_y = 0.1; s_z = 0.1;
    # insere alien
    mat_model = model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z)
    draw_obj('alien.obj', mat_model)

# desenha forno e luz 
def draw_stove():
    # rotacao
    angle = 45.0;
    r_x = 0.0; r_y = 1.0; r_z = 0.0;
    # translacao
    t_x = -2.6 ; t_y = -1.6; t_z = 5.7;
    # escala
    s_x = 10; s_y = 10; s_z = 10;
    # insere forno
    mat_model = model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z)

    ka = 0.1 # coeficiente de reflexao ambiente do modelo
    kd = 0.8 # coeficiente de reflexao difusa do modelo
    ks = 8 # coeficiente de reflexao especular do modelo
    ns = 1.0 # expoente de reflexao especular
    
    set_light(ka, kd, ks, ns)

    #loc_light_pos = glGetUniformLocation(program, "lightPos1") # recuperando localizacao da variavel lightPos na GPU
    
    #glUniform3f(loc_light_pos, t_x, t_y+0.1, t_z) ### posicao da fonte de luz
    
    draw_obj('stove.obj', mat_model)



def draw_forest():
    # rotacao
    angle = 0.0;
    r_x = 0.0; r_y = 0.0; r_z = 1.0;
    # translacao
    t_x = 0.0 ; t_y = -2.0; t_z = 0.0;
    # escala
    s_x = 1.0; s_y = 1.0; s_z = 1.0;
    # insere floresta e montanhas ao redor
    mat_model = model(angle, r_x, r_y, r_z, t_x, t_y, t_z, s_x, s_y, s_z)

    #### define parametros de ilumincao do modelo
    ka = 0.05 # coeficiente de reflexao ambiente do modelo
    kd = 0.6 # coeficiente de reflexao difusa do modelo
    ks = 0.3 # coeficiente de reflexao especular do modelo
    ns = 4.0 # expoente de reflexao especular
    
    set_light(ka, kd, ks, ns)

    draw_obj('pine_forest.obj',mat_model)
    draw_obj('mountain.obj',mat_model)
