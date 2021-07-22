from OpenGL.GL import *
import OpenGL.GL.shaders


###########################
######### SHADERS #########
###########################

# Código do shader de vértice
vertex_code = """
        attribute vec3 position;
        attribute vec2 texture_coord;
        varying vec2 out_texture;
                
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;        
        
        void main(){
            gl_Position = projection * view * model * vec4(position,1.0);
            out_texture = vec2(texture_coord);
        }
        """

# Código do shader de fragmento
fragment_code = """
        uniform vec4 color;
        varying vec2 out_texture;
        uniform sampler2D samplerTexture;
        
        void main(){
            vec4 texture = texture2D(samplerTexture, out_texture);
            if(texture.a < 0.5)
                discard;
            gl_FragColor = texture;
        }
        """


program = []

# Função para declarar programa principal e configurar shaders
def run_shader():

    global program

    # Requisitando slot para a GPU para os programas Vertex e Fragment Shaders
    program  = glCreateProgram()
    vertex   = glCreateShader(GL_VERTEX_SHADER)
    fragment = glCreateShader(GL_FRAGMENT_SHADER)

    # Associando código-fonte aos slots solicitados
    glShaderSource(vertex, vertex_code)
    glShaderSource(fragment, fragment_code)

    # Compilando o Vertex Shader
    glCompileShader(vertex)
    if not glGetShaderiv(vertex, GL_COMPILE_STATUS):
        error = glGetShaderInfoLog(vertex).decode()
        print(error)
        raise RuntimeError("Erro de compilacao do Vertex Shader")

    # Compilando o Fragment Shader
    glCompileShader(fragment)
    if not glGetShaderiv(fragment, GL_COMPILE_STATUS):
        error = glGetShaderInfoLog(fragment).decode()
        print(error)
        raise RuntimeError("Erro de compilacao do Fragment Shader")

    # Associando os programas compilado ao programa principal
    glAttachShader(program, vertex)
    glAttachShader(program, fragment)

    # Build program
    glLinkProgram(program)
    if not glGetProgramiv(program, GL_LINK_STATUS):
        print(glGetProgramInfoLog(program))
        raise RuntimeError('Linking error')

    # Seta como programa padrão
    glUseProgram(program)

    return program

###########################
######### BUFFERS #########
###########################

# Variável instanciada para armazenar buffers da GPU
buffer = []

# Função para configurar os buffers de vértice
def vertex_buffer(vertices):

    # Upload data
    glBindBuffer(GL_ARRAY_BUFFER, buffer[0])
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # Bind the position attribute
    # --------------------------------------
    stride = vertices.strides[0]
    offset = ctypes.c_void_p(0)

    loc_vertices = glGetAttribLocation(program, "position")
    glEnableVertexAttribArray(loc_vertices)

    glVertexAttribPointer(loc_vertices, 3, GL_FLOAT, False, stride, offset)


# Função para configurar os buffers de textura
def texture_buffer(textures):

    # Upload data
    glBindBuffer(GL_ARRAY_BUFFER, buffer[1])
    glBufferData(GL_ARRAY_BUFFER, textures.nbytes, textures, GL_STATIC_DRAW)

    # Bind the position attribute
    # --------------------------------------
    stride = textures.strides[0]
    offset = ctypes.c_void_p(0)

    loc_texture_coord = glGetAttribLocation(program, "texture_coord")
    glEnableVertexAttribArray(loc_texture_coord)

    glVertexAttribPointer(loc_texture_coord, 2, GL_FLOAT, False, stride, offset)




