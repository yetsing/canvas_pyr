#![deny(clippy::all)]
#![allow(clippy::many_single_char_names)]
#![allow(clippy::too_many_arguments)]
#![allow(clippy::new_without_default)]

#[macro_use]
extern crate serde_derive;

use std::{ffi::CString, mem, slice, str::FromStr};

use pyo3::{
  exceptions::{PyRuntimeError, PyValueError},
  prelude::*,
  types::{PyBytes, PyString, PyWeakrefReference},
};

use ctx::{
  CanvasRenderingContext2D, Context, ContextData, ContextOutputData, SvgExportFlag, encode_surface,
};
use font::{FONT_REGEXP, init_font_regexp};
use sk::{ColorSpace, SkiaDataRef, SurfaceRef};

use avif::AvifConfig;

use crate::a_either::PyEither;

#[global_allocator]
static ALLOC: mimalloc_safe::MiMalloc = mimalloc_safe::MiMalloc;

mod a_either;
mod a_geometry;
mod avif;
mod ctx;
mod error;
mod filter;
mod font;
mod gif;
pub mod global_fonts;
mod gradient;
mod image;
pub mod lottie;
mod page_recorder;
pub mod path;
mod pattern;
pub mod picture_recorder;
#[allow(dead_code)]
mod sk;
mod state;
pub mod svg;

const MIME_WEBP: &str = "image/webp";
const MIME_PNG: &str = "image/png";
const MIME_JPEG: &str = "image/jpeg";
const MIME_AVIF: &str = "image/avif";
const MIME_GIF: &str = "image/gif";

// Consistent with the default value of JPEG quality in Blink
// https://source.chromium.org/chromium/chromium/src/+/main:third_party/blink/renderer/platform/image-encoders/image_encoder.cc;l=85;drc=81c6f843fdfd8ef660d733289a7a32abe68e247a
const DEFAULT_JPEG_QUALITY: u8 = 92;

// Consistent with the default value of WebP quality in Blink
// https://source.chromium.org/chromium/chromium/src/+/main:third_party/blink/renderer/platform/image-encoders/image_encoder.cc;l=100;drc=81c6f843fdfd8ef660d733289a7a32abe68e247a
const DEFAULT_WEBP_QUALITY: u8 = 80;

const DEFAULT_WIDTH: i32 = 350;
const DEFAULT_HEIGHT: i32 = 150;

#[derive(Clone, Debug)]
pub struct ConvertToBlobOptions {
  pub mime: Option<String>,
  pub quality: Option<f64>,
}

impl Default for ConvertToBlobOptions {
  fn default() -> Self {
    Self {
      mime: Some(MIME_PNG.to_owned()),
      quality: None,
    }
  }
}

impl FromPyObject<'_, '_> for ConvertToBlobOptions {
  type Error = PyErr;

  fn extract(obj: Borrowed<'_, '_, PyAny>) -> Result<Self, Self::Error> {
    let dict = obj.cast::<pyo3::types::PyMapping>()?;
    let mut config = Self::default();
    if let Ok(value) = dict.get_item("mime") {
      config.mime = value.extract()?;
    }
    if let Ok(value) = dict.get_item("quality") {
      config.quality = value.extract()?;
    }

    Ok(config)
  }
}

#[derive(Clone, Debug, Default)]
pub struct CanvasRenderingContext2DAttributes {
  pub alpha: Option<bool>,
  pub color_space: Option<String>,
}

impl FromPyObject<'_, '_> for CanvasRenderingContext2DAttributes {
  type Error = PyErr;

  fn extract(obj: Borrowed<'_, '_, PyAny>) -> Result<Self, Self::Error> {
    let dict = obj.cast::<pyo3::types::PyMapping>()?;
    let mut config = Self::default();
    if let Ok(value) = dict.get_item("alpha") {
      config.alpha = value.extract()?;
    }
    if let Ok(value) = dict.get_item("colorSpace") {
      config.color_space = value.extract()?;
    }

    Ok(config)
  }
}

#[pyclass(module = "canvas_pyr", name = "Canvas", weakref)]
pub struct CanvasElement {
  pub(crate) width: u32,
  pub(crate) height: u32,
  // ctx 既要在 Rust 侧持有，也要在 Python 侧持有，所以用 Py<T> 包裹
  pub(crate) ctx: Py<CanvasRenderingContext2D>,
}

