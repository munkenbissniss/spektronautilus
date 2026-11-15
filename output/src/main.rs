//! Spektronautilus Output, phase 0: a measuring player.
//!
//! Plays one clip (or a test pattern) full screen on the projector, in step with its refresh (vsync), and counts every refresh
//! it missed. The answer to one question: does the picture stutter when the browser is not in the way? If it still stutters
//! here, the cause is the driver, the HDMI sound or the projector, not the browser.
//!
//!   spektronautilus-output clip.mp4               the clip, looped, on the second screen (the projector) if there is one
//!   spektronautilus-output --pattern              a white bar moving 16 pixels per refresh: every missed refresh is a jump
//!   options: --monitor N  --seconds S (default 600)  --windowed  --report FILE (default spektronautilus-output-report.json)
//!   Esc or Q stops early. The report is written either way.

use std::sync::Arc;
use std::time::Instant;

use gstreamer as gst;
use gstreamer::prelude::*;
use gstreamer_app as gst_app;
use gstreamer_video as gst_video;
use winit::application::ApplicationHandler;
use winit::dpi::LogicalSize;
use winit::event::{ElementState, WindowEvent};
use winit::event_loop::{ActiveEventLoop, ControlFlow, EventLoop};
use winit::keyboard::{Key, NamedKey};
use winit::window::{Fullscreen, Window, WindowId};

type Res<T> = Result<T, Box<dyn std::error::Error>>;
const W: u32 = 1920;
const H: u32 = 1080;

// ---------------------------------------------------------------------------------------------- options
struct Opts {
    file: Option<String>,
    monitor: Option<usize>,
    seconds: f64,
    windowed: bool,
    report: String,
}

fn parse_args() -> Opts {
    let mut o = Opts {
        file: None,
        monitor: None,
        seconds: 600.0,
        windowed: false,
        report: "spektronautilus-output-report.json".into(),
    };
    let mut it = std::env::args().skip(1);
    while let Some(a) = it.next() {
        match a.as_str() {
            "--pattern" => o.file = None,
            "--monitor" => o.monitor = it.next().and_then(|v| v.parse().ok()),
            "--seconds" => o.seconds = it.next().and_then(|v| v.parse().ok()).unwrap_or(600.0),
            "--windowed" => o.windowed = true,
            "--report" => o.report = it.next().unwrap_or(o.report),
            "-h" | "--help" => {
                println!("spektronautilus-output [CLIP | --pattern] [--monitor N] [--seconds S] [--windowed] [--report FILE]");
                std::process::exit(0);
            }
            f => o.file = Some(f.to_string()),
        }
    }
    o
}

// ---------------------------------------------------------------------------------------------- the video (GStreamer)
struct Video {
    pipeline: gst::Pipeline,
    sink: gst_app::AppSink,
    decoders: Vec<String>,
    fps: f64,
}

