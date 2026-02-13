#!/bin/bash

set -euo pipefail

rustup install
rustup target add x86_64-unknown-linux-gnu
maturin build -i "/usr/bin/python${python_version}" --target x86_64-unknown-linux-gnu --release --out dist --compatibility pypi
