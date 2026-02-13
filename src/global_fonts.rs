use std::env;
use std::fs::read_dir;
use std::path::{self, PathBuf};
use std::sync::{LazyLock, LockResult, Mutex, MutexGuard, OnceLock, PoisonError};

use pyo3::prelude::*;

use crate::sk::*;

#[cfg(target_os = "windows")]
const FONT_PATH: &str = "C:/Windows/Fonts";
#[cfg(target_os = "macos")]
const FONT_PATH: &str = "/System/Library/Fonts/";
#[cfg(target_os = "linux")]
const FONT_PATH: &str = "/usr/share/fonts/";
#[cfg(target_os = "android")]
const FONT_PATH: &str = "/system/fonts";

static FONT_DIR: OnceLock<PyResult<u32>> = OnceLock::new();

pub(crate) static GLOBAL_FONT_COLLECTION: LazyLock<Mutex<FontCollection>> =
  LazyLock::new(|| Mutex::new(FontCollection::new()));

#[inline]
pub(crate) fn get_font<'a>() -> LockResult<MutexGuard<'a, FontCollection>> {
  GLOBAL_FONT_COLLECTION.lock()
}

#[inline]
fn into_pyo3_error<E>(err: PoisonError<MutexGuard<'_, E>>) -> pyo3::PyErr {
  pyo3::exceptions::PyRuntimeError::new_err(format!("{err}"))
}

#[pyclass(module = "canvas_pyr", get_all, skip_from_py_object)]
#[derive(Clone, Debug, Serialize)]
pub struct PyFontStyles {
  pub weight: i32,
  pub width: String,
  pub style: String,
}

#[pyclass(module = "canvas_pyr", get_all)]
#[derive(Debug, Serialize)]
pub struct PyFontStyleSet {
  pub family: String,
  pub styles: Vec<PyFontStyles>,
}

#[pymethods]
impl PyFontStyleSet {
  pub fn __str__(&self) -> String {
    serde_json::to_string(self)
      .unwrap_or_else(|_| format!("FontStyleSet {{ family: {}, styles: [...] }}", self.family))
  }

  pub fn __repr__(&self) -> String {
    self.__str__()
  }
}

#[pyclass(from_py_object, module = "canvas_pyr", get_all)]
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct FontKey {
  #[pyo3(name = "typefaceId")]
  pub typeface_id: u32,
}

#[pymodule(name = "GlobalFonts")]
#[allow(non_snake_case)]
pub mod global_fonts {
  use pyo3::{exceptions::PyRuntimeError, prelude::*};

  use super::{
    FONT_DIR, FONT_PATH, FontKey, PyFontStyleSet, PyFontStyles, get_font, into_pyo3_error,
  };

  #[pyfunction]
  #[pyo3(signature = (font, nameAlias=None))]
  pub fn register(font: &[u8], nameAlias: Option<String>) -> PyResult<Option<FontKey>> {
    let maybe_name_alias = nameAlias.and_then(|s| if s.is_empty() { None } else { Some(s) });
    let font_ = get_font().map_err(into_pyo3_error)?;
    Ok(
      font_
        .register(font, maybe_name_alias)
        .map(|typeface_id| FontKey { typeface_id }),
    )
  }

