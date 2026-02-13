from __future__ import annotations

from types import TracebackType
from typing import (
    Any,
    Callable,
    Literal,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    TypedDict,
    Union,
    overload,
)
from typing_extensions import Self
from enum import IntEnum

ReadableStream = Any
Blob = Any

def clearAllCache() -> None: ...

class CanvasState(Protocol):
    def isContextLost(self) -> bool: ...
    def reset(self) -> None: ...
    def restore(self) -> None: ...
    def save(self) -> None: ...

class CanvasShadowStyles(Protocol):
    shadowBlur: float
    shadowColor: str
    shadowOffsetX: float
    shadowOffsetY: float

class CanvasRenderingContext2DAttributes:
    alpha: bool
    desynchronized: bool

class CanvasSettings(Protocol):
    def getContextAttributes(self) -> CanvasRenderingContext2DAttributes: ...

class CanvasRect(Protocol):
    def clearRect(self, x: float, y: float, w: float, h: float) -> None: ...
    def fillRect(self, x: float, y: float, w: float, h: float) -> None: ...
    def strokeRect(self, x: float, y: float, w: float, h: float) -> None: ...

class TextMetrics(Protocol):
    actualBoundingBoxAscent: float
    actualBoundingBoxDescent: float
    actualBoundingBoxLeft: float
    actualBoundingBoxRight: float
    alphabeticBaseline: float
    emHeightAscent: float
    emHeightDescent: float
    fontBoundingBoxAscent: float
    fontBoundingBoxDescent: float
    hangingBaseline: float
    ideographicBaseline: float
    width: float

    def to_dict(self) -> dict[str, float]: ...

class CanvasText(Protocol):
    def fillText(
        self, text: str, x: float, y: float, maxWidth: float | None = None
    ) -> None: ...
    def measureText(self, text: str) -> TextMetrics: ...
    def strokeText(
        self, text: str, x: float, y: float, maxWidth: float | None = None
    ) -> None: ...

CanvasLineCap = Literal["butt", "round", "square"]
CanvasLineJoin = Literal["bevel", "miter", "round"]

class CanvasPathDrawingStyles(Protocol):
    lineCap: CanvasLineCap
    lineDashOffset: float
    lineJoin: CanvasLineJoin
    lineWidth: float
    miterLimit: float

    def getLineDash(self) -> list[float]: ...
    def setLineDash(self, segments: list[float]) -> None: ...

class CanvasPath(Protocol):
    def arc(
        self,
        x: float,
        y: float,
        radius: float,
        startAngle: float,
        endAngle: float,
        counterclockwise: bool | None = None,
    ) -> None: ...
    def arcTo(
        self, x1: float, y1: float, x2: float, y2: float, radius: float
    ) -> None: ...
    def bezierCurveTo(
        self, cp1x: float, cp1y: float, cp2x: float, cp2y: float, x: float, y: float
    ) -> None: ...
    def closePath(self) -> None: ...
    def ellipse(
        self,
        x: float,
        y: float,
        radiusX: float,
        radiusY: float,
        rotation: float,
        startAngle: float,
        endAngle: float,
        counterclockwise: bool | None = None,
    ) -> None: ...
    def lineTo(self, x: float, y: float) -> None: ...
    def moveTo(self, x: float, y: float) -> None: ...
    def quadraticCurveTo(self, cpx: float, cpy: float, x: float, y: float) -> None: ...
    def rect(self, x: float, y: float, w: float, h: float) -> None: ...
    def roundRect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        radii: float | "DOMPointInit" | list[float | "DOMPointInit"] | None = None,
    ) -> None: ...

ImageSmoothingQuality = Literal["high", "low", "medium"]

class CanvasImageSmoothing(Protocol):
    imageSmoothingEnabled: bool
    imageSmoothingQuality: ImageSmoothingQuality

class CanvasTransform(Protocol):
    def resetTransform(self) -> None: ...
    def rotate(self, angle: float) -> None: ...
    def scale(self, x: float, y: float) -> None: ...
    @overload
    def setTransform(
        self, a: float, b: float, c: float, d: float, e: float, f: float
    ) -> None: ...
    @overload
    def setTransform(
        self, transform: "DOMMatrix2DInit" | "DOMMatrix" | None = None
    ) -> None: ...
    def transform(
        self, a: float, b: float, c: float, d: float, e: float, f: float
    ) -> None: ...
    def translate(self, x: float, y: float) -> None: ...

