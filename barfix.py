import barcode
from barcode.writer import ImageWriter
from PIL import Image
import os
import matplotlib.pyplot as plt

def generate_barcode_on_image(start_number, count, output_file, background_image, padding=10, move_up=1000, gap=20, rotation=0, background_width_increase=200, background_height_increase=200):
    barcode_images = []

    options = {
        'module_width': 1.4,  
        'module_height': 25.0, 
        'write_text': False,  
        'font_size': 0,  
        'quiet_zone': 2.0  
    }

    background = Image.open(background_image).convert("RGB")
    background_width, background_height = background.size

    new_background_width = background_width + background_width_increase
    new_background_height = background_height + background_height_increase
    background = background.resize((new_background_width, new_background_height), Image.LANCZOS)

    fixed_barcode_position = None  # calculate once and reuse later

    for i in range(count):
        number = str(start_number + i)  
        ean = barcode.get('code128', number, writer=ImageWriter())
        filename = ean.save(f"barcode_{number}", options=options)
        barcode_img = Image.open(filename).convert("RGB")
        os.remove(filename) 

        
        barcode_width, barcode_height = barcode_img.size
        if barcode_width > new_background_width - (2 * padding):  
            new_width = new_background_width - (2 * padding)  
            new_height = int(barcode_height * (new_width / barcode_width))
            barcode_img = barcode_img.resize((new_width, new_height), Image.LANCZOS)

        # fixed position for the barcode once
        if fixed_barcode_position is None:
            fixed_barcode_position = (
                (new_background_width - barcode_img.size[0]) // 2,  
                new_background_height - barcode_img.size[1] - padding - move_up  # Fixed vertical position
            )

        background_with_barcode = background.copy()
        background_with_barcode.paste(barcode_img, fixed_barcode_position)

        # Append the individual image 
        barcode_images.append(background_with_barcode)

    # multiple pages with 3 barcodes per page
    pages = [barcode_images[i:i+3] for i in range(0, len(barcode_images), 3)]

    dpi = 300
    page_width = int(13.9 * dpi / 2.54)  
    page_height = int(9.4 * dpi / 2.54)  

    final_pages = []

    for page_images in pages:
        
        final_image = Image.new('RGB', (page_width, page_height), (255, 255, 255))  

        
        total_width = sum(img.size[0] for img in page_images) + (gap * (len(page_images) - 1)) + (padding * 2)
        max_height = max(img.size[1] for img in page_images)

        scale_factor = min((page_width - (padding * 2) - (gap * (len(page_images) - 1))) / total_width, 
                           (page_height - (padding * 2)) / max_height)

        if scale_factor < 1:  
            for i in range(len(page_images)):
                page_images[i] = page_images[i].resize(
                    (int(page_images[i].size[0] * scale_factor), 
                     int(page_images[i].size[1] * scale_factor)),
                    Image.LANCZOS
                )

        x_offset = padding  
        for img in page_images:
            final_image.paste(img, (x_offset, (page_height - img.size[1]) // 2)) 
            x_offset += img.size[0] + gap 

        final_image = final_image.rotate(rotation, expand=True)
        final_pages.append(final_image)

    final_pages[0].save(output_file, save_all=True, append_images=final_pages[1:], resolution=150.0, format="PDF")

    for page in final_pages:
        plt.figure(figsize=(page.width / dpi, page.height / dpi))  
        plt.imshow(page)
        plt.axis('off')  
        plt.show()

    print(f"Barcodes saved in {output_file}")

if __name__ == "__main__":  
    start_number = 1000  
    count = 3 
    output_file = "barcodes_with_images_rotated_multiple_pages.pdf" 
    background_image = "C:\\Users\\G-RAJARAM\\Downloads\\img\\White and Orange Modern ID Card.png"  

    
    generate_barcode_on_image(
        start_number,
        count,
        output_file,
        background_image,
        padding=20,
        move_up=900,  
        gap=30,
        rotation=90,  
        background_width_increase=1181,  
        background_height_increase=1535  
    )
