use std::{borrow::Cow, str, str::FromStr};

use base64_simd::STANDARD;
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyByteArray;

use crate::avif::AvifImage;
use crate::error::SkError;
use crate::global_fonts::get_font;
use crate::sk::{AlphaType, Bitmap, ColorSpace, ColorType};

#[pyclass(unsendable, module = "canvas_pyr")]
pub struct ImageData {
  pub(crate) width: usize,
  pub(crate) height: usize,
  pub(crate) color_space: ColorSpace,
  data: *mut u8,
  data_owner: Py<PyByteArray>, // to keep ownership of data buffer
}

impl ImageData {
  pub fn new_zero(py: Python, width: u32, height: u32, color_space: ColorSpace) -> PyResult<Self> {
    Self::new_zero1(py, width as usize, height as usize, color_space)
  }
  pub fn new_zero1(
    py: Python,
    width: usize,
    height: usize,
    color_space: ColorSpace,
  ) -> PyResult<Self> {
    let arraybuffer_length = width * height * 4;
    let py_bytearray = PyByteArray::new_with(py, arraybuffer_length, |bytes: &mut [u8]| {
      bytes.fill(0); // zeroed buffer
      Ok(())
    })?;
    Ok(ImageData {
      width,
      height,
      color_space,
      data: py_bytearray.data(),
      data_owner: py_bytearray.unbind(),
    })
  }

  pub fn new_with_data<F>(
    py: Python,
    width: u32,
    height: u32,
    color_space: ColorSpace,
    f: F,
  ) -> PyResult<Self>
  where
    F: FnOnce(&mut [u8]) -> PyResult<()>,
  {
    let arraybuffer_length = (width * height * 4) as usize;
    let py_bytearray = PyByteArray::new_with(py, arraybuffer_length, f)?;
    Ok(ImageData {
      width: width as usize,
      height: height as usize,
      color_space,
      data: py_bytearray.data(),
      data_owner: py_bytearray.unbind(),
    })
  }

  pub fn data(&self) -> *mut u8 {
    self.data
  }

  pub fn clone_zero(&self, py: Python) -> PyResult<Self> {
    let arraybuffer_length = self.width * self.height * 4;
    let py_bytearray = PyByteArray::new_with(py, arraybuffer_length, |bytes: &mut [u8]| {
      bytes.fill(0); // zeroed buffer
      Ok(())
    })?;
    Ok(ImageData {
      width: self.width,
      height: self.height,
      color_space: self.color_space,
      data: py_bytearray.data(),
      data_owner: py_bytearray.unbind(),
    })
  }
}

#[derive(FromPyObject)]
#[pyo3(from_item_all)]
pub struct Settings {
  #[pyo3(item("colorSpace"))]
  pub color_space: String,
}

#[derive(FromPyObject)]
pub enum WidthOrDataArg {
  Width(u32),
  Datau8(Vec<u8>),
  Datau16(Vec<u16>),
  Dataf32(Vec<f32>),
}

#[derive(FromPyObject)]
pub enum HeightOrSettingsArg {
  Height(u32),
  Settings(Settings),
}

