window.addEventListener('DOMContentLoaded',()=>{
    const canvas = document.getElementById('webglSmoke');
    const gl = canvas.getContext('webgl', { alpha: false, preserveDrawingBuffer: false }) || canvas.getContext('experimental-webgl');

    if (gl) {
        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            gl.viewport(0, 0, canvas.width, canvas.height);
        }
        window.addEventListener('resize', resize);

        const vsSource = `
            attribute vec2 position;
            void main() {
                gl_Position = vec4(position, 0.0, 1.0);
            }
        `;

        const fsSource = `
            precision mediump float;
            uniform vec2 u_resolution;
            uniform float u_time;

            float hash(vec2 p) {
                p = fract(p * vec2(123.34, 456.21));
                p += dot(p, p + 45.32);
                return fract(p.x * p.y);
            }

            float noise(vec2 p) {
                vec2 i = floor(p);
                vec2 f = fract(p);
                f = f * f * (3.0 - 2.0 * f);
                float a = hash(i);
                float b = hash(i + vec2(1.0, 0.0));
                float c = hash(i + vec2(0.0, 1.0));
                float d = hash(i + vec2(1.0, 1.0));
                return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
            }

            float fbm(vec2 p) {
                float v = 0.0;
                float a = 0.5;
                vec2 shift = vec2(100.0);
                mat2 rot = mat2(cos(0.5), sin(0.5), -sin(0.5), cos(0.5));
                for (int i = 0; i < 5; ++i) {
                    v += a * noise(p);
                    p = rot * p * 2.0 + shift;
                    a *= 0.5;
                }
                return v;
            }

            void main() {
                vec2 st = gl_FragCoord.xy / u_resolution.xy;
                st.x *= u_resolution.x / u_resolution.y;

                vec2 q = vec2(0.0);
                q.x = fbm(st + 0.04 * u_time);
                q.y = fbm(st + vec2(1.0));

                vec2 r = vec2(0.0);
                r.x = fbm(st + 1.0 * q + vec2(1.7, 9.2) + 0.12 * u_time);
                r.y = fbm(st + 1.0 * q + vec2(8.3, 2.8) + 0.09 * u_time);

                float f = fbm(st + r);

                vec3 color1 = 0.5 + 0.5 * cos(u_time * 0.2 + vec3(0.0, 2.0, 4.0));
                vec3 color2 = 0.5 + 0.5 * cos(u_time * 0.3 + vec3(4.0, 2.0, 0.0));
                vec3 darkBg = vec3(0.02, 0.02, 0.04);

                vec3 color = mix(darkBg, color1, clamp(f * f * 3.5, 0.0, 1.0));
                color = mix(color, color2, clamp(length(q), 0.0, 1.0));

                gl_FragColor = vec4(color * (f * 2.0), 1.0);
            }
        `;

        function createShader(gl, type, source) {
            const shader = gl.createShader(type);
            gl.shaderSource(shader, source);
            gl.compileShader(shader);
            return shader;
        }

        const vertexShader = createShader(gl, gl.VERTEX_SHADER, vsSource);
        const fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, fsSource);

        const program = gl.createProgram();
        gl.attachShader(program, vertexShader);
        gl.attachShader(program, fragmentShader);
        gl.linkProgram(program);
        gl.useProgram(program);

        const buffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
            -1, -1,  1, -1, -1,  1,
            -1,  1,  1, -1,  1,  1
        ]), gl.STATIC_DRAW);

        const positionLocation = gl.getAttribLocation(program, "position");
        gl.enableVertexAttribArray(positionLocation);
        gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

        const resLocation = gl.getUniformLocation(program, "u_resolution");
        const timeLocation = gl.getUniformLocation(program, "u_time");

        resize();

        function render(time) {
            gl.uniform2f(resLocation, canvas.width, canvas.height);
            gl.uniform1f(timeLocation, time * 0.001);
            gl.drawArrays(gl.TRIANGLES, 0, 6);
            requestAnimationFrame(render);
        }

        requestAnimationFrame(render);
    }
})