impl CanvasElement {
  fn create_context(py: Python, width: u32, height: u32) -> PyResult<CanvasRenderingContext2D> {
    let default_style = PyString::intern(py, "#000000").into_any().unbind();
    let ctx = CanvasRenderingContext2D {
      context: Context::new(width, height, ColorSpace::default())?,
      fill_style_hidden: default_style.clone_ref(py),
      stroke_style_hidden: default_style.clone_ref(py),
      canvas: None,
    };
    Ok(ctx)
  }
  fn new_inner<'py>(py: Python<'py>, width: i32, height: i32) -> PyResult<Bound<'py, PyAny>> {
    // Default fallback of canvas on browser and skia-canvas is 350x150
    let width = (if width <= 0 { DEFAULT_WIDTH } else { width }) as u32;
    let height = (if height <= 0 { DEFAULT_HEIGHT } else { height }) as u32;
    let ctx = Self::create_context(py, width, height)?;
    // CanvasRenderingContext2D need share between Rust and Python,
    // so we need to create it in Python and get the handle here
    let py_ctx = Py::new(py, ctx)?;
    let canvas = Self {
      width,
      height,
      ctx: py_ctx,
    };
    // create a weak reference to the canvas and store it in the context,
    // so that context can get a reference to the canvas when needed
    let pycanvas = Bound::new(py, canvas)?;
    let weakref = PyWeakrefReference::new_with(&pycanvas, py.None())?;
    pycanvas.borrow().ctx.borrow_mut(py).canvas = Some(weakref.unbind());
    Ok(pycanvas.into_any())
  }

  fn encode_inner(
    &self,
    py: Python,
    format: String,
    quality_or_config: PyEither<u32, AvifConfig>,
  ) -> PyResult<ContextData> {
    let format_str = format.as_str();
    let quality = match &quality_or_config {
      PyEither::A(q) => (*q) as u8,
      PyEither::B(s) => s.quality.map(|q| q as u8).unwrap_or(DEFAULT_JPEG_QUALITY),
    };
    let ctx2d = &self.ctx.borrow_mut(py).context;
    let surface_ref = ctx2d.surface.reference();

    let task = match format_str {
      "webp" => ContextData::Webp(surface_ref, quality),
      "jpeg" => ContextData::Jpeg(surface_ref, quality),
      "png" => ContextData::Png(surface_ref),
      "avif" => {
        let cfg = AvifConfig::from(&quality_or_config);
        ContextData::Avif(surface_ref, cfg.into(), ctx2d.width, ctx2d.height)
      }
      "gif" => {
        let cfg = gif::GifConfig {
          quality: match &quality_or_config {
            &PyEither::A(q) => Some(q),
            _ => None,
          },
        };
        ContextData::Gif(surface_ref, cfg, ctx2d.width, ctx2d.height)
      }
      _ => {
        return Err(PyValueError::new_err(format!(
          "{format_str} is not valid format"
        )));
      }
    };

    Ok(task)
  }

  fn to_data_url_inner(
    &self,
    py: Python,
    mime: Option<&str>,
    quality_or_config: PyEither<f64, AvifConfig>,
  ) -> PyResult<String> {
    let mime = mime.unwrap_or(MIME_PNG);
    let mut output = format!("data:{};base64,", &mime);
    let surface_data = get_data_ref(
      &self.ctx.borrow(py).context.surface.reference(),
      mime,
      &match quality_or_config {
        PyEither::A(q) => PyEither::A((q * 100.0) as u32),
        PyEither::B(s) => PyEither::B(s),
      },
      self.width,
      self.height,
    )?;
    match surface_data {
      ContextOutputData::Skia(data_ref) => {
        base64_simd::STANDARD.encode_append(data_ref.slice(), &mut output);
      }
      ContextOutputData::Avif(data_ref) => {
        base64_simd::STANDARD.encode_append(data_ref.as_ref(), &mut output);
      }
      ContextOutputData::Gif(data_ref) => {
        base64_simd::STANDARD.encode_append(&data_ref, &mut output);
      }
    }
    Ok(output)
  }
}

#[pymethods]
impl CanvasElement {
  #[setter]
  pub fn set_width(&mut self, py: Python, width: i32) -> PyResult<()> {
    let width = (if width <= 0 { DEFAULT_WIDTH } else { width }) as u32;
    self.width = width;
    let height = self.height;
    let _ = mem::replace(
      &mut self.ctx.borrow_mut(py).context,
      Context::new(width, height, ColorSpace::default())?,
    );
    Ok(())
  }

