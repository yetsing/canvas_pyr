//! Rust port of https://github.com/Brooooooklyn/canvas/blob/main/geometry.js

use std::{collections::HashMap, f64::consts::PI};

use pyo3::exceptions::{PyNotImplementedError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyType;

use crate::a_either::PyEither;
use crate::sk::Transform;

const M11: usize = 0;
const M12: usize = 1;
const M13: usize = 2;
const M14: usize = 3;
const M21: usize = 4;
const M22: usize = 5;
const M23: usize = 6;
const M24: usize = 7;
const M31: usize = 8;
const M32: usize = 9;
const M33: usize = 10;
const M34: usize = 11;
const M41: usize = 12;
const M42: usize = 13;
const M43: usize = 14;
const M44: usize = 15;

const A: usize = M11;
const B: usize = M12;
const C: usize = M21;
const D: usize = M22;
const E: usize = M41;
const F: usize = M42;

const DEG_PER_RAD: f64 = 180.0 / PI;
const RAD_PER_DEG: f64 = PI / 180.0;

#[pyclass(from_py_object)]
#[derive(Clone, Copy, Debug, Default)]
pub struct DOMPoint {
  #[pyo3(get, set)]
  pub x: f64,
  #[pyo3(get, set)]
  pub y: f64,
  #[pyo3(get, set)]
  pub z: f64,
  #[pyo3(get, set)]
  pub w: f64,
}

impl DOMPoint {
  pub fn new(x: f64, y: f64, z: f64, w: f64) -> Self {
    Self { x, y, z, w }
  }
}

#[pymethods]
impl DOMPoint {
  #[new]
  #[pyo3(signature = (x=0.0, y=0.0, z=0.0, w=1.0))]
  pub fn new1(x: Option<f64>, y: Option<f64>, z: Option<f64>, w: Option<f64>) -> Self {
    Self {
      x: x.unwrap_or(0.0),
      y: y.unwrap_or(0.0),
      z: z.unwrap_or(0.0),
      w: w.unwrap_or(1.0),
    }
  }

  #[classmethod]
  #[pyo3(name = "fromPoint")]
  pub fn from_point(_cls: &Bound<'_, PyType>, other: &DOMPoint) -> PyResult<Self> {
    Ok(Self {
      x: other.x,
      y: other.y,
      z: other.z,
      w: other.w,
    })
  }

  #[pyo3(name = "matrixTransform")]
  pub fn matrix_transform(&self, matrix: &DOMMatrix) -> Self {
    if matrix.is_2d && self.z == 0.0 && self.w == 1.0 {
      Self::new(
        self.x * matrix.values[A] + self.y * matrix.values[C] + matrix.values[E],
        self.x * matrix.values[B] + self.y * matrix.values[D] + matrix.values[F],
        0.0,
        1.0,
      )
    } else {
      let v = &matrix.values;
      Self::new(
        self.x * v[M11] + self.y * v[M21] + self.z * v[M31] + self.w * v[M41],
        self.x * v[M12] + self.y * v[M22] + self.z * v[M32] + self.w * v[M42],
        self.x * v[M13] + self.y * v[M23] + self.z * v[M33] + self.w * v[M43],
        self.x * v[M14] + self.y * v[M24] + self.z * v[M34] + self.w * v[M44],
      )
    }
  }

  #[pyo3(name = "toJSON")]
  pub fn _to_json(&self) -> HashMap<String, f64> {
    let mut map = HashMap::new();
    map.insert("x".to_string(), self.x);
    map.insert("y".to_string(), self.y);
    map.insert("z".to_string(), self.z);
    map.insert("w".to_string(), self.w);
    map
  }

  pub fn __str__(&self) -> String {
    format!(
      r#"DOMPoint(x={}, y={}, z={}, w={})"#,
      self.x, self.y, self.z, self.w
    )
  }

  pub fn __eq__(&self, other: &DOMPoint) -> bool {
    self.x == other.x && self.y == other.y && self.z == other.z && self.w == other.w
  }
}

#[pyclass(from_py_object)]
#[derive(Clone, Copy, Debug, Default)]
pub struct DOMRect {
  #[pyo3(get, set)]
  pub x: f64,
  #[pyo3(get, set)]
  pub y: f64,
  #[pyo3(get, set)]
  pub width: f64,
  #[pyo3(get, set)]
  pub height: f64,
}

#[pymethods]
impl DOMRect {
  #[new]
  #[pyo3(signature = (x=0.0, y=0.0, width=0.0, height=0.0))]
  pub fn new(x: Option<f64>, y: Option<f64>, width: Option<f64>, height: Option<f64>) -> Self {
    Self {
      x: x.unwrap_or(0.0),
      y: y.unwrap_or(0.0),
      width: width.unwrap_or(0.0),
      height: height.unwrap_or(0.0),
    }
  }

  #[classmethod]
  #[pyo3(name = "fromRect")]
  pub fn from_rect(_cls: &Bound<'_, PyType>, other: &DOMRect) -> PyResult<Self> {
    Ok(Self {
      x: other.x,
      y: other.y,
      width: other.width,
      height: other.height,
    })
  }

  #[getter]
  pub fn top(&self) -> f64 {
    self.y
  }

  #[getter]
  pub fn left(&self) -> f64 {
    self.x
  }

  #[getter]
  pub fn right(&self) -> f64 {
    self.x + self.width
  }

  #[getter]
  pub fn bottom(&self) -> f64 {
    self.y + self.height
  }

  #[pyo3(name = "toJSON")]
  pub fn _to_json(&self) -> HashMap<String, f64> {
    let mut map = HashMap::new();
    map.insert("x".to_string(), self.x);
    map.insert("y".to_string(), self.y);
    map.insert("width".to_string(), self.width);
    map.insert("height".to_string(), self.height);
    map.insert("top".to_string(), self.top());
    map.insert("left".to_string(), self.left());
    map.insert("right".to_string(), self.right());
    map.insert("bottom".to_string(), self.bottom());
    map
  }

  pub fn __str__(&self) -> String {
    format!(
      r#"DOMRect(x={},y={},width={},height={},top={},left={},right={},bottom={})"#,
      self.x,
      self.y,
      self.width,
      self.height,
      self.top(),
      self.left(),
      self.right(),
      self.bottom()
    )
  }

  pub fn __eq__(&self, other: &DOMRect) -> bool {
    self.x == other.x
      && self.y == other.y
      && self.width == other.width
      && self.height == other.height
  }
}

#[pyclass(from_py_object)]
#[derive(Clone, Debug)]
pub struct DOMMatrix {
  values: [f64; 16],
  pub is_2d: bool,
}

impl DOMMatrix {
  pub(crate) fn xinto_context_transform(&self) -> Transform {
    Transform::new(
      self.get_a() as f32,
      self.get_c() as f32,
      self.get_e() as f32,
      self.get_b() as f32,
      self.get_d() as f32,
      self.get_f() as f32,
    )
  }
}

impl From<&DOMMatrix> for Transform {
  fn from(value: &DOMMatrix) -> Self {
    Self::new(
      value.get_a() as f32,
      value.get_b() as f32,
      value.get_c() as f32,
      value.get_d() as f32,
      value.get_e() as f32,
      value.get_f() as f32,
    )
  }
}

impl From<PyRef<'_, DOMMatrix>> for Transform {
  fn from(value: PyRef<'_, DOMMatrix>) -> Self {
    Self::new(
      value.get_a() as f32,
      value.get_b() as f32,
      value.get_c() as f32,
      value.get_d() as f32,
      value.get_e() as f32,
      value.get_f() as f32,
    )
  }
}