#[pymethods]
impl ImageData {
  #[new]
  #[pyo3(signature=(width_or_data, width_or_height, height_or_settings=None, maybe_settings=None, / ))]
  pub fn new(
    py: Python,
    width_or_data: WidthOrDataArg,
    width_or_height: u32,
    height_or_settings: Option<HeightOrSettingsArg>,
    maybe_settings: Option<Settings>,
  ) -> PyResult<Self> {
    match width_or_data {
      WidthOrDataArg::Width(width) => {
        let height = width_or_height;
        let color_space = match height_or_settings {
          Some(HeightOrSettingsArg::Settings(settings)) => {
            ColorSpace::from_str(&settings.color_space).unwrap_or_default()
          }
          _ => ColorSpace::default(),
        };
        Self::new_zero(py, width, height, color_space)
      }
      WidthOrDataArg::Datau8(data_object) => {
        // Uint8ClampedArray - each pixel takes 4 bytes
        let input_data_length = data_object.len();
        let width = width_or_height;
        let height = match &height_or_settings {
          Some(HeightOrSettingsArg::Height(height)) => *height,
          _ => (input_data_length as u32) / 4 / width,
        };
        let got = height * width * 4;
        let want = input_data_length as u32;
        if got != want {
          return Err(PyValueError::new_err(format!(
            "Index or size is negative or greater than the allowed amount({got} != {want})"
          )));
        }
        let color_space = maybe_settings
          .and_then(|settings| ColorSpace::from_str(&settings.color_space).ok())
          .unwrap_or_default();
        let image_data =
          Self::new_with_data(py, width, height, color_space, |bytes: &mut [u8]| {
            bytes.copy_from_slice(&data_object);
            Ok(())
          })?;
        Ok(image_data)
      }
      WidthOrDataArg::Datau16(data_object) => {
        // Vec<u16> - each pixel takes 4 elements (RGBA), 2 bytes per element
        let input_data_length = data_object.len();
        let width = width_or_height;
        let height = match &height_or_settings {
          Some(HeightOrSettingsArg::Height(height)) => *height,
          _ => (input_data_length as u32) / 4 / width,
        };
        let got = height * width * 4;
        let want = input_data_length as u32;
        if got != want {
          return Err(PyValueError::new_err(format!(
            "Index or size is negative or greater than the allowed amount({got} != {want})"
          )));
        }
        let color_space = maybe_settings
          .and_then(|settings| ColorSpace::from_str(&settings.color_space).ok())
          .unwrap_or_default();
        let image_data =
          Self::new_with_data(py, width, height, color_space, |bytes: &mut [u8]| {
            bytes.fill(0u8);
            // Convert Vec<u16> to Vec<u8>
            for (i, &val) in data_object.iter().enumerate() {
              // Convert from 16-bit (0-65535) to 8-bit (0-255)
              bytes[i] = ((val as u32 * 255 + 32767) / 65535) as u8;
            }
            Ok(())
          })?;
        Ok(image_data)
      }
      WidthOrDataArg::Dataf32(data_object) => {
        // Vec<f32> - each pixel takes 4 elements (RGBA), 4 bytes per element
        let input_data_length = data_object.len();
        let width = width_or_height;
        let height = match &height_or_settings {
          Some(HeightOrSettingsArg::Height(height)) => *height,
          _ => (input_data_length as u32) / 4 / width,
        };
        let got = height * width * 4;
        let want = input_data_length as u32;
        if got != want {
          return Err(PyValueError::new_err(format!(
            "Index or size is negative or greater than the allowed amount({got} != {want})"
          )));
        }
        let color_space = maybe_settings
          .and_then(|settings| ColorSpace::from_str(&settings.color_space).ok())
          .unwrap_or_default();
        let image_data =
          Self::new_with_data(py, width, height, color_space, |bytes: &mut [u8]| {
            bytes.fill(0u8);
            // Convert Vec<f32> to Vec<u8>
            for (i, &val) in data_object.iter().enumerate() {
              // Clamp float values to [0.0, 1.0] and convert to 8-bit (0-255)
              let clamped = val.clamp(0.0, 1.0);
              bytes[i] = (clamped * 255.0).round() as u8;
            }
            Ok(())
          })?;
        Ok(image_data)
      }
    }
  }

  #[getter]
  pub fn get_width(&self) -> u32 {
    self.width as u32
  }

  #[getter]
  pub fn get_height(&self) -> u32 {
    self.height as u32
  }

  #[getter]
  pub fn get_data(&self, py: Python) -> Py<PyByteArray> {
    self.data_owner.clone_ref(py)
  }
}

#[derive(FromPyObject)]
pub enum ImageSrcEnum {
  Buffer(Vec<u8>),
  String(String),
}

impl AsRef<[u8]> for ImageSrcEnum {
  fn as_ref(&self) -> &[u8] {
    match self {
      ImageSrcEnum::Buffer(buf) => buf.as_ref(),
      ImageSrcEnum::String(s) => s.as_bytes(),
    }
  }
}

