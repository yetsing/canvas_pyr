use pyo3::{
  exceptions::PyValueError,
  prelude::*,
  types::{PyAny, PyMapping},
};

use crate::a_either::PyEither3;
use crate::sk::{
  FillType as SkFillType, Matrix as SkMatrix, Path as SkPath, PathOp as SkPathOp, SkiaString,
  StrokeCap as SkStrokeCap, StrokeJoin as SkStrokeJoin,
};

#[derive(FromPyObject)]
#[pyo3(from_item_all)]
pub struct Matrix {
  pub a: f64,
  pub b: f64,
  pub c: f64,
  pub d: f64,
  pub e: f64,
  pub f: f64,
}

#[pyclass(module = "canvas_pyr", from_py_object, eq, eq_int)]
#[derive(PartialEq, Clone)]
pub enum PathOp {
  Difference,        // subtract the op path from the first path
  Intersect,         // intersect the two paths
  Union,             // union (inclusive-or) the two paths
  Xor,               // exclusive-or the two paths
  ReverseDifference, // subtract the first path from the op path
}

impl From<PathOp> for SkPathOp {
  fn from(value: PathOp) -> Self {
    match value {
      PathOp::Difference => SkPathOp::Difference,
      PathOp::Intersect => SkPathOp::Intersect,
      PathOp::Union => SkPathOp::Union,
      PathOp::Xor => SkPathOp::Xor,
      PathOp::ReverseDifference => SkPathOp::ReverseDifference,
    }
  }
}

#[pyclass(module = "canvas_pyr", from_py_object, eq, eq_int)]
#[derive(PartialEq, Hash, Debug, Clone)]
pub enum FillType {
  Winding = 0,
  EvenOdd = 1,
  InverseWinding = 2,
  InverseEvenOdd = 3,
}

impl From<FillType> for SkFillType {
  fn from(value: FillType) -> Self {
    match value {
      FillType::Winding => SkFillType::Winding,
      FillType::EvenOdd => SkFillType::EvenOdd,
      FillType::InverseWinding => SkFillType::InverseWinding,
      FillType::InverseEvenOdd => SkFillType::InverseEvenOdd,
    }
  }
}

impl From<i32> for FillType {
  fn from(value: i32) -> Self {
    match value {
      0 => FillType::Winding,
      1 => FillType::EvenOdd,
      2 => FillType::InverseWinding,
      3 => FillType::InverseEvenOdd,
      _ => unreachable!(),
    }
  }
}

#[pyclass(module = "canvas_pyr", from_py_object, eq, eq_int)]
#[derive(PartialEq, Default, Clone)]
pub enum StrokeCap {
  #[default]
  Butt = 0,
  Round = 1,
  Square = 2,
}

impl From<StrokeCap> for SkStrokeCap {
  fn from(value: StrokeCap) -> Self {
    match value {
      StrokeCap::Butt => SkStrokeCap::Butt,
      StrokeCap::Round => SkStrokeCap::Round,
      StrokeCap::Square => SkStrokeCap::Square,
    }
  }
}

#[pyclass(module = "canvas_pyr", from_py_object, eq, eq_int)]
#[derive(PartialEq, Default, Clone)]
pub enum StrokeJoin {
  #[default]
  Miter = 0,
  Round = 1,
  Bevel = 2,
}

impl From<StrokeJoin> for SkStrokeJoin {
  fn from(value: StrokeJoin) -> Self {
    match value {
      StrokeJoin::Miter => SkStrokeJoin::Miter,
      StrokeJoin::Round => SkStrokeJoin::Round,
      StrokeJoin::Bevel => SkStrokeJoin::Bevel,
    }
  }
}

#[derive(Default)]
pub struct StrokeOptions {
  pub width: Option<f64>,
  pub miter_limit: Option<f64>,
  pub cap: Option<StrokeCap>,
  pub join: Option<StrokeJoin>,
}

impl FromPyObject<'_, '_> for StrokeOptions {
  type Error = PyErr;

  fn extract(obj: Borrowed<'_, '_, PyAny>) -> Result<Self, Self::Error> {
    let dict = obj.cast::<PyMapping>()?;
    let mut config = Self::default();
    if let Ok(value) = dict.get_item("width") {
      config.width = value.extract()?;
    }
    if let Ok(value) = dict.get_item("miterLimit") {
      config.miter_limit = value.extract()?;
    }
    if let Ok(value) = dict.get_item("cap") {
      config.cap = value.extract()?;
    }
    if let Ok(value) = dict.get_item("join") {
      config.join = value.extract()?;
    }

    Ok(config)
  }
}

#[pyclass(unsendable, module = "canvas_pyr", name = "Path2D")]
pub struct Path {
  pub(crate) inner: SkPath,
}