impl From<Transform> for DOMMatrix {
  fn from(value: Transform) -> Self {
    DOMMatrix::from_values6([
      value.a as f64,
      value.b as f64,
      value.c as f64,
      value.d as f64,
      value.e as f64,
      value.f as f64,
    ])
  }
}

impl DOMMatrix {
  pub fn identity() -> Self {
    let values = [
      1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0,
    ];
    Self {
      values,
      is_2d: true,
    }
  }

  pub fn from_values6(values6: [f64; 6]) -> Self {
    let mut m = DOMMatrix::identity();
    m.values[A] = values6[0];
    m.values[B] = values6[1];
    m.values[C] = values6[2];
    m.values[D] = values6[3];
    m.values[E] = values6[4];
    m.values[F] = values6[5];
    m.is_2d = true;
    m
  }

  pub fn from_values16(values16: [f64; 16]) -> Self {
    let is_2d = is_2d_from_values(&values16);
    Self {
      values: values16,
      is_2d,
    }
  }

  pub fn from_css(transform_list: &str) -> Result<Self, String> {
    if transform_list.trim().is_empty() {
      return Ok(DOMMatrix::identity());
    }
    let mut transforms: Vec<[f64; 16]> = Vec::new();
    for seg in transform_list.splitn(20, ')') {
      let seg = seg.trim();
      if seg.is_empty() {
        continue;
      }
      let t = format!("{})", seg);
      transforms.push(parse_transform(&t)?);
    }
    if transforms.is_empty() {
      return Ok(DOMMatrix::identity());
    }
    let mut acc = transforms[0];
    for item in transforms.iter().skip(1) {
      acc = multiply(item, &acc);
    }
    Ok(DOMMatrix::from_values16(acc))
  }