  #[getter]
  pub fn get_width(&self) -> u32 {
    self.width
  }

  #[setter]
  pub fn set_height(&mut self, py: Python, height: i32) -> PyResult<()> {
    let height = (if height <= 0 { DEFAULT_HEIGHT } else { height }) as u32;
    self.height = height;
    let width = self.width;
    let _ = mem::replace(
      &mut self.ctx.borrow_mut(py).context,
      Context::new(width, height, ColorSpace::default())?,
    );
    Ok(())
  }

  #[getter]
  pub fn get_height(&self) -> u32 {
    self.height
  }

  #[pyo3(name = "getContext")]
  #[pyo3(signature = (context_type, attrs=None))]
  pub fn get_context(
    &mut self,
    py: Python,
    context_type: String,
    attrs: Option<CanvasRenderingContext2DAttributes>,
  ) -> PyResult<Py<CanvasRenderingContext2D>> {
    if context_type != "2d" {
      return Err(PyValueError::new_err(format!(
        "{context_type} is not supported"
      )));
    }
    let context_2d = &mut self.ctx.borrow_mut(py).context;
    if !attrs.as_ref().and_then(|a| a.alpha).unwrap_or(true) {
      let mut fill_paint = context_2d.fill_paint()?;
      fill_paint.set_color(255, 255, 255, 255);
      context_2d.alpha = false;
      context_2d.surface.draw_rect(
        0f32,
        0f32,
        self.width as f32,
        self.height as f32,
        &fill_paint,
      );
    }
    let color_space = attrs
      .and_then(|a| a.color_space)
      .and_then(|cs| ColorSpace::from_str(&cs).ok())
      .unwrap_or_default();
    context_2d.color_space = color_space;
    Ok(self.ctx.clone_ref(py))
  }

  #[pyo3(signature = (format, quality_or_config=None))]
  pub fn encode<'py>(
    &mut self,
    py: Python<'py>,
    format: String,
    quality_or_config: Option<PyEither<u32, AvifConfig>>,
  ) -> PyResult<Bound<'py, PyBytes>> {
    // Flush deferred rendering before encoding
    self.ctx.borrow_mut(py).context.flush();
    let quality_or_config = quality_or_config.unwrap_or(PyEither::A(DEFAULT_JPEG_QUALITY as u32));
    let data = self.encode_inner(py, format, quality_or_config)?;
    let output = encode_surface(&data)?;
    Ok(output.into_bytes(py))
  }

  pub fn data<'py>(&mut self, py: Python<'py>) -> PyResult<Bound<'py, PyBytes>> {
    // Flush deferred rendering before reading data
    self.ctx.borrow_mut(py).context.flush();
    let ctx2d = &self.ctx.borrow(py).context;

    let surface_ref = ctx2d.surface.reference();

    let (ptr, size) = surface_ref
      .data()
      .ok_or_else(|| PyRuntimeError::new_err("Get png data from surface failed"))?;
    unsafe { Ok(PyBytes::from_ptr(py, ptr, size)) }
  }

  #[pyo3(name="toDataURL", signature = (mime=None, quality_or_config=None))]
  pub fn to_data_url(
    &mut self,
    py: Python,
    mime: Option<String>,
    quality_or_config: Option<PyEither<f64, AvifConfig>>,
  ) -> PyResult<String> {
    // Flush deferred rendering before reading data
    self.ctx.borrow_mut(py).context.flush();
    let default_quality_or_config = PyEither::A((DEFAULT_JPEG_QUALITY as f64) / 100.0);
    let quality_or_config = quality_or_config.unwrap_or(default_quality_or_config);
    self.to_data_url_inner(py, mime.as_deref(), quality_or_config)
  }

  #[pyo3(name = "savePng")]
  pub fn save_png(&self, py: Python, path: String) {
    let ctx2d = &self.ctx.borrow(py).context;
    ctx2d.surface.save_png(&path);
  }
}

