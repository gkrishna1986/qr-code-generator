from flask import Flask, render_template, request, send_file, jsonify
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
import io
import base64

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    text = data.get('text', '').strip()
    fg_color = data.get('fg_color', '#000000')
    bg_color = data.get('bg_color', '#ffffff')
    style = data.get('style', 'square')
    error_level = data.get('error_level', 'M')

    if not text:
        return jsonify({'error': 'Please enter text or URL'}), 400

    error_map = {'L': qrcode.constants.ERROR_CORRECT_L,
                 'M': qrcode.constants.ERROR_CORRECT_M,
                 'Q': qrcode.constants.ERROR_CORRECT_Q,
                 'H': qrcode.constants.ERROR_CORRECT_H}

    qr = qrcode.QRCode(
        version=None,
        error_correction=error_map.get(error_level, qrcode.constants.ERROR_CORRECT_M),
        box_size=12,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    if style == 'rounded':
        img = qr.make_image(image_factory=StyledPilImage,
                            module_drawer=RoundedModuleDrawer(),
                            fill_color=fg_color, back_color=bg_color)
    else:
        img = qr.make_image(fill_color=fg_color, back_color=bg_color)

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_b64 = base64.b64encode(buffer.read()).decode('utf-8')

    return jsonify({'image': f'data:image/png;base64,{img_b64}'})

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    text = data.get('text', '').strip()
    fg_color = data.get('fg_color', '#000000')
    bg_color = data.get('bg_color', '#ffffff')
    style = data.get('style', 'square')
    error_level = data.get('error_level', 'M')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    error_map = {'L': qrcode.constants.ERROR_CORRECT_L,
                 'M': qrcode.constants.ERROR_CORRECT_M,
                 'Q': qrcode.constants.ERROR_CORRECT_Q,
                 'H': qrcode.constants.ERROR_CORRECT_H}

    qr = qrcode.QRCode(
        version=None,
        error_correction=error_map.get(error_level, qrcode.constants.ERROR_CORRECT_M),
        box_size=15,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    if style == 'rounded':
        img = qr.make_image(image_factory=StyledPilImage,
                            module_drawer=RoundedModuleDrawer(),
                            fill_color=fg_color, back_color=bg_color)
    else:
        img = qr.make_image(fill_color=fg_color, back_color=bg_color)

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return send_file(buffer, mimetype='image/png',
                     as_attachment=True, download_name='qrcode_CITNC.png')

if __name__ == '__main__':
    app.run(debug=True)
