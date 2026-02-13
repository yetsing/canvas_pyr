import functools
import gc
import sys
import statistics
import time
import tracemalloc
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar, Dict, List

import psutil

import canvas_pyr

T = TypeVar("T")
KB = 1024
MB = KB * 1024
GB = MB * 1024
script_dir = Path(__file__).resolve().parent


# region Helper functions


def _get_rss() -> int:
    """Return current process RSS in bytes. Uses psutil if available, else resource."""
    return psutil.Process().memory_info().rss


def _sample_rss(samples: int = 5, delay: float = 0.02) -> int:
    values = []
    for _ in range(samples):
        values.append(_get_rss())
        time.sleep(delay)
    return int(statistics.median(values))


def check_memory_leak(
    warmup: int = 3,
    repeats: int = 5,
    threshold_bytes: int = 1024 * 50,
    collect: bool = True,
    rss_samples: int = 5,
    rss_delay: float = 0.02,
    gc_interval: int = 100,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for tests: runs the function `repeats` times and fails if
    net memory growth exceeds `threshold_bytes`.
    """

    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            for _ in range(warmup):
                fn(*args, **kwargs)
            if collect:
                gc.collect()
                time.sleep(0.1)
            before_garbage_count = len(gc.garbage)
            before_rss = _sample_rss(rss_samples, rss_delay)
            tracemalloc.start()
            start_current, _ = tracemalloc.get_traced_memory()
            result: Optional[T] = None
            for i in range(repeats):
                result = fn(*args, **kwargs)
                if collect and i % gc_interval == 0:
                    gc.collect()
            if collect:
                gc.collect()
                time.sleep(0.1)
            end_current, _ = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            after_rss = _sample_rss(rss_samples, rss_delay)
            tracemalloc_leak = end_current - start_current
            after_garbage_count = len(gc.garbage)
            if tracemalloc_leak > threshold_bytes:
                raise AssertionError(
                    f"Possible memory leak: +{tracemalloc_leak} bytes (garbage {after_garbage_count - before_garbage_count}) (threshold {threshold_bytes}, repeats: {repeats})\n"
                )
            leak = after_rss - before_rss
            if leak > threshold_bytes:
                raise AssertionError(
                    f"Possible memory leak (RSS): +{leak} bytes (garbage {after_garbage_count - before_garbage_count}, tracemalloc {tracemalloc_leak}) (threshold {threshold_bytes}, repeats: {repeats})\n"
                )
            return result  # type: ignore[return-value]

        return wrapper

    return decorator


checker_center: Dict[str, Callable[..., Any]] = {}


def register(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to register a memory checker function under a given name."""

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        checker_center[name] = fn
        return fn

    return decorator


def _test_path(*names: str) -> Path:
    return script_dir / "canvas_upstream" / "__test__" / Path(*names)


# endregion


# region Checkers


@register("create_canvas")
@check_memory_leak(repeats=200_000, threshold_bytes=4 * MB)
def check_create_canvas():
    canvas_pyr.createCanvas(512, 512)


@register("create_svg_canvas")
@check_memory_leak(repeats=200_000, threshold_bytes=4 * MB)
def check_create_svg_canvas():
    for flag in [
        canvas_pyr.SvgExportFlag.ConvertTextToPaths,
        canvas_pyr.SvgExportFlag.NoPrettyXML,
        canvas_pyr.SvgExportFlag.RelativePathEncoding,
    ]:
        canvas_pyr.createCanvas(512, 512, flag)


@register("resize_canvas")
@check_memory_leak(repeats=10, threshold_bytes=4 * MB)
def check_resize_canvas():
    canvas = canvas_pyr.createCanvas(512, 512)
    for i in range(1000):
        canvas.width = max(512 - i, 32)
        canvas.height = max(512 - i, 32)


@register("resize_canvas2")
@check_memory_leak(repeats=10, threshold_bytes=4 * MB)
def check_resize_canvas2():
    canvas = canvas_pyr.createCanvas(128, 512)
    for i in range(1000):
        canvas.width = 128 + i
        canvas.height = 512 + i


@register("resize_canvas3")
@check_memory_leak(repeats=10, threshold_bytes=4 * MB)
def check_resize_canvas3():
    canvas = canvas_pyr.createCanvas(512, 128)
    for i in range(1000):
        canvas.width = 512 + (i % 10)
        canvas.height = 128 + (i % 30)


@register("resize_svg_canvas")
@check_memory_leak(repeats=10, threshold_bytes=4 * MB)
def check_resize_svg_canvas():
    for flag in [
        canvas_pyr.SvgExportFlag.ConvertTextToPaths,
        canvas_pyr.SvgExportFlag.NoPrettyXML,
        canvas_pyr.SvgExportFlag.RelativePathEncoding,
    ]:
        canvas = canvas_pyr.createCanvas(512, 512, flag)
        for i in range(1000):
            canvas.width = 512 + (i % 16)
            canvas.height = 128 + (i % 32)


@register("draw_emoji")
@check_memory_leak(repeats=1000, threshold_bytes=4 * MB)
def check_draw_emoji():
    canvas_pyr.GlobalFonts.registerFromPath(
        str(_test_path("fonts", "AppleColorEmoji.ttf")), "Apple Color Emoji"
    )
    canvas_pyr.GlobalFonts.registerFromPath(
        str(_test_path("fonts", "COLR-v1.ttf")), "COLRv1"
    )

    canvas = canvas_pyr.createCanvas(760, 360)
    ctx = canvas.getContext("2d")

    ctx.font = "50px Apple Color Emoji"
    ctx.fillText("😀😃😄😁😆😅😂🤣☺️😊😊😇", 50, 150)

    ctx.font = "100px COLRv1"
    ctx.fillText("abc", 50, 300)

    b = canvas.encode("png")

    script_dir.joinpath("draw-emoji.png").write_bytes(b)


@register("draw_text")
@check_memory_leak(repeats=3000, threshold_bytes=5 * MB, gc_interval=500)
def check_draw_text():
    font_data = _test_path("fonts", "iosevka-slab-regular.ttf").read_bytes()
    woff_font_path = _test_path("fonts", "Virgil.woff2")

    assert woff_font_path.exists(), f"Font file not found: {woff_font_path}"
    assert _test_path(
        "fonts", "iosevka-slab-regular.ttf"
    ).exists(), (
        f"Font file not found: {_test_path('fonts', 'iosevka-slab-regular.ttf')}"
    )

    canvas_pyr.GlobalFonts.register(font_data)
    canvas_pyr.GlobalFonts.registerFromPath(str(woff_font_path), "Virgil")
    canvas_pyr.GlobalFonts.getFamilies()

    canvas = canvas_pyr.createCanvas(1024, 768)
    ctx = canvas.getContext("2d")
    ctx.fillStyle = "yellow"
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    ctx.strokeStyle = "black"
    ctx.lineWidth = 3
    ctx.font = "50px Iosevka Slab"
    ctx.strokeText("skr canvas", 50, 150)
    gradient = ctx.createConicGradient(0, 100, 100)

    # Add five color stops
    gradient.addColorStop(0, "red")
    gradient.addColorStop(0.15, "orange")
    gradient.addColorStop(0.25, "yellow")
    gradient.addColorStop(0.35, "orange")
    gradient.addColorStop(0.5, "green")
    gradient.addColorStop(0.75, "cyan")
    gradient.addColorStop(1, "blue")

    # Set the fill style and draw a rectangle
    ctx.strokeStyle = gradient
    ctx.strokeText("@napi-rs/canvas", 50, 300)

    b = canvas.encode("png")
    script_dir.joinpath("draw-text.png").write_bytes(b)


# endregion


# region Runner


def _run_checker_by_name(name: str):
    try:
        checker_center[name]()
        return (name, True, "")
    except AssertionError as e:
        return (name, False, str(e))
    except Exception as e:
        return (name, False, f"Unexpected error: {e}")


def run(names: List[str]) -> int:
    import multiprocessing as mp

    fails = []
    start = time.time()
    with mp.Pool(processes=1) as pool:
        results = pool.map(_run_checker_by_name, names)
    for name, ok, msg in results:
        if ok:
            print(f"{name} ... ok")
        else:
            if msg:
                print(f"{name} {msg}")
            print(f"{name} ... failed")
            fails.append(name)
    end = time.time()
    print()
    print("----------------------------------------------------------------------")
    print(f"Run {len(names)} checkers in {end - start:.2f}s.")
    print()
    if fails:
        print(f"OK: {len(names) - len(fails)} (failed={len(fails)})")
    else:
        print(f"OK: {len(names)}")
    return 0 if not fails else 1


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Run a registered memory checker.")
    parser.add_argument("name", nargs="?", help="Name of the memory checker to run.")
    # --all
    parser.add_argument(
        "--all", action="store_true", help="Run all registered memory checkers."
    )
    parser.add_argument(
        "--list", action="store_true", help="List all registered memory checkers."
    )
    args = parser.parse_args()

    if args.list:
        print("Registered memory checkers:")
        for name in checker_center:
            print(f" - {name}")
        return

    names = [args.name] if args.name else []
    if args.all:
        names = list(checker_center.keys())
    elif args.name not in checker_center:
        print(
            f"Memory checker '{args.name}' not found. Available checkers: {list(checker_center.keys())}"
        )
        return

    sys.exit(run(names))


# endregion

if __name__ == "__main__":
    main()