impl Video {
    fn open(path: &str) -> Res<Video> {
        gst::init()?;
        // decodebin picks the hardware decoder when there is one (VA-API on Intel, NVDEC on NVIDIA). The picture is scaled to
        // 1920x1080 (black bars if the shape differs) and handed over as NV12, which the graphics card turns into RGB.
        // (videoconvert + videoscale rather than videoconvertscale: the latter needs GStreamer 1.22, Pop!_OS 22.04 has 1.20)
        let desc = "filesrc name=src ! decodebin ! videoconvert ! videoscale add-borders=true ! \
                    video/x-raw,format=NV12,width=1920,height=1080,pixel-aspect-ratio=1/1 ! \
                    appsink name=sink sync=true max-buffers=3 drop=true";
        let pipeline = gst::parse::launch(desc)?
            .downcast::<gst::Pipeline>()
            .map_err(|_| "not a pipeline")?;
        pipeline.by_name("src").ok_or("no source element")?.set_property("location", path);
        let sink = pipeline
            .by_name("sink")
            .ok_or("no sink element")?
            .downcast::<gst_app::AppSink>()
            .map_err(|_| "not an appsink")?;
        pipeline.set_state(gst::State::Paused)?;
        let (res, _, _) = pipeline.state(gst::ClockTime::from_seconds(15));
        res.map_err(|_| format!("could not open {path} (no decoder for it?)"))?;
        let mut decoders = Vec::new();
        for e in pipeline.iterate_recurse().into_iter().flatten() {
            if let Some(f) = e.factory() {
                if f.metadata("klass").unwrap_or("").contains("Decoder") {
                    decoders.push(f.name().to_string());
                }
            }
        }
        let mut fps = 0.0;
        if let Some(caps) = sink.static_pad("sink").and_then(|p| p.current_caps()) {
            if let Ok(info) = gst_video::VideoInfo::from_caps(&caps) {
                let f = info.fps();
                if f.denom() != 0 {
                    fps = f.numer() as f64 / f.denom() as f64;
                }
            }
        }
        pipeline.set_state(gst::State::Playing)?;
        Ok(Video {
            pipeline,
            sink,
            decoders,
            fps,
        })
    }

    /// The newest frame that is due, and the time stamps of all frames that arrived (to find gaps).
    fn latest(&self) -> (Option<gst::Sample>, Vec<u64>) {
        let mut last = None;
        let mut pts = Vec::new();
        while let Some(s) = self.sink.try_pull_sample(gst::ClockTime::ZERO) {
            if let Some(t) = s.buffer().and_then(|b| b.pts()) {
                pts.push(t.nseconds());
            }
            last = Some(s);
        }
        (last, pts)
    }

    /// Loops at the end; returns Err on a playback error. true = it started over.
    fn poll_bus(&self) -> Res<bool> {
        let mut looped = false;
        if let Some(bus) = self.pipeline.bus() {
            while let Some(m) = bus.pop() {
                match m.view() {
                    gst::MessageView::Eos(_) => {
                        self.pipeline
                            .seek_simple(gst::SeekFlags::FLUSH | gst::SeekFlags::KEY_UNIT, gst::ClockTime::ZERO)?;
                        looped = true;
                    }
                    gst::MessageView::Error(e) => return Err(format!("playback error: {} ({:?})", e.error(), e.debug()).into()),
                    _ => {}
                }
            }
        }
        Ok(looped)
    }
}

impl Drop for Video {
    fn drop(&mut self) {
        let _ = self.pipeline.set_state(gst::State::Null);
    }
}

// ---------------------------------------------------------------------------------------------- the numbers
struct Stats {
    start: Instant,
    warm: f64,
    last: Option<Instant>,
    period: f64,
    early: Vec<f64>,
    presents: u64,
    missed: u64,
    worst: f64,
    hist: [u64; 5],
    shown: u64,
    dropped: u64,
    cadence: [u64; 6],
    run: u32,
    last_pts: Option<u64>,
    frame_ns: u64,
    loops: u64,
}

