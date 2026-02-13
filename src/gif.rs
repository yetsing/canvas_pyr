use gif::{DisposalMethod, Encoder, Frame, Repeat};
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyMapping;

use crate::error::SkError;
use crate::sk::SurfaceRef;

/// GIF encoding configuration for single-frame encoding
#[derive(Default, Clone)]
pub struct GifConfig {
  /// Quality for NeuQuant color quantization (1-30, lower = slower but better quality)
  /// Default: 10
  pub quality: Option<u32>,
}

impl FromPyObject<'_, '_> for GifConfig {
  type Error = PyErr;

  fn extract(obj: Borrowed<'_, '_, PyAny>) -> Result<Self, Self::Error> {
    let dict = obj.cast::<PyMapping>()?;
    let mut config = Self::default();
    if let Ok(value) = dict.get_item("quality") {
      config.quality = Some(value.extract()?);
    }

    Ok(config)
  }
}

/// Configuration for the GIF encoder (animated GIFs)
#[derive(Default, Clone)]
pub struct GifEncoderConfig {
  /// Loop count: 0 = infinite loop, positive number = finite loops
  /// Default: 0 (infinite)
  pub repeat: Option<i32>,
  /// Quality for NeuQuant color quantization (1-30, lower = slower but better quality)
  /// Default: 10
  pub quality: Option<u32>,
}

impl FromPyObject<'_, '_> for GifEncoderConfig {
  type Error = PyErr;

  fn extract(obj: Borrowed<'_, '_, PyAny>) -> Result<Self, Self::Error> {
    let dict = obj.cast::<PyMapping>()?;
    let mut config = Self::default();
    if let Ok(value) = dict.get_item("repeat") {
      config.repeat = Some(value.extract()?);
    }
    if let Ok(value) = dict.get_item("quality") {
      config.quality = Some(value.extract()?);
    }

    Ok(config)
  }
}

/// Configuration for individual GIF frames
#[derive(Default, Clone)]
pub struct GifFrameConfig {
  /// Frame delay in milliseconds
  /// Default: 100 (100ms = 10 centiseconds)
  pub delay: Option<u32>,
  /// Disposal method for this frame
  pub disposal: Option<GifDisposal>,
  /// Transparent color index (0-255), if the frame has transparency
  pub transparent: Option<u32>,
  /// X offset of this frame within the canvas
  pub left: Option<u32>,
  /// Y offset of this frame within the canvas
  pub top: Option<u32>,
}

impl FromPyObject<'_, '_> for GifFrameConfig {
  type Error = PyErr;

  fn extract(obj: Borrowed<'_, '_, PyAny>) -> Result<Self, Self::Error> {
    let dict = obj.cast::<PyMapping>()?;
    let mut config = Self::default();
    if let Ok(value) = dict.get_item("delay") {
      config.delay = Some(value.extract()?);
    }
    if let Ok(value) = dict.get_item("disposal") {
      config.disposal = Some(value.extract()?);
    }
    if let Ok(value) = dict.get_item("transparent") {
      config.transparent = Some(value.extract()?);
    }
    if let Ok(value) = dict.get_item("left") {
      config.left = Some(value.extract()?);
    }
    if let Ok(value) = dict.get_item("top") {
      config.top = Some(value.extract()?);
    }

    Ok(config)
  }
}

/// GIF frame disposal method
#[pyclass(module = "canvas_pyr", from_py_object)]
#[derive(Clone, Copy, Default)]
pub enum GifDisposal {
  /// Keep the frame visible (default)
  #[default]
  Keep,
  /// Clear the frame area to the background color
  Background,
  /// Restore to the previous frame
  Previous,
}

impl From<GifDisposal> for DisposalMethod {
  fn from(disposal: GifDisposal) -> Self {
    match disposal {
      GifDisposal::Keep => DisposalMethod::Keep,
      GifDisposal::Background => DisposalMethod::Background,
      GifDisposal::Previous => DisposalMethod::Previous,
    }
  }
}

struct GifFrameData {
  pixels: Vec<u8>,
  width: u16,
  height: u16,
  delay: u16,
  disposal: DisposalMethod,
  transparent: Option<u8>,
  left: u16,
  top: u16,
}

/// GIF Encoder for creating animated GIFs
///
/// Example usage:
/// ```javascript
/// const encoder = new GifEncoder(800, 600, { repeat: 0, quality: 10 });
///
/// // Draw first frame
/// ctx.fillStyle = 'red';
/// ctx.fillRect(0, 0, 800, 600);
/// encoder.addFrame(canvas, { delay: 100 });
///
/// // Draw second frame
/// ctx.fillStyle = 'blue';
/// ctx.fillRect(0, 0, 800, 600);
/// encoder.addFrame(canvas, { delay: 100 });
///
/// // Encode
/// const buffer = encoder.finish();
/// ```
#[pyclass(module = "canvas_pyr")]
pub struct GifEncoder {
  width: u16,
  height: u16,
  frames: Vec<GifFrameData>,
  repeat: Repeat,
  quality: i32,
}

#[pymethods]
impl GifEncoder {
  /// Create a new GIF encoder with the specified dimensions
  #[new]
  #[pyo3(signature = (width, height, config=None))]
  pub fn new(width: u32, height: u32, config: Option<GifEncoderConfig>) -> Self {
    let config = config.unwrap_or_default();
    let repeat = match config.repeat {
      Some(0) | None => Repeat::Infinite,
      Some(n) if n > 0 => Repeat::Finite(n as u16),
      Some(_) => Repeat::Infinite,
    };
    let quality = config.quality.unwrap_or(10).clamp(1, 30) as i32;

    GifEncoder {
      width: width as u16,
      height: height as u16,
      frames: Vec::new(),
      repeat,
      quality,
    }
  }

