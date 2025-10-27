from flask import Flask, render_template, jsonify, request, send_file
import os
import sys
from pathlib import Path
from datetime import datetime
import pytz

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from main import generate_once, list_categories
from app.config import CFG

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/categories')
def get_categories():
    """获取所有分类"""
    try:
        from app.data_loader import load_numbers_excel
        from app.used_storage import UsedStorage
        from app.selection import _unused_numbers_in_category

        df = load_numbers_excel(CFG.excel_file)
        store = UsedStorage(CFG.used_json)
        store.load()

        categories = []
        for cat in df['分类说明'].dropna().unique():
            total = int((df['分类说明'] == cat).sum())
            unused = len(_unused_numbers_in_category(df, store, cat))
            categories.append({
                'name': cat,
                'total': total,
                'unused': unused,
                'available': unused >= 9
            })

        return jsonify({'success': True, 'categories': categories})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/generate', methods=['POST'])
def generate_poster():
    """生成海报"""
    try:
        data = request.get_json() or {}
        category = data.get('category')  # None表示随机选择

        output_path = generate_once(category)

        if output_path:
            return jsonify({
                'success': True,
                'message': '海报生成成功！',
                'filename': output_path.name,
                'path': str(output_path)
            })
        else:
            return jsonify({'success': False, 'error': '生成失败，可能是号码不足'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/outputs')
def get_outputs():
    """获取输出文件列表"""
    try:
        output_dir = CFG.output_dir
        if not output_dir.exists():
            return jsonify({'success': True, 'files': []})

        files = []
        for file in output_dir.glob('*.jpg'):
            stat = file.stat()
            files.append({
                'name': file.name,
                'size': f"{stat.st_size / 1024:.1f} KB",
                'created': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            })

        # 按创建时间倒序
        files.sort(key=lambda x: x['created'], reverse=True)
        return jsonify({'success': True, 'files': files})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/download/<filename>')
def download_file(filename):
    """下载文件"""
    try:
        file_path = CFG.output_dir / filename
        if file_path.exists() and file_path.suffix == '.jpg':
            return send_file(str(file_path), as_attachment=True)
        else:
            return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)