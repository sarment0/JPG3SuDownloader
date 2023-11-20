import os
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import argparse
import uuid
from concurrent.futures import ThreadPoolExecutor


def download_image(img_url, img_path):
    img_data = requests.get(img_url).content
    print("Downloading... " + img_url)

    # Skip if the file already exists
    if os.path.exists(img_path):
        print(f"Skipping {img_path} as it already exists.")
        return

    with open(img_path, "wb") as img_file:
        img_file.write(img_data)


def download_images(url, download_directory):
    # Step 1: Access the URL
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Step 2: Get links to images and modify URLs
    image_links = [
        img["src"] for img in soup.select("div.list-item-image.fixed-size > a > img")
    ]
    image_links = [link.replace(".md.jpg", ".jpg") for link in image_links]

    # Step 3: Download images and save to a folder
    folder_name = f"images_{uuid.uuid4()}"
    folder_path = os.path.join(download_directory, folder_name)

    # Create the folder if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)

    # Create a ThreadPoolExecutor with 3 threads
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Download and save images concurrently
        futures = []
        for idx, img_link in enumerate(image_links):
            img_url = urljoin(url, img_link)
            img_name = f"image_{uuid.uuid4()}.jpg"  # Unique ID as the image name
            img_path = os.path.join(folder_path, img_name)

            futures.append(executor.submit(download_image, img_url, img_path))

        # Wait for all threads to complete
        for future in futures:
            future.result()

    return folder_path


def download_images_for_urls(urls, download_directory):
    for url in urls:
        download_images(url, download_directory)


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Download images from specified URLs.")
    parser.add_argument(
        "-u", "--urls", nargs="+", type=str, help="List of album URLs", required=True
    )
    args = parser.parse_args()

    # Specify the download directory
    download_directory = "downloads"

    # Download images for each URL
    for url in args.urls:
        folder_path = download_images(url, download_directory)
        print(f"Done! Images downloaded and saved to {folder_path}")


if __name__ == "__main__":
    main()