class CanvasPDFAnnotations(Protocol):
    def annotateLinkUrl(
        self, left: float, top: float, right: float, bottom: float, url: str
    ) -> None: ...
    def annotateNamedDestination(self, x: float, y: float, name: str) -> None: ...
    def annotateLinkToDestination(
        self, left: float, top: float, right: float, bottom: float, name: str
    ) -> None: ...

PredefinedColorSpace = Literal["display-p3", "srgb"]

class ImageDataSettings(TypedDict, total=False):
    colorSpace: PredefinedColorSpace

class CanvasImageData(Protocol):
    @overload
    def createImageData(
        self,
        sw: float,
        sh: float,
        settings: ImageDataSettings | None = None,
        /,
    ) -> "ImageData": ...
    @overload
    def createImageData(self, imagedata: "ImageData", /) -> "ImageData": ...
    def getImageData(
        self,
        sx: float,
        sy: float,
        sw: float,
        sh: float,
        settings: ImageDataSettings | None = None,
    ) -> "ImageData": ...
    def putImageData(
        self,
        imagedata: "ImageData",
        dx: float,
        dy: float,
        dirtyX: Optional[float] = None,
        dirtyY: Optional[float] = None,
        dirtyWidth: Optional[float] = None,
        dirtyHeight: Optional[float] = None,
    ) -> None: ...

CanvasDirection = Literal["inherit", "ltr", "rtl"]
CanvasFontKerning = Literal["auto", "none", "normal"]
CanvasFontStretch = Literal[
    "condensed",
    "expanded",
    "extra-condensed",
    "extra-expanded",
    "normal",
    "semi-condensed",
    "semi-expanded",
    "ultra-condensed",
    "ultra-expanded",
]
CanvasFontVariantCaps = Literal[
    "all-petite-caps",
    "all-small-caps",
    "normal",
    "petite-caps",
    "small-caps",
    "titling-caps",
    "unicase",
]
CanvasTextAlign = Literal["center", "end", "left", "right", "start"]
CanvasTextBaseline = Literal[
    "alphabetic", "bottom", "hanging", "ideographic", "middle", "top"
]
CanvasTextRendering = Literal[
    "auto", "geometricPrecision", "optimizeLegibility", "optimizeSpeed"
]

class CanvasTextDrawingStyles(Protocol):
    direction: CanvasDirection
    font: str
    fontKerning: CanvasFontKerning
    fontStretch: CanvasFontStretch
    fontVariantCaps: CanvasFontVariantCaps
    letterSpacing: str
    textAlign: CanvasTextAlign
    textBaseline: CanvasTextBaseline
    textRendering: CanvasTextRendering
    wordSpacing: str
    fontVariationSettings: str
    lang: str

class CanvasFilters(Protocol):
    filter: str

class CanvasFillStrokeStyles(Protocol):
    fillStyle: str | "CanvasGradient" | "CanvasPattern"
    strokeStyle: str | "CanvasGradient" | "CanvasPattern"
    def createConicGradient(
        self, startAngle: float, x: float, y: float
    ) -> "CanvasGradient": ...
    def createLinearGradient(
        self, x0: float, y0: float, x1: float, y1: float
    ) -> "CanvasGradient": ...
    def createRadialGradient(
        self, x0: float, y0: float, r0: float, x1: float, y1: float, r1: float
    ) -> "CanvasGradient": ...

CanvasFillRule = Literal["evenodd", "nonzero"]

class CanvasDrawPath(Protocol):
    def beginPath(self) -> None: ...
    @overload
    def clip(self, fillRule: CanvasFillRule | None = None) -> None: ...
    @overload
    def clip(self, path: "Path2D", fillRule: CanvasFillRule | None = None) -> None: ...
    @overload
    def fill(self, fillRule: CanvasFillRule | None = None) -> None: ...
    @overload
    def fill(self, path: "Path2D", fillRule: CanvasFillRule | None = None) -> None: ...
    @overload
    def isPointInPath(
        self,
        x: float,
        y: float,
        fillRule: CanvasFillRule | None = None,
        /,
    ) -> bool: ...
    @overload
    def isPointInPath(
        self,
        path: "Path2D",
        x: float,
        y: float,
        fillRule: CanvasFillRule | None = None,
        /,
    ) -> bool: ...
    @overload
    def isPointInStroke(self, x: float, y: float) -> bool: ...
    @overload
    def isPointInStroke(self, path: "Path2D", x: float, y: float) -> bool: ...
    def stroke(self, path: "Path2D" | None = None) -> None: ...

