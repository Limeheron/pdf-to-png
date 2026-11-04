# pdf_to_png — PDF의 각 페이지를 고화질 PNG로 저장하고, PDF에 들어 있는 원본 이미지를 추출한다.
# 사용법과 참고 사항은 README.md에 있다.

import os
import sys

# PyMuPDF가 없어도 사용법은 볼 수 있도록, 설치 여부는 변환 직전에 확인한다
try:
    import pymupdf
except ImportError:
    pymupdf = None

ZOOM = 4    # 페이지 이미지 배율 (4배 = 288 DPI)

# 터미널에 출력할 때만 색을 넣는다 (파일로 돌리거나 NO_COLOR가 설정되어 있으면 넣지 않음)
def color(text, code, out):
    if out.isatty() and not os.environ.get("NO_COLOR"):
        return f"\033[{code}m{text}\033[0m"
    return text

def red(text, out=None):
    return color(text, 31, out or sys.stdout)

def green(text, out=None):
    return color(text, 32, out or sys.stdout)

# 사용법
def usage(out=None):
    name = os.path.basename(sys.argv[0])
    print(f"""사용법: {name} <PDF경로>

PDF의 각 페이지를 고화질 PNG로 저장하고, PDF에 들어 있는 원본 이미지를 추출합니다.
결과는 PDF와 같은 폴더의 <PDF 이름> 폴더에 저장됩니다.

옵션:
  -h, --help      사용법 출력

예:
  {name} ~/Documents/report.pdf""", file=out)

# 잘못 실행했을 때: 무엇이 잘못됐는지와 사용법을 보여 주고 끝낸다
def usage_error(message):
    print(red(f"오류: {message}", sys.stderr), file=sys.stderr)
    print(file=sys.stderr)
    usage(sys.stderr)
    sys.exit(1)

# 실행할 수 없을 때: 무엇이 잘못됐는지만 보여 주고 끝낸다
def error_exit(message):
    print(red(f"오류: {message}", sys.stderr), file=sys.stderr)
    sys.exit(1)

# 경로가 이미 있으면 이름 뒤에 _1, _2 …를 붙여 아직 없는 경로를 만든다
def unique_path(path):
    if not os.path.exists(path):
        return path
    n = 1
    while os.path.exists(f"{path}_{n}"):
        n += 1
    return f"{path}_{n}"

# PDF 안의 이미지를 PNG로 변환한다 (CMYK 등은 RGB로, 투명 마스크는 알파 채널로)
def image_to_png(doc, xref, smask):
    pix = pymupdf.Pixmap(doc, xref)
    if pix.colorspace and pix.colorspace.n not in (1, 3):
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    if smask and not pix.alpha:
        pix = pymupdf.Pixmap(pix, pymupdf.Pixmap(doc, smask))
    return pix.tobytes("png")

# 원본 이미지 하나를 저장한다
# JPEG, PNG는 PDF에 들어 있는 그대로 저장하고, 투명 정보가 있거나 그 밖의 형식이면 PNG로 변환한다
def save_image(doc, xref, path_base):
    info = doc.extract_image(xref)
    if not info:
        raise ValueError("이미지를 읽을 수 없음")
    data, ext = info["image"], info["ext"]
    if ext not in ("jpeg", "png") or info["smask"]:
        try:
            data, ext = image_to_png(doc, xref, info["smask"]), "png"
        except Exception:
            pass    # 변환할 수 없으면 원본 그대로 저장한다
    with open(f"{path_base}.{ext}", "wb") as f:
        f.write(data)