  pub fn from_values(values: Vec<f64>) -> Result<Self, String> {
    if values.len() == 6 {
      let mut arr = [0.0f64; 6];
      arr.copy_from_slice(&values[..6]);
      Ok(Self::from_values6(arr))
    } else if values.len() == 16 {
      let mut arr = [0.0f64; 16];
      arr.copy_from_slice(&values[..16]);
      Ok(Self::from_values16(arr))
    } else {
      Err(format!("Expected 6 or 16 values, got {}", values.len()))
    }
  }

  pub fn invert_self(&mut self) -> Result<(), String> {
    if self.is_2d {
      let det = self.values[A] * self.values[D] - self.values[B] * self.values[C];

      // Invertable
      if det != 0.0 {
        let new_a = self.values[D] / det;
        let new_b = -self.values[B] / det;
        let new_c = -self.values[C] / det;
        let new_d = self.values[A] / det;
        let new_e = (self.values[C] * self.values[F] - self.values[D] * self.values[E]) / det;
        let new_f = (self.values[B] * self.values[E] - self.values[A] * self.values[F]) / det;
        self.values[A] = new_a;
        self.values[B] = new_b;
        self.values[C] = new_c;
        self.values[D] = new_d;
        self.values[E] = new_e;
        self.values[F] = new_f;
        return Ok(());
      }
      self.is_2d = false;
      self.values = [f64::NAN; 16];
      return Ok(());
    }
    Err("3D matrix inversion not implemented".to_string())
  }

  pub fn multiply_self(&mut self, other: &DOMMatrix) {
    self.values = multiply(&other.values, &self.values);
    if !other.is_2d {
      self.is_2d = false;
    }
  }
  pub fn pre_multiply_self(&mut self, other: &DOMMatrix) {
    self.values = multiply(&self.values, &other.values);
    if !other.is_2d {
      self.is_2d = false;
    }
  }

  pub fn rotate_axis_angle_self(&mut self, mut x: f64, mut y: f64, mut z: f64, mut angle: f64) {
    let length = (x * x + y * y + z * z).sqrt();
    if length == 0.0 {
      return;
    }
    if length != 1.0 {
      x /= length;
      y /= length;
      z /= length;
    }
    angle *= RAD_PER_DEG;

    let c = angle.cos();
    let s = angle.sin();
    let t = 1.0 - c;
    let tx = t * x;
    let ty = t * y;

    let m = [
      tx * x + c,
      tx * y + s * z,
      tx * z - s * y,
      0.0,
      tx * y - s * z,
      ty * y + c,
      ty * z + s * x,
      0.0,
      tx * z + s * y,
      ty * z - s * x,
      t * z * z + c,
      0.0,
      0.0,
      0.0,
      0.0,
      1.0,
    ];
    self.values = multiply(&m, &self.values);
    if x != 0.0 || y != 0.0 {
      self.is_2d = false;
    }
  }

  pub fn rotate_from_vector_self(&mut self, x: f64, y: f64) {
    let theta = if x == 0.0 && y == 0.0 {
      0.0
    } else {
      y.atan2(x) * DEG_PER_RAD
    };
    self.rotate_self(theta, None, None);
  }

  pub fn rotate_self(&mut self, mut rx: f64, mut ry: Option<f64>, mut rz: Option<f64>) {
    if ry.is_none() && rz.is_none() {
      rz = Some(rx);
      rx = 0.0;
      ry = Some(0.0);
    }
    let mut ry = ry.unwrap_or(0.0);
    let mut rz = rz.unwrap_or(0.0);

    if rx != 0.0 || ry != 0.0 {
      self.is_2d = false;
    }

    rx *= RAD_PER_DEG;
    ry *= RAD_PER_DEG;
    rz *= RAD_PER_DEG;

    let (mut c, mut s) = (rz.cos(), rz.sin());
    let rzs = [
      c, s, 0.0, 0.0, -s, c, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0,
    ];
    self.values = multiply(&rzs, &self.values);

    c = ry.cos();
    s = ry.sin();
    let rys = [
      c, 0.0, -s, 0.0, 0.0, 1.0, 0.0, 0.0, s, 0.0, c, 0.0, 0.0, 0.0, 0.0, 1.0,
    ];
    self.values = multiply(&rys, &self.values);

    c = rx.cos();
    s = rx.sin();
    let rxs = [
      1.0, 0.0, 0.0, 0.0, 0.0, c, s, 0.0, 0.0, -s, c, 0.0, 0.0, 0.0, 0.0, 1.0,
    ];
    self.values = multiply(&rxs, &self.values);
  }