#[pyclass(rename_all = "camelCase", unsendable, module = "canvas_pyr")]
pub struct Image {
  pub(crate) bitmap: Option<Bitmap>,
  pub(crate) complete: bool,
  pub(crate) alt: String,
  pub(crate) current_src: Option<String>,
  width: f64,
  height: f64,
  // Natural dimensions - extracted from image header, available before full decode
  natural_width: f64,
  natural_height: f64,
  pub(crate) need_regenerate_bitmap: bool,
  pub(crate) is_svg: bool,
  pub(crate) color_space: ColorSpace,
  pub(crate) src: Option<ImageSrcEnum>,
  // read data from file path
  file_content: Option<Vec<u8>>,
  // take ownership of avif image, let it be dropped when image is dropped
  _avif_image_ref: Option<AvifImage>,
}

const BYTES_SRC_REPR: &str = "<bytes>";

#[pymethods]
#[allow(non_snake_case)]
impl Image {
  #[new]
  #[pyo3(signature=(width=None, height=None, attrs=None))]
  pub fn new(width: Option<f64>, height: Option<f64>, attrs: Option<Settings>) -> PyResult<Self> {
    let width = width.unwrap_or(-1.0);
    let height = height.unwrap_or(-1.0);
    let color_space = attrs
      .and_then(|settings| ColorSpace::from_str(&settings.color_space).ok())
      .unwrap_or_default();
    Ok(Image {
      complete: true,
      bitmap: None,
      alt: "".to_string(),
      current_src: None,
      width,
      height,
      natural_width: 0.0,
      natural_height: 0.0,
      need_regenerate_bitmap: false,
      is_svg: false,
      color_space,
      src: None,
      file_content: None,
      _avif_image_ref: None,
    })
  }

  #[getter]
  pub fn get_width(&self) -> f64 {
    if self.width >= 0.0 { self.width } else { 0.0 }
  }

  #[setter]
  pub fn set_width(&mut self, width: f64) {
    if (width - self.width).abs() > f64::EPSILON {
      self.width = width;
      self.need_regenerate_bitmap = true;
    }
  }

  #[getter(naturalWidth)]
  pub fn get_natural_width(&self) -> f64 {
    // Return stored natural_width (set from imagesize header parsing)
    // Falls back to bitmap dimensions if natural_width not set
    if self.natural_width > 0.0 {
      self.natural_width
    } else {
      self.bitmap.as_ref().map(|b| b.0.width).unwrap_or(0) as f64
    }
  }

  #[getter]
  pub fn get_height(&self) -> f64 {
    if self.height >= 0.0 { self.height } else { 0.0 }
  }

  #[setter]
  pub fn set_height(&mut self, height: f64) {
    if (height - self.height).abs() > f64::EPSILON {
      self.height = height;
      self.need_regenerate_bitmap = true;
    }
  }

  #[getter(naturalHeight)]
  pub fn get_natural_height(&self) -> f64 {
    // Return stored natural_height (set from imagesize header parsing)
    // Falls back to bitmap dimensions if natural_height not set
    if self.natural_height > 0.0 {
      self.natural_height
    } else {
      self.bitmap.as_ref().map(|b| b.0.height).unwrap_or(0) as f64
    }
  }

  #[getter]
  pub fn get_complete(&self) -> bool {
    self.complete
  }

  #[getter(currentSrc)]
  pub fn get_current_src(&self) -> Option<&str> {
    self.current_src.as_deref()
  }

  #[getter]
  pub fn get_alt(&self) -> String {
    self.alt.clone()
  }

  #[setter]
  pub fn set_alt(&mut self, alt: String) {
    self.alt = alt;
  }

  #[getter]
  pub fn get_src(&mut self) -> Option<&str> {
    match self.src.as_mut() {
      Some(ImageSrcEnum::Buffer(_)) => Some(BYTES_SRC_REPR),
      Some(ImageSrcEnum::String(s)) => Some(s.as_str()),
      None => None,
    }
  }

