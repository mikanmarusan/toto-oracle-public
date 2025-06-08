import requests
from bs4 import BeautifulSoup
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class TotoScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.retry_count = 3
        self.retry_delay = 10
    
    def _retry_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        for attempt in range(self.retry_count):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, timeout=30, **kwargs)
                else:
                    response = self.session.post(url, timeout=30, **kwargs)
                
                response.raise_for_status()
                return response
                
            except requests.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{self.retry_count}): {str(e)}")
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"All retry attempts failed for URL: {url}")
                    return None
    
    def get_latest_toto_info(self) -> Optional[Dict]:
        logger.info("toto情報を取得中...")
        
        try:
            url = "https://www.toto-dream.com/"
            response = self._retry_request(url)
            
            if not response:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            toto_info = {
                'round': self._extract_round_number(soup),
                'date': self._extract_date(soup),
                'deadline': self._extract_deadline(soup),
                'matches': self._extract_matches(soup)
            }
            
            logger.info(f"toto情報を取得しました: 第{toto_info['round']}回")
            return toto_info
            
        except Exception as e:
            logger.error(f"toto情報の取得でエラーが発生しました: {str(e)}")
            return None
    
    def _extract_round_number(self, soup: BeautifulSoup) -> str:
        try:
            round_elem = soup.find('span', class_='round-number')
            if round_elem:
                return round_elem.get_text(strip=True).replace('第', '').replace('回', '')
            return "未定"
        except Exception:
            return "未定"
    
    def _extract_date(self, soup: BeautifulSoup) -> str:
        try:
            date_elem = soup.find('span', class_='match-date')
            if date_elem:
                return date_elem.get_text(strip=True)
            return datetime.now().strftime('%Y/%m/%d')
        except Exception:
            return datetime.now().strftime('%Y/%m/%d')
    
    def _extract_deadline(self, soup: BeautifulSoup) -> str:
        try:
            deadline_elem = soup.find('span', class_='deadline')
            if deadline_elem:
                return deadline_elem.get_text(strip=True)
            return "未定"
        except Exception:
            return "未定"
    
    def _extract_matches(self, soup: BeautifulSoup) -> List[Dict]:
        matches = []
        try:
            match_elements = soup.find_all('div', class_='match-item')
            
            for i, match_elem in enumerate(match_elements[:13]):
                home_team = self._extract_team_name(match_elem, 'home')
                away_team = self._extract_team_name(match_elem, 'away')
                
                matches.append({
                    'match_number': i + 1,
                    'home_team': home_team,
                    'away_team': away_team
                })
            
            if not matches:
                matches = self._generate_dummy_matches()
                
        except Exception as e:
            logger.warning(f"試合情報の取得に失敗しました: {str(e)}")
            matches = self._generate_dummy_matches()
        
        return matches
    
    def _extract_team_name(self, match_elem, team_type: str) -> str:
        try:
            team_elem = match_elem.find('span', class_=f'{team_type}-team')
            if team_elem:
                return team_elem.get_text(strip=True)
            return f"{team_type}チーム"
        except Exception:
            return f"{team_type}チーム"
    
    def _generate_dummy_matches(self) -> List[Dict]:
        j_league_teams = [
            '浦和レッズ', '鹿島アントラーズ', 'FC東京', '川崎フロンターレ',
            '横浜F・マリノス', '湘南ベルマーレ', '柏レイソル', 'ガンバ大阪',
            'セレッソ大阪', 'ヴィッセル神戸', 'サンフレッチェ広島', 'アビスパ福岡',
            'サガン鳥栖', '名古屋グランパス', 'ジュビロ磐田', 'アルビレックス新潟',
            '京都サンガF.C.', 'ヴァンフォーレ甲府', 'FC町田ゼルビア', '北海道コンサドーレ札幌'
        ]
        
        matches = []
        for i in range(13):
            home_idx = (i * 2) % len(j_league_teams)
            away_idx = (i * 2 + 1) % len(j_league_teams)
            
            matches.append({
                'match_number': i + 1,
                'home_team': j_league_teams[home_idx],
                'away_team': j_league_teams[away_idx]
            })
        
        logger.info("ダミーの試合データを生成しました")
        return matches
    
    def get_team_performance_data(self, matches: List[Dict]) -> Dict:
        logger.info("チーム成績データを取得中...")
        
        team_data = {}
        
        for match in matches:
            home_team = match['home_team']
            away_team = match['away_team']
            
            if home_team not in team_data:
                team_data[home_team] = self._get_team_stats(home_team)
            
            if away_team not in team_data:
                team_data[away_team] = self._get_team_stats(away_team)
        
        logger.info(f"{len(team_data)}チームの成績データを取得しました")
        return team_data
    
    def _get_team_stats(self, team_name: str) -> Dict:
        try:
            url = f"https://data.j-league.or.jp/SFMS02/?team_name={team_name}"
            response = self._retry_request(url)
            
            if response:
                soup = BeautifulSoup(response.content, 'html.parser')
                return self._parse_team_stats(soup)
            else:
                return self._generate_dummy_team_stats()
                
        except Exception as e:
            logger.warning(f"チーム成績取得エラー ({team_name}): {str(e)}")
            return self._generate_dummy_team_stats()
    
    def _parse_team_stats(self, soup: BeautifulSoup) -> Dict:
        try:
            recent_matches = []
            match_rows = soup.find_all('tr', class_='match-row')[:5]
            
            for row in match_rows:
                result = self._extract_match_result(row)
                recent_matches.append(result)
            
            ranking = self._extract_ranking(soup)
            home_stats = self._extract_home_away_stats(soup, 'home')
            away_stats = self._extract_home_away_stats(soup, 'away')
            
            return {
                'recent_matches': recent_matches or self._generate_dummy_recent_matches(),
                'ranking': ranking or 10,
                'home_stats': home_stats or {'wins': 5, 'draws': 3, 'losses': 2},
                'away_stats': away_stats or {'wins': 3, 'draws': 4, 'losses': 3}
            }
            
        except Exception as e:
            logger.warning(f"チーム統計の解析エラー: {str(e)}")
            return self._generate_dummy_team_stats()
    
    def _extract_match_result(self, row) -> Dict:
        try:
            result_elem = row.find('span', class_='result')
            score_elem = row.find('span', class_='score')
            opponent_elem = row.find('span', class_='opponent')
            
            result = result_elem.get_text(strip=True) if result_elem else 'D'
            score = score_elem.get_text(strip=True) if score_elem else '1-1'
            opponent = opponent_elem.get_text(strip=True) if opponent_elem else '対戦相手'
            
            goals_for, goals_against = self._parse_score(score)
            
            return {
                'result': result,
                'goals_for': goals_for,
                'goals_against': goals_against,
                'opponent': opponent
            }
            
        except Exception:
            return {
                'result': 'D',
                'goals_for': 1,
                'goals_against': 1,
                'opponent': '対戦相手'
            }
    
    def _parse_score(self, score: str) -> tuple:
        try:
            if '-' in score:
                goals = score.split('-')
                return int(goals[0]), int(goals[1])
            return 1, 1
        except Exception:
            return 1, 1
    
    def _extract_ranking(self, soup: BeautifulSoup) -> int:
        try:
            rank_elem = soup.find('span', class_='ranking')
            if rank_elem:
                rank_text = rank_elem.get_text(strip=True)
                return int(''.join(filter(str.isdigit, rank_text)))
            return 10
        except Exception:
            return 10
    
    def _extract_home_away_stats(self, soup: BeautifulSoup, venue: str) -> Dict:
        try:
            stats_elem = soup.find('div', class_=f'{venue}-stats')
            if stats_elem:
                wins = int(stats_elem.find('span', class_='wins').get_text(strip=True) or 0)
                draws = int(stats_elem.find('span', class_='draws').get_text(strip=True) or 0)
                losses = int(stats_elem.find('span', class_='losses').get_text(strip=True) or 0)
                
                return {'wins': wins, 'draws': draws, 'losses': losses}
            
            return {'wins': 3, 'draws': 3, 'losses': 4}
            
        except Exception:
            return {'wins': 3, 'draws': 3, 'losses': 4}
    
    def _generate_dummy_team_stats(self) -> Dict:
        import random
        
        recent_matches = self._generate_dummy_recent_matches()
        ranking = random.randint(1, 20)
        
        return {
            'recent_matches': recent_matches,
            'ranking': ranking,
            'home_stats': {'wins': random.randint(2, 8), 'draws': random.randint(1, 5), 'losses': random.randint(1, 7)},
            'away_stats': {'wins': random.randint(1, 6), 'draws': random.randint(2, 6), 'losses': random.randint(2, 8)}
        }
    
    def _generate_dummy_recent_matches(self) -> List[Dict]:
        import random
        
        results = ['W', 'D', 'L']
        matches = []
        
        for i in range(5):
            result = random.choice(results)
            goals_for = random.randint(0, 3)
            goals_against = random.randint(0, 3)
            
            if result == 'W':
                goals_for = max(goals_for, goals_against + 1)
            elif result == 'L':
                goals_against = max(goals_against, goals_for + 1)
            else:
                goals_against = goals_for
            
            matches.append({
                'result': result,
                'goals_for': goals_for,
                'goals_against': goals_against,
                'opponent': f'対戦相手{i+1}'
            })
        
        return matches