impl Stats {
    fn new(period: f64, fps: f64) -> Stats {
        Stats {
            start: Instant::now(),
            warm: 2.0,
            last: None,
            period,
            early: Vec::new(),
            presents: 0,
            missed: 0,
            worst: 0.0,
            hist: [0; 5],
            shown: 0,
            dropped: 0,
            cadence: [0; 6],
            run: 0,
            last_pts: None,
            frame_ns: if fps > 0.0 { (1e9 / fps) as u64 } else { 0 },
            loops: 0,
        }
    }
    fn counting(&self) -> bool {
        self.start.elapsed().as_secs_f64() >= self.warm
    }
    /// Called once per refresh, right after the swap chain hands out the next image (that is when vsync has passed).
    fn refresh(&mut self, now: Instant) {
        if let Some(l) = self.last {
            let iv = (now - l).as_secs_f64();
            if self.early.len() < 240 {
                self.early.push(iv);
                if self.early.len() == 240 {
                    // the real refresh period, measured: the monitor's own number is sometimes rounded (59.94 shown as 60)
                    let mut v = self.early.clone();
                    v.sort_by(|a, b| a.partial_cmp(b).unwrap());
                    self.period = v[120];
                }
            }
            if self.counting() {
                let k = iv / self.period;
                let i = if k < 1.5 {
                    0
                } else if k < 2.5 {
                    1
                } else if k < 3.5 {
                    2
                } else if k < 4.5 {
                    3
                } else {
                    4
                };
                self.hist[i] += 1;
                self.missed += (k.round() as u64).saturating_sub(1);
                if iv > self.worst {
                    self.worst = iv;
                }
                self.presents += 1;
            }
        }
        self.last = Some(now);
        self.run += 1;
    }
    /// A new video frame goes on screen. pts = the time stamps of every frame that arrived since the last refresh.
    fn new_frame(&mut self, pts: &[u64], looped: bool) {
        if looped {
            self.loops += 1;
            self.last_pts = None;
        }
        if self.counting() {
            if self.run > 0 {
                self.cadence[(self.run.min(6) - 1) as usize] += 1;
            }
            self.shown += 1;
            if let (Some(prev), Some(&newest), true) = (self.last_pts, pts.last(), self.frame_ns > 0) {
                if newest > prev {
                    let steps = ((newest - prev) as f64 / self.frame_ns as f64).round() as u64;
                    self.dropped += steps.saturating_sub(1);
                }
            }
        }
        self.run = 0;
        if let Some(&p) = pts.last() {
            self.last_pts = Some(p);
        }
    }
    fn line(&self, fps: f64) -> String {
        let t = self.start.elapsed().as_secs_f64();
        let mut s = format!(
            "t={:>4.0} s | {:.2} Hz | missed refreshes: {} | worst {:.1} ms",
            t,
            1.0 / self.period,
            self.missed,
            self.worst * 1000.0
        );
        if fps > 0.0 {
            s += &format!(
                " | video {:.2} fps: shown {}, dropped {}, refreshes per frame 1:{} 2:{} 3:{} 4+:{}",
                fps,
                self.shown,
                self.dropped,
                self.cadence[0],
                self.cadence[1],
                self.cadence[2],
                self.cadence[3] + self.cadence[4] + self.cadence[5]
            );
        }
        s
    }
}

// ---------------------------------------------------------------------------------------------- drawing (wgpu)
struct Gpu {
    surface: wgpu::Surface<'static>,
    device: wgpu::Device,
    queue: wgpu::Queue,
    config: wgpu::SurfaceConfiguration,
    pipeline: wgpu::RenderPipeline,
    bind: wgpu::BindGroup,
    tex_y: wgpu::Texture,
    tex_uv: wgpu::Texture,
    ubuf: wgpu::Buffer,
    adapter_name: String,
    backend: String,
}