  pub fn load(&mut self, data: ImageSrcEnum) -> PyResult<()> {
    let data = self.src.insert(data);

    // Check if src is empty (per HTML spec)
    // Also treat very small buffers as empty to avoid invalid/ambiguous image headers.
    let is_empty_or_too_small = match &data {
      ImageSrcEnum::Buffer(buffer) => buffer.is_empty() || buffer.len() < 5,
      ImageSrcEnum::String(string) => string.is_empty(),
    };

    if is_empty_or_too_small {
      // HTML spec: empty src = clear state, complete=true, NO events
      self.src = None;
      self.current_src = None;
      self.width = -1.0;
      self.height = -1.0;
      self.natural_width = 0.0;
      self.natural_height = 0.0;
      self.bitmap = None;
      self.file_content = None;
      self._avif_image_ref = None;
      self.complete = true;
      self.is_svg = false;
      self.need_regenerate_bitmap = false;
      return Ok(());
    }

    if let ImageSrcEnum::Buffer(buffer) = &data {
      let buffer_data = buffer.as_slice();
      let length = buffer_data.len();

      // Check if it's SVG (imagesize doesn't support SVG)
      let is_svg = is_svg_image(buffer_data, length);
      // Try to extract dimensions from image header using imagesize (fast, no full decode)
      let (img_width, img_height, is_valid_image) = if is_svg {
        // For SVG, we'll get dimensions after decode; for invalid images, we'll error
        (0.0, 0.0, false)
      } else if let Ok(size) = imagesize::blob_size(buffer_data) {
        (size.width as f64, size.height as f64, true)
      } else {
        (0.0, 0.0, false)
      };

      if is_valid_image || is_svg {
        // Set natural dimensions (sync, from header)
        // For SVG (where imagesize fails), leave at 0 - will be set after decode
        self.natural_width = img_width;
        self.natural_height = img_height;

        // Set width/height if not explicitly set (auto sizing)
        // For SVG, keep at -1.0 to signal that we need auto-sizing after decode
        if is_valid_image {
          if (self.width - -1.0).abs() < f64::EPSILON {
            self.width = img_width;
          }
          if (self.height - -1.0).abs() < f64::EPSILON {
            self.height = img_height;
          }
        }

        // For SVG
        if is_svg {
          let font = get_font().map_err(SkError::from)?;
          if (self.width - -1.0).abs() > f64::EPSILON && (self.height - -1.0).abs() > f64::EPSILON {
            if let Some(bitmap) = Bitmap::from_svg_data_with_custom_size(
              buffer_data.as_ptr(),
              length,
              self.width as f32,
              self.height as f32,
              self.color_space,
              &font,
            ) {
              self.is_svg = true;
              self.natural_width = bitmap.0.width as f64;
              self.natural_height = bitmap.0.height as f64;
              self.bitmap = Some(bitmap);
            } else {
              // Invalid SVG - fire onerror synchronously
              // Clear prior image state to prevent stale data from being drawn
              // Reset width/height to auto (-1.0) so getters return 0 for broken image
              self.complete = true;
              self.width = -1.0;
              self.height = -1.0;
              self.natural_width = 0.0;
              self.natural_height = 0.0;
              self.bitmap = None;
              self.file_content = None;
              self._avif_image_ref = None;
              self.is_svg = false;
              self.need_regenerate_bitmap = false;

              return Err(PyValueError::new_err("Invalid SVG image"));
            }
          } else {
            // SVG without explicit dimensions - use default decode
            match Bitmap::from_svg_data(buffer_data.as_ptr(), length, self.color_space, &font) {
              Some(Ok(bitmap)) => {
                self.is_svg = true;
                self.natural_width = bitmap.0.width as f64;
                self.natural_height = bitmap.0.height as f64;
                self.width = bitmap.0.width as f64;
                self.height = bitmap.0.height as f64;
                self.bitmap = Some(bitmap);
              }
              Some(Err(_)) => {
                // Invalid SVG - fire onerror synchronously
                // Clear prior image state to prevent stale data from being drawn
                // Reset width/height to auto (-1.0) so getters return 0 for broken image
                self.complete = true;
                self.width = -1.0;
                self.height = -1.0;
                self.natural_width = 0.0;
                self.natural_height = 0.0;
                self.bitmap = None;
                self.file_content = None;
                self._avif_image_ref = None;
                self.is_svg = false;
                self.need_regenerate_bitmap = false;

                return Err(PyValueError::new_err("Invalid SVG image"));
              }
              None => {
                // SVG has no dimensions - valid but empty, still fire onload
                self.is_svg = true;
              }
            }
          }

          self.complete = true;
          self.current_src = Some(BYTES_SRC_REPR.to_string());
          return Ok(());
        }

        self.complete = true; // reserve same with node api

        // For not-SVG
        self.bitmap = None;
        self._avif_image_ref = None;
        self.file_content = None;
        self.is_svg = false;
        self.need_regenerate_bitmap = false;

        let mut decoder = BitmapDecoder {
          width: self.width,
          height: self.height,
          color_space: self.color_space,
          file_content: None,
          original_url: None,
        };
        let decoded = decoder.compute(data)?;
        return decoder.resolve(decoded, self);
      } else {
        // imagesize failed (format not supported by imagesize, e.g. BMP, ICO, TIFF)
        self.complete = true;

        // Clear previous state to avoid exposing stale data from previous loads.
        self.natural_width = 0.0;
        self.natural_height = 0.0;
        self.bitmap = None;
        self._avif_image_ref = None;
        self.file_content = None;
        self.is_svg = false;
        self.need_regenerate_bitmap = false;

        let mut decoder = BitmapDecoder {
          width: self.width,
          height: self.height,
          color_space: self.color_space,
          file_content: None,
          original_url: None,
        };
        let decoded = decoder.compute(data)?;
        return decoder.resolve(decoded, self);
      }
    }

    // Check if this is an HTTP/HTTPS URL
    if let ImageSrcEnum::String(url_string) = data
      && is_http_url(url_string)
    {
      self.complete = true;
      self.width = -1.0;
      self.height = -1.0;
      self.natural_width = 0.0;
      self.natural_height = 0.0;
      self.bitmap = None;
      self.file_content = None;
      self._avif_image_ref = None;
      self.is_svg = false;
      self.need_regenerate_bitmap = false;

      return Err(PyValueError::new_err("Unsupported URL scheme"));
    }

    // For file path/URL
    self.complete = true;

    let mut decoder = BitmapDecoder {
      width: self.width,
      height: self.height,
      color_space: self.color_space,
      file_content: None,
      original_url: None,
    };
    let decoded = decoder.compute(data)?;
    decoder.resolve(decoded, self)
  }
}

