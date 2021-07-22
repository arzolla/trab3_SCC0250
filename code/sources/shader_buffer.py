from OpenGL.GL import *
import OpenGL.GL.shaders


###########################
######### SHADERS #########
###########################

# Código do shader de vértice
vertex_code = """
        attribute vec3 position;
        attribute vec2 texture_coord;
        attribute vec3 normals;
        
       
        varying vec2 out_texture;
        varying vec3 out_fragPos;
        varying vec3 out_normal;
                
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;        
        
        void main(){
            gl_Position = projection * view * model * vec4(position,1.0);
            out_texture = vec2(texture_coord);
            out_fragPos = vec3(model * vec4(position, 1.0));
            out_normal = normals;            
        }
        """

# Código do shader de fragmento
fragment_code = """

        // parametros da iluminacao ambiente e difusa
        uniform vec3 lightPos1; // define coordenadas de posicao da luz #1
        uniform vec3 lightPos2; // define coordenadas de posicao da luz #2
        uniform float ka; // coeficiente de reflexao ambiente
        uniform float kd; // coeficiente de reflexao difusa
        
        // parametros da iluminacao especular
        uniform vec3 viewPos; // define coordenadas com a posicao da camera/observador
        uniform float ks; // coeficiente de reflexao especular
        uniform float ns; // expoente de reflexao especular
        
        // parametro com a cor da(s) fonte(s) de iluminacao
        vec3 lightColor = vec3(1.0, 1.0, 1.0);

        // parametros recebidos do vertex shader
        varying vec2 out_texture; // recebido do vertex shader
        varying vec3 out_normal; // recebido do vertex shader
        varying vec3 out_fragPos; // recebido do vertex shader
        uniform sampler2D samplerTexture;
        
        
        
        void main(){
        
            // calculando reflexao ambiente
            vec3 ambient = ka * lightColor;             
        
            ////////////////////////
            // Luz #1
            ////////////////////////
            
            // calculando reflexao difusa
            vec3 norm1 = normalize(out_normal); // normaliza vetores perpendiculares
            vec3 lightDir1 = normalize(lightPos1 - out_fragPos); // direcao da luz
            float diff1 = max(dot(norm1, lightDir1), 0.0); // verifica limite angular (entre 0 e 90)
            vec3 diffuse1 = kd * diff1 * lightColor; // iluminacao difusa
            
            // calculando reflexao especular
            vec3 viewDir1 = normalize(viewPos - out_fragPos); // direcao do observador/camera
            vec3 reflectDir1 = reflect(-lightDir1, norm1); // direcao da reflexao
            float spec1 = pow(max(dot(viewDir1, reflectDir1), 0.0), ns);
            vec3 specular1 = ks * spec1 * lightColor;    
            
            
            ////////////////////////
            // Luz #2
            ////////////////////////
            
            // calculando reflexao difusa
            vec3 norm2 = normalize(out_normal); // normaliza vetores perpendiculares
            vec3 lightDir2 = normalize(lightPos2 - out_fragPos); // direcao da luz
            float diff2 = max(dot(norm2, lightDir2), 0.0); // verifica limite angular (entre 0 e 90)
            vec3 diffuse2 = kd * diff2 * lightColor; // iluminacao difusa
            
            // calculando reflexao especular
            vec3 viewDir2 = normalize(viewPos - out_fragPos); // direcao do observador/camera
            vec3 reflectDir2 = reflect(-lightDir2, norm2); // direcao da reflexao
            float spec2 = pow(max(dot(viewDir2, reflectDir2), 0.0), ns);
            vec3 specular2 = ks * spec2 * lightColor;    
            
            ////////////////////////
            // Combinando as duas fontes
            ////////////////////////
            
            // aplicando o modelo de iluminacao
            vec4 texture = texture2D(samplerTexture, out_texture);
            vec4 result = vec4((ambient + diffuse1 + diffuse2 + specular1 + specular2),1.0) * texture; // aplica iluminacao
            gl_FragColor = result;

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