  /// Register a font from a file path.
  ///
  /// Fonts registered via path are deduplicated by the path string itself, not by file contents.
  /// This means:
  /// - Registering the same path multiple times returns the existing registration
  /// - If the font file is modified on disk and `registerFromPath` is called again,
  ///   the new contents will NOT be loaded - it returns the existing registration
  ///
  /// This behavior is intentional to prevent memory waste from duplicate registrations.
  ///
  /// ## Hot-reload workaround
  ///
  /// To reload a font after modifying the file on disk:
  /// 1. Call `GlobalFonts.remove(fontKey)` with the key from the original registration
  /// 2. Call `GlobalFonts.registerFromPath()` again to register the updated font
  ///
  /// Note: The `register()` function (buffer-based) deduplicates by content hash,
  /// so it will detect when font data has changed.
  // TODO: Do file extensions in font_path need to be converted to lowercase?
  // Windows and macOS are case-insensitive, Linux is not.
  // See: https://github.com/Brooooooklyn/canvas/actions/runs/5893418006/job/15985737723
  #[pyfunction]
  #[pyo3(name = "registerFromPath", signature = (fontPath, nameAlias=None))]
  pub fn register_from_path(
    fontPath: String,
    nameAlias: Option<String>,
  ) -> PyResult<Option<FontKey>> {
    let maybe_name_alias = nameAlias.and_then(|s| if s.is_empty() { None } else { Some(s) });
    let font = get_font().map_err(into_pyo3_error)?;
    Ok(
      font
        .register_from_path(fontPath.as_str(), maybe_name_alias)
        .map(|typeface_id| FontKey { typeface_id }),
    )
  }

  #[pyfunction]
  pub fn has(name: String) -> PyResult<bool> {
    let font = get_font().map_err(into_pyo3_error)?;
    let families = font.get_families();
    Ok(families.iter().any(|f| f.family == name))
  }

  // #[pyfunction]
  // #[pyo3(name = "getFamilies")]
  // pub fn get_families() -> PyResult<Vec<u8>> {
  //   let font = get_font().map_err(into_pyo3_error)?;
  //   serde_json::to_vec(&font.get_families())
  //     .map_err(|e| PyRuntimeError::new_err(format!("Failed to serialize font families: {e}")))
  // }

  #[pyfunction]
  #[pyo3(name = "getFamilies")]
  pub fn get_families() -> PyResult<Vec<PyFontStyleSet>> {
    let font = get_font().map_err(into_pyo3_error)?;
    let ret = font
      .get_families()
      .into_iter()
      .map(|f| PyFontStyleSet {
        family: f.family,
        styles: f
          .styles
          .into_iter()
          .map(|s| PyFontStyles {
            weight: s.weight,
            width: s.width,
            style: s.style,
          })
          .collect(),
      })
      .collect::<Vec<PyFontStyleSet>>();
    Ok(ret)
  }

  pub fn load_system_fonts() -> PyResult<u32> {
    FONT_DIR
      .get_or_init(move || super::load_fonts_from_dir(FONT_PATH))
      .as_ref()
      .map(|s| *s)
      .map_err(PyRuntimeError::new_err)
  }

  #[pyfunction]
  #[pyo3(name = "loadFontsFromDir")]
  pub fn load_fonts_from_dir(dir: String) -> PyResult<u32> {
    super::load_fonts_from_dir(dir.as_str())
  }

  #[pyfunction]
  #[pyo3(name = "setAlias", signature = (fontName, alias))]
  pub fn set_alias(fontName: String, alias: String) -> PyResult<bool> {
    let font = get_font().map_err(into_pyo3_error)?;
    Ok(font.set_alias(fontName.as_str(), alias.as_str()))
  }

  /// Remove a previously registered font from the global font collection.
  /// Returns true if the font was successfully removed, false if it was not found.
  #[pyfunction]
  pub fn remove(key: &FontKey) -> PyResult<bool> {
    let font = get_font().map_err(into_pyo3_error)?;
    Ok(font.unregister(key.typeface_id))
  }

  #[pyfunction]
  #[pyo3(name = "removeBatch")]
  /// Remove multiple fonts by their keys in a single operation.
  /// More efficient than calling remove() multiple times as it triggers only one rebuild.
  /// Returns the number of fonts successfully removed.
  pub fn remove_batch(font_keys: Vec<FontKey>) -> PyResult<u32> {
    let typeface_ids: Vec<u32> = font_keys.iter().map(|k| k.typeface_id).collect();
    let font = get_font().map_err(into_pyo3_error)?;
    Ok(font.unregister_batch(&typeface_ids) as u32)
  }

  #[pyfunction]
  #[pyo3(name = "removeAll")]
  /// Remove ALL registered fonts in a single operation.
  /// Returns the number of fonts removed.
  pub fn remove_all() -> PyResult<u32> {
    let font = get_font().map_err(into_pyo3_error)?;
    Ok(font.unregister_all() as u32)
  }