  /// Add a frame from RGBA pixel data
  ///
  /// The data must be width * height * 4 bytes (RGBA format)
  #[pyo3(name = "addFrame", signature = (data, width, height, config=None))]
  pub fn add_frame(
    &mut self,
    data: Vec<u8>,
    width: u32,
    height: u32,
    config: Option<GifFrameConfig>,
  ) -> PyResult<()> {
    let config = config.unwrap_or_default();
    let expected_len = (width as usize) * (height as usize) * 4;

    if data.len() != expected_len {
      return Err(PyValueError::new_err(format!(
        "Invalid data length: expected {} bytes for {}x{} RGBA image, got {}",
        expected_len,
        width,
        height,
        data.len()
      )));
    }

    // GIF delay is in centiseconds (1/100th of a second)
    let delay_ms = config.delay.unwrap_or(100);
    let delay_cs = (delay_ms / 10) as u16;

    let frame_data = GifFrameData {
      pixels: data,
      width: width as u16,
      height: height as u16,
      delay: delay_cs.max(1), // Minimum 1 centisecond
      disposal: config.disposal.unwrap_or_default().into(),
      transparent: config.transparent.map(|t| t as u8),
      left: config.left.unwrap_or(0) as u16,
      top: config.top.unwrap_or(0) as u16,
    };

    self.frames.push(frame_data);
    Ok(())
  }

  /// Get the number of frames added so far
  #[getter]
  #[pyo3(name = "frameCount")]
  pub fn frame_count(&self) -> u32 {
    self.frames.len() as u32
  }

  /// Get the width of the GIF canvas
  #[getter]
  pub fn width(&self) -> u32 {
    self.width as u32
  }

  /// Get the height of the GIF canvas
  #[getter]
  pub fn height(&self) -> u32 {
    self.height as u32
  }

  /// Finish encoding and return the GIF data
  pub fn finish(&mut self) -> PyResult<Vec<u8>> {
    if self.frames.is_empty() {
      return Err(PyValueError::new_err("Cannot encode GIF with no frames"));
    }

    let data = encode_gif_frames(
      &self.frames,
      self.width,
      self.height,
      self.repeat,
      self.quality,
    )
    .map_err(|e| PyRuntimeError::new_err(format!("GIF encoding failed: {e}")))?;

    // Clear frames after encoding
    self.frames.clear();

    Ok(data)
  }

  /// Dispose of the encoder, clearing all accumulated frames without encoding.
  /// This is called automatically when using the context manager (the with statement).
  ///
  /// Example:
  /// ```python
  /// with GifEncoder(100, 100) as encoder:
  ///     encoder.add_frame(data, 100, 100)
  ///     # If an error is raised here, frames are automatically cleaned up
  ///     buffer = encoder.finish()
  /// # encoder.__exit__() called automatically
  /// ```
  pub fn __exit__(&mut self) {
    self.frames.clear();
  }

  pub fn __enter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
    slf
  }
}

/// Encode multiple frames into an animated GIF
fn encode_gif_frames(
  frames: &[GifFrameData],
  width: u16,
  height: u16,
  repeat: Repeat,
  quality: i32,
) -> std::result::Result<Vec<u8>, SkError> {
  let mut buffer = Vec::new();

  {
    let mut encoder = Encoder::new(&mut buffer, width, height, &[])
      .map_err(|e| SkError::Generic(format!("Failed to create GIF encoder: {e}")))?;

    encoder
      .set_repeat(repeat)
      .map_err(|e| SkError::Generic(format!("Failed to set repeat: {e}")))?;

    for frame_data in frames {
      let mut pixels = frame_data.pixels.clone();

      let mut frame =
        Frame::from_rgba_speed(frame_data.width, frame_data.height, &mut pixels, quality);

      frame.delay = frame_data.delay;
      frame.dispose = frame_data.disposal;
      frame.left = frame_data.left;
      frame.top = frame_data.top;

      if let Some(transparent) = frame_data.transparent {
        frame.transparent = Some(transparent);
      }

      encoder
        .write_frame(&frame)
        .map_err(|e| SkError::Generic(format!("Failed to write frame: {e}")))?;
    }
  }

  Ok(buffer)
}

/// Encode a single frame as a static GIF
pub(crate) fn encode(
  pixels: &[u8],
  width: u32,
  height: u32,
  config: &GifConfig,
) -> std::result::Result<Vec<u8>, SkError> {
  let quality = config.quality.unwrap_or(10).clamp(1, 30) as i32;
  let mut pixels = pixels.to_vec();

  let frame = Frame::from_rgba_speed(width as u16, height as u16, &mut pixels, quality);

  let mut buffer = Vec::new();
  {
    let mut encoder = Encoder::new(&mut buffer, width as u16, height as u16, &[])
      .map_err(|e| SkError::Generic(format!("Failed to create GIF encoder: {e}")))?;

    encoder
      .write_frame(&frame)
      .map_err(|e| SkError::Generic(format!("Failed to write frame: {e}")))?;
  }

  Ok(buffer)
}

/// Encode a surface reference as a static GIF
pub(crate) fn encode_surface(
  surface: &SurfaceRef,
  width: u32,
  height: u32,
  config: &GifConfig,
) -> std::result::Result<Vec<u8>, SkError> {
  let (data, size) = surface
    .data()
    .ok_or_else(|| SkError::Generic("Failed to get surface pixels for GIF encoding".to_owned()))?;

  let pixels = unsafe { std::slice::from_raw_parts(data, size) };
  encode(pixels, width, height, config)
}
