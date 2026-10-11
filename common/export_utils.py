"""
Export Utilities

Export application data to Excel/CSV formats with enhanced formatting.
"""
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import json


def export_to_excel(
    data: List[Dict],
    output_file: str,
    sheet_name: str = "Applications"
) -> bool:
    """
    Export data to Excel format.
    
    Args:
        data: List of dictionaries with application data
        output_file: Output Excel file path
        sheet_name: Name of the Excel sheet
        
    Returns:
        True if successful, False otherwise
    """
    try:
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment
            from openpyxl.utils import get_column_letter
        except ImportError:
            print("openpyxl not installed. Install with: python -m pip install openpyxl")
            return False
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = sheet_name
        
        if not data:
            print("No data to export")
            return False
        
        # Get headers from first item
        headers = list(data[0].keys())
        
        # Write headers with styling
        header_fill = PatternFill(start_color="667eea", end_color="764ba2", fill_type="gradient")
        header_font = Font(bold=True, color="FFFFFF")
        
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")
        
        # Write data
        for row_num, row_data in enumerate(data, 2):
            for col_num, header in enumerate(headers, 1):
                value = row_data.get(header, "")
                ws.cell(row=row_num, column=col_num, value=value)
        
        # Auto-adjust column widths
        for col_num in range(1, len(headers) + 1):
            column_letter = get_column_letter(col_num)
            max_length = 0
            for row in ws[column_letter]:
                try:
                    if len(str(row.value)) > max_length:
                        max_length = len(str(row.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Save
        wb.save(output_file)
        print(f"Exported {len(data)} records to {output_file}")
        return True
        
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return False


def export_to_csv(
    data: List[Dict],
    output_file: str,
    include_bom: bool = True
) -> bool:
    """
    Export data to CSV format with enhanced formatting.
    
    Args:
        data: List of dictionaries with application data
        output_file: Output CSV file path
        include_bom: Include BOM for Excel compatibility
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not data:
            print("No data to export")
            return False
        
        # Get all unique headers from all items
        headers = set()
        for row in data:
            if row:
                headers.update([k for k in row.keys() if k is not None])
        headers = list(headers)
        
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
            writer.writeheader()
            for row in data:
                if row:
                    writer.writerow(row)
        
        print(f"Exported {len(data)} records to {output_file}")
        return True
        
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return False


def export_application_log(
    log_file: str = "applications_log.csv",
    output_format: str = "csv",
    output_file: Optional[str] = None
) -> bool:
    """
    Export application log to specified format.
    
    Args:
        log_file: Input log file path
        output_format: Output format ('csv' or 'excel')
        output_file: Output file path (auto-generated if not provided)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        log_path = Path(log_file)
        if not log_path.exists():
            print(f"Log file not found: {log_file}")
            return False
        
        # Read CSV log
        data = []
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        
        if not data:
            print("No data in log file")
            return False
        
        # Generate output filename if not provided
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if output_format == "excel":
                output_file = f"applications_export_{timestamp}.xlsx"
            else:
                output_file = f"applications_export_{timestamp}.csv"
        
        # Export
        if output_format == "excel":
            return export_to_excel(data, output_file)
        else:
            return export_to_csv(data, output_file)
            
    except Exception as e:
        print(f"Error exporting application log: {e}")
        return False


def export_statistics(
    stats_file: str = "application_stats.json",
    output_format: str = "csv",
    output_file: Optional[str] = None
) -> bool:
    """
    Export application statistics to specified format.
    
    Args:
        stats_file: Input stats file path
        output_format: Output format ('csv' or 'excel')
        output_file: Output file path (auto-generated if not provided)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        stats_path = Path(stats_file)
        if not stats_path.exists():
            print(f"Stats file not found: {stats_file}")
            return False
        
        # Read JSON stats
        with open(stats_path, 'r', encoding='utf-8') as f:
            stats = json.load(f)
        
        # Flatten stats for export
        data = []
        
        # Overall stats
        overall = {
            "metric": "Overall",
            "total_seen": stats.get("total_seen", 0),
            "total_qualified": stats.get("total_qualified", 0),
            "total_skipped": stats.get("total_skipped", 0),
            "total_applied": stats.get("total_applied", 0),
            "total_errors": stats.get("total_errors", 0),
            "total_uncertain": stats.get("total_uncertain", 0),
            "total_duplicates_skipped": stats.get("total_duplicates_skipped", 0),
            "total_security_stops": stats.get("total_security_stops", 0),
            "success_rate": stats.get("success_rate", 0),
            "duration_seconds": stats.get("duration_seconds", 0),
        }
        data.append(overall)
        
        # By role stats
        if "by_role" in stats:
            for role, counts in stats["by_role"].items():
                role_data = {
                    "metric": f"Role: {role}",
                    "total_seen": counts.get("seen", 0),
                    "total_qualified": counts.get("qualified", 0),
                    "total_skipped": counts.get("skipped", 0),
                    "total_applied": counts.get("applied", 0),
                    "total_errors": 0,
                    "total_uncertain": 0,
                    "total_duplicates_skipped": 0,
                    "total_security_stops": 0,
                    "success_rate": 0,
                    "duration_seconds": 0,
                }
                data.append(role_data)
        
        # Generate output filename if not provided
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if output_format == "excel":
                output_file = f"statistics_export_{timestamp}.xlsx"
            else:
                output_file = f"statistics_export_{timestamp}.csv"
        
        # Export
        if output_format == "excel":
            return export_to_excel(data, output_file)
        else:
            return export_to_csv(data, output_file)
            
    except Exception as e:
        print(f"Error exporting statistics: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Export application data")
    parser.add_argument("--type", choices=["log", "stats"], required=True,
                       help="Type of data to export")
    parser.add_argument("--format", choices=["csv", "excel"], default="csv",
                       help="Output format")
    parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    if args.type == "log":
        export_application_log(output_format=args.format, output_file=args.output)
    elif args.type == "stats":
        export_statistics(output_format=args.format, output_file=args.output)
