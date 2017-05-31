import ctypes
from ctypes import *
from distutils.errors import CompileError

from pyglet import gl


class ShadersManager:
    def __init__(self):
        self.programs = {}

        # shader_source = self._source.encode("utf8")#

    # +        shader_id = glCreateShader(_shader_types[self.shader_type])
    # +        source_buffer = c_char_p(shader_source)
    # +        source_buffer_pointer = cast(pointer(source_buffer), POINTER(POINTER(c_char)))
    # +        source_length = c_int(len(shader_source) + 1)
    # +  # shader id, count, string, length:
    # +        glShaderSource(shader_id, 1, source_buffer_pointer, source_length)
    # +        glCompileShader(shader_id)
    # +  # TODO: use the pyglet debug settings
    # +        self._get_shader_log(shader_id)
    # +
    # return shader_id

    def _create_shader(self, source, shader_type):
        shader_id = gl.glCreateShader(shader_type)

        src_buffer = ctypes.create_string_buffer(source)
        buf_pointer = ctypes.cast(ctypes.pointer(ctypes.pointer(src_buffer)),
                                  ctypes.POINTER(ctypes.POINTER(ctypes.c_char)))
        length = ctypes.c_int(len(source) + 1)
        gl.glShaderSource(shader_id, 1, buf_pointer, length)

        # gl.glShaderSource(shader_id, source)
        gl.glCompileShader(shader_id)

        # if not bool(self._get(gl.GL_COMPILE_STATUS)):
        #     raise CompileError(self.getInfoLog())

        # src_buffer = ctypes.create_string_buffer(shader_source)
        # buf_pointer = ctypes.cast(ctypes.pointer(ctypes.pointer(src_buffer)), ctypes.POINTER(ctypes.POINTER(ctypes.c_char)))
        # length = ctypes.c_int(len(shader_source) + 1)
        # gl.glShaderSource(shader_name, 1, buf_pointer, ctypes.byref(length))
        # gl.glCompileShader(shader_name)

        # test if compilation is succesful and print status messages
        success = gl.GLint(0)
        gl.glGetShaderiv(shader_id, gl.GL_COMPILE_STATUS, ctypes.byref(success))

        length = gl.GLint(0)
        gl.glGetShaderiv(shader_id, gl.GL_INFO_LOG_LENGTH, ctypes.byref(length))
        log_buffer = ctypes.create_string_buffer(length.value)
        gl.glGetShaderInfoLog(shader_id, length, None, log_buffer)

        log_message = log_buffer.value[:length.value].decode('ascii').strip()
        if log_message:
            print(log_message + '\n')

        if not success:
            raise CompileError("Error compiling Shader (%d)" % shader_type)

        return shader_id

    def test(self):
        self._create_shader(DEFAULT_VERTEX_SHADER_SOURCE, gl.GL_VERTEX_SHADER)


DEFAULT_VERTEX_SHADER_SOURCE = b'''
#version 120
varying vec4 vertex;
void main() {
    gl_Position = gl_ModelViewProjectionMatrix * vertex;
}
'''


# var FB_SHADERS = new function() {
#
#     this.createProgram = function (id, vertexShaderCode, fragmentShaderCode) {
#
#
# 		if (vertexShaderCode == null) {
# 			vertexShaderCode = defaultVertexShader;
# 		}
#
# 		var fragShader = fragmentShaderCode.replace(/\$SCREEN_WIDTH/g, FB_CORE.CONFIG_SCREEN_WIDTH);
#     	fragShader = fragShader.replace(/\$SCREEN_HEIGHT/g, FB_CORE.CONFIG_SCREEN_HEIGHT);
#
#         var shaderProgram = gl.createProgram();
#         gl.attachShader(shaderProgram, getVertexShaderFromString(vertexShaderCode));
#         gl.attachShader(shaderProgram, getFragmentShaderFromString(fragShader));
#         gl.linkProgram(shaderProgram);
#
#         if (!gl.getProgramParameter(shaderProgram, gl.LINK_STATUS)) {
#             alert("Could not initialise shaders");
#         }
#
#         gl.useProgram(shaderProgram);
#
#         var vertexPositionAttribute = gl.getAttribLocation(shaderProgram, "aVertexPosition");
#         gl.enableVertexAttribArray(vertexPositionAttribute);
#
#         var textureCoordAttribute = gl.getAttribLocation(shaderProgram, "aTextureCoord");
#         gl.enableVertexAttribArray(textureCoordAttribute);
#
# 		if (this.programs[id]) {
# 			gl.deleteProgram(this.programs[id]);
# 		}
#
#         this.programs[id] = shaderProgram;
#     }
#
#     this.getProgramById = function (id) {
#         return this.programs[id];
#     }
# };