fn get_data_ref(
  surface_ref: &SurfaceRef,
  mime: &str,
  quality_or_config: &PyEither<u32, AvifConfig>,
  width: u32,
  height: u32,
) -> PyResult<ContextOutputData> {
  let quality = quality_or_config.to_quality(mime);

  if let Some(data_ref) = match mime {
    MIME_WEBP => surface_ref.encode_data(sk::SkEncodedImageFormat::Webp, quality),
    MIME_JPEG => surface_ref.encode_data(sk::SkEncodedImageFormat::Jpeg, quality),
    MIME_PNG => surface_ref.png_data(),
    MIME_AVIF => {
      let (data, size) = surface_ref.data().ok_or_else(|| {
        PyRuntimeError::new_err("Encode to avif error, failed to get surface pixels")
      })?;
      let config = AvifConfig::from(quality_or_config).into();
      let output = avif::encode(
        unsafe { slice::from_raw_parts(data, size) },
        width,
        height,
        &config,
      )
      .map_err(|e| PyRuntimeError::new_err(format!("{e}")))?;
      return Ok(ContextOutputData::Avif(output));
    }
    MIME_GIF => {
      let config = gif::GifConfig {
        quality: match quality_or_config {
          PyEither::A(q) => Some(*q),
          _ => None,
        },
      };
      let output = gif::encode_surface(surface_ref, width, height, &config)
        .map_err(|e| PyRuntimeError::new_err(format!("{e}")))?;
      return Ok(ContextOutputData::Gif(output));
    }
    _ => {
      return Err(PyValueError::new_err(format!("{mime} is not valid mime")));
    }
  } {
    Ok(ContextOutputData::Skia(data_ref))
  } else {
    Err(PyRuntimeError::new_err(format!(
      "encode {mime} output failed"
    )))
  }
}

trait ToQuality {
  fn to_quality(&self, mime: &str) -> u8;
}

impl ToQuality for &PyEither<u32, AvifConfig> {
  fn to_quality(&self, mime_or_format: &str) -> u8 {
    if let PyEither::A(q) = &self {
      *q as u8
    } else {
      match mime_or_format {
        MIME_WEBP | "webp" => DEFAULT_WEBP_QUALITY,
        _ => DEFAULT_JPEG_QUALITY, // https://developer.mozilla.org/en-US/docs/Web/API/HTMLCanvasElement/toDataURL
      }
    }
  }
}

impl ToQuality for PyEither<u32, AvifConfig> {
  fn to_quality(&self, mime: &str) -> u8 {
    ToQuality::to_quality(&self, mime)
  }
}

#[derive(FromPyObject)]
#[pyo3(from_item_all)]
pub struct ContextAttr {
  pub alpha: Option<bool>,
}

#[pyclass(module = "canvas_pyr", weakref)]
pub struct SVGCanvas {
  pub width: u32,
  pub height: u32,
  pub(crate) ctx: Py<CanvasRenderingContext2D>,
  pub(crate) flag: SvgExportFlag,
}

impl SVGCanvas {
  fn create_context(
    py: Python,
    width: u32,
    height: u32,
    flag: SvgExportFlag,
  ) -> PyResult<CanvasRenderingContext2D> {
    let default_style = PyString::intern(py, "#000000").into_any().unbind();
    let ctx = CanvasRenderingContext2D {
      context: Context::new_svg(width, height, flag.into(), ColorSpace::default())?,
      fill_style_hidden: default_style.clone_ref(py),
      stroke_style_hidden: default_style.clone_ref(py),
      canvas: None,
    };
    Ok(ctx)
  }
  pub fn new_inner<'py>(
    py: Python<'py>,
    width: i32,
    height: i32,
    flag: SvgExportFlag,
  ) -> PyResult<Bound<'py, PyAny>> {
    // Default fallback of canvas on browser and skia-canvas is 350x150
    let width = (if width <= 0 { 350 } else { width }) as u32;
    let height = (if height <= 0 { 150 } else { height }) as u32;
    let ctx = Self::create_context(py, width, height, flag)?;
    // CanvasRenderingContext2D need share between Rust and Python,
    // so we need to create it in Python and get the handle here
    let py_ctx = Py::new(py, ctx)?;
    let canvas = Self {
      width,
      height,
      flag,
      ctx: py_ctx,
    };
    // create a weak reference to the canvas and store it in the context,
    // so that context can get a reference to the canvas when needed
    let pycanvas = Bound::new(py, canvas)?;
    let weakref = PyWeakrefReference::new_with(&pycanvas, py.None())?;
    pycanvas.borrow().ctx.borrow_mut(py).canvas = Some(weakref.unbind());
    Ok(pycanvas.into_any())
  }
}