impl Gpu {
    fn new(window: Arc<Window>) -> Res<Gpu> {
        let instance = wgpu::Instance::new(wgpu::InstanceDescriptor {
            backends: wgpu::Backends::PRIMARY,
            ..Default::default()
        });
        let surface = instance.create_surface(window.clone())?;
        let adapter = pollster::block_on(instance.request_adapter(&wgpu::RequestAdapterOptions {
            power_preference: wgpu::PowerPreference::HighPerformance,
            compatible_surface: Some(&surface),
            force_fallback_adapter: false,
        }))
        .ok_or("no graphics adapter that can draw to this window")?;
        let info = adapter.get_info();
        let (device, queue) = pollster::block_on(adapter.request_device(
            &wgpu::DeviceDescriptor {
                label: Some("output"),
                required_features: wgpu::Features::empty(),
                required_limits: wgpu::Limits::downlevel_defaults().using_resolution(adapter.limits()),
                memory_hints: wgpu::MemoryHints::Performance,
            },
            None,
        ))?;
        let size = window.inner_size();
        let caps = surface.get_capabilities(&adapter);
        // not an sRGB format: the video values are already gamma encoded and must go out as they are
        let format = caps.formats.iter().copied().find(|f| !f.is_srgb()).unwrap_or(caps.formats[0]);
        let config = wgpu::SurfaceConfiguration {
            usage: wgpu::TextureUsages::RENDER_ATTACHMENT,
            format,
            width: size.width.max(1),
            height: size.height.max(1),
            present_mode: wgpu::PresentMode::Fifo, // vsync: one picture per refresh, never torn
            desired_maximum_frame_latency: 2,
            alpha_mode: caps.alpha_modes[0],
            view_formats: vec![],
        };
        surface.configure(&device, &config);

        let tex = |label: &str, w: u32, h: u32, f: wgpu::TextureFormat| {
            device.create_texture(&wgpu::TextureDescriptor {
                label: Some(label),
                size: wgpu::Extent3d {
                    width: w,
                    height: h,
                    depth_or_array_layers: 1,
                },
                mip_level_count: 1,
                sample_count: 1,
                dimension: wgpu::TextureDimension::D2,
                format: f,
                usage: wgpu::TextureUsages::TEXTURE_BINDING | wgpu::TextureUsages::COPY_DST,
                view_formats: &[],
            })
        };
        let tex_y = tex("y", W, H, wgpu::TextureFormat::R8Unorm);
        let tex_uv = tex("uv", W / 2, H / 2, wgpu::TextureFormat::Rg8Unorm);
        let sampler = device.create_sampler(&wgpu::SamplerDescriptor {
            mag_filter: wgpu::FilterMode::Linear,
            min_filter: wgpu::FilterMode::Linear,
            ..Default::default()
        });
        let ubuf = device.create_buffer(&wgpu::BufferDescriptor {
            label: Some("u"),
            size: 16,
            usage: wgpu::BufferUsages::UNIFORM | wgpu::BufferUsages::COPY_DST,
            mapped_at_creation: false,
        });
        let t_entry = |b: u32| wgpu::BindGroupLayoutEntry {
            binding: b,
            visibility: wgpu::ShaderStages::FRAGMENT,
            ty: wgpu::BindingType::Texture {
                sample_type: wgpu::TextureSampleType::Float { filterable: true },
                view_dimension: wgpu::TextureViewDimension::D2,
                multisampled: false,
            },
            count: None,
        };
        let layout = device.create_bind_group_layout(&wgpu::BindGroupLayoutDescriptor {
            label: Some("layout"),
            entries: &[
                t_entry(0),
                t_entry(1),
                wgpu::BindGroupLayoutEntry {
                    binding: 2,
                    visibility: wgpu::ShaderStages::FRAGMENT,
                    ty: wgpu::BindingType::Sampler(wgpu::SamplerBindingType::Filtering),
                    count: None,
                },
                wgpu::BindGroupLayoutEntry {
                    binding: 3,
                    visibility: wgpu::ShaderStages::FRAGMENT,
                    ty: wgpu::BindingType::Buffer {
                        ty: wgpu::BufferBindingType::Uniform,
                        has_dynamic_offset: false,
                        min_binding_size: None,
                    },
                    count: None,
                },
            ],
        });
        let vy = tex_y.create_view(&wgpu::TextureViewDescriptor::default());
        let vuv = tex_uv.create_view(&wgpu::TextureViewDescriptor::default());
        let bind = device.create_bind_group(&wgpu::BindGroupDescriptor {
            label: Some("bind"),
            layout: &layout,
            entries: &[
                wgpu::BindGroupEntry {
                    binding: 0,
                    resource: wgpu::BindingResource::TextureView(&vy),
                },
                wgpu::BindGroupEntry {
                    binding: 1,
                    resource: wgpu::BindingResource::TextureView(&vuv),
                },
                wgpu::BindGroupEntry {
                    binding: 2,
                    resource: wgpu::BindingResource::Sampler(&sampler),
                },
                wgpu::BindGroupEntry {
                    binding: 3,
                    resource: ubuf.as_entire_binding(),
                },
            ],
        });
        let shader = device.create_shader_module(wgpu::ShaderModuleDescriptor {
            label: Some("shader"),
            source: wgpu::ShaderSource::Wgsl(include_str!("shader.wgsl").into()),
        });
        let pl = device.create_pipeline_layout(&wgpu::PipelineLayoutDescriptor {
            label: Some("pl"),
            bind_group_layouts: &[&layout],
            push_constant_ranges: &[],
        });
        let pipeline = device.create_render_pipeline(&wgpu::RenderPipelineDescriptor {
            label: Some("draw"),
            layout: Some(&pl),
            vertex: wgpu::VertexState {
                module: &shader,
                entry_point: "vs_main",
                buffers: &[],
                compilation_options: Default::default(),
            },
            fragment: Some(wgpu::FragmentState {
                module: &shader,
                entry_point: "fs_main",
                targets: &[Some(wgpu::ColorTargetState {
                    format,
                    blend: None,
                    write_mask: wgpu::ColorWrites::ALL,
                })],
                compilation_options: Default::default(),
            }),
            primitive: wgpu::PrimitiveState::default(),
            depth_stencil: None,
            multisample: wgpu::MultisampleState::default(),
            multiview: None,
            cache: None,
        });
        Ok(Gpu {
            surface,
            device,
            queue,
            config,
            pipeline,
            bind,
            tex_y,
            tex_uv,
            ubuf,
            adapter_name: info.name,
            backend: format!("{:?}", info.backend),
        })
    }

