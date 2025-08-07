"""
Enhanced TreeLLM Flask App - V3
───────────────────────────────
Web interface with optimized hyperparameters and quality metrics
"""

from flask import Flask, request, jsonify, render_template, send_file, Response, session
from flask_cors import CORS
import os
from pathlib import Path
import json
from datetime import datetime
import logging
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import uuid
from typing import Dict, Any, Optional
import time
import threading
from queue import Queue

# Load environment variables
load_dotenv()

# Import enhanced V3 modules
from Orchestrator import EnhancedOrchestratorV3
from config import load_config, TreeLLMConfig

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Configuration
UPLOAD_FOLDER = Path("uploads")
RESULT_FOLDER = Path("results")
CACHE_FOLDER = Path("cache")
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'md'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Create necessary directories
for folder in [UPLOAD_FOLDER, RESULT_FOLDER, CACHE_FOLDER]:
    folder.mkdir(exist_ok=True)

# Enhanced logging setup
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app_enhanced.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Store active orchestrator sessions
active_sessions = {}
progress_queues = {}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_size(file):
    """Get file size"""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size


class ProgressTracker:
    """Track pipeline progress for real-time updates"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.progress = {
            "current_stage": "",
            "stage_number": 0,
            "total_stages": 7,
            "percentage": 0,
            "message": "",
            "start_time": time.time(),
            "estimated_time_remaining": None,
            "quality_score": None,
            "stage_details": {}
        }
    
    def update(self, stage_name: str, stage_number: int, message: str = ""):
        """Update progress information"""
        self.progress["current_stage"] = stage_name
        self.progress["stage_number"] = stage_number
        self.progress["percentage"] = int((stage_number / self.progress["total_stages"]) * 100)
        self.progress["message"] = message
        
        # Estimate time remaining
        elapsed = time.time() - self.progress["start_time"]
        if stage_number > 0:
            avg_per_stage = elapsed / stage_number
            remaining_stages = self.progress["total_stages"] - stage_number
            self.progress["estimated_time_remaining"] = avg_per_stage * remaining_stages
    
    def get_progress(self) -> Dict:
        """Get current progress"""
        return self.progress.copy()


@app.route('/')
def index():
    """Render main page"""
    # Check if enhanced template exists, otherwise use basic one
    try:
        return render_template('index_enhanced.html')
    except:
        # Fall back to existing template if available
        try:
            return render_template('index.html')
        except:
            # Return a simple HTML response if no template exists
            return '''
            <!DOCTYPE html>
            <html>
            <head><title>TreeLLM V3</title></head>
            <body>
                <h1>TreeLLM V3 Enhanced</h1>
                <p>API is running. Use the API endpoints directly or create a frontend.</p>
                <ul>
                    <li>POST /api/upload - Upload a file</li>
                    <li>POST /api/analyze - Start analysis</li>
                    <li>GET /api/progress/[session_id] - Check progress</li>
                    <li>GET /api/results/[session_id] - Get results</li>
                </ul>
            </body>
            </html>
            '''


@app.route('/api/presets', methods=['GET'])
def get_presets():
    """Get available configuration presets"""
    presets = {
        "fast": {
            "name": "Fast Processing",
            "description": "Quick draft analysis using GPT-3.5-turbo",
            "estimated_time": "2-3 minutes",
            "quality": "Draft",
            "cost": "$"
        },
        "balanced": {
            "name": "Balanced (Recommended)",
            "description": "Optimized balance of quality and speed",
            "estimated_time": "5-7 minutes",
            "quality": "Good",
            "cost": "$$"
        },
        "precision": {
            "name": "High Precision",
            "description": "Publication-quality analysis",
            "estimated_time": "10-12 minutes",
            "quality": "Excellent",
            "cost": "$$$"
        },
        "research": {
            "name": "Research Grade",
            "description": "Maximum quality for academic research",
            "estimated_time": "15-20 minutes",
            "quality": "Best",
            "cost": "$$$$"
        }
    }
    return jsonify(presets)


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload with validation"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Check file size
        file_size = get_file_size(file)
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': f'File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB'}), 400
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        session_id = str(uuid.uuid4())[:8]
        filename = secure_filename(file.filename)
        unique_filename = f"{timestamp}_{session_id}_{filename}"
        filepath = UPLOAD_FOLDER / unique_filename
        
        # Save file
        file.save(filepath)
        logger.info(f"File uploaded: {unique_filename}")
        
        # Analyze file content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            word_count = len(content.split())
            char_count = len(content)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'filename': unique_filename,
            'original_name': filename,
            'file_info': {
                'size': file_size,
                'word_count': word_count,
                'char_count': char_count,
                'estimated_tokens': word_count * 1.3  # Rough estimate
            }
        })
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_paper():
    """Start paper analysis with enhanced orchestrator"""
    try:
        data = request.json
        session_id = data.get('session_id')
        filename = data.get('filename')
        preset = data.get('preset', 'balanced')
        
        # Advanced options
        enable_cache = data.get('enable_cache', True)
        enable_metrics = data.get('enable_metrics', True)
        save_intermediate = data.get('save_intermediate', True)
        
        if not session_id or not filename:
            return jsonify({'error': 'Missing session_id or filename'}), 400
        
        filepath = UPLOAD_FOLDER / filename
        if not filepath.exists():
            return jsonify({'error': 'File not found'}), 404
        
        # Initialize progress tracker
        tracker = ProgressTracker(session_id)
        progress_queues[session_id] = tracker
        
        # Start analysis in background thread
        def run_analysis():
            try:
                logger.info(f"Starting analysis for session {session_id} with preset {preset}")
                
                # Create orchestrator with enhanced settings
                orchestrator = EnhancedOrchestratorV3(
                    preset=preset,
                    enable_metrics=enable_metrics,
                    enable_caching=enable_cache
                )
                
                # Store in active sessions
                active_sessions[session_id] = {
                    'orchestrator': orchestrator,
                    'start_time': datetime.now(),
                    'status': 'running',
                    'preset': preset
                }
                
                # Update progress for each stage
                def update_stage(stage_name, stage_num):
                    tracker.update(stage_name, stage_num, f"Processing {stage_name}...")
                
                # Hook into orchestrator logging to track progress
                original_log = orchestrator.log
                def enhanced_log(message, level="INFO", stage=None):
                    original_log(message, level, stage)
                    
                    # Update progress based on stage
                    if "Starting split" in message:
                        update_stage("Split", 1)
                    elif "Starting build" in message:
                        update_stage("Build", 2)
                    elif "Starting fuse" in message:
                        update_stage("Fuse", 3)
                    elif "Starting audit" in message:
                        update_stage("Audit", 4)
                    elif "Starting edit_pass1" in message:
                        update_stage("Edit Pass 1", 5)
                    elif "Starting global_check" in message:
                        update_stage("Global Check", 6)
                    elif "Starting edit_pass2" in message:
                        update_stage("Edit Pass 2", 7)
                
                orchestrator.log = enhanced_log
                
                # Run analysis
                result = orchestrator.run(str(filepath), save_intermediate=save_intermediate)
                
                # Update final status
                active_sessions[session_id]['status'] = 'completed'
                active_sessions[session_id]['result'] = result
                active_sessions[session_id]['end_time'] = datetime.now()
                
                # Extract quality score
                if 'quality_metrics' in result:
                    tracker.progress['quality_score'] = result['quality_metrics']['overall_score']
                
                tracker.update("Complete", 7, "Analysis completed successfully!")
                
                logger.info(f"Analysis completed for session {session_id}")
                
            except Exception as e:
                logger.error(f"Analysis error for session {session_id}: {e}")
                active_sessions[session_id]['status'] = 'error'
                active_sessions[session_id]['error'] = str(e)
                tracker.update("Error", tracker.progress['stage_number'], f"Error: {str(e)}")
        
        # Start background thread
        thread = threading.Thread(target=run_analysis)
        thread.start()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Analysis started',
            'preset': preset
        })
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/progress/<session_id>', methods=['GET'])
def get_progress(session_id):
    """Get real-time progress updates"""
    if session_id not in progress_queues:
        return jsonify({'error': 'Session not found'}), 404
    
    tracker = progress_queues[session_id]
    progress = tracker.get_progress()
    
    # Add session status
    if session_id in active_sessions:
        progress['status'] = active_sessions[session_id]['status']
        
        if active_sessions[session_id]['status'] == 'completed':
            result = active_sessions[session_id].get('result', {})
            progress['quality_score'] = result.get('quality_metrics', {}).get('overall_score')
            progress['total_duration'] = result.get('performance', {}).get('total_duration')
    
    return jsonify(progress)


@app.route('/api/results/<session_id>', methods=['GET'])
def get_results(session_id):
    """Get analysis results"""
    if session_id not in active_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = active_sessions[session_id]
    
    if session['status'] != 'completed':
        return jsonify({'error': 'Analysis not completed', 'status': session['status']}), 202
    
    result = session.get('result', {})
    
    # Format results for frontend
    formatted_result = {
        'session_id': session_id,
        'preset': session['preset'],
        'start_time': session['start_time'].isoformat(),
        'end_time': session['end_time'].isoformat(),
        'duration': (session['end_time'] - session['start_time']).total_seconds(),
        'quality_metrics': result.get('quality_metrics', {}),
        'performance': result.get('performance', {}),
        'stages': result.get('stages', {}),
        'final_output': result.get('final_output', {})
    }
    
    return jsonify(formatted_result)


@app.route('/api/download/<session_id>', methods=['GET'])
def download_results(session_id):
    """Download analysis results as JSON"""
    if session_id not in active_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = active_sessions[session_id]
    
    if session['status'] != 'completed':
        return jsonify({'error': 'Analysis not completed'}), 202
    
    result = session.get('result', {})
    
    # Create downloadable file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"treellm_analysis_{session_id}_{timestamp}.json"
    filepath = RESULT_FOLDER / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
    
    return send_file(filepath, as_attachment=True, download_name=filename)


@app.route('/api/test-config', methods=['POST'])
def test_configuration():
    """Test custom hyperparameter configuration"""
    try:
        data = request.json
        
        # Create custom config
        config = TreeLLMConfig()
        config.model.temperature = data.get('temperature', 0.3)
        config.model.top_p = data.get('top_p', 0.3)
        config.model.max_tokens = data.get('max_tokens', 4096)
        config.model.frequency_penalty = data.get('frequency_penalty', 0.0)
        config.model.presence_penalty = data.get('presence_penalty', 0.0)
        
        # Validate config
        try:
            config.validate()
            return jsonify({
                'valid': True,
                'message': 'Configuration is valid',
                'estimated_quality': 'Custom',
                'config': {
                    'temperature': config.model.temperature,
                    'top_p': config.model.top_p,
                    'max_tokens': config.model.max_tokens,
                    'frequency_penalty': config.model.frequency_penalty,
                    'presence_penalty': config.model.presence_penalty
                }
            })
        except ValueError as e:
            return jsonify({
                'valid': False,
                'message': str(e)
            }), 400
            
    except Exception as e:
        logger.error(f"Config test error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/metrics/<session_id>', methods=['GET'])
def get_metrics(session_id):
    """Get detailed quality metrics for completed analysis"""
    if session_id not in active_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = active_sessions[session_id]
    
    if session['status'] != 'completed':
        return jsonify({'error': 'Analysis not completed'}), 202
    
    result = session.get('result', {})
    metrics = result.get('quality_metrics', {})
    performance = result.get('performance', {})
    
    # Calculate additional metrics
    response = {
        'quality': {
            'overall_score': metrics.get('overall_score', 0),
            'accuracy': metrics.get('detailed', {}).get('accuracy', {}),
            'completeness': metrics.get('detailed', {}).get('completeness', {}),
            'consistency': metrics.get('detailed', {}).get('consistency', {})
        },
        'performance': {
            'total_duration': performance.get('total_duration', 0),
            'stage_durations': performance.get('stage_metrics', {}),
            'total_api_calls': performance.get('total_api_calls', 0),
            'total_tokens': performance.get('total_tokens', 0),
            'estimated_cost': performance.get('estimated_cost', 0)
        },
        'recommendations': []
    }
    
    # Generate recommendations based on metrics
    overall_score = metrics.get('overall_score', 0)
    if overall_score < 0.5:
        response['recommendations'].append("Consider using 'precision' or 'research' preset for better quality")
    elif overall_score < 0.7:
        response['recommendations'].append("Results are good, but 'precision' preset might improve quality")
    else:
        response['recommendations'].append("Excellent results achieved with current settings")
    
    return jsonify(response)


@app.route('/api/compare', methods=['POST'])
def compare_presets():
    """Compare multiple presets on the same document"""
    try:
        data = request.json
        filename = data.get('filename')
        presets_to_compare = data.get('presets', ['fast', 'balanced', 'precision'])
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        filepath = UPLOAD_FOLDER / filename
        if not filepath.exists():
            return jsonify({'error': 'File not found'}), 404
        
        comparison_id = str(uuid.uuid4())[:8]
        
        def run_comparison():
            results = {}
            
            for preset in presets_to_compare:
                logger.info(f"Running comparison with preset: {preset}")
                
                orchestrator = EnhancedOrchestratorV3(
                    preset=preset,
                    enable_metrics=True,
                    enable_caching=False  # Disable cache for fair comparison
                )
                
                try:
                    result = orchestrator.run(str(filepath), save_intermediate=False)
                    
                    results[preset] = {
                        'quality_score': result.get('quality_metrics', {}).get('overall_score', 0),
                        'duration': result.get('performance', {}).get('total_duration', 0),
                        'tokens': result.get('performance', {}).get('total_tokens', 0),
                        'success': True
                    }
                except Exception as e:
                    results[preset] = {
                        'error': str(e),
                        'success': False
                    }
            
            # Store comparison results
            active_sessions[comparison_id] = {
                'type': 'comparison',
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
        
        # Run in background
        thread = threading.Thread(target=run_comparison)
        thread.start()
        
        return jsonify({
            'success': True,
            'comparison_id': comparison_id,
            'message': 'Comparison started'
        })
        
    except Exception as e:
        logger.error(f"Comparison error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/comparison/<comparison_id>', methods=['GET'])
def get_comparison_results(comparison_id):
    """Get preset comparison results"""
    if comparison_id not in active_sessions:
        return jsonify({'error': 'Comparison not found'}), 404
    
    session = active_sessions[comparison_id]
    
    if session.get('type') != 'comparison':
        return jsonify({'error': 'Not a comparison session'}), 400
    
    return jsonify(session.get('results', {}))


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '3.0',
        'active_sessions': len(active_sessions),
        'timestamp': datetime.now().isoformat()
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Check for API key
    if not os.environ.get('OPENAI_API_KEY'):
        logger.warning("OPENAI_API_KEY not found in environment variables")
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5001))
    
    logger.info(f"Starting Enhanced TreeLLM Flask App on port {port}")
    logger.info("Available presets: fast, balanced, precision, research")
    
    # Run app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
