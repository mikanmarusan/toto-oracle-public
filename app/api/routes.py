from flask import Blueprint, jsonify
import logging

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

@api_bp.route('/run-batch', methods=['POST'])
def run_batch():
    try:
        from app.batch.scraper import TotoScraper
        from app.batch.predictor import TotoPredictor
        
        logger.info("バッチ処理を開始します")
        
        scraper = TotoScraper()
        predictor = TotoPredictor()
        
        toto_info = scraper.get_latest_toto_info()
        if not toto_info:
            return jsonify({'error': 'toto情報の取得に失敗しました'}), 500
            
        team_data = scraper.get_team_performance_data(toto_info['matches'])
        if not team_data:
            return jsonify({'error': 'チーム成績データの取得に失敗しました'}), 500
            
        predictions = predictor.predict_matches(toto_info, team_data)
        
        logger.info("バッチ処理が完了しました")
        
        return jsonify({
            'status': 'success',
            'toto_info': toto_info,
            'predictions': predictions
        }), 200
        
    except Exception as e:
        logger.error(f"バッチ処理でエラーが発生しました: {str(e)}")
        return jsonify({'error': f'バッチ処理でエラーが発生しました: {str(e)}'}), 500

@api_bp.route('/latest-prediction', methods=['GET'])
def get_latest_prediction():
    try:
        return jsonify({
            'message': '最新の予想データを取得する機能は未実装です',
            'status': 'not_implemented'
        }), 501
    except Exception as e:
        logger.error(f"予想データ取得でエラーが発生しました: {str(e)}")
        return jsonify({'error': str(e)}), 500