# pdf_to_png

PDF의 각 페이지를 고화질 PNG로 저장하고, PDF에 들어 있는 원본 이미지를 추출하는 Python 스크립트

## 사용법

```
python3 pdf_to_png.py <PDF경로>
```

- `-h`, `--help`: 사용법 출력
- Windows에서는 python3 대신 python이나 py로 실행한다.

```
python3 pdf_to_png.py ~/Documents/report.pdf
```

- 예: 12페이지짜리 ~/Documents/report.pdf는 ~/Documents/report 폴더에 저장된다.
    - 페이지: p01.png, p02.png … p12.png
    - 원본 이미지: extract/p01_1.jpeg, extract/p03_1.png …

## 필요 환경

- Python 3.9 이상
- PyMuPDF 1.24 이상

```
python3 -m pip install pymupdf
```

## 참고

- 페이지는 288 DPI(PDF 원래 크기의 4배) PNG로 저장한다.
- 원본 이미지는 가능하면 PDF에 들어 있는 형식 그대로 저장하고, 여러 페이지에 쓰인 이미지는 한 번만 저장한다.
- 같은 이름의 폴더가 이미 있으면 덮어쓰지 않고 report_1처럼 새 폴더에 저장한다.
- 암호가 걸린 PDF는 변환하지 않는다.
