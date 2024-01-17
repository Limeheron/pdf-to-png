import os, sys
import fitz

def PDF_to_PNG(file_path):
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    folder_path = os.path.dirname(file_path)
    page_path = os.path.join(folder_path, file_name)
    image_path = os.path.join(page_path, 'extract')

    if not os.path.exists(page_path):
        os.makedirs(page_path)
    if not os.path.exists(image_path):
        os.makedirs(image_path)
    print("Output Folder Created")

    Pages_to_PNG(file_path, page_path)
    PDF_Image_Extract(file_path, image_path)
    print(f"Saved in {page_path}")
    
# 페이지 전체 추출
def Pages_to_PNG(file_path, output_path):
    docs = fitz.open(file_path)
    for page in docs:
        pix = page.get_pixmap(matrix=fitz.Matrix(4, 4))     # 4배 해상도
        output = os.path.join(output_path, "p_%i.png" % page.number)
        pix.save(output)
    print("All Pages Saved")

# 모든 이미지 추출
def PDF_Image_Extract(file_path, output_path):
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

    print("All Image Extracted")
    docs.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print("Error: File not found")
        sys.exit(1)

    PDF_to_PNG(file_path)
