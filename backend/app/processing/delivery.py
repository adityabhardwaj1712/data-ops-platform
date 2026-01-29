import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

class DeliveryService:
    """
    Automates the final packaging of data for client delivery.
    Replaces manual folder creation and zipping.
    """
    
    def __init__(self, output_dir: str = "deliveries"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def create_package(
        self, 
        job_id: str, 
        client_name: str, 
        data: List[Dict[str, Any]], 
        metadata: Dict[str, Any]
    ) -> str:
        """
        Create a standardized delivery package (ZIP).
        Folder: Client_YYYY-MM-DD_JobID
        Returns: Path to the created ZIP file.
        """
        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_client = "".join([c for c in client_name if c.isalnum() or c in (' ', '_', '-')]).strip().replace(' ', '_')
        folder_name = f"{safe_client}_{date_str}_{job_id[:8]}"
        package_path = os.path.join(self.output_dir, folder_name)
        
        # 1. Create Folder Structure
        if os.path.exists(package_path):
            shutil.rmtree(package_path)
        os.makedirs(package_path)
        
        # 2. Write Main Data (JSON & CSV)
        self._write_data(package_path, data)
        
        # 3. Generate & Write Metadata
        final_metadata = self._enrich_metadata(metadata, len(data))
        with open(os.path.join(package_path, "METADATA.json"), "w", encoding="utf-8") as f:
            json.dump(final_metadata, f, indent=2)
            
        # 4. Add Readme/Manifest
        self._write_readme(package_path, final_metadata)
        
        # 5. Zip it up
        zip_path = shutil.make_archive(package_path, 'zip', package_path)
        
        # Cleanup folder after zipping (optional, maybe keep for debug)
        # shutil.rmtree(package_path) 
        
        return zip_path

    def _write_data(self, base_path: str, data: List[Dict]):
        # JSON output
        json_path = os.path.join(base_path, "data.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            
        # CSV output
        if not data:
            return
            
        import csv
        keys = data[0].keys()
        csv_path = os.path.join(base_path, "data.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)

    def _enrich_metadata(self, metadata: Dict, row_count: int) -> Dict:
        return {
            "generated_at": datetime.now().isoformat(),
            "row_count": row_count,
            "status": "DELIVERED",
            "system_version": "1.0",
            **metadata
        }

    def _write_readme(self, base_path: str, metadata: Dict):
        content = f"""# Data Delivery
        
**Client**: {metadata.get('client_id', 'Unknown')}
**Date**: {datetime.now().strftime("%Y-%m-%d")}
**Rows**: {metadata.get('row_count')}

## Contents
- `data.json`: Full dataset in JSON format.
- `data.csv`: Full dataset in CSV format.
- `METADATA.json`: Job details and parameters.

## Support
For any issues, please contact the DataOps team.
"""
        with open(os.path.join(base_path, "README.md"), "w", encoding="utf-8") as f:
            f.write(content)

# Global Instance
delivery_service = DeliveryService()