#[pymethods]
impl SVGCanvas {
  #[pyo3(name = "getContext", signature = (context_type, attrs=None))]
  pub fn get_context(
    &mut self,
    py: Python,
    context_type: String,
    attrs: Option<CanvasRenderingContext2DAttributes>,
  ) -> PyResult<Py<CanvasRenderingContext2D>> {
    if context_type != "2d" {
      return Err(PyValueError::new_err(format!(
        "{context_type} is not supported"
      )));
    }
    let context_2d = &mut self.ctx.borrow_mut(py).context;
    if !attrs.as_ref().and_then(|a| a.alpha).unwrap_or(true) {
      let mut fill_paint = context_2d.fill_paint()?;
      fill_paint.set_color(255, 255, 255, 255);
      context_2d.alpha = false;
      context_2d.surface.draw_rect(
        0f32,
        0f32,
        self.width as f32,
        self.height as f32,
        &fill_paint,
      );
    }
    let color_space = attrs
      .and_then(|a| a.color_space)
      .and_then(|cs| ColorSpace::from_str(&cs).ok())
      .unwrap_or_default();
    context_2d.color_space = color_space;
    Ok(self.ctx.clone_ref(py))
  }

  #[pyo3(name = "getContent")]
  pub fn get_content<'py>(&mut self, py: Python<'py>) -> PyResult<Bound<'py, PyBytes>> {
    let context_2d = &mut self.ctx.borrow_mut(py).context;
    let svg_data_stream = context_2d
      .stream
      .take()
      .ok_or_else(|| PyRuntimeError::new_err("SVGCanvas has no stream"))?;
    unsafe {
      sk::ffi::skiac_canvas_destroy(context_2d.surface.0);
    };
    // Null out the canvas pointer so that Surface::drop() won't double-free it.
    // The canvas was already destroyed above to flush/finalize SVG content to the stream.
    context_2d.surface.canvas.0 = std::ptr::null_mut();
    let svg_data = svg_data_stream.data(context_2d.width, context_2d.height);
    let (surface, stream) = sk::Surface::new_svg(
      context_2d.width,
      context_2d.height,
      context_2d.surface.alpha_type(),
      self.flag.into(),
      ColorSpace::default(),
    )
    .ok_or_else(|| PyRuntimeError::new_err("Failed to create surface"))?;
    context_2d.surface = surface;
    context_2d.stream = Some(stream);
    unsafe { Ok(PyBytes::from_ptr(py, svg_data.0.ptr, svg_data.0.size)) }
  }

  #[setter]
  pub fn set_width(&mut self, py: Python, width: i32) -> PyResult<()> {
    let width = (if width <= 0 { DEFAULT_WIDTH } else { width }) as u32;
    self.width = width;
    let height = self.height;
    let _old_ctx = mem::replace(
      &mut self.ctx.borrow_mut(py).context,
      Context::new_svg(width, height, self.flag.into(), ColorSpace::default())?,
    );
    Ok(())
  }

  #[getter]
  pub fn get_width(&self) -> u32 {
    self.width
  }

  #[setter]
  pub fn set_height(&mut self, py: Python, height: i32) -> PyResult<()> {
    let height = (if height <= 0 { 150 } else { height }) as u32;
    self.height = height;
    let width = self.width;
    let _old_ctx = mem::replace(
      &mut self.ctx.borrow_mut(py).context,
      Context::new_svg(width, height, self.flag.into(), ColorSpace::default())?,
    );
    Ok(())
  }

  #[getter]
  pub fn get_height(&self) -> u32 {
    self.height
  }
}

#[derive(FromPyObject)]
#[pyo3(from_item_all)]
pub struct Rect {
  pub left: f64,
  pub top: f64,
  pub right: f64,
  pub bottom: f64,
}

#[derive(Clone, Debug, Default)]
pub struct PDFMetadata {
  /// The document's title
  pub title: Option<String>,
  /// The name of the person who created the document
  pub author: Option<String>,
  /// The subject of the document
  pub subject: Option<String>,
  /// Keywords associated with the document
  pub keywords: Option<String>,
  /// The product that created the original document
  pub creator: Option<String>,
  /// The product that is converting this document to PDF (defaults to "Skia/PDF")
  pub producer: Option<String>,
  /// The DPI for rasterization (default: 72.0)
  pub raster_dpi: Option<f64>,
  /// Encoding quality: 0-100 for lossy JPEG, 101 for lossless (default: 101)
  pub encoding_quality: Option<i32>,
  /// Whether to conform to PDF/A-2b standard (default: false)
  pub pdfa: Option<bool>,
  /// Compression level: -1 (default), 0 (none), 1 (low/fast), 6 (average), 9 (high/slow)
  pub compression_level: Option<i32>,
}

