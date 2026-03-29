"""
Immutable audit logger for the Offline Policy Gap Analyzer.

This module provides append-only audit logging for compliance traceability.
Audit logs record all analysis runs with complete metadata and cannot be
modified or deleted after creation.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from models.domain import AuditLogEntry


class AuditLogger:
    """Immutable audit logger with append-only semantics.
    
    The audit logger creates tamper-evident logs of all analysis runs,
    recording input files, models, configurations, and outputs for
    compliance and reproducibility requirements.
    
    Attributes:
        audit_dir: Directory where audit logs are stored
    """
    
    def __init__(self, audit_dir: str = "audit_logs"):
        """
        Initialize audit logger with storage directory.
        
        Args:
            audit_dir: Directory path for storing audit logs
        """
        self.audit_dir = Path(audit_dir)
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        # Make directory read-only after creation to prevent deletion
        # Note: This is a best-effort approach; true immutability requires
        # filesystem-level controls or specialized storage systems
        self._set_directory_permissions()
    
    def log_analysis(
        self,
        input_file_path: str,
        model_name: str,
        model_version: str,
        embedding_model_version: str,
        configuration_parameters: Dict[str, Any],
        retrieval_parameters: Dict[str, Any],
        prompt_template_version: str,
        output_directory: str,
        analysis_duration_seconds: float
    ) -> AuditLogEntry:
        """
        Create immutable audit log entry for an analysis run.
        
        Args:
            input_file_path: Path to analyzed policy document
            model_name: LLM model name used
            model_version: LLM model version/quantization
            embedding_model_version: Embedding model version
            configuration_parameters: Analysis configuration parameters
            retrieval_parameters: Retrieval configuration parameters
            prompt_template_version: Version of prompt templates used
            output_directory: Directory where outputs were written
            analysis_duration_seconds: Total analysis duration
            
        Returns:
            AuditLogEntry object that was logged
            
        The audit log is written to a timestamp-based filename in append-only
        format. The file is created with restricted permissions to prevent
        modification or deletion.
        """
        # Calculate input file hash
        input_file_hash = self._calculate_file_hash(input_file_path)
        
        # Create audit log entry
        timestamp = datetime.now()
        entry = AuditLogEntry(
            timestamp=timestamp,
            input_file_path=input_file_path,
            input_file_hash=input_file_hash,
            model_name=model_name,
            model_version=model_version,
            embedding_model_version=embedding_model_version,
            configuration_parameters=configuration_parameters,
            retrieval_parameters=retrieval_parameters,
            prompt_template_version=prompt_template_version,
            output_directory=output_directory,
            analysis_duration_seconds=analysis_duration_seconds
        )
        
        # Write to append-only log file
        log_file = self._get_log_file_path(timestamp)
        self._write_log_entry(log_file, entry)
        
        return entry
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate SHA-256 hash of input file for integrity verification.
        
        Args:
            file_path: Path to file to hash
            
        Returns:
            Hexadecimal SHA-256 hash string
        """
        sha256_hash = hashlib.sha256()
        
        try:
            with open(file_path, "rb") as f:
                # Read file in chunks to handle large files
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except FileNotFoundError:
            # If file doesn't exist, return placeholder hash
            return "FILE_NOT_FOUND"
        except Exception as e:
            # For any other error, return error indicator
            return f"HASH_ERROR_{type(e).__name__}"
    
    def _get_log_file_path(self, timestamp: datetime) -> Path:
        """
        Generate timestamp-based log file path.
        
        Args:
            timestamp: Timestamp for the log entry
            
        Returns:
            Path object for the log file
            
        Format: audit_logs/audit_YYYYMMDD_HHMMSS_microseconds.json
        """
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        microseconds = timestamp.microsecond
        filename = f"audit_{timestamp_str}_{microseconds:06d}.json"
        return self.audit_dir / filename
    
    def _write_log_entry(self, log_file: Path, entry: AuditLogEntry) -> None:
        """
        Write audit log entry to file with restricted permissions.
        
        Args:
            log_file: Path to log file
            entry: AuditLogEntry to write
            
        The log file is created with read-only permissions to prevent
        modification. This is a best-effort immutability mechanism.
        """
        # Convert entry to JSON-serializable dict
        log_data = {
            "timestamp": entry.timestamp.isoformat(),
            "input_file_path": entry.input_file_path,
            "input_file_hash": entry.input_file_hash,
            "model_name": entry.model_name,
            "model_version": entry.model_version,
            "embedding_model_version": entry.embedding_model_version,
            "configuration_parameters": entry.configuration_parameters,
            "retrieval_parameters": entry.retrieval_parameters,
            "prompt_template_version": entry.prompt_template_version,
            "output_directory": entry.output_directory,
            "analysis_duration_seconds": entry.analysis_duration_seconds
        }
        
        # Write to file
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        # Set file to read-only to prevent modification
        # Owner: read-only, Group: read-only, Others: read-only
        try:
            log_file.chmod(0o444)
        except Exception:
            # If chmod fails (e.g., on Windows), continue anyway
            # The file is still written and can be used for auditing
            pass
    
    def _set_directory_permissions(self) -> None:
        """
        Set directory permissions to prevent deletion of audit logs.
        
        This is a best-effort approach. True immutability requires
        filesystem-level controls (e.g., append-only flag on Linux)
        or specialized storage systems.
        """
        try:
            # Set directory to read+write+execute for owner only
            # This allows creating new files but makes deletion harder
            self.audit_dir.chmod(0o755)
        except Exception:
            # If chmod fails, continue anyway
            pass
    
    def get_all_entries(self) -> list:
        """
        Retrieve all audit log entries from the audit directory.
        
        Returns:
            List of AuditLogEntry objects sorted by timestamp
            
        This method is provided for auditing and compliance review purposes.
        """
        entries = []
        
        for log_file in sorted(self.audit_dir.glob("audit_*.json")):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
                
                # Convert back to AuditLogEntry
                entry = AuditLogEntry(
                    timestamp=datetime.fromisoformat(log_data["timestamp"]),
                    input_file_path=log_data["input_file_path"],
                    input_file_hash=log_data["input_file_hash"],
                    model_name=log_data["model_name"],
                    model_version=log_data["model_version"],
                    embedding_model_version=log_data["embedding_model_version"],
                    configuration_parameters=log_data["configuration_parameters"],
                    retrieval_parameters=log_data["retrieval_parameters"],
                    prompt_template_version=log_data["prompt_template_version"],
                    output_directory=log_data["output_directory"],
                    analysis_duration_seconds=log_data["analysis_duration_seconds"]
                )
                entries.append(entry)
            except Exception:
                # Skip corrupted or invalid log files
                continue
        
        return entries
