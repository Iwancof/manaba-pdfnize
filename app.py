import os
import shutil
import time
import threading
import json
from flask import Flask, send_file, abort, render_template, request, redirect, url_for
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)
auth = HTTPBasicAuth()
# pdf_storage_path = tempfile.mkdtemp()
pdf_storage_path = "./static"

with open("./secret.json") as sf:
    secrets = json.load(sf)

    # Replace these with your desired username and password
    USER = secrets["basic_user"]
    PASSWORD = secrets["basic_password"]
    USER_DATA = {
        USER: generate_password_hash(PASSWORD)
    }

    # Replace these with your website's login credentials
    WEB_USER = secrets["manaba_user"]
    WEB_PASSWORD = secrets["manaba_password"]


@auth.verify_password
def verify_password(username, password):
    if username in USER_DATA:
        return check_password_hash(USER_DATA.get(username), password)
    return False


def remove_pdf_after_timeout(file_path, timeout):
    threading.Timer(timeout, os.remove, args=[file_path]).start()


def download_pdf_with_login(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-application-cache")
    options.add_argument("--disable-infobars")
    options.add_argument("--no-zygote")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-extensions")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    print("[+] driver started")

    # Replace this with the appropriate login logic for your website
    # driver.get("https://idp.account.tsukuba.ac.jp/idp/profile/SAML2/Redirect/SSO?execution=e1s2")
    driver.get("https://manaba.tsukuba.ac.jp/")
    username_field = driver.find_element(By.NAME, "j_username")
    username_field.send_keys(WEB_USER)
    password_field = driver.find_element(By.NAME, "j_password")
    password_field.send_keys(WEB_PASSWORD)
    password_field.send_keys(Keys.RETURN)

    # Click the login button and wait for the page to load
    # login_button = driver.find_element(By.NAME, "_eventId_proceed")
    # login_button.click()

    # Wait for the login to complete (adjust the timeout value as needed)
    WebDriverWait(driver, 10).until(
        EC.url_changes("https://manaba.tsukuba.ac.jp/"))

    # print(driver.page_source)
    print("[+] logged in")

    driver.get(url)
    time.sleep(5)

    pdf_files = [f for f in os.listdir("./") if f.lower().endswith('.pdf')]
    for pdf_file in pdf_files:
        src_path = os.path.join("./", pdf_file)
        dest_path = os.path.join(pdf_storage_path, pdf_file)
        shutil.move(src_path, dest_path)

    print("[+] download complated")


@app.route("/", methods=["GET", "POST"])
@auth.login_required
def index():
    if request.method == "POST":
        url = request.form.get("url")
        return redirect(url_for("download_pdf", url=url))

    pdf_files = list_pdf_files(pdf_storage_path)
    return render_template('index.html', pdf_files=pdf_files)


def list_pdf_files(directory):
    pdf_files = [f for f in os.listdir(directory) if f.lower().endswith('.pdf')]
    return pdf_files


@app.route("/download_pdf/<path:url>")
@auth.login_required
def download_pdf(url):
    try:
        download_pdf_with_login(url)
    except Exception as e:
        abort(500, str(e))

    return "[+] download complated!"

if __name__ == "main":
    try:
        app.run(port=5000)
    finally:
        shutil.rmtree(pdf_storage_path)