GlobalCompositeOperation = Literal[
    "color",
    "color-burn",
    "color-dodge",
    "copy",
    "darken",
    "destination-atop",
    "destination-in",
    "destination-out",
    "destination-over",
    "difference",
    "exclusion",
    "hard-light",
    "hue",
    "lighten",
    "lighter",
    "luminosity",
    "multiply",
    "overlay",
    "saturation",
    "screen",
    "soft-light",
    "source-atop",
    "source-in",
    "source-out",
    "source-over",
    "xor",
]

class CanvasCompositing(Protocol):
    globalAlpha: float
    globalCompositeOperation: GlobalCompositeOperation

class DOMPointInit(TypedDict, total=False):
    w: float
    x: float
    y: float
    z: float

class CanvasPattern(Protocol):
    def setTransform(self, transform: "DOMMatrix" | None = None) -> None: ...

class CanvasGradient(Protocol):
    def addColorStop(self, offset: float, color: str) -> None: ...

class DOMRectInit(TypedDict, total=False):
    height: float
    width: float
    x: float
    y: float

class DOMMatrixInit(TypedDict, total=False):
    is2D: bool
    m13: float
    m14: float
    m23: float
    m24: float
    m31: float
    m32: float
    m33: float
    m34: float
    m43: float
    m44: float
    a: float
    b: float
    c: float
    d: float
    e: float
    f: float

class DOMMatrix2DInit(TypedDict):
    a: float
    b: float
    c: float
    d: float
    e: float
    f: float

class DOMMatrixReadOnly(Protocol):
    a: float
    b: float
    c: float
    d: float
    e: float
    f: float
    is2D: bool
    isIdentity: bool
    m11: float
    m12: float
    m13: float
    m14: float
    m21: float
    m22: float
    m23: float
    m24: float
    m31: float
    m32: float
    m33: float
    m34: float
    m41: float
    m42: float
    m43: float
    m44: float

    def flipX(self) -> "DOMMatrix": ...
    def flipY(self) -> "DOMMatrix": ...
    def inverse(self) -> "DOMMatrix": ...
    def multiply(self, other: DOMMatrixReadOnly) -> "DOMMatrix": ...
    def rotate(
        self,
        rotX: float,
        rotY: float | None = None,
        rotZ: float | None = None,
    ) -> "DOMMatrix": ...
    def rotateAxisAngle(
        self,
        x: float = 0,
        y: float = 0,
        z: float = 0,
        angle: float = 0,
    ) -> "DOMMatrix": ...
    def rotateFromVector(self, x: float = 0, y: float = 0) -> "DOMMatrix": ...
    def scale(
        self,
        scaleX: float | None = None,
        scaleY: float | None = None,
        scaleZ: float | None = None,
        originX: float | None = None,
        originY: float | None = None,
        originZ: float | None = None,
    ) -> "DOMMatrix": ...
    def scale3d(
        self,
        scale: float | None = None,
        originX: float | None = None,
        originY: float | None = None,
        originZ: float | None = None,
    ) -> "DOMMatrix": ...
    def skewX(self, sx: float | None = None) -> "DOMMatrix": ...
    def skewY(self, sy: float | None = None) -> "DOMMatrix": ...
    def toFloatArray(self) -> list[float]: ...
    def transformPoint(self, point: DOMPoint | None = None) -> "DOMPoint": ...
    def translate(
        self,
        tx: float = 0,
        ty: float = 0,
        tz: float = 0,
    ) -> "DOMMatrix": ...

class DOMMatrixDict(TypedDict):
    a: float
    b: float
    c: float
    d: float
    e: float
    f: float
    is2D: float
    isIdentity: float
    m11: float
    m12: float
    m13: float
    m14: float
    m21: float
    m22: float
    m23: float
    m24: float
    m31: float
    m32: float
    m33: float
    m34: float
    m41: float
    m42: float
    m43: float
    m44: float