impl Image {
  pub(crate) fn regenerate_bitmap_if_need(&mut self) -> PyResult<()> {
    if !self.need_regenerate_bitmap || !self.is_svg || self.src.is_none() {
      return Ok(());
    }

    if let Some(data) = self.file_content.as_deref() {
      let font = get_font().map_err(SkError::from)?;
      self.bitmap = Bitmap::from_svg_data_with_custom_size(
        data.as_ptr(),
        data.len(),
        self.width as f32,
        self.height as f32,
        self.color_space,
        &font,
      );
      self.need_regenerate_bitmap = false;
      return Ok(());
    }
    if let Some(data) = self.src.as_ref() {
      let font = get_font().map_err(SkError::from)?;
      self.bitmap = Bitmap::from_svg_data_with_custom_size(
        data.as_ref().as_ptr(),
        data.as_ref().len(),
        self.width as f32,
        self.height as f32,
        self.color_space,
        &font,
      );
      self.need_regenerate_bitmap = false;
    }
    Ok(())
  }
}

fn is_svg_image(data: &[u8], length: usize) -> bool {
  let mut is_svg = false;
  if length >= 11 {
    for i in 3..length {
      if '<' == data[i - 3] as char {
        match data[i - 2] as char {
          '?' | '!' => continue,
          's' => {
            is_svg = 'v' == data[i - 1] as char && 'g' == data[i] as char;
            break;
          }
          _ => {
            is_svg = false;
          }
        }
      }
    }
  }
  is_svg
}

