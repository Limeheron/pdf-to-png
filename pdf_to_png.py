import os, sys

# PyMuPDF가 없어도 사용법은 볼 수 있도록, 설치 여부는 변환 직전에 확인한다
try:
    import fitz
except ImportError:
    fitz = None

# 사용법
def usage(out=None):
    name = os.path.basename(sys.argv[0])
    print(f"""사용법: {name} <PDF경로>

PDF의 각 페이지를 PNG로 저장하고, 내장 이미지를 추출합니다.
결과는 PDF와 같은 폴더의 <PDF 이름> 폴더에 저장됩니다.

옵션:
  -h, --help      도움말 보기

예:
  {name} ~/Documents/report.pdf""", file=out)

# 잘못 실행했을 때: 무엇이 잘못됐는지와 사용법을 보여 주고 끝낸다
def usage_error(message):
    print(f"❌ {message}", file=sys.stderr)
    print(file=sys.stderr)
    usage(sys.stderr)
    sys.exit(1)

def pdf_to_png(file_path):
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    folder_path = os.path.dirname(file_path)
    page_path = os.path.join(folder_path, file_name)
    image_path = os.path.join(page_path, 'extract')

    if not os.path.exists(page_path):
        os.makedirs(page_path)
    if not os.path.exists(image_path):
        os.makedirs(image_path)
    print("Output Folder Created")

    pages_to_png(file_path, page_path)
    pdf_image_extract(file_path, image_path)
    print(f"Saved in {page_path}")

# 페이지 전체 추출
def pages_to_png(file_path, output_path):
    docs = fitz.open(file_path)
    for page in docs:
        pix = page.get_pixmap(matrix=fitz.Matrix(4, 4))     # 4배 해상도
        output = os.path.join(output_path, "p_%i.png" % page.number)
        pix.save(output)
    print("페이지 저장 완료")

# 모든 이미지 추출
def pdf_image_extract(file_path, output_path):
    docs = fitz.open(file_path)
    for pages in range(docs.page_count):
        page = docs[pages]

        images = page.get_images(full=True)
        for img_index, img_info in enumerate(images):
            image_index = img_info[0]
            base_image = docs.extract_image(image_index)
            image_bytes = base_image["image"]

            image_filename = f"p{pages + 1}_{img_index + 1}.png"
            full_path = os.path.join(output_path, image_filename)
            with open(full_path, "wb") as image_file:
                image_file.write(image_bytes)
    print("이미지 추출 완료")
    docs.close()

if __name__ == "__main__":
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
    if not os.path.exists(file_path):
        usage_error(f"파일이 없습니다: {file_path}")
    if not os.path.isfile(file_path):
        usage_error(f"파일이 아닙니다: {file_path}")

    # PDF는 앞부분 1024바이트 안에 %PDF- 헤더가 있다
    try:
        with open(file_path, "rb") as f:
            header = f.read(1024)
    except OSError:
        print(f"❌ 파일을 읽을 수 없습니다: {file_path}", file=sys.stderr)
        sys.exit(1)
    if b"%PDF-" not in header:
        usage_error(f"PDF 파일이 아닙니다: {file_path}")

    if fitz is None:
        print("❌ PyMuPDF가 설치되어 있지 않습니다. 설치: pip install pymupdf", file=sys.stderr)
        sys.exit(1)

    pdf_to_png(file_path)
