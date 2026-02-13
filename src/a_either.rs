//! 对 [napi Either](https://docs.rs/napi/latest/napi/enum.Either.html) 的拙劣模仿

use pyo3::prelude::*;

#[derive(FromPyObject)]
pub enum PyEither<A, B> {
  A(A),
  B(B),
}

#[derive(FromPyObject)]
pub enum PyEither3<A, B, C> {
  A(A),
  B(B),
  C(C),
}

#[derive(FromPyObject)]
pub enum PyEither4<A, B, C, D> {
  A(A),
  B(B),
  C(C),
  D(D),
}