    fn resize(&mut self, w: u32, h: u32) {
        self.config.width = w.max(1);
        self.config.height = h.max(1);
        self.surface.configure(&self.device, &self.config);
    }

    fn upload(&self, sample: &gst::Sample) -> Res<()> {
        let buffer = sample.buffer().ok_or("frame without data")?;
        let caps = sample.caps().ok_or("frame without format")?;
        let info = gst_video::VideoInfo::from_caps(caps)?;
        let frame = gst_video::VideoFrameRef::from_buffer_ref_readable(buffer, &info).map_err(|_| "frame not readable")?;
        let stride = frame.plane_stride();
        let plane = |tex: &wgpu::Texture, data: &[u8], bpr: i32, w: u32, h: u32| {
            self.queue.write_texture(
                wgpu::ImageCopyTexture {
                    texture: tex,
                    mip_level: 0,
                    origin: wgpu::Origin3d::ZERO,
                    aspect: wgpu::TextureAspect::All,
                },
                data,
                wgpu::ImageDataLayout {
                    offset: 0,
                    bytes_per_row: Some(bpr as u32),
                    rows_per_image: Some(h),
                },
                wgpu::Extent3d {
                    width: w,
                    height: h,
                    depth_or_array_layers: 1,
                },
            );
        };
        plane(&self.tex_y, frame.plane_data(0)?, stride[0], W, H);
        plane(&self.tex_uv, frame.plane_data(1)?, stride[1], W / 2, H / 2);
        Ok(())
    }