#[derive(FromPyObject)]
pub enum NewPathArg<'py> {
  A(String),
  B(PyRefMut<'py, Path>),
  C(Bound<'py, PyAny>),
}

#[pymethods]
#[allow(non_snake_case)]
impl Path {
  #[new]
  #[pyo3(signature = (path=None))]
  pub fn new(path: Option<NewPathArg>) -> PyResult<Self> {
    let inner = match &path {
      Some(NewPathArg::A(path)) => SkPath::from_svg_path(path)
        .ok_or_else(|| PyValueError::new_err("Create path from provided path string failed."))?,
      Some(NewPathArg::B(path)) => path.inner.clone(),
      Some(NewPathArg::C(c)) => {
        return Err(PyValueError::new_err(format!(
          "Create path from provided unknown value failed {}.",
          c.get_type(),
        )));
      }
      None => SkPath::new(),
    };
    Ok(Path { inner })
  }

  #[pyo3(name="addPath", signature = (sub_path, matrix=None))]
  pub fn add_path(&mut self, sub_path: &Path, matrix: Option<Matrix>) {
    let transform = matrix
      .map(|m| {
        SkMatrix::new(
          m.a as f32, m.c as f32, m.e as f32, m.b as f32, m.d as f32, m.f as f32,
        )
      })
      .unwrap_or_else(SkMatrix::identity);
    self.inner.add_path(&sub_path.inner, &transform);
  }

  #[pyo3(name = "closePath")]
  pub fn close_path(&mut self) {
    self.inner.close();
  }

  #[pyo3(name = "moveTo")]
  pub fn move_to(&mut self, x: f64, y: f64) {
    self.inner.move_to(x as f32, y as f32);
  }

  #[pyo3(name = "lineTo")]
  pub fn line_to(&mut self, x: f64, y: f64) {
    self.inner.line_to(x as f32, y as f32);
  }

  #[pyo3(name = "bezierCurveTo")]
  pub fn bezier_curve_to(&mut self, cp1x: f64, cp1y: f64, cp2x: f64, cp2y: f64, x: f64, y: f64) {
    self.inner.cubic_to(
      cp1x as f32,
      cp1y as f32,
      cp2x as f32,
      cp2y as f32,
      x as f32,
      y as f32,
    );
  }

  #[pyo3(name = "quadraticCurveTo")]
  pub fn quadratic_curve_to(&mut self, cpx: f64, cpy: f64, x: f64, y: f64) {
    self
      .inner
      .quad_to(cpx as f32, cpy as f32, x as f32, y as f32);
  }

  #[pyo3(name = "arc", signature = (x, y, radius, startAngle, endAngle, anticlockwise=None))]
  pub fn arc(
    &mut self,
    x: f64,
    y: f64,
    radius: f64,
    startAngle: f64,
    endAngle: f64,
    anticlockwise: Option<bool>,
  ) {
    self.inner.arc(
      x as f32,
      y as f32,
      radius as f32,
      startAngle as f32,
      endAngle as f32,
      anticlockwise.unwrap_or(false),
    );
  }

  #[pyo3(name = "arcTo")]
  pub fn arc_to(&mut self, x1: f64, y1: f64, x2: f64, y2: f64, radius: f64) {
    self
      .inner
      .arc_to_tangent(x1 as f32, y1 as f32, x2 as f32, y2 as f32, radius as f32);
  }

  #[pyo3(name = "ellipse", signature = (x, y, radiusX, radiusY, rotation, startAngle, endAngle, anticlockwise=None))]
  pub fn ellipse(
    &mut self,
    x: f64,
    y: f64,
    radiusX: f64,
    radiusY: f64,
    rotation: f64,
    startAngle: f64,
    endAngle: f64,
    anticlockwise: Option<bool>,
  ) {
    self.inner.ellipse(
      x as f32,
      y as f32,
      radiusX as f32,
      radiusY as f32,
      rotation as f32,
      startAngle as f32,
      endAngle as f32,
      anticlockwise.unwrap_or(false),
    );
  }

  #[pyo3(name = "rect")]
  pub fn rect(&mut self, x: f64, y: f64, width: f64, height: f64) {
    self
      .inner
      .add_rect(x as f32, y as f32, width as f32, height as f32);
  }

  #[pyo3(name = "roundRect")]
  pub fn round_rect(
    &mut self,
    x: f64,
    y: f64,
    width: f64,
    height: f64,
    radii: PyEither3<f64, Vec<f64>, Bound<'_, PyAny>>,
  ) {
    let radii_array: [f32; 4] = match radii {
      PyEither3::A(radii) => [radii as f32; 4],
      PyEither3::B(radii_vec) => match radii_vec.len() {
        0 => [0f32; 4],
        1 => [radii_vec[0] as f32; 4],
        2 => [
          radii_vec[0] as f32,
          radii_vec[1] as f32,
          radii_vec[0] as f32,
          radii_vec[1] as f32,
        ],
        3 => [
          radii_vec[0] as f32,
          radii_vec[1] as f32,
          radii_vec[1] as f32,
          radii_vec[2] as f32,
        ],
        _ => [
          radii_vec[0] as f32,
          radii_vec[1] as f32,
          radii_vec[2] as f32,
          radii_vec[3] as f32,
        ],
      },
      PyEither3::C(_) => [0f32; 4],
    };
    self
      .inner
      .round_rect(x as f32, y as f32, width as f32, height as f32, radii_array);
  }

  pub fn op<'a>(mut slf: PyRefMut<'a, Self>, other: &Path, op: PathOp) -> PyRefMut<'a, Self> {
    slf.inner.op(&other.inner, op.into());
    slf
  }

  #[pyo3(name = "toSVGString")]
  pub fn to_svg_string(&self) -> SkiaString {
    self.inner.to_svg_string()
  }

  pub fn simplify(mut slf: PyRefMut<'_, Self>) -> PyRefMut<'_, Self> {
    slf.inner.simplify();
    slf
  }

  #[pyo3(name = "setFillType")]
  pub fn set_fill_type(&mut self, fill_type: FillType) {
    self.inner.set_fill_type(fill_type.into());
  }

  #[pyo3(name = "getFillType")]
  pub fn get_fill_type(&mut self) -> FillType {
    self.inner.get_fill_type().into()
  }

  #[pyo3(name = "getFillTypeString")]
  pub fn get_fill_type_string(&mut self) -> String {
    match self.get_fill_type() {
      FillType::EvenOdd => "evenodd".to_owned(),
      _ => "nonzero".to_owned(),
    }
  }

  #[pyo3(name = "asWinding")]
  pub fn as_winding(mut slf: PyRefMut<'_, Self>) -> PyRefMut<'_, Self> {
    slf.inner.as_winding();
    slf
  }

  #[pyo3(name="stroke", signature = (options=None))]
  pub fn stroke(mut slf: PyRefMut<'_, Self>, options: Option<StrokeOptions>) -> PyRefMut<'_, Self> {
    let options = options.unwrap_or_default();
    slf.inner.stroke(
      options.cap.unwrap_or_default().into(),
      options.join.unwrap_or_default().into(),
      options.width.unwrap_or(1.0) as f32,
      options.miter_limit.unwrap_or(4.0) as f32,
    );
    slf
  }

  #[pyo3(name = "computeTightBounds")]
  pub fn compute_tight_bounds(&self) -> Vec<f64> {
    let ltrb = self.inner.compute_tight_bounds();
    vec![ltrb.0 as f64, ltrb.1 as f64, ltrb.2 as f64, ltrb.3 as f64]
  }

  #[pyo3(name = "getBounds")]
  pub fn get_bounds(&self) -> (f64, f64, f64, f64) {
    let ltrb = self.inner.get_bounds();
    (ltrb.0 as f64, ltrb.1 as f64, ltrb.2 as f64, ltrb.3 as f64)
  }

  #[pyo3(name = "transform")]
  pub fn transform(mut slf: PyRefMut<'_, Self>, matrix: Matrix) -> PyRefMut<'_, Self> {
    let trans = SkMatrix::new(
      matrix.a as f32,
      matrix.c as f32,
      matrix.e as f32,
      matrix.b as f32,
      matrix.d as f32,
      matrix.f as f32,
    );
    slf.inner.transform_self(&trans);
    slf
  }

  #[pyo3(name = "trim", signature = (start, end, is_complement=None))]
  pub fn trim(
    mut slf: PyRefMut<'_, Self>,
    start: f64,
    end: f64,
    is_complement: Option<bool>,
  ) -> PyRefMut<'_, Self> {
    slf
      .inner
      .trim(start as f32, end as f32, is_complement.unwrap_or(false));
    slf
  }

  #[pyo3(name = "dash")]
  pub fn dash(mut slf: PyRefMut<'_, Self>, on: f64, off: f64, phase: f64) -> PyRefMut<'_, Self> {
    slf.inner.dash(on as f32, off as f32, phase as f32);
    slf
  }

  pub fn equals(&self, other: &Path) -> bool {
    self.inner == other.inner
  }

  pub fn round(mut slf: PyRefMut<'_, Self>, radius: f64) -> PyRefMut<'_, Self> {
    slf.inner.round(radius as f32);
    slf
  }

  #[pyo3(name = "isPointInPath", signature = (x, y, fillType=None))]
  pub fn is_point_in_path(&self, x: f64, y: f64, fillType: Option<FillType>) -> bool {
    self.inner.hit_test(
      x as f32,
      y as f32,
      fillType.unwrap_or(FillType::Winding).into(),
    )
  }
}

fn skia_to_rust_string(s: &SkiaString) -> String {
  if s.ptr.is_null() || s.length == 0 {
    return String::new();
  }
  // 把 ptr,length 当作字节切片读取（保证合法性是调用者/FFI 的责任）
  let bytes = unsafe { std::slice::from_raw_parts(s.ptr as *const u8, s.length) };
  match str::from_utf8(bytes) {
    Ok(valid) => valid.to_owned(),
    Err(_) => String::from_utf8_lossy(bytes).into_owned(),
  }
}

impl<'py> IntoPyObject<'py> for SkiaString {
  type Target = PyAny;
  type Output = Bound<'py, Self::Target>;
  type Error = std::convert::Infallible;

  fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
    let rust_string = skia_to_rust_string(&self);
    Ok(rust_string.into_pyobject(py)?.into_any())
  }
}
