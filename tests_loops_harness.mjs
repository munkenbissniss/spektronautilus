import { spawnSync, execFileSync } from 'node:child_process'; import { mkdtempSync, readFileSync, writeFileSync, unlinkSync, existsSync } from 'node:fs'; import { tmpdir } from 'node:os'; import { join } from 'node:path';
export const d = mkdtempSync(join(tmpdir(), 'lp_'));
export const ff = (...a) => execFileSync('ffmpeg', ['-v', 'error', '-y', '-nostdin', ...a], { cwd: d });
export const engine = { async exec(args) { const r = spawnSync('ffmpeg', ['-nostdin', ...args], { cwd: d, maxBuffer: 1e9 }); return { code: r.status, log: r.stderr.toString().split(/\r?\n/) }; },
  async read(p) { return new Uint8Array(readFileSync(join(d, p))); }, async write(p, u8) { writeFileSync(join(d, p), u8); }, async remove(p) { try { unlinkSync(join(d, p)); } catch {} } };
// gray frames at WxH as array of Uint8Array
export function frames(file, w = 96, h = 54) { const raw = execFileSync('ffmpeg', ['-v', 'error', '-nostdin', '-i', join(d, file), '-vf', `scale=${w}:${h}:flags=area,format=gray`, '-f', 'rawvideo', '-'], { maxBuffer: 1e9 }); const S = w * h, n = Math.floor(raw.length / S); return Array.from({ length: n }, (_, i) => raw.subarray(i * S, (i + 1) * S)); }
export const mad = (a, b) => { let s = 0; for (let i = 0; i < a.length; i++) s += Math.abs(a[i] - b[i]); return s / a.length; };
export function info(file) { const j = JSON.parse(execFileSync('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate,avg_frame_rate,nb_frames,codec_name:format=duration', '-of', 'json', join(d, file)])); const s = j.streams[0], [a, b] = s.r_frame_rate.split('/').map(Number); return { width: s.width, height: s.height, fps: a / b, duration: +j.format.duration, hasAudio: false, codec: s.codec_name }; }
