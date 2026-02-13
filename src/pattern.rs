use std::result::Result as StdResult;
use std::sync::{Arc, OnceLock};

use cssparser::{Parser, ParserInput};
use cssparser_color::{Color as CSSColor, hsl_to_rgb};
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use rgb::RGBA;

use crate::a_either::{PyEither, PyEither4};
use crate::a_geometry::DOMMatrix;
use crate::ctx::{Context, TransformObject};
use crate::error::SkError;
use crate::gradient::Gradient;
use crate::image::{Image, ImageData};
use crate::sk::{AlphaType, Bitmap, ColorType, ImagePattern, Surface, TileMode, Transform};
use crate::{CanvasElement, SVGCanvas};

#[derive(Debug)]
pub enum Pattern {
  #[allow(dead_code)]
  Color(RGBA<u8>, String),
  Gradient(Gradient),
  Image(ImagePattern),
}

impl Clone for Pattern {
  fn clone(&self) -> Self {
    match self {
      Pattern::Color(rgba, s) => Pattern::Color(*rgba, s.clone()),
      Pattern::Gradient(g) => Pattern::Gradient(g.clone()),
      Pattern::Image(img) => Pattern::Image(img.clone()),
    }
  }
}

impl Default for Pattern {
  fn default() -> Self {
    Self::Color(RGBA::new(0, 0, 0, 255), "#000000".to_owned())
  }
}

impl Pattern {
  pub fn from_color(color_str: &str) -> StdResult<Self, SkError> {
    let mut parser_input = ParserInput::new(color_str);
    let mut parser = Parser::new(&mut parser_input);
    let color = CSSColor::parse(&mut parser)
      .map_err(|e| SkError::Generic(format!("Parse color [{color_str}] error: {e:?}")))?;
    match color {
      CSSColor::CurrentColor => Err(SkError::Generic(
        "Color should not be `currentcolor` keyword".to_owned(),
      )),
      CSSColor::Rgba(rgba) => Ok(Pattern::Color(
        RGBA {
          r: rgba.red,
          g: rgba.green,
          b: rgba.blue,
          a: (rgba.alpha * 255.0) as u8,
        },
        color_str.to_owned(),
      )),
      CSSColor::Hsl(hsl) => {
        let h = hsl.hue.unwrap_or(0.0) / 360.0;
        let s = hsl.saturation.unwrap_or(0.0);
        let l = hsl.lightness.unwrap_or(0.0);
        let a = hsl.alpha.unwrap_or(1.0);

        let (r, g, b) = hsl_to_rgb(h, s, l);

        Ok(Pattern::Color(
          RGBA {
            r: (r * 255.0) as u8,
            g: (g * 255.0) as u8,
            b: (b * 255.0) as u8,
            a: (a * 255.0) as u8,
          },
          color_str.to_owned(),
        ))
      }
      _ => Err(SkError::Generic("Unsupported color format".to_owned())),
    }
  }
}

#[pyclass(unsendable, module = "canvas_pyr")]
pub struct CanvasPattern {
  pub(crate) inner: Pattern,
  #[allow(unused)]
  // hold it for Drop
  bitmap: Option<Arc<Bitmap>>,
  #[allow(unused)]
  // hold cloned surface for Drop
  surface: Option<Surface>,
}