class DOMMatrix(DOMMatrixReadOnly):
    """
    ref: https://developer.mozilla.org/en-US/docs/Web/API/DOMMatrix
    """

    a: float
    b: float
    c: float
    d: float
    e: float
    f: float
    m11: float
    m12: float
    m13: float
    m14: float
    m21: float
    m22: float
    m23: float
    m24: float
    m31: float
    m32: float
    m33: float
    m34: float
    m41: float
    m42: float
    m43: float
    m44: float
    is2D: bool
    isIdentity: bool

    def __init__(self, init: str | Sequence[float] | None = None) -> None: ...
    def invertSelf(self) -> Self: ...
    def multiplySelf(self, other: DOMMatrix) -> Self: ...
    def preMultiplySelf(self, other: DOMMatrix) -> Self: ...
    def rotateAxisAngleSelf(
        self,
        x: float = 0,
        y: float = 0,
        z: float = 0,
        angle: float = 0,
    ) -> Self: ...
    def rotateFromVectorSelf(
        self,
        x: float = 0,
        y: float = 0,
    ) -> Self: ...
    def rotateSelf(
        self,
        rotX: float,
        rotY: float | None = None,
        rotZ: float | None = None,
    ) -> Self:
        """
        If only one parameter is passed, rotZ is the value of rotX, and both rotX and rotY are 0, and the rotation is a 2D rotation.
        """

    def scale3dSelf(
        self,
        scale: float | None = None,
        originX: float | None = None,
        originY: float | None = None,
        originZ: float | None = None,
    ) -> Self: ...
    def scaleSelf(
        self,
        scaleX: float | None = None,
        scaleY: float | None = None,
        scaleZ: float | None = None,
        originX: float | None = None,
        originY: float | None = None,
        originZ: float | None = None,
    ) -> Self: ...
    def setMatrixValue(self, transformList: str) -> Self: ...
    def skewXSelf(self, sx: float | None = None) -> Self: ...
    def skewYSelf(self, sy: float | None = None) -> Self: ...
    def translateSelf(
        self,
        tx: float = 0,
        ty: float = 0,
        tz: float = 0,
    ) -> Self: ...
    def toJSON(self) -> DOMMatrixDict: ...
    @classmethod
    def fromFloatArray(cls, array: Sequence[float]) -> "DOMMatrix": ...
    @classmethod
    def fromMatrix(cls, other: DOMMatrix) -> "DOMMatrix": ...

class DOMRectReadOnly(Protocol):
    bottom: float
    height: float
    left: float
    right: float
    top: float
    width: float
    x: float
    y: float

class DOMRectDict(TypedDict):
    bottom: float
    height: float
    left: float
    right: float
    top: float
    width: float
    x: float
    y: float

class DOMRect(DOMRectReadOnly):
    height: float
    width: float
    x: float
    y: float

    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        width: float = 0.0,
        height: float = 0.0,
    ) -> None: ...
    def toJSON(self) -> DOMRectDict: ...
    @classmethod
    def fromRect(cls, other: "DOMRect") -> "DOMRect": ...

class DOMPointDict(TypedDict):
    w: float
    x: float
    y: float
    z: float

class DOMPoint:
    w: float
    x: float
    y: float
    z: float

    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        w: float = 1.0,
    ) -> None: ...
    def matrixTransform(self, matrix: "DOMMatrix") -> "DOMPoint": ...
    def toJSON(self) -> DOMPointDict: ...
    @classmethod
    def fromPoint(cls, other: "DOMPoint") -> "DOMPoint": ...

class ImageDataAttribute(TypedDict):
    colorSpace: PredefinedColorSpace

class ImageData:
    data: bytearray  # readonly
    height: int  # readonly
    width: int  # readonly

    @overload
    def __init__(
        self, sw: int, sh: int, attr: Optional[ImageDataAttribute] = None, /
    ) -> None: ...
    @overload
    def __init__(
        self,
        data: bytes | list[int] | list[float],
        sw: int,
        sh: Optional[int] = None,
        /,
    ) -> None: ...

