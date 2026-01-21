"""
Results Repository
Data access for analysis results
"""

import json
from pathlib import Path
from typing import List, Optional
from models.analysis_result import AnalysisResult
from utils.exceptions import DatabaseError
import logging

logger = logging.getLogger(__name__)


class ResultsRepository:
    """Manages persistence of analysis results"""
    
    def __init__(self, results_dir: str = "./results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.results_dir / "index.json"
        self._index: List[dict] = self._load_index()
    
    def _load_index(self) -> List[dict]:
        """Load results index"""
        try:
            if self.index_file.exists():
                with open(self.index_file, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load results index: {e}")
        
        return []
    
    def _save_index(self) -> None:
        """Save results index"""
        try:
            with open(self.index_file, 'w') as f:
                json.dump(self._index, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save results index: {e}")
            raise DatabaseError(f"Failed to save results index: {e}")
    
    def save(self, result: AnalysisResult) -> None:
        """
        Save an analysis result
        
        Args:
            result: AnalysisResult to save
        """
        result_id = Path(result.image_path).stem
        result_file = self.results_dir / f"{result_id}_result.json"
        
        try:
            with open(result_file, 'w') as f:
                json.dump(result.to_dict(), f, indent=2)
            
            # Update index
            index_entry = {
                'id': result_id,
                'image': result.image_filename,
                'timestamp': result.timestamp,
                'porosity': result.porosity_percent,
                'file': str(result_file)
            }
            
            # Remove existing entry if present
            self._index = [e for e in self._index if e['id'] != result_id]
            self._index.append(index_entry)
            self._save_index()
            
            logger.debug(f"Saved result for {result.image_filename}")
        except IOError as e:
            logger.error(f"Failed to save result: {e}")
            raise DatabaseError(f"Failed to save result: {e}")
    
    def find_by_image_name(self, image_filename: str) -> Optional[AnalysisResult]:
        """Find result by image filename"""
        stem = Path(image_filename).stem
        result_file = self.results_dir / f"{stem}_result.json"
        
        if result_file.exists():
            try:
                with open(result_file, 'r') as f:
                    data = json.load(f)
                    return AnalysisResult.from_dict(data)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load result {result_file}: {e}")
        
        return None
    
    def find_all(self) -> List[AnalysisResult]:
        """Get all analysis results"""
        results = []
        for entry in self._index:
            result_file = Path(entry['file'])
            if result_file.exists():
                try:
                    with open(result_file, 'r') as f:
                        data = json.load(f)
                        results.append(AnalysisResult.from_dict(data))
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"Failed to load result {result_file}: {e}")
        
        return results
    
    def count(self) -> int:
        """Get total number of results"""
        return len(self._index)
    
    def get_latest(self, limit: int = 10) -> List[AnalysisResult]:
        """Get most recent results"""
        results = self.find_all()
        # Sort by timestamp descending
        results.sort(key=lambda r: r.timestamp, reverse=True)
        return results[:limit]
