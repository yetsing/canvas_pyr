use pyo3::{exceptions::PyValueError, prelude::*, types::PyBytes, types::PyString};

use crate::{error::SkError, global_fonts::get_font, sk::sk_svg_text_to_path};

#[pyfunction]
#[pyo3(name = "convertSVGTextToPath")]
pub fn convert_svg_text_to_path<'py>(
  py: Python<'py>,
  input: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyBytes>> {
  let font = get_font().map_err(SkError::from)?;
  let input = if let Ok(bytes) = input.cast::<PyBytes>() {
    bytes.as_bytes()
  } else if let Ok(s) = input.cast::<PyString>() {
    s.to_str()?.as_bytes()
  } else {
    return Err(PyValueError::new_err("data must be bytes or str"));
  };
  sk_svg_text_to_path(input, &font)
    .ok_or_else(|| PyValueError::new_err("Convert svg text to path failed"))
    .map(|v| unsafe { PyBytes::from_ptr(py, v.0.ptr, v.0.size) })
}