fn is_http_url(s: &str) -> bool {
  s.starts_with("http://") || s.starts_with("https://")
}

pub(crate) struct DecodedBitmap {
  bitmap: DecodeStatus,
  width: f64,
  height: f64,
}

unsafe impl Send for DecodedBitmap {}

struct BitmapInfo {
  data: Bitmap,
  is_svg: bool,
  #[allow(dead_code)]
  decoded_image: Option<AvifImage>,
}

enum DecodeStatus {
  Ok(BitmapInfo),
  Empty,
  InvalidSvg,
  InvalidImage,
}

struct BitmapDecoder {
  width: f64,
  height: f64,
  color_space: ColorSpace,
  // data from file path
  file_content: Option<Vec<u8>>,
  #[allow(dead_code)]
  // Preserve original HTTP URL for currentSrc when data is downloaded bytes
  original_url: Option<String>,
}

impl BitmapDecoder {
  fn compute(&mut self, image_src: &ImageSrcEnum) -> PyResult<DecodedBitmap> {
    let data_ref = match image_src {
      ImageSrcEnum::Buffer(data) => Cow::Borrowed(data.as_ref()),
      ImageSrcEnum::String(path_or_svg) => {
        if path_or_svg.starts_with("data:") {
          Cow::Borrowed(path_or_svg.as_bytes())
        } else {
          match std::fs::read(path_or_svg) {
            Ok(file_content) => {
              self.file_content = Some(file_content);
              Cow::Borrowed(self.file_content.as_ref().unwrap().as_ref())
            }
            Err(io_err) => {
              return Err(PyRuntimeError::new_err(format!(
                "Failed to read {path_or_svg}: {io_err}"
              )));
            }
          }
        }
      }
    };
    let length = data_ref.len();
    let mut width = self.width;
    let mut height = self.height;
    let bitmap = if data_ref.as_ref().starts_with(b"data:") {
      let data_str = str::from_utf8(&data_ref)
        .map_err(|e| PyValueError::new_err(format!("Decode data url failed {e}")))?;
      if let Some(base64_str) = data_str.split(',').next_back() {
        let image_binary = STANDARD
          .decode_to_vec(base64_str)
          .map_err(|e| PyValueError::new_err(format!("Decode data url failed {e}")))?;
        if let Some(kind) = infer::get(&image_binary) {
          if kind.matcher_type() == infer::MatcherType::Image {
            DecodeStatus::Ok(BitmapInfo {
              data: Bitmap::from_buffer(image_binary.as_ptr().cast_mut(), image_binary.len()),
              is_svg: false,
              decoded_image: None,
            })
          } else {
            DecodeStatus::InvalidImage
          }
        } else {
          DecodeStatus::InvalidImage
        }
      } else {
        DecodeStatus::Empty
      }
    } else if libavif::is_avif(data_ref.as_ref()) {
      // Check AVIF first - infer::get() may not recognize AVIF format
      let avif_image = AvifImage::decode_from(data_ref.as_ref())
        .map_err(|e| PyValueError::new_err(format!("Decode avif image failed {e}")))?;

      let bitmap = Bitmap::from_image_data(
        avif_image.data,
        avif_image.width as usize,
        avif_image.height as usize,
        avif_image.row_bytes as usize,
        (avif_image.row_bytes * avif_image.height) as usize,
        ColorType::RGBA8888,
        AlphaType::Premultiplied,
      );
      DecodeStatus::Ok(BitmapInfo {
        data: bitmap,
        is_svg: false,
        decoded_image: Some(avif_image),
      })
    } else if if let Some(kind) = infer::get(&data_ref) {
      kind.matcher_type() == infer::MatcherType::Image
    } else {
      false
    } {
      // Other image formats detected by infer (PNG, JPEG, GIF, WebP, etc.)
      DecodeStatus::Ok(BitmapInfo {
        data: Bitmap::from_buffer(data_ref.as_ptr().cast_mut(), length),
        is_svg: false,
        decoded_image: None,
      })
    } else if is_svg_image(&data_ref, length) {
      let font = get_font().map_err(SkError::from)?;
      if (self.width - -1.0).abs() > f64::EPSILON && (self.height - -1.0).abs() > f64::EPSILON {
        if let Some(bitmap) = Bitmap::from_svg_data_with_custom_size(
          data_ref.as_ptr(),
          length,
          self.width as f32,
          self.height as f32,
          self.color_space,
          &font,
        ) {
          DecodeStatus::Ok(BitmapInfo {
            data: bitmap,
            is_svg: true,
            decoded_image: None,
          })
        } else {
          DecodeStatus::InvalidSvg
        }
      } else if let Some(bitmap) =
        Bitmap::from_svg_data(data_ref.as_ptr(), length, self.color_space, &font)
      {
        if let Ok(bitmap) = bitmap {
          DecodeStatus::Ok(BitmapInfo {
            data: bitmap,
            is_svg: true,
            decoded_image: None,
          })
        } else {
          DecodeStatus::InvalidSvg
        }
      } else {
        DecodeStatus::Empty
      }
    } else {
      DecodeStatus::InvalidImage
    };

    if let DecodeStatus::Ok(ref b) = bitmap {
      if (self.width - -1.0).abs() < f64::EPSILON
        || (self.width - b.data.0.width as f64).abs() > f64::EPSILON
      {
        width = b.data.0.width as f64;
      }
      if (self.height - -1.0).abs() < f64::EPSILON
        || (self.height - b.data.0.height as f64).abs() > f64::EPSILON
      {
        height = b.data.0.height as f64;
      }
    }
    Ok(DecodedBitmap {
      bitmap,
      width,
      height,
    })
  }