impl FromPyObject<'_, '_> for PDFMetadata {
  type Error = PyErr;

  fn extract(obj: Borrowed<'_, '_, PyAny>) -> Result<Self, Self::Error> {
    let dict = obj.cast::<pyo3::types::PyMapping>()?;
    let mut config = Self::default();
    if let Ok(value) = dict.get_item("title") {
      config.title = value.extract()?;
    }
    if let Ok(value) = dict.get_item("author") {
      config.author = value.extract()?;
    }
    if let Ok(value) = dict.get_item("subject") {
      config.subject = value.extract()?;
    }
    if let Ok(value) = dict.get_item("keywords") {
      config.keywords = value.extract()?;
    }
    if let Ok(value) = dict.get_item("creator") {
      config.creator = value.extract()?;
    }
    if let Ok(value) = dict.get_item("producer") {
      config.producer = value.extract()?;
    }
    if let Ok(value) = dict.get_item("rasterDpi") {
      config.raster_dpi = value.extract()?;
    }
    if let Ok(value) = dict.get_item("encodingQuality") {
      config.encoding_quality = value.extract()?;
    }
    if let Ok(value) = dict.get_item("pdfa") {
      config.pdfa = value.extract()?;
    }
    if let Ok(value) = dict.get_item("compressionLevel") {
      config.compression_level = value.extract()?;
    }

    Ok(config)
  }
}

struct PDFMetadataStrings {
  _title: Option<CString>,
  _author: Option<CString>,
  _subject: Option<CString>,
  _keywords: Option<CString>,
  _creator: Option<CString>,
  _producer: Option<CString>,
}

#[pyclass(unsendable, module = "canvas_pyr")]
pub struct PDFDocument {
  document: sk::ffi::skiac_pdf_document,
  // Keep CStrings alive for the lifetime of the document
  _metadata_strings: Option<PDFMetadataStrings>,
}

#[pymethods]
impl PDFDocument {
  #[new]
  #[pyo3(signature = (metadata=None))]
  pub fn new(metadata: Option<PDFMetadata>) -> Self {
    let mut document = sk::ffi::skiac_pdf_document {
      document: std::ptr::null_mut(),
      stream: std::ptr::null_mut(),
    };

    let (c_metadata, metadata_strings) = if let Some(meta) = metadata {
      let title = meta.title.and_then(|s| CString::new(s).ok());
      let author = meta.author.and_then(|s| CString::new(s).ok());
      let subject = meta.subject.and_then(|s| CString::new(s).ok());
      let keywords = meta.keywords.and_then(|s| CString::new(s).ok());
      let creator = meta.creator.and_then(|s| CString::new(s).ok());
      let producer = meta.producer.and_then(|s| CString::new(s).ok());

      let c_meta = sk::ffi::skiac_pdf_metadata {
        title: title.as_ref().map_or(std::ptr::null(), |s| s.as_ptr()),
        author: author.as_ref().map_or(std::ptr::null(), |s| s.as_ptr()),
        subject: subject.as_ref().map_or(std::ptr::null(), |s| s.as_ptr()),
        keywords: keywords.as_ref().map_or(std::ptr::null(), |s| s.as_ptr()),
        creator: creator.as_ref().map_or(std::ptr::null(), |s| s.as_ptr()),
        producer: producer.as_ref().map_or(std::ptr::null(), |s| s.as_ptr()),
        raster_dpi: meta.raster_dpi.unwrap_or(72.0) as f32,
        encoding_quality: meta.encoding_quality.unwrap_or(101),
        pdfa: meta.pdfa.unwrap_or(false),
        compression_level: meta.compression_level.unwrap_or(-1),
      };

      let strings = PDFMetadataStrings {
        _title: title,
        _author: author,
        _subject: subject,
        _keywords: keywords,
        _creator: creator,
        _producer: producer,
      };

      (Some(c_meta), Some(strings))
    } else {
      (None, None)
    };

    unsafe {
      sk::ffi::skiac_document_create(
        &mut document,
        c_metadata
          .as_ref()
          .map_or(std::ptr::null(), |m| m as *const _),
      );
    }

    Self {
      document,
      _metadata_strings: metadata_strings,
    }
  }

