from PIL import Image

def convert_jpg_to_pdf(image_path, pdf_path):
    print(f"Converting {image_path} to {pdf_path}")
    image = Image.open(image_path)
    pdf_bytes = image.convert('RGB')
    pdf_bytes.save(pdf_path)
    print(f"Conversion completed: {pdf_path}")
