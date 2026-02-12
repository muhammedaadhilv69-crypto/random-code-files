"""
Form Manager Module - Handles PDF form fields
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Union
import uuid
from datetime import datetime
import fitz


class FieldType(Enum):
    """Types of form fields."""
    TEXT = "text"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    DROPDOWN = "dropdown"
    LISTBOX = "listbox"
    BUTTON = "button"
    SIGNATURE = "signature"
    DATE = "date"
    NUMBER = "number"
    MULTILINE = "multiline"
    PASSWORD = "password"
    FILE = "file"


@dataclass
class FormField:
    """Represents a form field."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: FieldType = FieldType.TEXT
    name: str = ""
    page: int = 0
    rect: Optional[fitz.Rect] = None
    
    # Field properties
    value: Any = None
    default_value: Any = None
    
    # Text field properties
    max_length: int = 0  # 0 = unlimited
    multiline: bool = False
    password: bool = False
    font_size: float = 12.0
    font_name: str = "Helvetica"
    text_color: tuple = (0, 0, 0)
    alignment: str = "left"  # left, center, right
    
    # Choice field properties
    options: List[str] = field(default_factory=list)
    selected_indices: List[int] = field(default_factory=list)
    editable: bool = False  # For dropdown - allow custom values
    multi_select: bool = False
    
    # Checkbox/Radio properties
    export_value: str = "Yes"
    is_checked: bool = False
    
    # Button properties
    button_type: str = "push"  # push, submit, reset
    action: str = ""  # JavaScript action or URL
    
    # Validation
    required: bool = False
    validation_script: str = ""  # JavaScript validation
    format_category: str = ""  # None, Number, Percentage, Date, Time, Special
    format_string: str = ""  # Format pattern
    
    # Appearance
    border_width: float = 1.0
    border_color: tuple = (0, 0, 0)
    background_color: tuple = (1, 1, 1)
    
    # Calculations
    calculation_script: str = ""  # JavaScript calculation
    
    # Internal reference
    _fitz_widget: Optional[Any] = field(default=None, repr=False)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'type': self.type.value,
            'name': self.name,
            'page': self.page,
            'rect': [self.rect.x0, self.rect.y0, self.rect.x1, self.rect.y1] if self.rect else None,
            'value': self.value,
            'default_value': self.default_value,
            'max_length': self.max_length,
            'multiline': self.multiline,
            'password': self.password,
            'font_size': self.font_size,
            'font_name': self.font_name,
            'text_color': self.text_color,
            'alignment': self.alignment,
            'options': self.options,
            'selected_indices': self.selected_indices,
            'editable': self.editable,
            'multi_select': self.multi_select,
            'export_value': self.export_value,
            'is_checked': self.is_checked,
            'button_type': self.button_type,
            'action': self.action,
            'required': self.required,
            'validation_script': self.validation_script,
            'format_category': self.format_category,
            'format_string': self.format_string,
            'border_width': self.border_width,
            'border_color': self.border_color,
            'background_color': self.background_color,
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'FormField':
        """Create from dictionary."""
        field = cls()
        field.id = data.get('id', str(uuid.uuid4()))
        field.type = FieldType(data.get('type', 'text'))
        field.name = data.get('name', '')
        field.page = data.get('page', 0)
        
        rect_data = data.get('rect')
        if rect_data:
            field.rect = fitz.Rect(rect_data)
            
        field.value = data.get('value')
        field.default_value = data.get('default_value')
        field.max_length = data.get('max_length', 0)
        field.multiline = data.get('multiline', False)
        field.password = data.get('password', False)
        field.font_size = data.get('font_size', 12.0)
        field.font_name = data.get('font_name', 'Helvetica')
        field.text_color = tuple(data.get('text_color', [0, 0, 0]))
        field.alignment = data.get('alignment', 'left')
        field.options = data.get('options', [])
        field.selected_indices = data.get('selected_indices', [])
        field.editable = data.get('editable', False)
        field.multi_select = data.get('multi_select', False)
        field.export_value = data.get('export_value', 'Yes')
        field.is_checked = data.get('is_checked', False)
        field.button_type = data.get('button_type', 'push')
        field.action = data.get('action', '')
        field.required = data.get('required', False)
        field.validation_script = data.get('validation_script', '')
        field.format_category = data.get('format_category', '')
        field.format_string = data.get('format_string', '')
        field.border_width = data.get('border_width', 1.0)
        field.border_color = tuple(data.get('border_color', [0, 0, 0]))
        field.background_color = tuple(data.get('background_color', [1, 1, 1]))
        
        return field


