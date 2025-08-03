"""
TreeLLM Flask App - V2
───────────────────────
하이퍼파라미터 최적화가 적용된 웹 인터페이스
"""

from flask import Flask, request, jsonify, render_template, send_file, Response
from flask_cors import CORS
import os
from pathlib import Path
import json
from datetime import datetime
import logging
from werkzeug.utils import secure_filename

# V2 모듈 임포트
from OrchestratorV2 import OrchestratorV2
from config import load_config, PRESETS

app = Flask(__name__)
CORS(app)

# 설정
UPLOAD_FOLDER = Path("uploads")
RESULT_FOLDER = Path("sample")
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'md'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

UPLOAD_FOLDER.mkdir(exist_ok=True)
RESULT_FOLDER.mkdir(exist_ok=True)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def allowed_file(filename):
    """파일 확장자 검증"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_file(filepath):
    """파일에서 텍스트 추출"""
    ext = filepath.suffix.lower()
    
    if ext == '.txt' or ext == '.md':
        return filepath.read_text(encoding='utf-8')
    elif ext == '.pdf':
        # PyMuPDF 사용
        import fitz
        text = ""
        with fitz.open(str(filepath)) as doc:
            for page in doc:
                text += page.get_text()
        return text
    elif ext == '.docx':
        # python-docx 사용
        from docx import Document
        doc = Document(str(filepath))
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        raise ValueError(f"Unsupported file type: {ext}")


@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')


@app.route('/api/presets', methods=['GET'])
def get_presets():
    """사용 가능한 프리셋 목록"""
    preset_info = {
        "fast": {
            "name": "Fast",
            "description": "빠른 처리, 기본적인 분석",
            "temperature": 0.5,
            "parallel": True,
            "workers": 5
        },
        "balanced": {
            "name": "Balanced",
            "description": "균형잡힌 속도와 품질",
            "temperature": 0.3,
            "parallel": True,
            "workers": 3
        },
        "thorough": {
            "name": "Thorough",
            "description": "세밀한 분석, 높은 품질",
            "temperature": 0.2,
            "parallel": True,
            "workers": 2
        },
        "research": {
            "name": "Research",
            "description": "연구용 최고 품질 분석",
            "temperature": 0.1,
            "parallel": True,
            "workers": 2
        }
    }
    return jsonify(preset_info)


@app.route('/api/config/<preset>', methods=['GET'])
def get_config(preset):
    """특정 프리셋의 상세 설정"""
    try:
        config = load_config(preset)
        return jsonify({
            "model": config.model.__dict__,
            "split": config.split.__dict__,
            "build": config.build.__dict__,
            "fuse": config.fuse.__dict__,
            "audit": config.audit.__dict__,
            "edit": config.edit.__dict__,
            "global_check": config.global_check.__dict__,
            "output": config.output.__dict__
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """논문 분석 실행"""
    try:
        # 파일 검증
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400
        
        # 파일 크기 검증
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({"error": f"File too large. Max size: {MAX_FILE_SIZE/1024/1024}MB"}), 400
        
        # 파일 저장
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        filepath = UPLOAD_FOLDER / filename
        file.save(str(filepath))
        
        # 텍스트 추출
        try:
            text = extract_text_from_file(filepath)
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return jsonify({"error": f"Failed to extract text: {str(e)}"}), 400
        
        # 임시 텍스트 파일 생성
        text_file = UPLOAD_FOLDER / f"{timestamp}_text.txt"
        text_file.write_text(text, encoding='utf-8')
        
        # 설정 파싱
        preset = request.form.get('preset', 'balanced')
        custom_params = request.form.get('custom_params')
        
        # 커스텀 파라미터 적용
        overrides = {}
        if custom_params:
            try:
                overrides = json.loads(custom_params)
            except json.JSONDecodeError:
                logger.warning("Invalid custom parameters, using defaults")
        
        # Orchestrator 실행
        config = load_config(preset, **overrides)
        orchestrator = OrchestratorV2(config)
        
        result = orchestrator.run(str(text_file))
        
        # 결과 반환
        return jsonify({
            "success": True,
            "result": result["final"],
            "metrics": result["metrics"],
            "steps": result["steps"],
            "files": {
                "json": f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "final": f"final_paper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{config.output.output_format}"
            }
        })
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        # 임시 파일 정리
        if 'filepath' in locals() and filepath.exists():
            filepath.unlink()
        if 'text_file' in locals() and text_file.exists():
            text_file.unlink()


@app.route('/api/analyze/stream', methods=['POST'])
def analyze_stream():
    """스트리밍 모드로 논문 분석"""
    try:
        # 파일 처리 (위와 동일)
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if not file or not allowed_file(file.filename):
            return jsonify({"error": "Invalid file"}), 400
        
        # 파일 저장 및 텍스트 추출
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        filepath = UPLOAD_FOLDER / filename
        file.save(str(filepath))
        
        text = extract_text_from_file(filepath)
        text_file = UPLOAD_FOLDER / f"{timestamp}_text.txt"
        text_file.write_text(text, encoding='utf-8')
        
        # 설정 로드
        preset = request.form.get('preset', 'balanced')
        custom_params = request.form.get('custom_params', '{}')
        overrides = json.loads(custom_params) if custom_params else {}
        
        config = load_config(preset, **overrides)
        orchestrator = OrchestratorV2(config)
        
        def generate():
            """SSE 스트림 생성"""
            try:
                for update in orchestrator.run_stream(str(text_file)):
                    yield f"data: {update}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
            finally:
                # 정리
                if filepath.exists():
                    filepath.unlink()
                if text_file.exists():
                    text_file.unlink()
        
        return Response(
            generate(),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no"
            }
        )
        
    except Exception as e:
        logger.error(f"Stream analysis failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """결과 파일 다운로드"""
    try:
        # 보안을 위한 파일명 검증
        filename = secure_filename(filename)
        filepath = RESULT_FOLDER / filename
        
        if not filepath.exists():
            return jsonify({"error": "File not found"}), 404
        
        return send_file(
            str(filepath),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/status', methods=['GET'])
def status():
    """서비스 상태 확인"""
    try:
        # OpenAI API 키 확인
        api_key_set = bool(os.getenv("OPENAI_API_KEY"))
        
        # 디스크 공간 확인
        import shutil
        stat = shutil.disk_usage(str(Path.cwd()))
        disk_free_gb = stat.free / (1024**3)
        
        return jsonify({
            "status": "healthy",
            "api_key_configured": api_key_set,
            "disk_free_gb": round(disk_free_gb, 2),
            "upload_folder": str(UPLOAD_FOLDER),
            "result_folder": str(RESULT_FOLDER)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """파일 크기 초과 에러 처리"""
    return jsonify({
        "error": f"File too large. Maximum size: {MAX_FILE_SIZE/1024/1024}MB"
    }), 413


@app.errorhandler(500)
def internal_error(error):
    """내부 서버 에러 처리"""
    logger.error(f"Internal error: {error}")
    return jsonify({
        "error": "Internal server error"
    }), 500


if __name__ == '__main__':
    # 환경 변수 확인
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set!")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
    
    # 개발 서버 실행
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        threaded=True
    )
