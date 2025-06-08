import logging
from typing import Dict, List, Optional
import random

logger = logging.getLogger(__name__)

class TotoPredictor:
    def __init__(self):
        self.home_advantage = 5
        self.recent_matches_weight = 0.4
        self.ranking_weight = 0.3
        self.home_away_weight = 0.3
    
    def predict_matches(self, toto_info: Dict, team_data: Dict) -> List[Dict]:
        logger.info("試合予想を開始します")
        
        predictions = []
        match_scores = []
        
        for match in toto_info['matches']:
            home_team = match['home_team']
            away_team = match['away_team']
            
            home_stats = team_data.get(home_team, {})
            away_stats = team_data.get(away_team, {})
            
            prediction, confidence = self._predict_single_match(home_stats, away_stats)
            
            match_scores.append({
                'match_number': match['match_number'],
                'home_team': home_team,
                'away_team': away_team,
                'prediction': prediction,
                'confidence': confidence
            })
        
        match_scores.sort(key=lambda x: x['confidence'])
        
        draw_count = 0
        max_draws = 3
        
        for i, match_score in enumerate(match_scores):
            if draw_count < max_draws and i < len(match_scores) // 2:
                if match_score['confidence'] < 60:
                    match_score['prediction'] = '0'
                    draw_count += 1
            
            predictions.append({
                'match_number': match_score['match_number'],
                'home_team': match_score['home_team'],
                'away_team': match_score['away_team'],
                'prediction': match_score['prediction']
            })
        
        predictions.sort(key=lambda x: x['match_number'])
        
        logger.info(f"予想完了: {len(predictions)}試合")
        return predictions
    
    def _predict_single_match(self, home_stats: Dict, away_stats: Dict) -> tuple:
        try:
            home_score = self._calculate_team_score(home_stats, is_home=True)
            away_score = self._calculate_team_score(away_stats, is_home=False)
            
            score_diff = home_score - away_score
            confidence = min(abs(score_diff) * 2, 95)
            
            if score_diff > 5:
                return '1', confidence
            elif score_diff < -5:
                return '2', confidence
            else:
                return random.choice(['1', '0', '2']), max(confidence, 30)
                
        except Exception as e:
            logger.warning(f"予想計算エラー: {str(e)}")
            return random.choice(['1', '0', '2']), 50
    
    def _calculate_team_score(self, team_stats: Dict, is_home: bool) -> float:
        if not team_stats:
            return 50 + (self.home_advantage if is_home else 0)
        
        recent_score = self._calculate_recent_form_score(team_stats.get('recent_matches', []))
        ranking_score = self._calculate_ranking_score(team_stats.get('ranking', 10))
        venue_score = self._calculate_venue_score(team_stats, is_home)
        
        total_score = (
            recent_score * self.recent_matches_weight +
            ranking_score * self.ranking_weight +
            venue_score * self.home_away_weight
        )
        
        if is_home:
            total_score += self.home_advantage
        
        return total_score
    
    def _calculate_recent_form_score(self, recent_matches: List[Dict]) -> float:
        if not recent_matches:
            return 50
        
        total_points = 0
        total_goal_diff = 0
        
        for match in recent_matches[:5]:
            result = match.get('result', 'D')
            goals_for = match.get('goals_for', 1)
            goals_against = match.get('goals_against', 1)
            
            if result == 'W':
                total_points += 3
            elif result == 'D':
                total_points += 1
            
            total_goal_diff += (goals_for - goals_against)
        
        avg_points = total_points / len(recent_matches)
        avg_goal_diff = total_goal_diff / len(recent_matches)
        
        form_score = (avg_points / 3) * 60 + avg_goal_diff * 5 + 40
        
        return max(0, min(100, form_score))
    
    def _calculate_ranking_score(self, ranking: int) -> float:
        if ranking <= 0:
            ranking = 10
        
        ranking_score = max(0, 100 - (ranking - 1) * 4)
        return ranking_score
    
    def _calculate_venue_score(self, team_stats: Dict, is_home: bool) -> float:
        venue_key = 'home_stats' if is_home else 'away_stats'
        venue_stats = team_stats.get(venue_key, {'wins': 3, 'draws': 3, 'losses': 4})
        
        total_games = venue_stats['wins'] + venue_stats['draws'] + venue_stats['losses']
        if total_games == 0:
            return 50
        
        win_rate = venue_stats['wins'] / total_games
        venue_score = win_rate * 80 + 20
        
        return venue_score