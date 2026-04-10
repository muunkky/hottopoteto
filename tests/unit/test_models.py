"""Tests for core.models module."""
import pytest
from datetime import datetime
from core.models import GenericEntryModel, RecipeDefinition, PackageInfo


class TestGenericEntryModel:
    """Tests for GenericEntryModel base class."""
    
    def test_initialization_with_defaults(self):
        """Test that GenericEntryModel initializes with default values."""
        entry = GenericEntryModel(id="test-123")
        
        assert entry.id == "test-123"
        assert entry.metadata == {}
        assert isinstance(entry.created_at, datetime)
        assert isinstance(entry.updated_at, datetime)
        assert entry.tags == []
    
    def test_initialization_with_custom_values(self):
        """Test initialization with custom field values."""
        custom_time = datetime(2025, 12, 18, 10, 30, 0)
        entry = GenericEntryModel(
            id="custom-456",
            metadata={"key": "value"},
            created_at=custom_time,
            updated_at=custom_time,
            tags=["tag1", "tag2"]
        )
        
        assert entry.id == "custom-456"
        assert entry.metadata == {"key": "value"}
        assert entry.created_at == custom_time
        assert entry.updated_at == custom_time
        assert entry.tags == ["tag1", "tag2"]
    
    def test_to_dict_converts_datetimes_to_iso(self):
        """Test that to_dict() converts datetime objects to ISO format strings."""
        entry = GenericEntryModel(id="test-789")
        result = entry.to_dict()
        
        assert isinstance(result["created_at"], str)
        assert isinstance(result["updated_at"], str)
        assert "T" in result["created_at"]  # ISO format includes T separator
    
    def test_to_dict_handles_nested_metadata_dates(self):
        """Test that to_dict() converts datetime objects in metadata."""
        custom_time = datetime(2025, 12, 18, 10, 30, 0)
        entry = GenericEntryModel(
            id="test-metadata",
            metadata={
                "created_at": custom_time,
                "updated_at": custom_time,
                "other_field": "value"
            }
        )
        result = entry.to_dict()
        
        assert isinstance(result["metadata"]["created_at"], str)
        assert isinstance(result["metadata"]["updated_at"], str)
        assert result["metadata"]["other_field"] == "value"
    
    def test_from_dict_creates_instance(self):
        """Test that from_dict() creates valid instance from dictionary."""
        data = {
            "id": "from-dict-test",
            "metadata": {"key": "value"},
            "tags": ["test"]
        }
        entry = GenericEntryModel.from_dict(data)
        
        assert entry.id == "from-dict-test"
        assert entry.metadata == {"key": "value"}
        assert entry.tags == ["test"]
        assert isinstance(entry.created_at, datetime)


class TestRecipeDefinition:
    """Tests for RecipeDefinition model."""
    
    def test_initialization_with_minimal_fields(self):
        """Test RecipeDefinition with only required name field."""
        recipe = RecipeDefinition(name="test-recipe")
        
        assert recipe.name == "test-recipe"
        assert recipe.description == ""
        assert recipe.version == "1.0"
        assert recipe.domain == "generic"
        assert recipe.links == []
    
    def test_initialization_with_all_fields(self):
        """Test RecipeDefinition with all fields populated."""
        links = [
            {"type": "llm", "params": {"prompt": "test"}},
            {"type": "storage", "params": {"collection": "data"}}
        ]
        recipe = RecipeDefinition(
            name="full-recipe",
            description="A complete recipe",
            version="2.1",
            domain="llm",
            links=links
        )
        
        assert recipe.name == "full-recipe"
        assert recipe.description == "A complete recipe"
        assert recipe.version == "2.1"
        assert recipe.domain == "llm"
        assert recipe.links == links
        assert len(recipe.links) == 2
    
    def test_to_dict_conversion(self):
        """Test that to_dict() returns proper dictionary representation."""
        recipe = RecipeDefinition(
            name="dict-test",
            description="Test description",
            version="3.0"
        )
        result = recipe.to_dict()
        
        assert isinstance(result, dict)
        assert result["name"] == "dict-test"
        assert result["description"] == "Test description"
        assert result["version"] == "3.0"
        assert result["domain"] == "generic"
        assert result["links"] == []


class TestPackageInfo:
    """Tests for PackageInfo model."""
    
    def test_initialization_with_name_only(self):
        """Test PackageInfo with only required name field."""
        pkg = PackageInfo(name="test-package")
        
        assert pkg.name == "test-package"
        assert pkg.version == "0.1.0"
        assert pkg.type == "extension"
        assert pkg.description == ""
        assert pkg.author == ""
        assert pkg.dependencies == []
    
    def test_initialization_with_all_fields(self):
        """Test PackageInfo with complete metadata."""
        pkg = PackageInfo(
            name="full-package",
            version="1.2.3",
            type="core",
            description="A full package",
            author="Test Author",
            author_email="test@example.com",
            homepage="https://example.com",
            documentation="https://docs.example.com",
            dependencies=["pydantic>=2.0", "pytest>=7.0"]
        )
        
        assert pkg.name == "full-package"
        assert pkg.version == "1.2.3"
        assert pkg.type == "core"
        assert pkg.description == "A full package"
        assert pkg.author == "Test Author"
        assert pkg.author_email == "test@example.com"
        assert pkg.homepage == "https://example.com"
        assert pkg.documentation == "https://docs.example.com"
        assert len(pkg.dependencies) == 2
    
    def test_to_dict_conversion(self):
        """Test that to_dict() returns dictionary with all fields."""
        pkg = PackageInfo(
            name="dict-pkg",
            version="2.0.0",
            author="Dict Test"
        )
        result = pkg.to_dict()
        
        assert isinstance(result, dict)
        assert result["name"] == "dict-pkg"
        assert result["version"] == "2.0.0"
        assert result["author"] == "Dict Test"
        assert "type" in result
        assert "dependencies" in result
    
    def test_from_dict_creates_instance(self):
        """Test that from_dict() creates valid PackageInfo from dict."""
        data = {
            "name": "from-dict-pkg",
            "version": "3.1.0",
            "type": "extension",
            "description": "Created from dict",
            "dependencies": ["dep1", "dep2"]
        }
        pkg = PackageInfo.from_dict(data)
        
        assert pkg.name == "from-dict-pkg"
        assert pkg.version == "3.1.0"
        assert pkg.type == "extension"
        assert pkg.description == "Created from dict"
        assert pkg.dependencies == ["dep1", "dep2"]
    
    def test_package_type_validation(self):
        """Test that package type can be 'core' or 'extension'."""
        core_pkg = PackageInfo(name="core-test", type="core")
        ext_pkg = PackageInfo(name="ext-test", type="extension")
        
        assert core_pkg.type == "core"
        assert ext_pkg.type == "extension"