  #[pyclass(from_py_object, get_all)]
  #[derive(Debug, Clone)]
  pub struct FontVariationAxis {
    pub tag: u32,
    pub value: f64,
    pub min: f64,
    pub max: f64,
    #[pyo3(name = "def_")]
    pub def: f64,
    pub hidden: bool,
  }

  #[pyfunction]
  #[pyo3(name = "getVariationAxes")]
  pub fn get_variation_axes(
    familyName: String,
    weight: i32,
    width: i32,
    slant: i32,
  ) -> PyResult<Vec<FontVariationAxis>> {
    let font = get_font().map_err(into_pyo3_error)?;
    let axes = font.get_variation_axes(&familyName, weight, width, slant);
    Ok(
      axes
        .into_iter()
        .map(|axis| FontVariationAxis {
          tag: axis.tag,
          value: axis.value as f64,
          min: axis.min as f64,
          max: axis.max as f64,
          def: axis.def as f64,
          hidden: axis.hidden,
        })
        .collect(),
    )
  }

  #[pyfunction]
  #[pyo3(name = "hasVariations")]
  pub fn has_variations(familyName: String, weight: i32, width: i32, slant: i32) -> PyResult<bool> {
    let font = get_font().map_err(into_pyo3_error)?;
    Ok(font.has_variations(&familyName, weight, width, slant))
  }
}

fn load_fonts_from_dir<P: AsRef<path::Path>>(dir: P) -> PyResult<u32> {
  let mut count = 0u32;
  if let Ok(dir) = read_dir(dir) {
    for f in dir.flatten() {
      if let Ok(meta) = f.metadata() {
        if meta.is_dir() {
          load_fonts_from_dir(f.path())?;
        } else {
          let p = f.path();
          // The font file extensions are case-insensitive.
          let ext = p
            .extension()
            .and_then(|s| s.to_str())
            .map(|s| s.to_ascii_lowercase());

          match ext.as_deref() {
            Some("ttf") | Some("ttc") | Some("otf") | Some("pfb") | Some("woff2")
            | Some("woff") => {
              if let Some(p) = p.into_os_string().to_str() {
                let font_collection = get_font().map_err(into_pyo3_error)?;
                if font_collection
                  .register_from_path::<String>(p, None)
                  .is_some()
                {
                  count += 1;
                }
              }
            }
            _ => {}
          }
        }
      }
    }
  }
  Ok(count)
}

fn home_dir() -> Option<PathBuf> {
  env::var_os("HOME")
    .or_else(|| env::var_os("USERPROFILE"))
    .map(PathBuf::from)
}

fn load_fonts_and_log<P: AsRef<path::Path>>(dir: P) {
  if let Err(e) = load_fonts_from_dir(dir.as_ref()) {
    eprintln!("Failed to load fonts from {}: {e}", dir.as_ref().display());
  }
}

pub fn init_fonts() {
  // Preload system fonts on startup to avoid latency on first use.
  // The GlobalFonts module provides a Python API to load additional fonts on demand.
  if env::var_os("DISABLE_SYSTEM_FONTS_LOAD").is_some() {
    return;
  }

  if let Err(e) = global_fonts::load_system_fonts() {
    eprintln!("Failed to load system fonts: {e}");
  }

  #[cfg(target_os = "windows")]
  {
    if let Some(local_app_data) = env::var_os("LOCALAPPDATA") {
      let dir = PathBuf::from(local_app_data)
        .join("Microsoft")
        .join("Windows")
        .join("Fonts");
      load_fonts_and_log(dir);
    }
  }

  #[cfg(target_os = "macos")]
  {
    if let Some(home) = home_dir() {
      load_fonts_and_log(home.join("Library").join("Fonts"));
    }
  }

  #[cfg(target_os = "linux")]
  {
    load_fonts_and_log("/usr/local/share/fonts");
    if let Some(home) = home_dir() {
      load_fonts_and_log(home.join(".fonts"));
    }
  }
}