  pub fn scale_self(
    &mut self,
    scale_x: Option<f64>,
    scale_y: Option<f64>,
    scale_z: Option<f64>,
    origin_x: Option<f64>,
    origin_y: Option<f64>,
    origin_z: Option<f64>,
  ) {
    let ox = origin_x.unwrap_or(0.0);
    let oy = origin_y.unwrap_or(0.0);
    let oz = origin_z.unwrap_or(0.0);

    self.translate_self(ox, oy, oz);

    let sx = scale_x.unwrap_or(1.0);
    let sy = scale_y.unwrap_or(sx);
    let sz = scale_z.unwrap_or(1.0);

    let s = [
      sx, 0.0, 0.0, 0.0, 0.0, sy, 0.0, 0.0, 0.0, 0.0, sz, 0.0, 0.0, 0.0, 0.0, 1.0,
    ];
    self.values = multiply(&s, &self.values);

    self.translate_self(-ox, -oy, -oz);

    if sz != 1.0 || oz != 0.0 {
      self.is_2d = false;
    }
  }

  pub fn skew_x_self(&mut self, sx: Option<f64>) {
    let sx = match sx {
      Some(s) => s,
      None => return,
    };
    let t = (sx * RAD_PER_DEG).tan();
    let m = [
      1.0, 0.0, 0.0, 0.0, t, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0,
    ];
    self.values = multiply(&m, &self.values);
  }

  pub fn skew_y_self(&mut self, sy: Option<f64>) {
    let sy = match sy {
      Some(s) => s,
      None => return,
    };
    let t = (sy * RAD_PER_DEG).tan();
    let m = [
      1.0, t, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0,
    ];
    self.values = multiply(&m, &self.values);
  }

  pub fn translate_self(&mut self, tx: f64, ty: f64, tz: f64) {
    let t = [
      1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, tx, ty, tz, 1.0,
    ];
    self.values = multiply(&t, &self.values);
    if tz != 0.0 {
      self.is_2d = false;
    }
  }
}

#[pymethods]
#[allow(non_snake_case)]
impl DOMMatrix {
  #[getter]
  pub fn get_a(&self) -> f64 {
    self.values[A]
  }

  #[setter]
  pub fn set_a(&mut self, value: f64) {
    self.values[A] = value;
  }

  #[getter]
  pub fn get_b(&self) -> f64 {
    self.values[B]
  }

  #[setter]
  pub fn set_b(&mut self, value: f64) {
    self.values[B] = value;
  }

  #[getter]
  pub fn get_c(&self) -> f64 {
    self.values[C]
  }

  #[setter]
  pub fn set_c(&mut self, value: f64) {
    self.values[C] = value;
  }

  #[getter]
  pub fn get_d(&self) -> f64 {
    self.values[D]
  }

  #[setter]
  pub fn set_d(&mut self, value: f64) {
    self.values[D] = value;
  }

  #[getter]
  pub fn get_e(&self) -> f64 {
    self.values[E]
  }

  #[setter]
  pub fn set_e(&mut self, value: f64) {
    self.values[E] = value;
  }

  #[getter]
  pub fn get_f(&self) -> f64 {
    self.values[F]
  }

  #[setter]
  pub fn set_f(&mut self, value: f64) {
    self.values[F] = value;
  }

  #[getter]
  pub fn get_m11(&self) -> f64 {
    self.values[M11]
  }
  #[setter]
  pub fn set_m11(&mut self, value: f64) {
    self.values[M11] = value;
  }

  #[getter]
  pub fn get_m12(&self) -> f64 {
    self.values[M12]
  }
  #[setter]
  pub fn set_m12(&mut self, value: f64) {
    self.values[M12] = value;
  }

  #[getter]
  pub fn get_m13(&self) -> f64 {
    self.values[M13]
  }
  #[setter]
  pub fn set_m13(&mut self, value: f64) {
    self.values[M13] = value;
    self.is_2d = is_2d_from_values(&self.values);
  }

