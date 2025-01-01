from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List

class NewFieldsOption(Enum):
    ADD_TO_SETUP = "AddToSetup"
    IGNORE = "Ignore"
    SKIP_TRANSLATION_UNIT = "SkipTranslationUnit"
    ERROR = "Error"

class FieldUpdateMode(Enum):
    MERGE = "Merge"
    OVERWRITE = "Overwrite"
    LEAVE_UNCHANGED = "LeaveUnchanged"

class ImportTUProcessingMode(Enum):
    PROCESS_CLEANED_TU_ONLY = "ProcessCleanedTUOnly"
    PROCESS_RAW_TU_ONLY = "ProcessRawTUOnly"
    PROCESS_BOTH_TUS = "ProcessBothTUs"

class TUUpdateMode(Enum):
    ADD_NEW = "AddNew"
    OVERWRITE = "Overwrite"
    LEAVE_UNCHANGED = "LeaveUnchanged"
    KEEP_MOST_RECENT = "KeepMostRecent"
    OVERWRITE_CURRENT = "OverwriteCurrent"

@dataclass
class ImportSettings:
    override_tu_user_id_with_current_context_user: bool = False
    use_tm_user_id_from_bilingual_file: bool = True
    new_fields: NewFieldsOption = NewFieldsOption.ERROR
    existing_fields_update_mode: FieldUpdateMode = FieldUpdateMode.MERGE
    overwrite_existing_tus: bool = False  # Obsolete, use existing_tus_update_mode instead
    existing_tus_update_mode: TUUpdateMode = TUUpdateMode.ADD_NEW
    is_document_import: bool = False
    plain_text: bool = False
    tag_count_limit: int = 250
    increment_usage_count: bool = False
    project_settings: Optional[dict] = None
    check_matching_sublanguages: bool = False
    filter_expression: Optional[dict] = None
    edit_script: Optional[dict] = None
    invalid_translation_units_export_path: Optional[str] = None
    confirmation_levels: Optional[List[str]] = None
    field_identifier_mappings: Optional[Dict[str, str]] = None
    tu_processing_mode: ImportTUProcessingMode = ImportTUProcessingMode.PROCESS_BOTH_TUS
    acronyms_auto_substitution: bool = False  # Obsolete
    alignment_quality: int = field(default=0)

    DEFAULT_TAG_COUNT_LIMIT = 250

    def __post_init__(self):
        if not (0 <= self.alignment_quality <= 100):
            raise ValueError("alignment_quality must be between 0 and 100")
