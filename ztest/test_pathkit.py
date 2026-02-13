import math
import sys
from pathlib import Path
from platform import platform

import canvas_pyr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import BaseTestCase


class PathKitTestCase(BaseTestCase):

    def setUp(self) -> None:
        super().setUp()

        self._load_ava_snapshot("pathkit.spec.ts.md")

    def test_to_svg_string(self):
        path = canvas_pyr.Path2D()
        path.rect(0, 0, 100, 100)
        self.assertEqual(
            path.toSVGString(),
            "M0 0L100 0L100 100L0 100L0 0Z",
        )

    def test_create_mountain_via_op(self):
        path_one = canvas_pyr.Path2D()
        path_two = canvas_pyr.Path2D()
        path_one.moveTo(0, 20)
        path_one.lineTo(10, 10)
        path_one.lineTo(20, 20)
        path_one.closePath()
        path_two.moveTo(10, 20)
        path_two.lineTo(20, 10)
        path_two.lineTo(30, 20)
        path_two.closePath()
        self.assertEqual(
            path_one.op(path_two, canvas_pyr.PathOp.Union).toSVGString(),
            "M10 10L0 20L30 20L20 10L15 15L10 10Z",
        )

    def test_union_boolean_operation(self):
        path_one = canvas_pyr.Path2D(
            "M8 50H92C96.4183 50 100 53.5817 100 58V142C100 146.418 96.4183 150 92 150H8C3.58172 150 0 146.418 0 142V58C0 53.5817 3.58172 50 8 50Z",
        )
        path_two = canvas_pyr.Path2D(
            "M58 0H142C146.418 0 150 3.58172 150 8V92C150 96.4183 146.418 100 142 100H58C53.5817 100 50 96.4183 50 92V8C50 3.58172 53.5817 0 58 0Z",
        )
        got = path_one.op(path_two, canvas_pyr.PathOp.Union).toSVGString()
        self._ava_snapshot("Union boolean operation", got)

    def test_difference_boolean_operation(self):
        path_one = canvas_pyr.Path2D(
            "M8 50H92C96.4183 50 100 53.5817 100 58V142C100 146.418 96.4183 150 92 150H8C3.58172 150 0 146.418 0 142V58C0 53.5817 3.58172 50 8 50Z",
        )
        path_two = canvas_pyr.Path2D(
            "M58 0H142C146.418 0 150 3.58172 150 8V92C150 96.4183 146.418 100 142 100H58C53.5817 100 50 96.4183 50 92V8C50 3.58172 53.5817 0 58 0Z",
        )
        self.assertEqual(
            path_one.op(path_two, canvas_pyr.PathOp.Difference).toSVGString(),
            "M50 50L8 50C3.5817201 50 0 53.581699 0 58L0 142C0 146.418 3.5817201 150 8 150L92 150C96.418297 150 100 146.418 100 142L100 100L58 100C53.581699 100 50 96.418297 50 92L50 50Z",
        )

    def test_reverse_difference_boolean_operation(self):
        path_one = canvas_pyr.Path2D(
            "M8 50H92C96.4183 50 100 53.5817 100 58V142C100 146.418 96.4183 150 92 150H8C3.58172 150 0 146.418 0 142V58C0 53.5817 3.58172 50 8 50Z",
        )
        path_two = canvas_pyr.Path2D(
            "M58 0H142C146.418 0 150 3.58172 150 8V92C150 96.4183 146.418 100 142 100H58C53.5817 100 50 96.4183 50 92V8C50 3.58172 53.5817 0 58 0Z",
        )
        self.assertEqual(
            path_one.op(path_two, canvas_pyr.PathOp.ReverseDifference).toSVGString(),
            "M142 0L58 0C53.581699 0 50 3.5817201 50 8L50 50L92 50C96.418297 50 100 53.581699 100 58L100 100L142 100C146.418 100 150 96.418297 150 92L150 8C150 3.5817201 146.418 0 142 0Z",
        )

    def test_intersect_boolean_operation(self):
        path_one = canvas_pyr.Path2D(
            "M8 50H92C96.4183 50 100 53.5817 100 58V142C100 146.418 96.4183 150 92 150H8C3.58172 150 0 146.418 0 142V58C0 53.5817 3.58172 50 8 50Z",
        )
        path_two = canvas_pyr.Path2D(
            "M58 0H142C146.418 0 150 3.58172 150 8V92C150 96.4183 146.418 100 142 100H58C53.5817 100 50 96.4183 50 92V8C50 3.58172 53.5817 0 58 0Z",
        )
        self.assertEqual(
            path_one.op(path_two, canvas_pyr.PathOp.Intersect).toSVGString(),
            "M100 100L58 100C53.581699 100 50 96.418297 50 92L50 50L92 50C96.418297 50 100 53.581699 100 58L100 100Z",
        )

    def test_xor_boolean_operation(self):
        path_one = canvas_pyr.Path2D(
            "M8 50H92C96.4183 50 100 53.5817 100 58V142C100 146.418 96.4183 150 92 150H8C3.58172 150 0 146.418 0 142V58C0 53.5817 3.58172 50 8 50Z",
        )
        path_two = canvas_pyr.Path2D(
            "M58 0H142C146.418 0 150 3.58172 150 8V92C150 96.4183 146.418 100 142 100H58C53.5817 100 50 96.4183 50 92V8C50 3.58172 53.5817 0 58 0Z",
        )
        got = path_one.op(path_two, canvas_pyr.PathOp.Xor).toSVGString()
        self._ava_snapshot("Xor boolean operation", got)

    def test_filltype_as_winding(self):
        path = canvas_pyr.Path2D()
        path.rect(1, 2, 3, 4)
        path.setFillType(canvas_pyr.FillType.EvenOdd)
        self.assertEqual(path.asWinding().getFillType(), canvas_pyr.FillType.Winding)

    def test_get_filltype_string(self):
        path = canvas_pyr.Path2D()
        path.rect(1, 2, 3, 4)
        self.assertEqual(path.getFillTypeString(), "nonzero")

    def test_get_filltype_string_after_set(self):
        path = canvas_pyr.Path2D()
        path.rect(1, 2, 3, 4)
        path.setFillType(canvas_pyr.FillType.EvenOdd)
        self.assertEqual(path.getFillTypeString(), "evenodd")

    def test_use_as_winding_convert_evenodd(self):
        even_odd_path = canvas_pyr.Path2D(
            "M24.2979 13.6364H129.394V40.9091H24.2979L14.6278 27.2727L24.2979 13.6364ZM21.9592 0C19.0246 0 16.2716 1.42436 14.571 3.82251L1.67756 22.0043C-0.559186 25.1585 -0.559186 29.387 1.67756 32.5411L14.571 50.7227C16.2716 53.1209 19.0246 54.5455 21.9592 54.5455H70.4673V68.1818H16.073C11.0661 68.1818 7.00728 72.2518 7.00728 77.2727V113.636C7.00728 118.657 11.0661 122.727 16.073 122.727H70.4673V150H84.0658V122.727H128.041C130.975 122.727 133.729 121.303 135.429 118.905L148.323 100.723C150.559 97.5686 150.559 93.3405 148.323 90.1864L135.429 72.0045C133.729 69.6064 130.975 68.1818 128.041 68.1818H84.0658V54.5455H133.927C138.934 54.5455 142.993 50.4755 142.993 45.4545V9.09091C142.993 4.07014 138.934 0 133.927 0H21.9592ZM125.702 109.091H20.6058V81.8182H125.702L135.372 95.4545L125.702 109.091Z",
        )
        nonzero_path = "M24.297899 13.6364L129.394 13.6364L129.394 40.9091L24.297899 40.9091L14.6278 27.272699L24.297899 13.6364ZM21.9592 0C19.024599 0 16.271601 1.42436 14.571 3.82251L1.67756 22.004299C-0.55918598 25.158501 -0.55918598 29.386999 1.67756 32.5411L14.571 50.722698C16.271601 53.120899 19.024599 54.545502 21.9592 54.545502L70.4673 54.545502L70.4673 68.181801L16.073 68.181801C11.0661 68.181801 7.0072799 72.251801 7.0072799 77.272697L7.0072799 113.636C7.0072799 118.657 11.0661 122.727 16.073 122.727L70.4673 122.727L70.4673 150L84.065804 150L84.065804 122.727L128.041 122.727C130.97501 122.727 133.729 121.303 135.429 118.905L148.323 100.723C150.55901 97.568604 150.55901 93.3405 148.323 90.186401L135.429 72.004501C133.729 69.6064 130.97501 68.181801 128.041 68.181801L84.065804 68.181801L84.065804 54.545502L133.927 54.545502C138.93401 54.545502 142.993 50.475498 142.993 45.454498L142.993 9.09091C142.993 4.0701399 138.93401 0 133.927 0L21.9592 0ZM125.702 109.091L20.605801 109.091L20.605801 81.818199L125.702 81.818199L135.37199 95.454498L125.702 109.091Z"
        even_odd_path.setFillType(canvas_pyr.FillType.EvenOdd)
        self.assertEqual(even_odd_path.asWinding().toSVGString(), nonzero_path)

    def test_as_winding_simplify_quadratic(self):
        path = canvas_pyr.Path2D(
            "M0 10C0 4.47715 4.47715 0 10 0H90C95.5229 0 100 4.47715 100 10C100 15.5228 95.5229 20 90 20H10C4.47715 20 0 15.5228 0 10Z",
        )
        quadratic_path = "M0 10C0 4.47715 4.47715 0 10 0L90 0C95.522903 0 100 4.47715 100 10C100 15.5228 95.522903 20 90 20L10 20C4.47715 20 0 15.5228 0 10Z"
        self.assertEqual(path.asWinding().simplify().toSVGString(), quadratic_path)

    def test_simplify_remove_overlapping_paths(self):
        path = canvas_pyr.Path2D(
            "M2.933,89.89 L89.005,3.818 Q90.412,2.411 92.249,1.65 Q94.087,0.889 96.076,0.889 Q98.065,0.889 99.903,1.65 Q101.741,2.411 103.147,3.818 L189.22,89.89 Q190.626,91.296 191.387,93.134 Q192.148,94.972 192.148,96.961 Q192.148,98.95 191.387,100.788 Q190.626,102.625 189.219,104.032 Q187.813,105.439 185.975,106.2 Q184.138,106.961 182.148,106.961 Q180.159,106.961 178.322,106.2 Q176.484,105.439 175.077,104.032 L89.005,17.96 L96.076,10.889 L103.147,17.96 L17.075,104.032 Q15.668,105.439 13.831,106.2 Q11.993,106.961 10.004,106.961 Q8.015,106.961 6.177,106.2 Q4.339,105.439 2.933,104.032 Q1.526,102.625 0.765,100.788 Q0.004,98.95 0.004,96.961 Q0.004,94.972 0.765,93.134 Q1.526,91.296 2.933,89.89 Z",
        )
        self.assertEqual(
            path.simplify().toSVGString(),
            "M89.004997 3.8180001L2.9330001 89.889999Q1.526 91.295998 0.76499999 93.134003Q0.0040000002 94.972 0.0040000002 96.960999Q0.0040000002 98.949997 0.76499999 100.788Q1.526 102.625 2.9330001 104.032Q4.3390002 105.439 6.177 106.2Q8.0150003 106.961 10.004 106.961Q11.993 106.961 13.831 106.2Q15.668 105.439 17.075001 104.032L96.075996 25.031002L175.077 104.032Q176.48399 105.439 178.32201 106.2Q180.159 106.961 182.14799 106.961Q184.138 106.961 185.97501 106.2Q187.813 105.439 189.21899 104.032Q190.62601 102.625 191.38699 100.788Q192.14799 98.949997 192.14799 96.960999Q192.14799 94.972 191.38699 93.134003Q190.62601 91.295998 189.22 89.889999L103.147 3.8180001Q101.741 2.411 99.903 1.65Q98.065002 0.889 96.075996 0.889Q94.086998 0.889 92.249001 1.65Q90.412003 2.411 89.004997 3.8180001Z",
        )

    def test_convert_filltype_and_quadratic(self):
        path_triangle = canvas_pyr.Path2D(
            "M70 0L0.717957 120H139.282L70 0ZM70 30L26.6987 105H113.301L70 30Z"
        )
        quadratic_path = "M0.71795702 120L70 0L139.282 120L0.71795702 120ZM113.301 105L70 30L26.6987 105L113.301 105Z"
        path_triangle.setFillType(canvas_pyr.FillType.EvenOdd)
        self.assertEqual(
            path_triangle.asWinding().simplify().toSVGString(), quadratic_path
        )

    def test_stroke(self):
        box = canvas_pyr.Path2D()
        box.rect(0, 0, 100, 100)
        # Shrink effect, in which we subtract away from the original
        simplified = canvas_pyr.Path2D(
            box
        ).simplify()  # sometimes required for complicated paths
        shrink = (
            canvas_pyr.Path2D(box)
            .stroke({"width": 15, "cap": canvas_pyr.StrokeCap.Butt})
            .op(simplified, canvas_pyr.PathOp.ReverseDifference)
        )
        self.assertEqual(
            shrink.toSVGString(), "M7.5 92.5L7.5 7.5L92.5 7.5L92.5 92.5L7.5 92.5Z"
        )

    def test_convert_stroke_to_path(self):
        path = canvas_pyr.Path2D(
            "M32.9641 7L53.3157 42.25C54.8553 44.9167 52.9308 48.25 49.8516 48.25H9.14841C6.0692 48.25 4.1447 44.9167 5.6843 42.25L26.0359 7C27.5755 4.33333 31.4245 4.33333 32.9641 7Z",
        )
        got = (
            path.stroke({"width": 10, "miterLimit": 1})
            .simplify()
            .asWinding()
            .toSVGString()
        )
        self._ava_snapshot("Convert stroke to path", got)

    def test_convert_stroke_to_path_2(self):
        path = canvas_pyr.Path2D("M4 23.5L22.5 5L41 23.5")
        got = (
            path.stroke(
                {"width": 10, "join": canvas_pyr.StrokeJoin.Round, "miterLimit": 1}
            )
            .simplify()
            .toSVGString()
        )
        if "arm64" in platform() and sys.platform == "win32":
            self.skipTest("Skip on arm64-windows-msvc")
        self._ava_snapshot("Convert stroke to path 2", got)

    def test_strokejoin_miter(self):
        box = canvas_pyr.Path2D()
        box.rect(0, 0, 100, 100)
        box.stroke({"width": 20, "join": canvas_pyr.StrokeJoin.Miter})
        self.assertEqual(
            box.toSVGString(),
            "M-10 -10L110 -10L110 110L-10 110L-10 -10ZM10 10L10 90L90 90L90 10L10 10Z",
        )

    def test_strokejoin_bevel(self):
        box = canvas_pyr.Path2D()
        box.rect(0, 0, 100, 100)
        box.stroke({"width": 20, "join": canvas_pyr.StrokeJoin.Bevel})
        self.assertEqual(
            box.toSVGString(),
            "M0 -10L100 -10L110 0L110 100L100 110L0 110L-10 100L-10 0L0 -10ZM10 10L10 90L90 90L90 10L10 10Z",
        )

    def test_strokejoin_round(self):
        box = canvas_pyr.Path2D()
        box.rect(0, 0, 100, 100)
        box.stroke({"width": 20, "join": canvas_pyr.StrokeJoin.Round})
        self._ava_snapshot(
            "StrokeJoin.Round",
            box.toSVGString(),
        )

    def test_compute_tight_bounds(self):
        p = canvas_pyr.Path2D()
        self.assertEqual(p.computeTightBounds(), [0, 0, 0, 0])
        p.arc(50, 45, 25, 0, 2 * math.pi)
        self.assertEqual(p.computeTightBounds(), [25, 20, 75, 70])

    def test_transform(self):
        p = canvas_pyr.Path2D()
        p.transform({"a": 1, "b": 0.2, "c": 0.8, "d": 1, "e": 0, "f": 0})
        p.rect(0, 0, 100, 100)
        p.transform({"a": 1, "b": 0, "c": 0, "d": 1, "e": 0, "f": 0})
        p.rect(220, 0, 100, 100)
        self.assertEqual(
            p.toSVGString(),
            "M0 0L100 0L100 100L0 100L0 0ZM220 0L320 0L320 100L220 100L220 0Z",
        )

    def test_trim(self):
        box = canvas_pyr.Path2D()
        box.rect(0, 0, 100, 100)
        # box is now the 3 segments that look like a U.
        # (the top segment has been removed).
        box.trim(0.25, 1).stroke({"width": 10}).simplify()
        svg = f'<svg width="100" height="100" viewBox="0 0 100 100"><path fill="blue" d="{box.toSVGString()}"></path></svg>'

        self._ava_snapshot("trim", svg)

    def test_dash(self):
        phased = draw_star().dash(10, 3, 0.2)
        c = canvas_pyr.createCanvas(500, 500, canvas_pyr.SvgExportFlag.NoPrettyXML)
        ctx = c.getContext("2d")
        ctx.moveTo(100, 100)
        ctx.strokeStyle = "black"
        ctx.stroke(phased)
        if "arm64" in platform() and sys.platform == "win32":
            self.skipTest("Skip on arm64-windows-msvc")
        got = c.getContent().decode("utf-8")
        want = r'<?xml version="1.0" encoding="utf-8" ?><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="500" height="500"><path fill="none" stroke="black" stroke-width="1" stroke-miterlimit="10" d="M252.72093 130.84827L242.97165 133.07347M240.04688 133.74104L230.29759 135.96625M227.3728 136.63382L217.62354 138.85902M214.69875 139.52658L204.94946 141.7518M202.02469 142.41936L192.27541 144.64456M189.35062 145.31213L179.60135 147.53734M176.67654 148.20491L166.92728 150.43011M164.00249 151.09767L154.2532 153.32289M151.32843 153.99045L141.57913 156.21567M138.65436 156.88322L128.90509 159.10843M125.9803 159.776L116.23103 162.00121M113.30623 162.66876L103.55696 164.89398M100.63217 165.56154L90.882904 167.78674M87.958115 168.45432L78.208832 170.67952M75.284058 171.34708L65.534775 173.5723M62.609985 174.23985L52.860703 176.46506M49.935928 177.13263L46.208385 177.98341L51.037449 174.13237M53.382942 172.26189L61.20126 166.02699M63.546753 164.15652L71.365051 157.92163M73.710548 156.05116L81.528862 149.81627M83.874359 147.9458L91.692673 141.71091M94.038162 139.84044L101.85648 133.60553M104.20197 131.73506L112.02029 125.50017M114.36578 123.6297L122.1841 117.3948M124.52959 115.52433L132.3479 109.28943M134.69341 107.41896L142.5117 101.18407M144.85721 99.313591L152.67552 93.078697M155.02101 91.208229L162.83932 84.973335M165.18481 83.102867L173.00314 76.867958M175.34863 74.99749L183.16695 68.762596M185.51244 66.892128L193.33076 60.657227M195.67625 58.786758L203.49457 52.551857M205.84006 50.681396L213.65839 44.446487M216.00388 42.576019L221.82602 37.933014L220.71823 40.23336M219.41658 42.936268L215.07774 51.945953M213.77609 54.648865L209.43726 63.65855M208.1356 66.361458L203.79677 75.371147M202.49512 78.074051L198.15628 87.08374M196.85463 89.786652L192.51579 98.796341M191.21414 101.49924L186.87531 110.50893M185.57365 113.21184L181.23482 122.22153M179.93317 124.92444L175.59433 133.93411M174.29268 136.63702L169.95383 145.64673M168.65219 148.34962L164.31335 157.35931M163.01169 160.06223L158.67285 169.07191M157.37122 171.77481L153.03238 180.7845M151.73071 183.48741L147.39188 192.4971M146.09024 195.20001L141.7514 204.20969M140.44974 206.91261L136.1109 215.92229M134.80927 218.6252L130.47043 227.63489M129.16876 230.3378L124.82993 239.34749M124.36559 238.38188L124.36559 228.38188M124.36559 225.38188L124.36559 215.38188M124.36559 212.38188L124.36559 202.38188M124.36559 199.38188L124.36559 189.38187M124.36559 186.38187L124.36559 176.38187M124.36559 173.38187L124.36559 163.38187M124.36559 160.38187L124.36559 150.38187M124.36559 147.38187L124.36559 137.38187M124.36559 134.38187L124.36559 124.38187M124.36559 121.38187L124.36559 111.38187M124.36559 108.38187L124.36559 98.381866M124.36559 95.381851L124.36559 85.381866M124.36559 82.381866L124.36559 72.381851M124.36559 69.381851L124.36559 59.381866M124.36559 56.381851L124.36559 46.381851M124.36559 43.381851L124.36559 33.381851M124.36559 30.381851L124.36559 20.381851M124.36559 17.381851L124.36559 15.688305L127.96962 23.172163M129.27127 25.875069L133.61011 34.884758M134.91176 37.587662L139.2506 46.597351M140.55225 49.300259L144.89108 58.309944M146.19273 61.012852L150.53157 70.022537M151.83322 72.725449L156.17206 81.735138M157.47371 84.438034L161.81255 93.447723M163.1142 96.150635L167.45303 105.16032M168.75468 107.86324L173.09352 116.87291M174.39517 119.57582L178.73401 128.58551M180.03569 131.28847L184.37453 140.29816M185.67618 143.00107L190.01501 152.01076M191.31667 154.71367L195.6555 163.72334M196.95715 166.42625L201.29599 175.43594M202.59764 178.13885L206.93648 187.14854M208.23813 189.85144L212.57697 198.86113M213.87863 201.56404L218.21745 210.57373M219.5191 213.27663L221.82602 218.06699L218.16463 215.14713M215.81912 213.27664L208.00081 207.04175M205.65532 205.17128L197.83701 198.93639M195.49152 197.06592L187.6732 190.83102M185.3277 188.96056L177.5094 182.72565M175.16389 180.85518L167.34558 174.62029M165.00009 172.74982L157.18176 166.51492M154.83627 164.64445L147.01797 158.40955M144.67247 156.53909L136.85416 150.30418M134.50867 148.43372L126.69035 142.19882M124.34486 140.32835L116.52654 134.09346M114.18105 132.22299L106.36274 125.9881M104.01723 124.11762L96.198929 117.88272M93.853432 116.01226L86.035126 109.77736M83.689621 107.90688L75.871307 101.67199M73.525818 99.801521L65.707504 93.566628M63.362015 91.696159L55.543701 85.461258M53.198196 83.59079L46.208385 78.016594L47.241508 78.252396M50.166294 78.91996L59.915573 81.145172M62.840355 81.812729L72.58963 84.037941M75.51442 84.705505L85.263695 86.93071M88.188477 87.598274L97.937759 89.823486M100.86254 90.491051L110.61182 92.716255M113.53661 93.38382L123.28589 95.609032M126.21066 96.276588L135.95995 98.501801M138.88474 99.169365L148.634 101.39457M151.55879 102.06213L161.30806 104.28734M164.23285 104.95491L173.98213 107.18011M176.90692 107.84768L186.65619 110.07289M189.58098 110.74045L199.33026 112.96566M202.25505 113.63322L212.00432 115.85843M214.92911 116.52599L224.67838 118.75121M227.60316 119.41876L237.35245 121.64397M240.27722 122.31154L250.0265 124.53674M252.95128 125.20431L262.70056 127.42952M265.20001 128L255.64572 130.18071"/></svg>'
        self.assertEqual(len(got), len(want))
        self.assertEqual(
            got,
            want,
        )

    def test_equals(self):
        p1 = draw_simple_path()
        p2 = draw_simple_path()
        self.assertNotEqual(p1, p2)
        self.assertTrue(p1.equals(p2))
        self.assertTrue(p2.equals(p1))
        blank = canvas_pyr.Path2D()
        self.assertFalse(p1.equals(blank))
        self.assertFalse(p2.equals(blank))
        self.assertFalse(blank.equals(p1))
        self.assertFalse(blank.equals(p2))


def draw_simple_path():
    path = canvas_pyr.Path2D()
    path.moveTo(0, 0)
    path.lineTo(10, 0)
    path.lineTo(10, 10)
    path.closePath()
    return path


def draw_star():
    path = canvas_pyr.Path2D()
    r = 115.2
    c = 128.0
    path.moveTo(c + r + 22, c)
    for i in range(1, 8):
        a = 2.6927937 * i
        path.lineTo(c + r * math.cos(a) + 22, c + r * math.sin(a))
    path.closePath()
    return path