# PDF 하나를 변환하고, 실패한 것이 없으면 True를 돌려준다
def pdf_to_png(file_path):
    try:
        doc = pymupdf.open(file_path)
    except Exception:
        error_exit(f"PDF를 열 수 없습니다. 손상된 파일일 수 있습니다: {file_path}")

    with doc:
        if doc.needs_pass:
            error_exit(f"암호가 걸린 PDF는 변환할 수 없습니다: {file_path}")
        if doc.page_count == 0:
            error_exit(f"페이지가 없는 PDF입니다: {file_path}")

        # PDF와 같은 폴더에 PDF 이름으로 출력 폴더를 만든다 (이미 있으면 _1, _2 …)
        name = os.path.splitext(os.path.basename(file_path))[0]
        out_dir = unique_path(os.path.join(os.path.dirname(file_path), name))
        image_dir = os.path.join(out_dir, "extract")
        try:
            os.makedirs(out_dir)
        except OSError:
            error_exit(f"출력 폴더를 만들 수 없습니다: {out_dir}")
        print(f"{os.path.basename(file_path)} ({doc.page_count}페이지) → {out_dir}{os.sep}")

        width = len(str(doc.page_count))    # 페이지 번호 자릿수 (12페이지면 p01~p12)
        seen = set()                        # 이미 저장한 이미지 (여러 페이지에 쓰인 이미지는 한 번만)
        pages = images = duplicate = failed = 0

        for index in range(doc.page_count):
            num = index + 1
            prefix = f"p{num:0{width}d}"

            # 페이지 전체를 고화질 PNG로 저장
            try:
                pix = doc[index].get_pixmap(matrix=pymupdf.Matrix(ZOOM, ZOOM))
                with open(os.path.join(out_dir, f"{prefix}.png"), "wb") as f:
                    f.write(pix.tobytes("png"))
                pages += 1
            except Exception as e:
                print(red(f"  {num}페이지 — 페이지 저장 실패: {e}"))
                failed += 1

            # 이 페이지에서 처음 나온 원본 이미지 저장
            try:
                refs = list(dict.fromkeys(img[0] for img in doc.get_page_images(index, full=True)))
            except Exception as e:
                print(red(f"  {num}페이지 — 이미지 목록을 읽지 못함: {e}"))
                failed += 1
                continue
            new = [xref for xref in refs if xref not in seen]
            duplicate += len(refs) - len(new)
            seen.update(new)

            iwidth = len(str(len(new)))
            for i, xref in enumerate(new, 1):
                try:
                    os.makedirs(image_dir, exist_ok=True)
                    save_image(doc, xref, os.path.join(image_dir, f"{prefix}_{i:0{iwidth}d}"))
                    images += 1
                except Exception as e:
                    print(red(f"  {num}페이지 {i}번째 이미지 — 추출 실패: {e}"))
                    failed += 1

    result = f"페이지 {pages}장, 이미지 {images}개"
    if duplicate:
        result += f" (중복 {duplicate}개 제외)"
    if failed:
        print(red(f"완료 (일부 실패): {result}, 실패 {failed}개"))
    else:
        print(green(f"완료: {result}"))
    return failed == 0

if __name__ == "__main__":
    if os.name == "nt":
        os.system("")   # Windows 콘솔에서 색상 코드를 켠다

    file_path = None
    for arg in sys.argv[1:]:
        if arg in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif arg.startswith("-"):
            usage_error(f"알 수 없는 옵션: {arg}")
        elif file_path:
            usage_error("PDF는 하나만 지정할 수 있습니다.")
        else:
            file_path = arg

    if not file_path:
        usage_error("변환할 PDF를 지정하세요.")
    file_path = os.path.expanduser(file_path)   # Windows에서도 ~를 홈 폴더로 바꾼다
    if not os.path.exists(file_path):
        usage_error(f"파일이 없습니다: {file_path}")
    if not os.path.isfile(file_path):
        usage_error(f"파일이 아닙니다: {file_path}")

    # PDF는 앞부분 1024바이트 안에 %PDF- 헤더가 있다
    try:
        with open(file_path, "rb") as f:
            header = f.read(1024)
    except OSError:
        error_exit(f"파일을 읽을 수 없습니다: {file_path}")
    if b"%PDF-" not in header:
        usage_error(f"PDF 파일이 아닙니다: {file_path}")

    if pymupdf is None:
        python = os.path.splitext(os.path.basename(sys.executable))[0] or "python3"
        error_exit(f"PyMuPDF가 필요합니다. 설치: {python} -m pip install pymupdf")

    sys.exit(0 if pdf_to_png(file_path) else 1)