    /// Waits for the next refresh (Fifo), draws, shows. Returns the moment the image was handed out.
    fn draw(&self, mode: u32, frame: u32) -> Res<Instant> {
        let out = match self.surface.get_current_texture() {
            Ok(t) => t,
            Err(wgpu::SurfaceError::Outdated) | Err(wgpu::SurfaceError::Lost) => {
                self.surface.configure(&self.device, &self.config);
                self.surface.get_current_texture()?
            }
            Err(e) => return Err(e.into()),
        };
        let now = Instant::now();
        let mut u = [0u8; 16];
        u[0..4].copy_from_slice(&mode.to_ne_bytes());
        u[4..8].copy_from_slice(&frame.to_ne_bytes());
        u[8..12].copy_from_slice(&(self.config.width as f32).to_ne_bytes());
        u[12..16].copy_from_slice(&(self.config.height as f32).to_ne_bytes());
        self.queue.write_buffer(&self.ubuf, 0, &u);
        let view = out.texture.create_view(&wgpu::TextureViewDescriptor::default());
        let mut enc = self
            .device
            .create_command_encoder(&wgpu::CommandEncoderDescriptor { label: Some("frame") });
        {
            let mut pass = enc.begin_render_pass(&wgpu::RenderPassDescriptor {
                label: Some("pass"),
                color_attachments: &[Some(wgpu::RenderPassColorAttachment {
                    view: &view,
                    resolve_target: None,
                    ops: wgpu::Operations {
                        load: wgpu::LoadOp::Clear(wgpu::Color::BLACK),
                        store: wgpu::StoreOp::Store,
                    },
                })],
                depth_stencil_attachment: None,
                timestamp_writes: None,
                occlusion_query_set: None,
            });
            pass.set_pipeline(&self.pipeline);
            pass.set_bind_group(0, &self.bind, &[]);
            pass.draw(0..3, 0..1);
        }
        self.queue.submit(Some(enc.finish()));
        out.present();
        Ok(now)
    }
}

// ---------------------------------------------------------------------------------------------- the app
struct App {
    opts: Opts,
    window: Option<Arc<Window>>,
    gpu: Option<Gpu>,
    video: Option<Video>,
    stats: Option<Stats>,
    monitor_name: String,
    frame: u32,
    last_print: f64,
    error: Option<String>,
    done: bool,
}

impl App {
    fn finish(&mut self, event_loop: &ActiveEventLoop) {
        if !self.done {
            self.done = true;
            self.write_report();
        }
        event_loop.exit();
    }

    fn write_report(&self) {
        let (Some(s), Some(g)) = (&self.stats, &self.gpu) else {
            return;
        };
        let fps = self.video.as_ref().map(|v| v.fps).unwrap_or(0.0);
        let dec = self.video.as_ref().map(|v| v.decoders.join(", ")).unwrap_or_default();
        let esc = |t: &str| t.replace('\\', "\\\\").replace('"', "\\\"");
        let json = format!(
            "{{\n  \"seconds\": {:.1},\n  \"mode\": \"{}\",\n  \"file\": \"{}\",\n  \"monitor\": \"{}\",\n  \"session\": \"{}\",\n  \"gpu\": \"{}\",\n  \"backend\": \"{}\",\n  \"refresh_hz\": {:.3},\n  \"refreshes_counted\": {},\n  \"missed_refreshes\": {},\n  \"worst_interval_ms\": {:.2},\n  \"intervals\": {{\"1\": {}, \"2\": {}, \"3\": {}, \"4\": {}, \"5+\": {}}},\n  \"video_fps\": {:.3},\n  \"decoders\": \"{}\",\n  \"frames_shown\": {},\n  \"frames_dropped\": {},\n  \"refreshes_per_frame\": {{\"1\": {}, \"2\": {}, \"3\": {}, \"4\": {}, \"5\": {}, \"6+\": {}}},\n  \"loops\": {},\n  \"error\": \"{}\"\n}}\n",
            s.start.elapsed().as_secs_f64(),
            if self.video.is_some() { "clip" } else { "pattern" },
            esc(self.opts.file.as_deref().unwrap_or("")),
            esc(&self.monitor_name),
            esc(&std::env::var("XDG_SESSION_TYPE").unwrap_or_default()),
            esc(&g.adapter_name),
            g.backend,
            1.0 / s.period,
            s.presents,
            s.missed,
            s.worst * 1000.0,
            s.hist[0],
            s.hist[1],
            s.hist[2],
            s.hist[3],
            s.hist[4],
            fps,
            esc(&dec),
            s.shown,
            s.dropped,
            s.cadence[0],
            s.cadence[1],
            s.cadence[2],
            s.cadence[3],
            s.cadence[4],
            s.cadence[5],
            s.loops,
            esc(self.error.as_deref().unwrap_or(""))
        );
        match std::fs::write(&self.opts.report, &json) {
            Ok(_) => println!("Report written to {}", self.opts.report),
            Err(e) => eprintln!("Could not write the report: {e}"),
        }
        println!("{}", s.line(fps));
        let ideal = if fps > 0.0 { ((1.0 / s.period) / fps).round() as usize } else { 0 };
        let uneven = if ideal >= 1 && ideal <= 6 {
            s.shown.saturating_sub(s.cadence[ideal - 1])
        } else {
            0
        };
        if s.missed == 0 && s.dropped == 0 {
            println!(
                "RESULT: smooth. No refresh was missed{}.",
                if fps > 0.0 { " and no video frame was dropped" } else { "" }
            );
        } else {
            println!(
                "RESULT: {} missed refreshes, {} dropped video frames. The stutter is below the browser.",
                s.missed, s.dropped
            );
        }
        if fps > 0.0 && ideal >= 1 && uneven > 0 {
            println!(
                "Note: {} frames were not shown for exactly {} refreshes (judder from the clip's {:.2} fps against {:.2} Hz).",
                uneven,
                ideal,
                fps,
                1.0 / s.period
            );
        }
    }