class Image:
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(
        self, width: float, height: float, attrs: Optional[ImageDataAttribute] = None
    ) -> None: ...

    width: float
    height: float
    naturalWidth: float  # readonly
    naturalHeight: float  # readonly
    complete: bool  # readonly
    currentSrc: str | None  # readonly
    alt: str
    src: str | None  # readonly

    def load(self, data: bytes | str) -> None:
        """
        Load image data from bytes or a file path.

        :param self: self
        :param data: image data as bytes / file path as str / data URL as str / SVG as str
        :type data: bytes | str
        """

class Path2D:
    def __init__(self, path: "Path2D" | str | None = None) -> None: ...
    def addPath(
        self, path: "Path2D", transform: Optional[DOMMatrix] = None
    ) -> None: ...
    def arc(
        self,
        x: float,
        y: float,
        radius: float,
        startAngle: float,
        endAngle: float,
        anticlockwise: bool | None = None,
    ) -> None: ...
    def arcTo(
        self, x1: float, y1: float, x2: float, y2: float, radius: float
    ) -> None: ...
    def bezierCurveTo(
        self, cp1x: float, cp1y: float, cp2x: float, cp2y: float, x: float, y: float
    ) -> None: ...
    def closePath(self) -> None: ...
    def ellipse(
        self,
        x: float,
        y: float,
        radiusX: float,
        radiusY: float,
        rotation: float,
        startAngle: float,
        endAngle: float,
        anticlockwise: bool | None = None,
    ) -> None: ...
    def lineTo(self, x: float, y: float) -> None: ...
    def moveTo(self, x: float, y: float) -> None: ...
    def quadraticCurveTo(self, cpx: float, cpy: float, x: float, y: float) -> None: ...
    def rect(self, x: float, y: float, w: float, h: float) -> None: ...
    def roundRect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        radii: float | list[float] | None = None,
    ) -> None: ...
    def op(self, path: "Path2D", operation: "PathOp") -> "Path2D": ...
    def toSVGString(self) -> str: ...
    def getFillType(self) -> "FillType": ...
    def getFillTypeString(self) -> str: ...
    def setFillType(self, type: "FillType") -> None: ...
    def simplify(self) -> "Path2D": ...
    def asWinding(self) -> "Path2D": ...
    def stroke(self, stroke: "StrokeOptions" | None = None) -> "Path2D": ...
    def transform(self, transform: DOMMatrix2DInit) -> "Path2D": ...
    def getBounds(self) -> Tuple[float, float, float, float]: ...
    def computeTightBounds(self) -> Tuple[float, float, float, float]: ...
    def trim(
        self, start: float, end: float, isComplement: bool | None = None
    ) -> "Path2D": ...
    def dash(self, on: float, off: float, phase: float) -> "Path2D": ...
    def round(self, radius: float) -> "Path2D": ...
    def equals(self, path: "Path2D") -> bool: ...

class StrokeOptions(TypedDict, total=False):
    width: float
    miterLimit: float
    cap: "StrokeCap"
    join: "StrokeJoin"

class CanvasRenderingContext2D(
    CanvasCompositing,
    CanvasDrawPath,
    CanvasFillStrokeStyles,
    CanvasFilters,
    CanvasImageData,
    CanvasImageSmoothing,
    CanvasPath,
    CanvasPathDrawingStyles,
    CanvasRect,
    CanvasSettings,
    CanvasShadowStyles,
    CanvasState,
    CanvasText,
    CanvasTextDrawingStyles,
    CanvasTransform,
    CanvasPDFAnnotations,
):
    canvas: "Canvas"  # readonly
    letterSpacing: str
    wordSpacing: str

    def createConicGradient(
        self, startAngle: float, x: float, y: float
    ) -> CanvasGradient: ...
    @overload
    def drawImage(
        self,
        image: Image | "Canvas",
        dx: float,
        dy: float,
        /,
    ) -> None: ...
    @overload
    def drawImage(
        self,
        image: Image | "Canvas",
        dx: float,
        dy: float,
        dw: float,
        dh: float,
        /,
    ) -> None: ...
    @overload
    def drawImage(
        self,
        image: Image | "Canvas",
        sx: float,
        sy: float,
        sw: float,
        sh: float,
        dx: float,
        dy: float,
        dw: float,
        dh: float,
        /,
    ) -> None: ...
    @overload
    def drawCanvas(
        self,
        canvas: "Canvas",
        dx: float,
        dy: float,
        /,
    ) -> None: ...
    @overload
    def drawCanvas(
        self,
        canvas: "Canvas",
        dx: float,
        dy: float,
        dw: float,
        dh: float,
        /,
    ) -> None: ...
    @overload
    def drawCanvas(
        self,
        canvas: "Canvas",
        sx: float,
        sy: float,
        sw: float,
        sh: float,
        dx: float,
        dy: float,
        dw: float,
        dh: float,
        /,
    ) -> None: ...
    def createPattern(
        self,
        image: Image | ImageData | "Canvas" | "SvgCanvas",
        repeat: Literal["repeat", "repeat-x", "repeat-y", "no-repeat"] | None,
    ) -> CanvasPattern: ...
    def getTransform(self) -> DOMMatrix: ...

