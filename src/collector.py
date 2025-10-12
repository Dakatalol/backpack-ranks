import requests
from typing import List, Dict
from datetime import datetime

class BackpackCollector:
    BASE_URL = "https://api.backpack.exchange/wapi/v1/statistics/leaderboard/volume/week"

    def __init__(self):
        self.session = requests.Session()

    def fetch_leaderboard_page(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Fetch a single page of leaderboard data"""
        try:
            params = {
                'limit': limit,
                'offset': offset
            }

            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Normalize field names and add rank to each entry
            normalized_data = []
            for idx, entry in enumerate(data):
                normalized_entry = {
                    'rank': offset + idx + 1,
                    'user_alias': entry.get('userAlias', entry.get('user_alias', '')),
                    'volume': float(entry.get('volume', '0')),
                    'quote_symbol': entry.get('quoteSymbol', entry.get('quote_symbol', 'USDC'))
                }
                normalized_data.append(normalized_entry)

            return normalized_data

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data at offset {offset}: {e}")
            return []

    def fetch_full_leaderboard(self, max_entries: int = 1000, batch_size: int = 100) -> List[Dict]:
        """Fetch multiple pages of leaderboard data"""
        all_entries = []
        offset = 0

        print(f"Fetching leaderboard data (up to {max_entries} entries)...")

        while offset < max_entries:
            print(f"  Fetching entries {offset + 1} to {offset + batch_size}...")

            entries = self.fetch_leaderboard_page(limit=batch_size, offset=offset)

            if not entries:
                print(f"  No more data available at offset {offset}")
                break

            all_entries.extend(entries)
            offset += batch_size

            # If we got fewer entries than requested, we've reached the end
            if len(entries) < batch_size:
                print(f"  Reached end of leaderboard (got {len(entries)} entries)")
                break

        print(f"Successfully fetched {len(all_entries)} total entries")
        return all_entries

    @staticmethod
    def get_week_identifier() -> str:
        """Generate a week identifier string (e.g., '2024-W15')"""
        now = datetime.now()
        year, week, _ = now.isocalendar()
        return f"{year}-W{week:02d}"

    def collect_and_summarize(self, max_entries: int = 1000) -> Dict:
        """Fetch data and return summary statistics"""
        entries = self.fetch_full_leaderboard(max_entries=max_entries)

        if not entries:
            return {
                'success': False,
                'entries': [],
                'stats': {}
            }

        volumes = [entry['volume'] for entry in entries]

        stats = {
            'total_entries': len(entries),
            'total_volume': sum(volumes),
            'avg_volume': sum(volumes) / len(volumes) if volumes else 0,
            'min_volume': min(volumes) if volumes else 0,
            'max_volume': max(volumes) if volumes else 0,
            'median_volume': self._calculate_median(volumes),
            'week_identifier': self.get_week_identifier()
        }

        return {
            'success': True,
            'entries': entries,
            'stats': stats
        }

    @staticmethod
    def _calculate_median(values: List[float]) -> float:
        """Calculate median of a list of values"""
        if not values:
            return 0

        sorted_values = sorted(values)
        n = len(sorted_values)

        if n % 2 == 0:
            return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
        else:
            return sorted_values[n // 2]
