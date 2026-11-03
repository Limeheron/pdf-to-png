# pdf_to_png

PDF의 각 페이지를 고화질 PNG로 저장하고, PDF에 들어 있는 원본 이미지를 추출하는 Python 스크립트

## 사용법

```
python3 pdf_to_png.py <PDF경로>
```

- `-h`, `--help`: 도움말을 본다.
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

## 규칙

- 페이지는 288 DPI(PDF 원래 크기의 4배) PNG로 저장한다.
- 원본 이미지는 extract 폴더에 페이지 번호와 순번을 붙여 저장한다(p01_1, p01_2 …).
    - JPEG와 PNG는 PDF에 들어 있는 그대로 저장한다.
    - 투명 정보가 있는 이미지와 그 밖의 형식은 PNG로 변환한다.
    - 여러 페이지에 쓰인 같은 이미지는 처음 나온 페이지에서 한 번만 저장한다.
    - 원본 이미지가 없으면 extract 폴더를 만들지 않는다.
    - 페이지 내용에 직접 들어간 인라인 이미지는 추출하지 않는다.
- 페이지 번호는 1부터 붙이고, 자릿수는 전체 페이지 수에 맞춘다.
- 덮어쓰지 않는다. 같은 이름의 폴더나 파일이 있으면 이름 뒤에 _1, _2 …를 붙인 새 폴더에 저장한다.
- 암호가 걸렸거나 손상되어 열 수 없는 PDF는 변환하지 않는다.
- 일부 페이지나 이미지가 실패해도 나머지는 계속 저장하고, 끝에 결과를 요약한다.