ColorSpace = Literal["srgb", "display-p3"]

class ContextAttributes(TypedDict, total=False):
    alpha: bool
    colorSpace: ColorSpace

class SvgCanvas(Protocol):
    # Set width or height will create a new canvas inner surface, and the content will be cleared.
    width: int
    height: int
    def getContext(
        self,
        contextType: Literal["2d"],
        contextAttributes: ContextAttributes | None = None,
    ) -> CanvasRenderingContext2D: ...
    def getContent(self) -> bytes: ...

class AvifConfig:
    # 0-100 scale, 100 is lossless
    quality: Optional[int]
    # 0-100 scale
    alphaQuality: Optional[int]
    # rav1e preset 1 (slow) 10 (fast but crappy), default is 5
    speed: Optional[int]
    # How many threads should be used (0 = match core count)
    threads: Optional[int]
    # set to '4:2:0' to use chroma subsampling, default '4:4:4'
    chromaSubsampling: Optional["ChromaSubsampling"]

class GifConfig(TypedDict, total=False):
    quality: int

class GifEncoderConfig(TypedDict, total=False):
    repeat: int
    quality: int

class GifFrameConfig(TypedDict, total=False):
    delay: int
    disposal: "GifDisposal"
    transparent: int
    left: int
    top: int

class GifDisposal(IntEnum):
    Keep = 0
    Background = 1
    Previous = 2