  #[getter]
  pub fn get_m14(&self) -> f64 {
    self.values[M14]
  }
  #[setter]
  pub fn set_m14(&mut self, value: f64) {
    self.values[M14] = value;
    self.is_2d = is_2d_from_values(&self.values);
  }

  #[getter]
  pub fn get_m21(&self) -> f64 {
    self.values[M21]
  }
  #[setter]
  pub fn set_m21(&mut self, value: f64) {
    self.values[M21] = value;
  }

  #[getter]
  pub fn get_m22(&self) -> f64 {
    self.values[M22]
  }
  #[setter]
  pub fn set_m22(&mut self, value: f64) {
    self.values[M22] = value;
  }

  #[getter]
  pub fn get_m23(&self) -> f64 {
    self.values[M23]
  }
  #[setter]
  pub fn set_m23(&mut self, value: f64) {
    self.values[M23] = value;
    self.is_2d = is_2d_from_values(&self.values);
  }

  #[getter]
  pub fn get_m24(&self) -> f64 {
    self.values[M24]
  }
  #[setter]
  pub fn set_m24(&mut self, value: f64) {
    self.values[M24] = value;
    self.is_2d = is_2d_from_values(&self.values);
  }

  #[getter]
  pub fn get_m31(&self) -> f64 {
    self.values[M31]
  }
  #[setter]
  pub fn set_m31(&mut self, value: f64) {
    self.values[M31] = value;
    self.is_2d = is_2d_from_values(&self.values);
  }

  #[getter]
  pub fn get_m32(&self) -> f64 {
    self.values[M32]
  }
  #[setter]
  pub fn set_m32(&mut self, value: f64) {
    self.values[M32] = value;
    self.is_2d = is_2d_from_values(&self.values);
  }

  #[getter]
  pub fn get_m33(&self) -> f64 {
    self.values[M33]
  }
  #[setter]
  pub fn set_m33(&mut self, value: f64) {
    self.values[M33] = value;
    self.is_2d = is_2d_from_values(&self.values);
  }

  #[getter]
  pub fn get_m34(&self) -> f64 {
    self.values[M34]
  }
  #[setter]
  pub fn set_m34(&mut self, value: f64) {
    self.values[M34] = value;
    self.is_2d = is_2d_from_values(&self.values);
  }

  #[getter]
  pub fn get_m41(&self) -> f64 {
    self.values[M41]
  }
  #[setter]
  pub fn set_m41(&mut self, value: f64) {
    self.values[M41] = value;
  }

  #[getter]
  pub fn get_m42(&self) -> f64 {
    self.values[M42]
  }
  #[setter]
  pub fn set_m42(&mut self, value: f64) {
    self.values[M42] = value;
  }

  #[getter]
  pub fn get_m43(&self) -> f64 {
    self.values[M43]
  }
  #[setter]
  pub fn set_m43(&mut self, value: f64) {
    self.values[M43] = value;
    self.is_2d = is_2d_from_values(&self.values);
  }

  #[getter]
  pub fn get_m44(&self) -> f64 {
    self.values[M44]
  }
  #[setter]
  pub fn set_m44(&mut self, value: f64) {
    self.values[M44] = value;
    self.is_2d = is_2d_from_values(&self.values);
  }

  #[getter(is2D)]
  pub fn is_2d(&self) -> bool {
    self.is_2d
  }

  #[getter(isIdentity)]
  pub fn get_is_identity(&self) -> bool {
    let v = &self.values;
    v[M11] == 1.0
      && v[M12] == 0.0
      && v[M13] == 0.0
      && v[M14] == 0.0
      && v[M21] == 0.0
      && v[M22] == 1.0
      && v[M23] == 0.0
      && v[M24] == 0.0
      && v[M31] == 0.0
      && v[M32] == 0.0
      && v[M33] == 1.0
      && v[M34] == 0.0
      && v[M41] == 0.0
      && v[M42] == 0.0
      && v[M43] == 0.0
      && v[M44] == 1.0
  }

  #[new]
  #[pyo3(signature=(init = None))]
  fn new(init: Option<PyEither<String, Vec<f64>>>) -> PyResult<Self> {
    let init = match init {
      Some(i) => i,
      None => return Ok(Self::identity()),
    };
    match init {
      PyEither::A(s) => Self::from_css(&s).map_err(PyValueError::new_err),
      PyEither::B(values) => Self::from_values(values).map_err(PyValueError::new_err),
    }
  }

