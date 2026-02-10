from flask import Flask, render_template, request, send_file, jsonify
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
from io import BytesIO

app = Flask(__name__)

def collect_links(url):
    links = set()
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for a in soup.find_all("a", href=True):
            full_url = urljoin(url, a["href"])
            if urlparse(full_url).scheme in ["http", "https"]:
                links.add(full_url)
    except Exception as e:
        print(f"Error: {e}")
    return sorted(links)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    url = data.get("url")
    links = collect_links(url)

    if not links:
        return jsonify({"error": "No links found or invalid URL"}), 400

    # # Extract domain name for filename
    # parsed_url = urlparse(url)
    # domain = parsed_url.netloc.replace(".", "_")
    # filename = f"links_{domain}.txt"

    # Generate text file in memory
    buffer = BytesIO()
    content = f"Links collected from: {url}\n\n"
    for link in links:
        content += link + "\n"
    buffer.write(content.encode('utf-8'))
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="links.txt",
        mimetype="text/plain"
    )

if __name__ == "__main__":
    app.run(debug=True)



