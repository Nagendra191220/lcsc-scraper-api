from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

@app.route('/scrape', methods=['GET'])
def scrape():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing URL'}), 400

    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')

    title = soup.select_one('h1.product-title')
    title = title.get_text(strip=True) if title else ''

    desc_tag = soup.select_one('meta[name=description]')
    description = desc_tag['content'] if desc_tag else ''

    image_tag = soup.select_one('meta[property=\"og:image\"]')
    image_url = image_tag['content'] if image_tag else ''

    datasheet_tag = soup.select_one('a[data-datasheet-url]')
    datasheet_url = datasheet_tag['href'] if datasheet_tag else ''

    script_tag = soup.find('script', type='application/ld+json')
    price_tiers = []
    try:
        data = json.loads(script_tag.string)
        if 'offers' in data and 'priceSpecification' in data['offers']:
            for p in data['offers']['priceSpecification']:
                price_tiers.append({
                    'quantity': p['eligibleQuantity']['minValue'],
                    'price_usd': p['price']
                })
    except:
        pass

    return jsonify({
        'title': title,
        'description': description,
        'image_url': image_url,
        'datasheet_url': datasheet_url,
        'price_tiers': price_tiers
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