  fn resolve(&mut self, output: DecodedBitmap, self_mut: &mut Image) -> PyResult<()> {
    self_mut.complete = true;
    self_mut.bitmap = None;

    let mut err: Option<&str> = None;

    match output.bitmap {
      DecodeStatus::Ok(bitmap) => {
        // SUCCESS PATH: set dimensions, bitmap, currentSrc, file_content
        self_mut.width = output.width;
        self_mut.height = output.height;
        self_mut.natural_width = output.width;
        self_mut.natural_height = output.height;

        if let Some(data) = self.file_content.take() {
          self_mut.file_content = Some(data);
        }

        // Update current_src based on what was actually loaded
        self_mut.current_src = match &self_mut.src {
          Some(ImageSrcEnum::Buffer(_)) => Some(BYTES_SRC_REPR.to_string()),
          Some(ImageSrcEnum::String(s)) => Some(s.clone()),
          None => None,
        };
        self_mut.is_svg = bitmap.is_svg;
        self_mut.bitmap = Some(bitmap.data);
        self_mut._avif_image_ref = bitmap.decoded_image;
      }
      DecodeStatus::Empty => {}
      DecodeStatus::InvalidSvg => {
        // ERROR PATH: clear state like reject() does
        // Reset width/height to auto (-1.0) so getters return 0 (from natural_width/height)
        self_mut.width = -1.0;
        self_mut.height = -1.0;
        self_mut.natural_width = 0.0;
        self_mut.natural_height = 0.0;
        self_mut.file_content = None;
        self_mut._avif_image_ref = None;
        self_mut.is_svg = false;
        self_mut.need_regenerate_bitmap = false;
        err = Some("Invalid SVG image");
      }
      DecodeStatus::InvalidImage => {
        // ERROR PATH: clear state like reject() does
        // Reset width/height to auto (-1.0) so getters return 0 (from natural_width/height)
        self_mut.width = -1.0;
        self_mut.height = -1.0;
        self_mut.natural_width = 0.0;
        self_mut.natural_height = 0.0;
        self_mut.file_content = None;
        self_mut._avif_image_ref = None;
        self_mut.is_svg = false;
        self_mut.need_regenerate_bitmap = false;
        err = Some("Unsupported image type");
      }
    }

    if let Some(err_str) = err.take() {
      return Err(PyValueError::new_err(err_str));
    }

    Ok(())
  }
}