  #[classmethod]
  #[pyo3(name = "fromFloatArray")]
  pub fn from_float_array(_cls: &Bound<'_, PyType>, array: Vec<f64>) -> PyResult<Self> {
    Self::from_values(array).map_err(PyValueError::new_err)
  }

  #[classmethod]
  #[pyo3(name = "fromMatrix")]
  pub fn from_matrix(_cls: &Bound<'_, PyType>, other: &DOMMatrix) -> PyResult<Self> {
    Ok(Self::from_values16(other.values))
  }

  pub fn multiply(&self, other: &DOMMatrix) -> DOMMatrix {
    let mut ins = self.clone();
    ins.multiply_self(other);
    ins
  }

  pub fn multiplySelf<'a>(mut self_: PyRefMut<'a, Self>, other: &DOMMatrix) -> PyRefMut<'a, Self> {
    self_.multiply_self(other);
    self_
  }

  pub fn preMultiplySelf<'a>(
    mut self_: PyRefMut<'a, Self>,
    other: &DOMMatrix,
  ) -> PyRefMut<'a, Self> {
    self_.pre_multiply_self(other);
    self_
  }

  #[pyo3(signature=(tx=0.0, ty=0.0, tz=0.0))]
  pub fn translate(&self, tx: f64, ty: f64, tz: f64) -> DOMMatrix {
    let mut ins = self.clone();
    ins.translate_self(tx, ty, tz);
    ins
  }

  #[pyo3(name = "translateSelf")]
  pub fn translateSelf<'a>(
    mut self_: PyRefMut<'a, Self>,
    tx: f64,
    ty: f64,
    tz: f64,
  ) -> PyRefMut<'a, Self> {
    let t = [
      1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, tx, ty, tz, 1.0,
    ];
    self_.values = multiply(&t, &self_.values);
    if tz != 0.0 {
      self_.is_2d = false;
    }
    self_
  }

  #[pyo3(name = "scale", signature=(sx=None, sy=None, sz=None, ox=None, oy=None, oz=None))]
  pub fn scale(
    &self,
    sx: Option<f64>,
    sy: Option<f64>,
    sz: Option<f64>,
    ox: Option<f64>,
    oy: Option<f64>,
    oz: Option<f64>,
  ) -> Self {
    let mut ins = self.clone();
    ins.scale_self(sx, sy, sz, ox, oy, oz);
    ins
  }

  #[pyo3(name = "scaleSelf", signature=(scaleX=None, scaleY=None, scaleZ=None, originX=None, originY=None, originZ=None))]
  pub fn scaleSelf(
    mut self_: PyRefMut<Self>,
    scaleX: Option<f64>,
    scaleY: Option<f64>,
    scaleZ: Option<f64>,
    originX: Option<f64>,
    originY: Option<f64>,
    originZ: Option<f64>,
  ) -> PyRefMut<Self> {
    self_.scale_self(scaleX, scaleY, scaleZ, originX, originY, originZ);
    self_
  }

  #[pyo3(name = "scale3d", signature=(scale=None, originX=None, originY=None, originZ=None))]
  pub fn scale3d(
    &mut self,
    scale: Option<f64>,
    originX: Option<f64>,
    originY: Option<f64>,
    originZ: Option<f64>,
  ) -> Self {
    let mut ins = self.clone();
    ins.scale_self(scale, scale, scale, originX, originY, originZ);
    ins
  }

  #[pyo3(name = "scale3dSelf", signature=(scale=None, originX=None, originY=None, originZ=None))]
  pub fn scale3dSelf(
    mut self_: PyRefMut<Self>,
    scale: Option<f64>,
    originX: Option<f64>,
    originY: Option<f64>,
    originZ: Option<f64>,
  ) -> PyRefMut<Self> {
    self_.scale_self(scale, scale, scale, originX, originY, originZ);
    self_
  }

  #[pyo3(name = "rotate", signature=(rotX, rotY=None, rotZ=None))]
  pub fn rotate(&self, rotX: f64, rotY: Option<f64>, rotZ: Option<f64>) -> Self {
    let mut ins = self.clone();
    ins.rotate_self(rotX, rotY, rotZ);
    ins
  }

  #[pyo3(name = "rotateSelf", signature=(rotX, rotY=None, rotZ=None))]
  pub fn rotateSelf(
    mut self_: PyRefMut<Self>,
    rotX: f64,
    rotY: Option<f64>,
    rotZ: Option<f64>,
  ) -> PyRefMut<Self> {
    self_.rotate_self(rotX, rotY, rotZ);
    self_
  }

  #[pyo3(name = "rotateFromVector", signature=(x=0.0, y=0.0))]
  pub fn rotate_from_vector(&self, x: f64, y: f64) -> DOMMatrix {
    let mut ins = self.clone();
    ins.rotate_from_vector_self(x, y);
    ins
  }

  #[pyo3(name = "rotateFromVectorSelf", signature=(x=0.0, y=0.0))]
  pub fn rotateFromVectorSelf(mut self_: PyRefMut<Self>, x: f64, y: f64) -> PyRefMut<Self> {
    self_.rotate_from_vector_self(x, y);
    self_
  }

  #[pyo3(name = "rotateAxisAngle", signature=(x=0.0, y=0.0, z=0.0, angle=0.0))]
  pub fn rotate_axis_angle(&self, x: f64, y: f64, z: f64, angle: f64) -> Self {
    let mut ins = self.clone();
    ins.rotate_axis_angle_self(x, y, z, angle);
    ins
  }

  #[pyo3(name = "rotateAxisAngleSelf", signature=(x=0.0, y=0.0, z=0.0, angle=0.0))]
  pub fn rotateAxisAngleSelf<'a>(
    mut self_: PyRefMut<'a, Self>,
    x: f64,
    y: f64,
    z: f64,
    angle: f64,
  ) -> PyRefMut<'a, Self> {
    self_.rotate_axis_angle_self(x, y, z, angle);
    self_
  }

  #[pyo3(name = "skewX", signature=(sx=None))]
  pub fn skewX(&self, sx: Option<f64>) -> Self {
    let mut ins = self.clone();
    ins.skew_x_self(sx);
    ins
  }

  #[pyo3(name = "skewXSelf", signature=(sx=None))]
  pub fn skewXSelf<'a>(mut self_: PyRefMut<'a, Self>, sx: Option<f64>) -> PyRefMut<'a, Self> {
    self_.skew_x_self(sx);
    self_
  }

  #[pyo3(name = "skewY", signature=(sy=None))]
  pub fn skewY(&self, sy: Option<f64>) -> Self {
    let mut ins = self.clone();
    ins.skew_y_self(sy);
    ins
  }

  #[pyo3(name = "skewYSelf", signature=(sy=None))]
  pub fn skewYSelf<'a>(mut self_: PyRefMut<'a, Self>, sy: Option<f64>) -> PyRefMut<'a, Self> {
    self_.skew_y_self(sy);
    self_
  }

  #[pyo3(name = "flipX")]
  pub fn flip_x(&self) -> DOMMatrix {
    let m = [
      -1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0,
    ];
    DOMMatrix::from_values16(multiply(&m, &self.values))
  }

  #[pyo3(name = "flipY")]
  pub fn flip_y(&self) -> DOMMatrix {
    let m = [
      1.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0,
    ];
    DOMMatrix::from_values16(multiply(&m, &self.values))
  }

  pub fn inverse(&self) -> PyResult<Self> {
    let mut ins = self.clone();
    ins.invert_self().map_err(PyNotImplementedError::new_err)?;
    Ok(ins)
  }

  pub fn invertSelf(mut self_: PyRefMut<Self>) -> PyResult<PyRefMut<Self>> {
    self_
      .invert_self()
      .map_err(PyNotImplementedError::new_err)?;
    Ok(self_)
  }

  #[pyo3(name = "setMatrixValue")]
  pub fn set_matrix_value<'a>(
    mut self_: PyRefMut<'a, Self>,
    transformList: &str,
  ) -> PyResult<PyRefMut<'a, Self>> {
    let temp = DOMMatrix::from_css(transformList).map_err(PyValueError::new_err)?;
    self_.values = temp.values;
    self_.is_2d = temp.is_2d;
    Ok(self_)
  }

  #[pyo3(name = "transformPoint", signature=(point=None))]
  pub fn transform_point(&self, point: Option<&DOMPoint>) -> DOMPoint {
    let (x, y, z, w) = match point {
      Some(p) => (p.x, p.y, p.z, p.w),
      None => (0.0, 0.0, 0.0, 1.0),
    };

    let v = &self.values;
    let nx = v[M11] * x + v[M21] * y + v[M31] * z + v[M41] * w;
    let ny = v[M12] * x + v[M22] * y + v[M32] * z + v[M42] * w;
    let nz = v[M13] * x + v[M23] * y + v[M33] * z + v[M43] * w;
    let nw = v[M14] * x + v[M24] * y + v[M34] * z + v[M44] * w;

    DOMPoint::new(nx, ny, nz, nw)
  }

  #[pyo3(name = "toFloatArray")]
  pub fn _to_float_array(&self) -> Vec<f64> {
    self.values.to_vec()
  }

  #[pyo3(name = "toJSON")]
  pub fn _to_json(&self) -> HashMap<String, f64> {
    let mut map = HashMap::new();
    map.insert("a".to_string(), self.values[A]);
    map.insert("b".to_string(), self.values[B]);
    map.insert("c".to_string(), self.values[C]);
    map.insert("d".to_string(), self.values[D]);
    map.insert("e".to_string(), self.values[E]);
    map.insert("f".to_string(), self.values[F]);
    for i in 0..16 {
      map.insert(format!("m{}", (i / 4) * 10 + (i % 4)), self.values[i]);
    }
    map.insert("is2D".to_string(), if self.is_2d { 1.0 } else { 0.0 });
    map.insert(
      "isIdentity".to_string(),
      if self.get_is_identity() { 1.0 } else { 0.0 },
    );
    map
  }

  pub fn __eq__(&self, other: &DOMMatrix) -> bool {
    self.values == other.values && self.is_2d == other.is_2d
  }

  pub fn __str__(&self) -> String {
    if self.is_2d {
      format!(
        "matrix({}, {}, {}, {}, {}, {})",
        self.values[A],
        self.values[B],
        self.values[C],
        self.values[D],
        self.values[E],
        self.values[F]
      )
    } else {
      let list: Vec<String> = self.values.iter().map(|v| v.to_string()).collect();
      format!("matrix3d({})", list.join(", "))
    }
  }
}