    fn step(&mut self, event_loop: &ActiveEventLoop) -> Res<()> {
        let (Some(gpu), Some(stats)) = (&self.gpu, &mut self.stats) else {
            return Ok(());
        };
        let mut new_pts: Option<Vec<u64>> = None;
        let mut looped = false;
        if let Some(v) = &self.video {
            looped = v.poll_bus()?;
            let (sample, pts) = v.latest();
            if let Some(s) = sample {
                gpu.upload(&s)?;
                new_pts = Some(pts);
            }
        }
        let now = gpu.draw(if self.video.is_some() { 0 } else { 1 }, self.frame)?;
        self.frame = self.frame.wrapping_add(1);
        stats.refresh(now);
        if let Some(p) = new_pts {
            stats.new_frame(&p, looped);
        }
        let t = stats.start.elapsed().as_secs_f64();
        if t - self.last_print >= 5.0 {
            self.last_print = t;
            println!("{}", stats.line(self.video.as_ref().map(|v| v.fps).unwrap_or(0.0)));
        }
        if t >= self.opts.seconds {
            self.finish(event_loop);
        }
        Ok(())
    }
}

impl ApplicationHandler for App {
    fn resumed(&mut self, event_loop: &ActiveEventLoop) {
        if self.window.is_some() {
            return;
        }
        let monitors: Vec<_> = event_loop.available_monitors().collect();
        let primary = event_loop.primary_monitor();
        println!("Screens:");
        for (i, m) in monitors.iter().enumerate() {
            let hz = m.refresh_rate_millihertz().map(|r| r as f64 / 1000.0).unwrap_or(0.0);
            let size = m.size();
            println!(
                "  {i}: {} {}x{} {:.2} Hz{}",
                m.name().unwrap_or_default(),
                size.width,
                size.height,
                hz,
                if Some(m) == primary.as_ref() { " (main screen)" } else { "" }
            );
        }
        // the projector: the screen asked for, otherwise the first one that is not the main screen
        let chosen = match self.opts.monitor {
            Some(i) => monitors.get(i).cloned(),
            None => monitors
                .iter()
                .find(|m| Some(*m) != primary.as_ref())
                .cloned()
                .or_else(|| primary.clone()),
        };
        let mut attrs = Window::default_attributes().with_title("Spektronautilus Output");
        if self.opts.windowed {
            attrs = attrs.with_inner_size(LogicalSize::new(1280.0, 720.0));
        } else {
            attrs = attrs.with_fullscreen(Some(Fullscreen::Borderless(chosen.clone())));
        }
        let window = match event_loop.create_window(attrs) {
            Ok(w) => Arc::new(w),
            Err(e) => {
                eprintln!("Could not open a window: {e}");
                event_loop.exit();
                return;
            }
        };
        window.set_cursor_visible(false);
        self.monitor_name = chosen.as_ref().and_then(|m| m.name()).unwrap_or_else(|| "window".into());
        let hz = chosen
            .as_ref()
            .and_then(|m| m.refresh_rate_millihertz())
            .map(|r| r as f64 / 1000.0)
            .unwrap_or(60.0);
        match Gpu::new(window.clone()) {
            Ok(g) => {
                println!(
                    "Drawing with {} ({}), on {}, {} session",
                    g.adapter_name,
                    g.backend,
                    self.monitor_name,
                    std::env::var("XDG_SESSION_TYPE").unwrap_or_else(|_| "unknown".into())
                );
                self.gpu = Some(g);
            }
            Err(e) => {
                eprintln!("Could not start the graphics card: {e}");
                event_loop.exit();
                return;
            }
        }
        if let Some(f) = self.opts.file.clone() {
            match Video::open(&f) {
                Ok(v) => {
                    println!(
                        "Clip: {f}, {:.2} fps, decoded by {}",
                        v.fps,
                        if v.decoders.is_empty() { "?".into() } else { v.decoders.join(", ") }
                    );
                    self.video = Some(v);
                }
                Err(e) => {
                    eprintln!("Could not play {f}: {e}");
                    event_loop.exit();
                    return;
                }
            }
        } else {
            println!("Test pattern: a white bar moving 16 pixels every refresh. A jump in its movement is a missed refresh.");
        }
        let fps = self.video.as_ref().map(|v| v.fps).unwrap_or(0.0);
        self.stats = Some(Stats::new(1.0 / hz, fps));
        println!(
            "Measuring for {:.0} s (the first 2 s are not counted). Esc or Q stops early.",
            self.opts.seconds
        );
        self.window = Some(window);
        event_loop.set_control_flow(ControlFlow::Poll);
    }