  #[pyo3(name = "beginPage", signature = (width, height, rect=None))]
  pub fn begin_page(
    &mut self,
    py: Python,
    width: f64,
    height: f64,
    rect: Option<Rect>,
  ) -> PyResult<CanvasRenderingContext2D> {
    let canvas_ptr = unsafe {
      let rect = rect.map(|r| sk::ffi::skiac_rect {
        left: r.left as f32,
        top: r.top as f32,
        right: r.right as f32,
        bottom: r.bottom as f32,
      });
      sk::ffi::skiac_document_begin_page(
        &mut self.document,
        width as f32,
        height as f32,
        if let Some(mut rect) = rect {
          &mut rect
        } else {
          std::ptr::null_mut()
        },
      )
    };

    if canvas_ptr.is_null() {
      return Err(PyRuntimeError::new_err("Failed to begin page"));
    }

    // Create a borrowed surface from the canvas
    // The canvas is owned by the document, not by the Surface
    let canvas = sk::Canvas(canvas_ptr);
    let surface = sk::Surface::from_borrowed_canvas(canvas);
    let context = Context::new_from_surface(surface, width as u32, height as u32);

    let default_style = PyString::intern(py, "#000000").into_any().unbind();
    Ok(CanvasRenderingContext2D {
      context,
      fill_style_hidden: default_style.clone_ref(py),
      stroke_style_hidden: default_style.clone_ref(py),
      canvas: None,
    })
  }

  #[pyo3(name = "endPage")]
  pub fn end_page(&mut self) {
    unsafe {
      sk::ffi::skiac_document_end_page(&mut self.document);
    }
  }

  #[pyo3(name = "close")]
  pub fn close<'py>(&mut self, py: Python<'py>) -> PyResult<Bound<'py, PyBytes>> {
    let mut data = sk::ffi::skiac_sk_data {
      ptr: std::ptr::null_mut(),
      size: 0,
      data: std::ptr::null_mut(),
    };
    unsafe {
      sk::ffi::skiac_document_close(&mut self.document, &mut data);
    }
    let pdf_data = SkiaDataRef(data);
    if pdf_data.0.ptr.is_null() {
      return Ok(PyBytes::new(py, "".as_bytes()));
    }
    unsafe { Ok(PyBytes::from_ptr(py, pdf_data.0.ptr, pdf_data.0.size)) }
  }
}

impl Drop for PDFDocument {
  fn drop(&mut self) {
    unsafe {
      sk::ffi::skiac_document_destroy(&mut self.document);
    }
  }
}

#[pyfunction]
#[pyo3(name = "clearAllCache")]
pub fn clear_all_cache() {
  unsafe { sk::ffi::skiac_clear_all_cache() };
}

/// A Python canvas library powered by Skia, with bindings implemented in Rust.
#[pymodule]
#[allow(non_snake_case)]
mod canvas_pyr {
  use pyo3::prelude::*;

  #[pymodule_export]
  use super::{CanvasElement, PDFDocument, SVGCanvas};

  use super::{FONT_REGEXP, init_font_regexp};

  #[pymodule_export]
  use super::{
    a_geometry::{DOMMatrix, DOMPoint, DOMRect},
    avif::ChromaSubsampling,
    ctx::{CanvasRenderingContext2D, SvgExportFlag},
    gif::{GifDisposal, GifEncoder},
    global_fonts::global_fonts,
    image::{Image, ImageData},
    path::{FillType, Path, PathOp, StrokeCap, StrokeJoin},
    svg::convert_svg_text_to_path,
  };

  #[pymodule_init]
  fn init(_m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Arbitrary code to run at the module initialization
    // pre init font regexp
    FONT_REGEXP.get_or_init(init_font_regexp);
    crate::global_fonts::init_fonts();
    Ok(())
  }

  #[pyfunction]
  #[pyo3(name = "createCanvas", signature = (width, height, svgExportFlag=None))]
  fn create_canvas(
    py: Python<'_>,
    width: i32,
    height: i32,
    svgExportFlag: Option<SvgExportFlag>,
  ) -> PyResult<Bound<'_, PyAny>> {
    match svgExportFlag {
      Some(flag) => SVGCanvas::new_inner(py, width, height, flag),
      None => CanvasElement::new_inner(py, width, height),
    }
  }
}