impl CanvasPattern {
  pub fn new1(
    py: Python,
    input: PyEither4<
      PyRefMut<Image>,
      PyRefMut<ImageData>,
      PyRefMut<CanvasElement>,
      PyRefMut<SVGCanvas>,
    >,
    repetition: Option<String>,
    context: Option<&mut Context>,
  ) -> PyResult<Self> {
    let mut inner_bitmap = None;
    let mut inner_surface = None;
    let mut is_canvas = false;
    let bitmap = match input {
      PyEither4::A(mut image) => image
        .bitmap
        .as_mut()
        .map(|b| b.0.bitmap)
        .ok_or_else(|| PyValueError::new_err("Image is not completed."))?,
      PyEither4::B(image_data) => {
        let image_data_size = image_data.width * image_data.height * 4;
        let bitmap = Bitmap::from_image_data(
          image_data.data(),
          image_data.width,
          image_data.height,
          image_data.width * 4,
          image_data_size,
          ColorType::RGBA8888,
          AlphaType::Unpremultiplied,
        );
        let ptr = bitmap.0.bitmap;
        inner_bitmap = Some(Arc::new(bitmap));
        ptr
      }
      PyEither4::C(canvas) => {
        let context = match context {
          Some(c) => c,
          None => &mut canvas.ctx.borrow_mut(py).context,
        };
        // Flush deferred rendering before accessing the surface
        context.flush();
        // Clone the surface to capture its current state and prevent segfaults
        // when the original canvas is resized or destroyed
        let cloned_surface = context
          .surface
          .try_clone(context.color_space)
          .ok_or_else(|| PyRuntimeError::new_err("Failed to clone canvas surface"))?;
        // Get the bitmap pointer from the cloned surface
        let ptr = cloned_surface.get_bitmap_ptr();
        // Store the cloned surface to keep it alive
        inner_surface = Some(cloned_surface);
        is_canvas = true; // Keep as true since it's a surface pointer
        ptr
      }
      PyEither4::D(svg_canvas) => {
        let context = match context {
          Some(c) => c,
          None => &mut svg_canvas.ctx.borrow_mut(py).context,
        };
        // Clone the surface to capture its current state and prevent segfaults
        // when the original canvas is resized or destroyed
        let cloned_surface = context
          .surface
          .try_clone(context.color_space)
          .ok_or_else(|| PyRuntimeError::new_err("Failed to clone SVG canvas surface"))?;
        // Get the bitmap pointer from the cloned surface
        let ptr = cloned_surface.get_bitmap_ptr();
        // Store the cloned surface to keep it alive
        inner_surface = Some(cloned_surface);
        is_canvas = true; // Keep as true since it's a surface pointer
        ptr
      }
    };
    let (repeat_x, repeat_y) = match repetition {
      None => (TileMode::Repeat, TileMode::Repeat),
      Some(repetition) => match repetition.as_str() {
        "" | "repeat" => (TileMode::Repeat, TileMode::Repeat),
        "repeat-x" => (TileMode::Repeat, TileMode::Decal),
        "repeat-y" => (TileMode::Decal, TileMode::Repeat),
        "no-repeat" => (TileMode::Decal, TileMode::Decal),
        _ => {
          return Err(PyValueError::new_err(format!(
            "{repetition} is not valid repetition rule"
          )));
        }
      },
    };
    Ok(Self {
      inner: Pattern::Image(ImagePattern {
        transform: Transform::default(),
        bitmap,
        repeat_x,
        repeat_y,
        is_canvas,
        shader_cache: OnceLock::new(),
      }),
      bitmap: inner_bitmap,
      surface: inner_surface,
    })
  }
}

#[pymethods]
impl CanvasPattern {
  #[new]
  #[pyo3(signature = (input, repetition=None))]
  pub fn new(
    py: Python,
    input: PyEither4<
      PyRefMut<Image>,
      PyRefMut<ImageData>,
      PyRefMut<CanvasElement>,
      PyRefMut<SVGCanvas>,
    >,
    repetition: Option<String>,
  ) -> PyResult<Self> {
    Self::new1(py, input, repetition, None)
  }

  #[pyo3(name = "setTransform")]
  pub fn set_transform(&mut self, transform: PyEither<TransformObject, PyRef<DOMMatrix>>) {
    if let Pattern::Image(image) = &mut self.inner {
      image.transform = match transform {
        PyEither::A(transform) => transform.into(),
        PyEither::B(matrix) => matrix.into(),
      };
    }
  }
}