fn is_2d_from_values(values: &[f64; 16]) -> bool {
  values[M13] == 0.0
    && values[M14] == 0.0
    && values[M23] == 0.0
    && values[M24] == 0.0
    && values[M31] == 0.0
    && values[M32] == 0.0
    && values[M33] == 1.0
    && values[M34] == 0.0
    && values[M43] == 0.0
    && values[M44] == 1.0
}

fn multiply(first: &[f64; 16], second: &[f64; 16]) -> [f64; 16] {
  let mut dest = [0.0f64; 16];
  for i in 0..4 {
    for j in 0..4 {
      let mut sum = 0.0;
      for k in 0..4 {
        sum += first[i * 4 + k] * second[k * 4 + j];
      }
      dest[i * 4 + j] = sum;
    }
  }
  dest
}

fn parse_matrix(input: &str) -> Result<[f64; 16], String> {
  let inner = input
    .trim()
    .strip_prefix("matrix(")
    .and_then(|s| s.strip_suffix(')'))
    .ok_or_else(|| format!("Failed to parse {}", input))?;
  let parts: Vec<f64> = inner
    .split(',')
    .map(|v| v.trim().parse::<f64>())
    .collect::<Result<Vec<_>, _>>()
    .map_err(|_| format!("Failed to parse {}", input))?;
  if parts.len() != 6 {
    return Err(format!("Failed to parse {}", input));
  }
  Ok([
    parts[0], parts[1], 0.0, 0.0, parts[2], parts[3], 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, parts[4],
    parts[5], 0.0, 1.0,
  ])
}

fn parse_matrix3d(input: &str) -> Result<[f64; 16], String> {
  let inner = input
    .trim()
    .strip_prefix("matrix3d(")
    .and_then(|s| s.strip_suffix(')'))
    .ok_or_else(|| format!("Failed to parse {}", input))?;
  let parts: Vec<f64> = inner
    .split(',')
    .map(|v| v.trim().parse::<f64>())
    .collect::<Result<Vec<_>, _>>()
    .map_err(|_| format!("Failed to parse {}", input))?;
  if parts.len() != 16 {
    return Err(format!("Failed to parse {}", input));
  }
  let mut out = [0.0f64; 16];
  out.copy_from_slice(&parts[..16]);
  Ok(out)
}

fn parse_transform(input: &str) -> Result<[f64; 16], String> {
  if input.starts_with("matrix3d(") {
    parse_matrix3d(input)
  } else if input.starts_with("matrix(") {
    parse_matrix(input)
  } else {
    Err(format!("{} parsing not implemented", input))
  }
}
