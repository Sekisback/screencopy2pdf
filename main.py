from pyautogui import screenshot
from PIL import Image
from fpdf import FPDF
from PyPDF2 import PdfMerger
import os
import time
import subprocess
from pynput.mouse import Listener


################################################################################
#
#   Firefox auf bildschirm links mit F11 maximieren
#   Amazone Kindle über leseeinstellung auf eine Spalte schalten
#   Seitenrand Schmal
#
################################################################################


def capture_screen_to_pdf(area, page_filename):
    # Mache einen Screenshot mit dem definierten Bereich
    fscreenshot = screenshot(region=area)
    fscreenshot.save(page_filename)


def convert_image_to_pdf(image_filename, pdf_filename):
    # Öffne das Bild und konvertiere es zu PDF
    image = Image.open(image_filename)
    pdf = FPDF(unit="pt", format=[image.width, image.height])
    pdf.add_page()
    pdf.image(image_filename, 0, 0)
    pdf.output(pdf_filename, "F")


def merge_pdfs(pdf_filenames, output_filename):
    merger = PdfMerger()
    for pdf in pdf_filenames:
        merger.append(pdf)
    merger.write(output_filename)
    merger.close()


def main():
    area = get_area_coordinates()
    pagex, pagey = get_arrow_coordinates()
    file_name = str(input("\nName des pdf's: "))
    num_screenshots = int(input("Wie viele Screenshots möchtest du machen? "))
    pdfs = []

    for i in range(num_screenshots):  # Anzahl der Screenshots
        image_filename = f"screenshot_{i}.png"
        pdf_filename = f"page_{i}.pdf"

        capture_screen_to_pdf(area, image_filename)
        convert_image_to_pdf(image_filename, pdf_filename)
        pdfs.append(pdf_filename)

        subprocess.run(["xdotool", "mousemove", pagex, pagey])
        subprocess.run(["xdotool", "click", "1"])
        print(f"Screenshots durchgeführt: {i + 1} von {num_screenshots}", end='\r')
        time.sleep(1.5)

    # PDFs zusammenführen
    merge_pdfs(pdfs, f"{file_name}.pdf")

    # Aufräumen: Lösche die temporären Bilder und PDFs
    for filename in pdfs + [f"screenshot_{i}.png" for i in range(num_screenshots)]:
        os.remove(filename)


def get_area_coordinates():
    left, top, right, bottom = None, None, None, None
    print("[+] Linke obere Ecke erfassen")

    def on_click(x, y, button, pressed):
        nonlocal left, top, right, bottom

        if pressed:
            if button == button.left:
                if left is None and top is None:
                    left, top = x, y
                    print(f"    -> Werte {x}, {y} gespeichert")
                    print("\n[+] Rechte untere Ecke erfassen")
                elif right is None and bottom is None:
                    right, bottom = x, y
                    print(f"    -> Werte {x}, {y} gespeichert")

                    # Stop the listener
                    return False

    with Listener(on_click=on_click) as listener:
        listener.join()

    right = right - left
    bottom = bottom - top

    return left, top, right, bottom


def get_arrow_coordinates():
    pagex, pagey = None, None
    print("\n[+] Pfeil nach rechts erfassen")

    def on_click(x, y, button, pressed):
        nonlocal pagex, pagey

        if pressed:
            if button == button.left:
                if pagex is None and pagey is None:
                    pagex, pagey = x, y
                    print(f"    -> Werte {x}, {y} gespeichert")
                    # Stop the listener
                    return False

    with Listener(on_click=on_click) as listener:
        listener.join()

    pagex = str(pagex)
    pagey = str(pagey)
    return pagex, pagey


if __name__ == "__main__":
    main()