class Shader:
    # vert, frag and geom take arrays of source strings
    # the arrays will be concattenated into one string by OpenGL
    def __init__(self, vert=[], frag=[], geom=[]):
        # create the program handle
        self.handle = gl.glCreateProgram()
        # we are not linked yet
        self.linked = False
        # create the vertex shader
        self.createShader(vert, gl.GL_VERTEX_SHADER)
        # create the fragment shader
        self.createShader(frag, gl.GL_FRAGMENT_SHADER)
        # the geometry shader will be the same, once pyglet supports the extension
        # self.createShader(frag, GL_GEOMETRY_SHADER_EXT)
        # attempt to link the program
        self.link()

    def createShader(self, strings, type):
        count = len(strings)
        # if we have no source code, ignore this shader
        if count < 1:
            return

        # create the shader handle
        shader = gl.glCreateShader(type)

        # convert the source strings into a ctypes pointer-to-char array, and upload them
        # this is deep, dark, dangerous black magick - don't try stuff like this at home!
        src = (c_char_p * count)(*strings)

        gl.glShaderSource(shader, count, cast(pointer(src), POINTER(POINTER(c_char))), None)

        # compile the shader
        gl.glCompileShader(shader)

        temp = c_int(0)
        # retrieve the compile status
        gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS, byref(temp))

        # if compilation failed, print the log
        if not temp:
            # retrieve the log length
            gl.glGetShaderiv(shader, gl.GL_INFO_LOG_LENGTH, byref(temp))
            # create a buffer for the log
            buffer = create_string_buffer(temp.value)
            # retrieve the log text
            gl.glGetShaderInfoLog(shader, temp, None, buffer)
            # print the log to the console
            print(buffer.value)
        else:
            # all is well, so attach the shader to the program
            gl.glAttachShader(self.handle, shader)

    def link(self):
        # link the program
        gl.glLinkProgram(self.handle)

        temp = c_int(0)
        # retrieve the link status
        gl.glGetProgramiv(self.handle, gl.GL_LINK_STATUS, byref(temp))

        # if linking failed, print the log
        if not temp:
            # retrieve the log length
            gl.glGetProgramiv(self.handle, gl.GL_INFO_LOG_LENGTH, byref(temp))
            # create a buffer for the log
            buffer = create_string_buffer(temp.value)
            # retrieve the log text
            gl.glGetProgramInfoLog(self.handle, temp, None, buffer)
            # print the log to the console
            print(buffer.value)
        else:
            # all is well, so we are linked
            self.linked = True

    def bind(self):
        # bind the program
        gl.glUseProgram(self.handle)

    def unbind(self):
        # unbind whatever program is currently bound - not necessarily this program,
        # so this should probably be a class method instead
        gl.glUseProgram(0)

    # upload a floating point uniform
    # this program must be currently bound
    def uniformf(self, name, *vals):
        # check there are 1-4 values
        if len(vals) in range(1, 5):
            # select the correct function
            {1: gl.glUniform1f,
             2: gl.glUniform2f,
             3: gl.glUniform3f,
             4: gl.glUniform4f
             # retrieve the uniform location, and set
             }[len(vals)](gl.gl.glGetUniformLocation(self.handle, name), *vals)

    # upload an integer uniform
    # this program must be currently bound
    def uniformi(self, name, *vals):
        # check there are 1-4 values
        if len(vals) in range(1, 5):
            # select the correct function
            {1: gl.glUniform1i,
             2: gl.glUniform2i,
             3: gl.glUniform3i,
             4: gl.glUniform4i
             # retrieve the uniform location, and set
             }[len(vals)](gl.glGetUniformLocation(self.handle, name), *vals)

    # upload a uniform matrix
    # works with matrices stored as lists,
    # as well as euclid matrices
    def uniform_matrixf(self, name, mat):
        # obtian the uniform location
        loc = gl.glGetUniformLocation(self.handle, name)
        # uplaod the 4x4 floating point matrix
        gl.glUniformMatrix4fv(loc, 1, False, (c_float * 16)(*mat))
