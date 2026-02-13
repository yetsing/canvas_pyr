use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyString};

use crate::ctx::CanvasRenderingContext2D;
use crate::sk::{self, ffi::skiac_rect};

/// Options for loading Lottie animations
#[derive(FromPyObject)]
#[pyo3(from_item_all)]
pub struct LottieAnimationOptions {
  /// Base path for resolving external resources (images, fonts)
  #[pyo3(item("resourcePath"))]
  pub resource_path: Option<String>,
}

/// Destination rectangle for rendering
#[derive(FromPyObject)]
#[pyo3(from_item_all)]
pub struct LottieRenderRect {
  pub x: f64,
  pub y: f64,
  pub width: f64,
  pub height: f64,
}

/// Lottie animation loaded from JSON
#[pyclass(unsendable, module = "canvas_pyr")]
pub struct LottieAnimation {
  inner: sk::SkottieAnimation,
}

#[pymethods]
impl LottieAnimation {
  /// Load animation from JSON string or Buffer
  #[staticmethod]
  #[pyo3(name="loadFromData", signature=(data, options=None))]
  pub fn load_from_data(
    data: &Bound<'_, PyAny>,
    options: Option<LottieAnimationOptions>,
  ) -> PyResult<Self> {
    let data_bytes = if let Ok(bytes) = data.cast::<PyBytes>() {
      bytes.as_bytes()
    } else if let Ok(s) = data.cast::<PyString>() {
      s.to_str()?.as_bytes()
    } else {
      return Err(PyValueError::new_err("data must be bytes or str"));
    };

    let resource_path = options.as_ref().and_then(|o| o.resource_path.as_deref());

    let inner = sk::SkottieAnimation::from_data(data_bytes, resource_path)
      .ok_or_else(|| PyValueError::new_err("Failed to load Lottie animation from data"))?;

    Ok(Self { inner })
  }

  /// Load animation from file path
  /// External assets are resolved relative to the file's directory
  #[staticmethod]
  #[pyo3(name="loadFromFile", signature=(path))]
  pub fn load_from_file(path: String) -> PyResult<Self> {
    let inner = sk::SkottieAnimation::from_file(&path).ok_or_else(|| {
      PyValueError::new_err(format!(
        "Failed to load Lottie animation from file: {}",
        path
      ))
    })?;

    Ok(Self { inner })
  }

  /// Animation duration in seconds
  #[getter]
  pub fn duration(&self) -> f64 {
    self.inner.duration()
  }

  /// Frame rate (frames per second)
  #[getter]
  pub fn fps(&self) -> f64 {
    self.inner.fps()
  }

  /// Total frame count
  #[getter]
  pub fn frames(&self) -> f64 {
    self.inner.frames()
  }

  /// Animation width
  #[getter]
  pub fn width(&self) -> f64 {
    self.inner.width() as f64
  }

  /// Animation height
  #[getter]
  pub fn height(&self) -> f64 {
    self.inner.height() as f64
  }

  /// Lottie format version
  #[getter]
  pub fn version(&self) -> String {
    self.inner.version().to_string()
  }

  /// Animation in-point (start frame)
  #[getter(inPoint)]
  pub fn in_point(&self) -> f64 {
    self.inner.in_point()
  }

  /// Animation out-point (end frame)
  #[getter(outPoint)]
  pub fn out_point(&self) -> f64 {
    self.inner.out_point()
  }

  /// Seek to normalized position [0..1]
  pub fn seek(&self, t: f64) {
    self.inner.seek(t as f32);
  }

  /// Seek to specific frame index (0 = first frame)
  #[pyo3(name = "seekFrame")]
  pub fn seek_frame(&self, frame: f64) {
    self.inner.seek_frame(frame);
  }

  /// Seek to specific time in seconds
  #[pyo3(name = "seekTime")]
  pub fn seek_time(&self, seconds: f64) {
    self.inner.seek_frame_time(seconds);
  }

  /// Render current frame to canvas context
  #[pyo3(signature = (ctx, dst=None))]
  pub fn render(&self, ctx: &CanvasRenderingContext2D, dst: Option<LottieRenderRect>) {
    let canvas = &ctx.context.surface.canvas;
    let rect = dst.map(|d| skiac_rect {
      left: d.x as f32,
      top: d.y as f32,
      right: (d.x + d.width) as f32,
      bottom: (d.y + d.height) as f32,
    });
    self.inner.render(canvas, rect.as_ref());
  }
}
