 dict):
        return 0
    
    count = 1
    for value in tree.values():
        if isinstance(value, dict):
            count += _count_tree_nodes(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    count += _count_tree_nodes(item)
    
    return count


def _convert_to_markdown(data: dict) -> str:
    """결과를 Markdown으로 변환"""
    md_lines = []
    
    # 제목
    md_lines.append("# TreeLLM Analysis Result")
    md_lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 메트릭
    if "metrics" in data:
        md_lines.append("\n## Metrics")
        metrics = data["metrics"]
        md_lines.append(f"- Total Duration: {metrics.get('total_duration', 0):.2f}s")
        md_lines.append(f"- API Calls: {metrics.get('api_calls', 0)}")
        
        if "step_durations" in metrics:
            md_lines.append("\n### Step Durations")
            for step, duration in metrics["step_durations"].items():
                md_lines.append(f"- {step}: {duration:.2f}s")
    
    # 최종 결과
    if "final" in data:
        md_lines.append("\n## Final Output")
        md_lines.append(data["final"])
    
    # 단계별 결과
    if "steps" in data:
        md_lines.append("\n## Processing Steps")
        for step in data["steps"]:
            md_lines.append(f"\n### Step {step.get('step', 'N/A')}: {step.get('name', 'Unknown')}")
            if "content" in step:
                content_str = json.dumps(step["content"], ensure_ascii=False, indent=2)
                if len(content_str) > 1000:
                    content_str = content_str[:1000] + "\n... (truncated)"
                md_lines.append(f"```json\n{content_str}\n```")
    
    return "\n".join(md_lines)


def _estimate_build_cost(config: TreeLLMConfig, text_length: int) -> float:
    """Build 단계 비용 추정"""
    # 7개 프롬프트, 각각 텍스트 + 프롬프트 템플릿
    input_tokens = (text_length / 4) * 7  # 각 프롬프트마다
    output_tokens = config.model.max_tokens * 7
    
    return _calculate_api_cost(config.model.model_name, input_tokens, output_tokens)


def _estimate_audit_cost(config: TreeLLMConfig, text_length: int) -> float:
    """Audit 단계 비용 추정"""
    input_tokens = text_length / 4 + 1000  # 텍스트 + 트리 구조
    output_tokens = 2000
    
    return _calculate_api_cost(config.model.model_name, input_tokens, output_tokens)


def _estimate_edit1_cost(config: TreeLLMConfig, text_length: int) -> float:
    """Edit Pass 1 비용 추정"""
    # 섹션별 편집 (평균 7개 섹션 가정)
    input_tokens = (text_length / 7 / 4) * 7
    output_tokens = (text_length / 7 / 4) * 7
    
    return _calculate_api_cost(config.model.model_name, input_tokens, output_tokens)


def _estimate_global_check_cost(config: TreeLLMConfig, text_length: int) -> float:
    """Global Check 비용 추정"""
    input_tokens = text_length / 4
    output_tokens = 1500
    
    return _calculate_api_cost(config.model.model_name, input_tokens, output_tokens)


def _estimate_edit2_cost(config: TreeLLMConfig, text_length: int) -> float:
    """Edit Pass 2 비용 추정"""
    input_tokens = text_length / 4
    output_tokens = text_length / 4
    
    return _calculate_api_cost(config.model.model_name, input_tokens, output_tokens)


def _calculate_api_cost(model: str, input_tokens: float, output_tokens: float) -> float:
    """API 비용 계산"""
    prices = {
        "gpt-4o": {"input": 0.03, "output": 0.06},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.001, "output": 0.002}
    }
    
    model_prices = prices.get(model, prices["gpt-4o"])
    
    return (input_tokens * model_prices["input"] + 
            output_tokens * model_prices["output"]) / 1000


# ═══════════════════════════════════════════════════════════════
# 에러 핸들러
# ═══════════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {str(e)}")
    return jsonify({"error": "Internal server error"}), 500


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File too large"}), 413


# ═══════════════════════════════════════════════════════════════
# CLI 지원
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='TreeLLM API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', type=int, default=5001, help='Port to bind')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    
    args = parser.parse_args()
    
    # API 키 확인
    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your-api-key-here":
        logger.warning("⚠️  OpenAI API key not configured properly!")
        logger.warning("Set OPENAI_API_KEY environment variable or update .env file")
    
    logger.info(f"Starting TreeLLM API Server on {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)
