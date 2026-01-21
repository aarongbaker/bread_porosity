"""
Export Controller
Handles data export operations and coordinates with ExportService
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Optional, Dict, Any, Callable, List
import json

from services.export_service import ExportService
from models.analysis_result import AnalysisResult
from utils.logger import get_logger

logger = get_logger(__name__)


class ExportController:
    """Controller for data export operations"""

    def __init__(self, export_service: ExportService, view_callback: Optional[Callable] = None):
        """
        Initialize export controller

        Args:
            export_service: The export service to use
            view_callback: Callback to update the view (optional)
        """
        self.export_service = export_service
        self.view_callback = view_callback

    def export_csv(self, results: List[AnalysisResult], filename: Optional[str] = None) -> Optional[str]:
        """
        Export results to CSV format

        Args:
            results: List of analysis results to export
            filename: Output filename (optional, will prompt if not provided)

        Returns:
            Path to exported file if successful, None otherwise
        """
        try:
            if not filename:
                filename = self._prompt_save_filename("CSV files", "*.csv", "export.csv")

            if not filename:
                return None

            export_result = self.export_service.export_csv(results, filename)

            if export_result and export_result.success:
                logger.info(f"CSV export completed: {filename}")

                if self.view_callback:
                    self.view_callback('csv_exported', export_result)

                return filename
            else:
                error_msg = export_result.error_message if export_result else "Unknown export error"
                logger.error(f"CSV export failed: {error_msg}")
                return None

        except Exception as e:
            error_msg = f"CSV export failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return None

    def export_excel(self, results: List[AnalysisResult], filename: Optional[str] = None) -> Optional[str]:
        """
        Export results to Excel format

        Args:
            results: List of analysis results to export
            filename: Output filename (optional, will prompt if not provided)

        Returns:
            Path to exported file if successful, None otherwise
        """
        try:
            if not filename:
                filename = self._prompt_save_filename("Excel files", "*.xlsx", "export.xlsx")

            if not filename:
                return None

            export_result = self.export_service.export_excel(results, filename)

            if export_result and export_result.success:
                logger.info(f"Excel export completed: {filename}")

                if self.view_callback:
                    self.view_callback('excel_exported', export_result)

                return filename
            else:
                error_msg = export_result.error_message if export_result else "Unknown export error"
                logger.error(f"Excel export failed: {error_msg}")
                return None

        except Exception as e:
            error_msg = f"Excel export failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return None

    def export_pdf(self, results: List[AnalysisResult], filename: Optional[str] = None,
                   include_charts: bool = True) -> Optional[str]:
        """
        Export results to PDF format

        Args:
            results: List of analysis results to export
            filename: Output filename (optional, will prompt if not provided)
            include_charts: Whether to include charts in the PDF

        Returns:
            Path to exported file if successful, None otherwise
        """
        try:
            if not filename:
                filename = self._prompt_save_filename("PDF files", "*.pdf", "export.pdf")

            if not filename:
                return None

            export_result = self.export_service.export_pdf(results, filename, include_charts)

            if export_result and export_result.success:
                logger.info(f"PDF export completed: {filename}")

                if self.view_callback:
                    self.view_callback('pdf_exported', export_result)

                return filename
            else:
                error_msg = export_result.error_message if export_result else "Unknown export error"
                logger.error(f"PDF export failed: {error_msg}")
                return None

        except Exception as e:
            error_msg = f"PDF export failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return None

    def export_batch(self, results: List[AnalysisResult], formats: List[str],
                    base_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Export results in multiple formats

        Args:
            results: List of analysis results to export
            formats: List of formats to export ('csv', 'excel', 'pdf')
            base_filename: Base filename for exports

        Returns:
            Dictionary with export results for each format
        """
        export_results = {}

        for fmt in formats:
            try:
                if fmt == 'csv':
                    filename = f"{base_filename or 'batch_export'}.csv"
                    result = self.export_csv(results, filename)
                elif fmt == 'excel':
                    filename = f"{base_filename or 'batch_export'}.xlsx"
                    result = self.export_excel(results, filename)
                elif fmt == 'pdf':
                    filename = f"{base_filename or 'batch_export'}.pdf"
                    result = self.export_pdf(results, filename)
                else:
                    continue

                export_results[fmt] = {
                    'success': result is not None,
                    'filename': result
                }

            except Exception as e:
                logger.error(f"Batch export failed for {fmt}: {e}")
                export_results[fmt] = {
                    'success': False,
                    'error': str(e)
                }

        successful_exports = sum(1 for r in export_results.values() if r.get('success'))
        logger.info(f"Batch export completed: {successful_exports}/{len(formats)} formats successful")

        if self.view_callback:
            self.view_callback('batch_exported', export_results)

        return export_results

    def validate_export_data(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """
        Validate data before export

        Args:
            results: Results to validate

        Returns:
            Validation result with 'valid' boolean and 'issues' list
        """
        issues = []

        if not results:
            issues.append("No results to export")
        else:
            # Check for required fields
            for i, result in enumerate(results):
                if not hasattr(result, 'porosity_percent') or result.porosity_percent is None:
                    issues.append(f"Result {i+1}: Missing porosity data")

                if not hasattr(result, 'hole_count_total') or result.hole_count_total is None:
                    issues.append(f"Result {i+1}: Missing hole count data")

        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

    def get_export_formats(self) -> List[Dict[str, str]]:
        """
        Get available export formats

        Returns:
            List of format dictionaries with 'id', 'name', and 'extension'
        """
        return [
            {'id': 'csv', 'name': 'CSV (Spreadsheet)', 'extension': '.csv'},
            {'id': 'excel', 'name': 'Excel Workbook', 'extension': '.xlsx'},
            {'id': 'pdf', 'name': 'PDF Report', 'extension': '.pdf'}
        ]

    def _prompt_save_filename(self, file_type: str, extension: str, default_name: str) -> Optional[str]:
        """
        Prompt user for save filename

        Args:
            file_type: Description of file type
            extension: File extension pattern
            default_name: Default filename

        Returns:
            Selected filename or None if cancelled
        """
        try:
            filename = filedialog.asksaveasfilename(
                title=f"Save {file_type}",
                defaultextension=extension,
                filetypes=[(file_type, extension), ("All files", "*.*")],
                initialfile=default_name
            )
            return filename if filename else None

        except Exception as e:
            logger.error(f"Failed to prompt for save filename: {e}")
            return None

    def preview_export(self, results: List[AnalysisResult], format_type: str) -> Optional[str]:
        """
        Generate a preview of what would be exported

        Args:
            results: Results to preview
            format_type: Export format ('csv', 'excel', 'pdf')

        Returns:
            Preview text or None if failed
        """
        try:
            if format_type == 'csv':
                return self._generate_csv_preview(results)
            elif format_type == 'excel':
                return "Excel preview not available in text format"
            elif format_type == 'pdf':
                return "PDF preview not available in text format"
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to generate export preview: {e}")
            return None

    def _generate_csv_preview(self, results: List[AnalysisResult], max_rows: int = 5) -> str:
        """
        Generate CSV preview text

        Args:
            results: Results to preview
            max_rows: Maximum rows to show

        Returns:
            CSV preview as string
        """
        if not results:
            return "No data to preview"

        # Get headers from first result
        first_result = results[0]
        if hasattr(first_result, 'to_dict'):
            data = first_result.to_dict()
        else:
            data = {}

        headers = list(data.keys())
        preview_lines = [",".join(headers)]

        # Add data rows
        for result in results[:max_rows]:
            if hasattr(result, 'to_dict'):
                row_data = result.to_dict()
            else:
                row_data = {}

            row = []
            for header in headers:
                value = row_data.get(header, '')
                # Convert to string and escape commas if needed
                str_value = str(value)
                if ',' in str_value:
                    str_value = f'"{str_value}"'
                row.append(str_value)

            preview_lines.append(",".join(row))

        if len(results) > max_rows:
            preview_lines.append(f"... and {len(results) - max_rows} more rows")

        return "\n".join(preview_lines)