class GifEncoder:
    width: int
    height: int
    frameCount: int

    def __init__(
        self, width: int, height: int, config: GifEncoderConfig | None = None
    ) -> None: ...
    def addFrame(
        self, data: bytes, width: int, height: int, config: GifFrameConfig | None = None
    ) -> None: ...
    def finish(self) -> bytes: ...
    def __enter__(self) -> Self: ...
    def __exit__(
        self,
        exc_type: type | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

class ChromaSubsampling(IntEnum):
    Yuv444 = 0
    Yuv422 = 1
    Yuv420 = 2
    Yuv400 = 3

class ConvertToBlobOptions(TypedDict, total=False):
    mime: str
    quality: float

class Canvas:
    # Set width or height will create a new canvas inner surface, and the content will be cleared.
    width: int
    height: int

    def getContext(
        self,
        contextType: Literal["2d"],
        contextAttributes: ContextAttributes | None = None,
    ) -> CanvasRenderingContext2D: ...
    @overload
    def encode(
        self, format: Literal["webp", "jpeg"], quality: float | None = None
    ) -> bytes: ...
    @overload
    def encode(self, format: Literal["png"]) -> bytes: ...
    @overload
    def encode(
        self, format: Literal["avif"], cfg: AvifConfig | None = None
    ) -> bytes: ...
    @overload
    def encode(self, format: Literal["gif"], quality: float | None = None) -> bytes: ...
    def data(self) -> bytes:
        """raw pixel data in RGBA order"""

    @overload
    def toDataURL(
        self,
        mime: Literal[
            "image/jpeg", "image/webp", "image/png", "image/gif"
        ] = "image/png",
        quality: float | None = None,
    ) -> str: ...
    @overload
    def toDataURL(
        self, mime: Literal["image/avif"], cfg: AvifConfig | None = None
    ) -> str: ...
    def savePng(self, path: str) -> None: ...

@overload
def createCanvas(width: int, height: int) -> Canvas: ...
@overload
def createCanvas(
    width: int, height: int, svgExportFlag: "SvgExportFlag"
) -> SvgCanvas: ...

class FontKey:
    typefaceId: int

class FontVariationAxis:
    # OpenType tag as a 32-bit integer (e.g., 0x77676874 for 'wght')
    tag: int
    # Current value for this axis
    value: float
    # Minimum value for this axis
    min: float
    # Maximum value for this axis
    max: float
    # Default value for this axis
    def_: float
    # Whether this axis should be hidden from UI
    hidden: bool

class FontStyles:
    weight: int
    width: str
    style: str

class FontStyleSet:
    family: str
    styles: list[FontStyles]

class IGlobalFonts(Protocol):
    def getFamilies(self) -> list[FontStyleSet]: ...
    def register(self, font: bytes, nameAlias: str | None = None) -> FontKey | None: ...
    def registerFromPath(
        self, path: str, nameAlias: str | None = None
    ) -> FontKey | None: ...
    def has(self, name: str) -> bool: ...
    def loadFontsFromDir(self, path: str) -> int: ...
    def setAlias(self, fontName: str, alias: str) -> bool: ...
    def remove(self, key: FontKey) -> None: ...
    def removeBatch(self, fontKeys: list[FontKey]) -> int: ...
    def removeAll(self) -> int: ...
    def getVariationAxes(
        self, familyName: str, weight: int, width: int, slant: int
    ) -> list[FontVariationAxis]: ...
    def hasVariations(
        self, familyName: str, weight: int, width: int, slant: int
    ) -> bool: ...

GlobalFonts: IGlobalFonts

class PathOp(IntEnum):
    Difference = 0
    Intersect = 1
    Union = 2
    Xor = 3
    ReverseDifference = 4

class FillType(IntEnum):
    Winding = 0
    EvenOdd = 1
    InverseWinding = 2
    InverseEvenOdd = 3

class StrokeJoin(IntEnum):
    Miter = 0
    Round = 1
    Bevel = 2

class StrokeCap(IntEnum):
    Butt = 0
    Round = 1
    Square = 2

class SvgExportFlag(IntEnum):
    ConvertTextToPaths = 0x01
    NoPrettyXML = 0x02
    RelativePathEncoding = 0x04

def convertSVGTextToPath(svg: bytes | str) -> bytes: ...

class LoadImageOptions(TypedDict, total=False):
    alt: str
    maxRedirects: int
    requestOptions: dict[str, Any]

def loadImage(
    source: str | Any | bytes | Any | Image | Any,
    options: LoadImageOptions | None = None,
) -> Any: ...

class PDFMetadata(TypedDict, total=False):
    title: str
    author: str
    subject: str
    keywords: str
    creator: str
    producer: str
    rasterDPI: float
    encodingQuality: int
    pdfa: bool
    compressionLevel: int

class Rect(TypedDict):
    left: float
    top: float
    right: float
    bottom: float

class PDFDocument:
    def __init__(self, metadata: PDFMetadata | None = None) -> None: ...
    def beginPage(
        self, width: float, height: float, rect: Rect | None = None
    ) -> CanvasRenderingContext2D: ...
    def endPage(self) -> None: ...
    def close(self) -> bytes: ...

class LottieAnimationOptions(TypedDict, total=False):
    resourcePath: str

class LottieRenderRect(TypedDict):
    x: float
    y: float
    width: float
    height: float

class LottieAnimation:
    @staticmethod
    def loadFromData(
        data: str | bytes, options: Optional[LottieAnimationOptions] = None
    ) -> "LottieAnimation": ...
    @staticmethod
    def loadFromFile(path: str) -> "LottieAnimation": ...

    duration: float  # readonly
    fps: float  # readonly
    frames: int  # readonly
    width: int  # readonly
    height: int  # readonly
    version: str  # readonly
    inPoint: float  # readonly
    outPoint: float  # readonly

    def seek(self, t: float) -> None: ...
    def seekFrame(self, frame: int) -> None: ...
    def seekTime(self, seconds: float) -> None: ...
    def render(
        self, ctx: CanvasRenderingContext2D, dst: Optional[LottieRenderRect] = None
    ) -> None: ...
