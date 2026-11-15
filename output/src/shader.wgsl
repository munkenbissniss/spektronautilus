// Spektronautilus Output, phase 0. One full-screen triangle.
//   mode 0: a video frame in NV12 (Y plane + interleaved UV plane), turned into RGB on the graphics card (BT.709, limited range).
//   mode 1: the test pattern: a white bar that moves 16 pixels every refresh. Any missed refresh shows as a jump.

struct U {
    mode: u32,
    frame: u32,
    width: f32,
    height: f32,
};

@group(0) @binding(0) var tex_y: texture_2d<f32>;
@group(0) @binding(1) var tex_uv: texture_2d<f32>;
@group(0) @binding(2) var smp: sampler;
@group(0) @binding(3) var<uniform> u: U;

struct VO {
    @builtin(position) pos: vec4<f32>,
    @location(0) uv: vec2<f32>,
};

@vertex
fn vs_main(@builtin(vertex_index) i: u32) -> VO {
    var p = array<vec2<f32>, 3>(vec2<f32>(-1.0, -3.0), vec2<f32>(-1.0, 1.0), vec2<f32>(3.0, 1.0));
    var o: VO;
    let q = p[i];
    o.pos = vec4<f32>(q, 0.0, 1.0);
    o.uv = vec2<f32>((q.x + 1.0) * 0.5, (1.0 - q.y) * 0.5);
    return o;
}

@fragment
fn fs_main(v: VO) -> @location(0) vec4<f32> {
    // Sampled first, outside any branch: texture sampling must happen in uniform control flow.
    let y = textureSample(tex_y, smp, v.uv).r;
    let c = textureSample(tex_uv, smp, v.uv).rg;
    if (u.mode == 1u) {
        let bar = f32((u.frame * 16u) % u32(max(u.width, 1.0)));
        if (v.pos.x >= bar && v.pos.x < bar + 32.0) {
            return vec4<f32>(1.0, 1.0, 1.0, 1.0);
        }
        let band = floor(v.pos.y / max(u.height / 8.0, 1.0));
        let g = 0.06 + 0.04 * (band - 2.0 * floor(band / 2.0));
        return vec4<f32>(g, g, g, 1.0);
    }
    let yy = (y - 16.0 / 255.0) * 1.164;
    let cb = c.x - 0.5;
    let cr = c.y - 0.5;
    let rgb = vec3<f32>(yy + 1.793 * cr, yy - 0.213 * cb - 0.533 * cr, yy + 2.112 * cb);
    return vec4<f32>(clamp(rgb, vec3<f32>(0.0), vec3<f32>(1.0)), 1.0);
}
