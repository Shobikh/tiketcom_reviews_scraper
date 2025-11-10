from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd


def init_driver():
    # Gunakan ChromeDriverManager untuk mengelola driver
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()))

def scrape_reviews(driver, url):
    driver.get(url)

    # Tunggu halaman ulasan termuat
    time.sleep(10)

    # List untuk menyimpan data ulasan
    data = []

    while True:
        # Klik semua tombol "Selengkapnya" yang ada di halaman
        while True:
            try:
                more_buttons = driver.find_elements(By.XPATH, "//span[contains(text(), 'Selengkapnya')]")
                if not more_buttons:
                    break  # Jika tidak ada tombol lagi, keluar dari loop

                for btn in more_buttons:
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(1)  # Tunggu ulasan tambahan dimuat

            except Exception as e:
                print(f"Kesalahan saat klik 'Selengkapnya': {e}")
                break

        # Tunggu agar ulasan terbaru muncul
        time.sleep(2)

        # Ambil halaman sumber terbaru
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Ambil elemen ulasan
        review_section = soup.find("div", class_="pdp-review_pdp_review_container__ZOcXp pdp-review_with_summary__kcTbQ")
        reviews = review_section.find_all("div", class_="ReviewCard_review_card__4_CXC") if review_section else []

        # Loop untuk mengambil setiap ulasan
        for review in reviews:
            try:
                user = review.find(
                    "span", 
                    class_="ReviewCard_customer_name__mwGEt Text_text__S3RDm Text_variant_highEmphasis__R3Rpj Text_size_b3__lwDVc Text_weight_bold__oFbTr"
                    ).text.strip()
                # print(user)
            except:
                user = "Anonymous"

            try:
                rating = review.find("span", class_="ReviewCard_user_review__HvsOH Text_text__S3RDm Text_variant_highEmphasis__R3Rpj Text_size_h3__TewN_").text.strip()
                # print(rating)
            except:
                rating = None

            try:
                # Pertama cari komentar versi tanpa "Selengkapnya"
                comment_tag = review.find("span", class_="ReadMoreComments_review_card_comment__R_W2B Text_text__S3RDm Text_variant_highEmphasis__R3Rpj Text_size_b2__oDFka")
                
                # Kalau nggak ada, cari versi setelah diklik tombol "Selengkapnya"
                if comment_tag is None:
                    comment_tag = review.find("span", class_="ReadMoreComments_review_card_comment__R_W2B ReadMoreComments_on_open__AWmK2 Text_text__MwfKw Text_variant_highEmphasis__A8HpD Text_size_b2__3BJow")
                
                # Ambil teks komentar kalau ditemukan
                if comment_tag:
                    comment_raw = comment_tag.text.strip().replace("\n", " ")
                    comment = comment_raw.replace("Lihat lebih sedikit","").strip()
                else:
                    comment = "No comment"
                # print(comment)
            except:
                comment = "No comment"

            try:
                date = review.find("span", class_="ReviewCard_date__Nr8Lq Text_text__S3RDm Text_variant_lowEmphasis__LWwSR Text_size_b3__lwDVc").text.strip()
            except:
                date = "tidak ada tgl"
                
            data.append([user, rating, comment, date])

        # Klik tombol "Halaman Berikutnya" jika ada
        try:
            # Simpan halaman sebelum klik
            next_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='chevron-right-pagination']"))
            )
            last_class = next_button.get_attribute("class")
            if "ReviewPagination_page_number__GW6oE ReviewPagination_inactive__0UEop" in last_class:
                print("Sudah halaman terkahir")
                break
            next_button.click()
            time.sleep(3)  # Tunggu halaman baru dimuat
        except:
            print(f"Tidak ada halaman berikutnya atau error saat klik")
            break

    return data

def save_to_excel(data, nama_file):
    # Simpan ke dalam DataFrame
    df = pd.DataFrame(data, columns=["user", "rating", "review", "review_date"])

    # Simpan ke file Excel
    df.to_excel(nama_file+".xlsx", index=False)

# Fungsi utama
def main():
    # Input link review
    url = input("Masukkan link review produk: ")

    # Input nama file hasil scraping
    nama_file = input("Masukkan Nama File Hasil Scraping: ")
    
    # Inisialisasi driver
    driver = init_driver()

    # Menjalankan proses scraping data
    try:
        data = scrape_reviews(driver, url)
        save_to_excel(data, nama_file)
    finally:
        # Tutup browser
        driver.quit()
        print("Scraping selesai! Semua ulasan telah disimpan")

if __name__ == "__main__":
    main()