class FormManager:
    """Manages PDF form fields."""
    
    def __init__(self):
        self.fields: Dict[str, FormField] = {}
        self._field_order: List[str] = []
        self._tab_order: List[str] = []
        
    def add_field(self, field: FormField) -> FormField:
        """Add a new form field."""
        self.fields[field.id] = field
        self._field_order.append(field.id)
        return field
        
    def remove_field(self, field_id: str) -> bool:
        """Remove a form field."""
        if field_id in self.fields:
            del self.fields[field_id]
            if field_id in self._field_order:
                self._field_order.remove(field_id)
            if field_id in self._tab_order:
                self._tab_order.remove(field_id)
            return True
        return False
        
    def get_field(self, field_id: str) -> Optional[FormField]:
        """Get a field by ID."""
        return self.fields.get(field_id)
        
    def get_field_by_name(self, name: str) -> Optional[FormField]:
        """Get a field by name."""
        for field in self.fields.values():
            if field.name == name:
                return field
        return None
        
    def get_fields_for_page(self, page_num: int) -> List[FormField]:
        """Get all fields for a specific page."""
        return [f for f in self.fields.values() if f.page == page_num]
        
    def get_all_fields(self) -> List[FormField]:
        """Get all form fields."""
        return [self.fields[fid] for fid in self._field_order]
        
    def update_field(self, field_id: str, updates: Dict[str, Any]) -> bool:
        """Update field properties."""
        field = self.fields.get(field_id)
        if field:
            for key, value in updates.items():
                if hasattr(field, key):
                    setattr(field, key, value)
            return True
        return False
        
    def set_field_value(self, field_id: str, value: Any) -> bool:
        """Set a field's value."""
        field = self.fields.get(field_id)
        if field:
            field.value = value
            
            # Update fitz widget if available
            if field._fitz_widget:
                if field.type == FieldType.CHECKBOX:
                    field._fitz_widget.field_value = field.export_value if value else "Off"
                elif field.type == FieldType.RADIO:
                    field._fitz_widget.field_value = value if value else "Off"
                else:
                    field._fitz_widget.field_value = str(value) if value is not None else ""
                field._fitz_widget.update()
                
            return True
        return False
        
    def get_field_value(self, field_id: str) -> Any:
        """Get a field's value."""
        field = self.fields.get(field_id)
        return field.value if field else None
        
    def clear_all_fields(self):
        """Clear all field values."""
        for field in self.fields.values():
            field.value = None
            if field._fitz_widget:
                field._fitz_widget.field_value = ""
                field._fitz_widget.update()
                
    def reset_all_fields(self):
        """Reset all fields to default values."""
        for field in self.fields.values():
            field.value = field.default_value
            if field._fitz_widget:
                field._fitz_widget.field_value = str(field.default_value) if field.default_value else ""
                field._fitz_widget.update()
                
    def validate_field(self, field_id: str) -> Tuple[bool, str]:
        """Validate a field's value."""
        field = self.fields.get(field_id)
        if not field:
            return False, "Field not found"
            
        # Check required
        if field.required and (field.value is None or field.value == ""):
            return False, f"Field '{field.name}' is required"
            
        # Check max length for text fields
        if field.type == FieldType.TEXT and field.max_length > 0:
            if field.value and len(str(field.value)) > field.max_length:
                return False, f"Value exceeds maximum length of {field.max_length}"
                
        # Run custom validation script if provided
        if field.validation_script:
            # In a real implementation, this would execute JavaScript
            pass
            
        return True, "Valid"
        
    def validate_all(self) -> List[Tuple[str, str]]:
        """Validate all fields. Returns list of (field_id, error) tuples."""
        errors = []
        for field_id in self.fields:
            valid, message = self.validate_field(field_id)
            if not valid:
                errors.append((field_id, message))
        return errors
        
    # ==================== Field Creation Helpers ====================
    
    def create_text_field(
        self,
        page: int,
        rect: fitz.Rect,
        name: str,
        default_value: str = "",
        max_length: int = 0,
        multiline: bool = False,
        password: bool = False,
        required: bool = False
    ) -> FormField:
        """Create a text field."""
        field = FormField(
            type=FieldType.TEXT,
            name=name,
            page=page,
            rect=rect,
            default_value=default_value,
            max_length=max_length,
            multiline=multiline,
            password=password,
            required=required
        )
        return self.add_field(field)
        
    def create_checkbox(
        self,
        page: int,
        rect: fitz.Rect,
        name: str,
        export_value: str = "Yes",
        default_checked: bool = False,
        required: bool = False
    ) -> FormField:
        """Create a checkbox field."""
        field = FormField(
            type=FieldType.CHECKBOX,
            name=name,
            page=page,
            rect=rect,
            export_value=export_value,
            is_checked=default_checked,
            default_value=default_checked,
            required=required
        )
        return self.add_field(field)
        
    def create_radio_group(
        self,
        page: int,
        name: str,
        options: List[str],
        rects: List[fitz.Rect],
        default_selection: int = 0
    ) -> List[FormField]:
        """Create a radio button group."""
        fields = []
        for i, (option, rect) in enumerate(zip(options, rects)):
            field = FormField(
                type=FieldType.RADIO,
                name=name,  # Same name for all in group
                page=page,
                rect=rect,
                export_value=option,
                is_checked=(i == default_selection),
                default_value=(i == default_selection)
            )
            fields.append(self.add_field(field))
        return fields
        
    def create_dropdown(
        self,
        page: int,
        rect: fitz.Rect,
        name: str,
        options: List[str],
        default_index: int = 0,
        editable: bool = False,
        required: bool = False
    ) -> FormField:
        """Create a dropdown field."""
        field = FormField(
            type=FieldType.DROPDOWN,
            name=name,
            page=page,
            rect=rect,
            options=options,
            selected_indices=[default_index] if options else [],
            default_value=options[default_index] if options else None,
            editable=editable,
            required=required
        )
        return self.add_field(field)
        
    def create_listbox(
        self,
        page: int,
        rect: fitz.Rect,
        name: str,
        options: List[str],
        multi_select: bool = False,
        required: bool = False
    ) -> FormField:
        """Create a listbox field."""
        field = FormField(
            type=FieldType.LISTBOX,
            name=name,
            page=page,
            rect=rect,
            options=options,
            multi_select=multi_select,
            required=required
        )
        return self.add_field(field)
        
    def create_button(
        self,
        page: int,
        rect: fitz.Rect,
        name: str,
        label: str = "",
        button_type: str = "push",
        action: str = ""
    ) -> FormField:
        """Create a button field."""
        field = FormField(
            type=FieldType.BUTTON,
            name=name,
            page=page,
            rect=rect,
            value=label,
            button_type=button_type,
            action=action
        )
        return self.add_field(field)
        
    def create_signature_field(
        self,
        page: int,
        rect: fitz.Rect,
        name: str,
        required: bool = False
    ) -> FormField:
        """Create a signature field."""
        field = FormField(
            type=FieldType.SIGNATURE,
            name=name,
            page=page,
            rect=rect,
            required=required
        )
        return self.add_field(field)
        
    def create_date_field(
        self,
        page: int,
        rect: fitz.Rect,
        name: str,
        format_string: str = "mm/dd/yyyy",
        required: bool = False
    ) -> FormField:
        """Create a date field."""
        field = FormField(
            type=FieldType.DATE,
            name=name,
            page=page,
            rect=rect,
            format_category="Date",
            format_string=format_string,
            required=required
        )
        return self.add_field(field)
        
    def create_number_field(
        self,
        page: int,
        rect: fitz.Rect,
        name: str,
        decimal_places: int = 2,
        required: bool = False
    ) -> FormField:
        """Create a number field."""
        field = FormField(
            type=FieldType.NUMBER,
            name=name,
            page=page,
            rect=rect,
            format_category="Number",
            format_string=f"0.{ '0' * decimal_places }",
            required=required
        )
        return self.add_field(field)
        
    # ==================== PDF Integration ====================
    
    def import_from_pdf(self, pdf_engine):
        """Import form fields from a loaded PDF."""
        self.fields.clear()
        self._field_order.clear()
        
        for page_num in range(pdf_engine.page_count):
            page = pdf_engine.get_page(page_num)
            if page:
                fitz_page = page.fitz_page
                
                # Get widgets (form fields)
                for widget in fitz_page.widgets():
                    field = self._convert_widget(widget, page_num)
                    if field:
                        field._fitz_widget = widget
                        self.fields[field.id] = field
                        self._field_order.append(field.id)
                        
    def _convert_widget(self, widget, page_num: int) -> Optional[FormField]:
        """Convert a fitz widget to our FormField class."""
        # Map field types
        type_mapping = {
            fitz.PDF_WIDGET_TYPE_TEXT: FieldType.TEXT,
            fitz.PDF_WIDGET_TYPE_CHECKBOX: FieldType.CHECKBOX,
            fitz.PDF_WIDGET_TYPE_RADIOBUTTON: FieldType.RADIO,
            fitz.PDF_WIDGET_TYPE_LISTBOX: FieldType.LISTBOX,
            fitz.PDF_WIDGET_TYPE_COMBOBOX: FieldType.DROPDOWN,
            fitz.PDF_WIDGET_TYPE_BUTTON: FieldType.BUTTON,
            fitz.PDF_WIDGET_TYPE_SIGNATURE: FieldType.SIGNATURE,
        }
        
        field_type = type_mapping.get(widget.field_type, FieldType.TEXT)
        
        field = FormField(
            type=field_type,
            name=widget.field_name or "",
            page=page_num,
            rect=widget.rect,
        )
        
        # Get current value
        if field_type == FieldType.CHECKBOX:
            field.is_checked = widget.field_value == widget.button_caption()
            field.export_value = widget.button_caption() or "Yes"
        elif field_type == FieldType.RADIO:
            field.export_value = widget.field_value or ""
        elif field_type in [FieldType.DROPDOWN, FieldType.LISTBOX]:
            field.options = list(widget.choice_values) if widget.choice_values else []
            field.value = widget.field_value
        else:
            field.value = widget.field_value
            
        # Get text properties
        field.text_color = widget.text_color
        field.font_size = widget.text_fontsize
        
        return field
        
    def export_to_pdf(self, pdf_engine):
        """Export form fields to the PDF document."""
        for field in self.fields.values():
            self._apply_field(pdf_engine, field)
            
    def _apply_field(self, pdf_engine, field: FormField):
        """Apply a single field to the PDF."""
        page = pdf_engine.get_page(field.page)
        if not page or not field.rect:
            return
            
        # Create widget based on field type
        if field.type == FieldType.TEXT:
            widget = fitz.Widget()
            widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
            widget.field_name = field.name
            widget.rect = field.rect
            widget.field_value = str(field.value) if field.value else ""
            widget.text_fontsize = field.font_size
            widget.text_color = field.text_color
            
            # Add to page
            page.fitz_page.add_widget(widget)
            
        elif field.type == FieldType.CHECKBOX:
            widget = fitz.Widget()
            widget.field_type = fitz.PDF_WIDGET_TYPE_CHECKBOX
            widget.field_name = field.name
            widget.rect = field.rect
            widget.field_value = field.export_value if field.is_checked else "Off"
            
            page.fitz_page.add_widget(widget)
            
        elif field.type == FieldType.DROPDOWN:
            widget = fitz.Widget()
            widget.field_type = fitz.PDF_WIDGET_TYPE_COMBOBOX
            widget.field_name = field.name
            widget.rect = field.rect
            widget.choice_values = field.options
            widget.field_value = field.value if field.value else ""
            
            page.fitz_page.add_widget(widget)
            
    def flatten_forms(self, pdf_engine):
        """Flatten all form fields (make them non-editable)."""
        for page_num in range(pdf_engine.page_count):
            page = pdf_engine.get_page(page_num)
            if page:
                fitz_page = page.fitz_page
                # This would flatten widgets in a real implementation
                pass
                
    def save_to_file(self, file_path: str):
        """Save form fields to a JSON file."""
        import json
        data = [field.to_dict() for field in self.get_all_fields()]
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
    def load_from_file(self, file_path: str):
        """Load form fields from a JSON file."""
        import json
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.fields.clear()
            self._field_order.clear()
            for item in data:
                field = FormField.from_dict(item)
                self.fields[field.id] = field
                self._field_order.append(field.id)