    fn window_event(&mut self, event_loop: &ActiveEventLoop, _id: WindowId, event: WindowEvent) {
        match event {
            WindowEvent::CloseRequested => self.finish(event_loop),
            WindowEvent::KeyboardInput { event, .. } if event.state == ElementState::Pressed => {
                let stop = match &event.logical_key {
                    Key::Named(NamedKey::Escape) => true,
                    Key::Character(c) => c.as_str().eq_ignore_ascii_case("q"),
                    _ => false,
                };
                if stop {
                    self.finish(event_loop);
                }
            }
            WindowEvent::Resized(size) => {
                if let Some(g) = &mut self.gpu {
                    g.resize(size.width, size.height);
                }
            }
            WindowEvent::RedrawRequested => {
                if self.done {
                    return;
                }
                if let Err(e) = self.step(event_loop) {
                    eprintln!("Stopped: {e}");
                    self.error = Some(e.to_string());
                    self.finish(event_loop);
                }
            }
            _ => {}
        }
    }

    fn about_to_wait(&mut self, _event_loop: &ActiveEventLoop) {
        if let Some(w) = &self.window {
            w.request_redraw();
        }
    }
}

fn main() {
    let opts = parse_args();
    let event_loop = match EventLoop::new() {
        Ok(e) => e,
        Err(e) => {
            eprintln!("No screen to draw on: {e}");
            std::process::exit(1);
        }
    };
    let mut app = App {
        opts,
        window: None,
        gpu: None,
        video: None,
        stats: None,
        monitor_name: String::new(),
        frame: 0,
        last_print: 0.0,
        error: None,
        done: false,
    };
    if let Err(e) = event_loop.run_app(&mut app) {
        eprintln!("Stopped: {e}");
    }
    let failed = app.error.is_some() || app.stats.is_none();
    std::process::exit(if failed { 1 } else { 0 });
}
