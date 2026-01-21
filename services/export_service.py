"""
Export Service
Business logic for exporting analysis results and reports
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from models.analysis_result import AnalysisResult
from services.quality_control_service import QCEvaluation
from utils.exceptions import ExportError
from utils.logger import get_logger

# Import existing export engine
try:
    from export_reporting import ExportEngine
    EXPORT_AVAILABLE = True
except ImportError:
    EXPORT_AVAILABLE = False
    logger = get_logger(__name__)
    logger.warning("ExportEngine not available - export features disabled")

logger = get_logger(__name__)


class ExportResult:
    """Result of an export operation"""

    def __init__(self,
                 file_path: Path,
                 format: str,
                 record_count: int,
                 success: bool = True,
                 error_message: str = ""):
        self.file_path = file_path
        self.format = format
        self.record_count = record_count
        self.success = success
        self.error_message = error_message

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "file_path": str(self.file_path),
            "format": self.format,
            "record_count": self.record_count,
            "success": self.success,
            "error_message": self.error_message
        }


class ExportService:
    """
    Service for exporting analysis results and generating reports.

    Provides business logic for:
    - CSV export of analysis results
    - Excel export with charts
    - PDF report generation
    - Batch export operations
    - Export validation and error handling
    """

    def __init__(self, output_dir: str = "./output"):
        """
        Initialize the export service.

        Args:
            output_dir: Directory for exported files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if EXPORT_AVAILABLE:
            self.export_engine = ExportEngine(str(self.output_dir))
        else:
            self.export_engine = None

    def export_csv(self,
                  results: List[AnalysisResult],
                  filename: Optional[str] = None) -> ExportResult:
        """
        Export analysis results to CSV format.

        Args:
            results: List of AnalysisResult objects
            filename: Optional filename (auto-generated if None)

        Returns:
            ExportResult with operation details
        """
        if not EXPORT_AVAILABLE or not self.export_engine:
            return ExportResult(
                file_path=Path(""),
                format="csv",
                record_count=0,
                success=False,
                error_message="Export engine not available"
            )

        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"analysis_results_{timestamp}.csv"

            # Convert results to dict format expected by export engine
            result_dicts = [result.to_dict() for result in results]

            # Export using existing engine
            exported_path = self.export_engine.export_to_csv(result_dicts, filename)

            if exported_path:
                return ExportResult(
                    file_path=exported_path,
                    format="csv",
                    record_count=len(results),
                    success=True
                )
            else:
                return ExportResult(
                    file_path=Path(""),
                    format="csv",
                    record_count=0,
                    success=False,
                    error_message="Export failed"
                )

        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            return ExportResult(
                file_path=Path(""),
                format="csv",
                record_count=0,
                success=False,
                error_message=str(e)
            )

    def export_excel(self,
                    results: List[AnalysisResult],
                    filename: Optional[str] = None) -> ExportResult:
        """
        Export analysis results to Excel format with charts.

        Args:
            results: List of AnalysisResult objects
            filename: Optional filename (auto-generated if None)

        Returns:
            ExportResult with operation details
        """
        if not EXPORT_AVAILABLE or not self.export_engine:
            return ExportResult(
                file_path=Path(""),
                format="excel",
                record_count=0,
                success=False,
                error_message="Export engine not available"
            )

        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"analysis_results_{timestamp}.xlsx"

            # Convert results to dict format expected by export engine
            result_dicts = [result.to_dict() for result in results]

            # Export using existing engine
            exported_path = self.export_engine.export_to_excel(result_dicts, filename)

            if exported_path:
                return ExportResult(
                    file_path=exported_path,
                    format="excel",
                    record_count=len(results),
                    success=True
                )
            else:
                return ExportResult(
                    file_path=Path(""),
                    format="excel",
                    record_count=0,
                    success=False,
                    error_message="Export failed"
                )

        except Exception as e:
            logger.error(f"Excel export failed: {e}")
            return ExportResult(
                file_path=Path(""),
                format="excel",
                record_count=0,
                success=False,
                error_message=str(e)
            )

    def export_pdf(self,
                  results: List[AnalysisResult],
                  evaluations: Optional[List[QCEvaluation]] = None,
                  filename: Optional[str] = None) -> ExportResult:
        """
        Export analysis results to PDF report format.

        Args:
            results: List of AnalysisResult objects
            evaluations: Optional QC evaluations for enhanced reporting
            filename: Optional filename (auto-generated if None)

        Returns:
            ExportResult with operation details
        """
        if not EXPORT_AVAILABLE or not self.export_engine:
            return ExportResult(
                file_path=Path(""),
                format="pdf",
                record_count=0,
                success=False,
                error_message="Export engine not available"
            )

        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"analysis_report_{timestamp}.pdf"

            # Convert results to dict format expected by export engine
            result_dicts = [result.to_dict() for result in results]

            # Export using existing engine
            exported_path = self.export_engine.export_to_pdf(result_dicts, filename)

            if exported_path:
                return ExportResult(
                    file_path=exported_path,
                    format="pdf",
                    record_count=len(results),
                    success=True
                )
            else:
                return ExportResult(
                    file_path=Path(""),
                    format="pdf",
                    record_count=0,
                    success=False,
                    error_message="Export failed"
                )

        except Exception as e:
            logger.error(f"PDF export failed: {e}")
            return ExportResult(
                file_path=Path(""),
                format="pdf",
                record_count=0,
                success=False,
                error_message=str(e)
            )

    def export_batch(self,
                    results: List[AnalysisResult],
                    evaluations: Optional[List[QCEvaluation]] = None,
                    base_filename: Optional[str] = None) -> List[ExportResult]:
        """
        Export analysis results in multiple formats.

        Args:
            results: List of AnalysisResult objects
            evaluations: Optional QC evaluations
            base_filename: Base filename for all exports

        Returns:
            List of ExportResult objects for each format
        """
        export_results = []

        # Generate base filename
        if not base_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"batch_analysis_{timestamp}"

        # Export CSV
        csv_result = self.export_csv(results, f"{base_filename}.csv")
        export_results.append(csv_result)

        # Export Excel
        excel_result = self.export_excel(results, f"{base_filename}.xlsx")
        export_results.append(excel_result)

        # Export PDF
        pdf_result = self.export_pdf(results, evaluations, f"{base_filename}.pdf")
        export_results.append(pdf_result)

        successful_exports = sum(1 for r in export_results if r.success)
        logger.info(f"Batch export complete: {successful_exports}/{len(export_results)} formats successful")

        return export_results

    def get_export_formats(self) -> List[Dict[str, Any]]:
        """
        Get available export formats and their capabilities.

        Returns:
            List of format information dictionaries
        """
        formats = [
            {
                "format": "csv",
                "name": "CSV (Spreadsheet)",
                "description": "Comma-separated values for spreadsheet analysis",
                "available": EXPORT_AVAILABLE,
                "supports_charts": False,
                "supports_multiple_sheets": False
            },
            {
                "format": "excel",
                "name": "Excel (.xlsx)",
                "description": "Excel workbook with charts and multiple sheets",
                "available": EXPORT_AVAILABLE,
                "supports_charts": True,
                "supports_multiple_sheets": True
            },
            {
                "format": "pdf",
                "name": "PDF Report",
                "description": "Professional PDF report with tables and charts",
                "available": EXPORT_AVAILABLE,
                "supports_charts": True,
                "supports_multiple_sheets": False
            }
        ]

        return formats

    def validate_export_data(self, results: List[AnalysisResult]) -> Tuple[bool, List[str]]:
        """
        Validate data before export.

        Args:
            results: Results to validate

        Returns:
            (is_valid, list_of_issues)
        """
        issues = []

        if not results:
            issues.append("No results to export")
            return False, issues

        for i, result in enumerate(results):
            is_valid, errors = result.validate()
            if not is_valid:
                issues.extend(f"Result {i+1}: {error}" for error in errors)

        return len(issues) == 0, issues