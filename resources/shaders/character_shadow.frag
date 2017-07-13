#version 330 core

in vec2 uv;
out vec4 color;
uniform sampler2D tex;

void main() {
    vec4 c = vec4(0.0);
    float alpha = texture(tex, uv).a * 0.3 * pow(uv.y,6);
    color = vec4(0,0,0,alpha);
}
