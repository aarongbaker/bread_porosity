"""
Unit tests for repositories
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from repositories.config_repository import ConfigRepository
from repositories.recipe_repository import RecipeRepository
from repositories.results_repository import ResultsRepository
from models.recipe import Recipe
from models.analysis_result import AnalysisResult


class TestConfigRepository:
    """Test cases for ConfigRepository"""

    def test_init_with_default_path(self):
        """Test initialization with default config path"""
        repo = ConfigRepository()
        assert repo.config_path == Path("config.json")
        assert isinstance(repo._config, dict)

    def test_init_with_custom_path(self):
        """Test initialization with custom config path"""
        repo = ConfigRepository("custom_config.json")
        assert repo.config_path == Path("custom_config.json")

    def test_load_from_file_defaults_when_no_file(self):
        """Test loading defaults when config file doesn't exist"""
        with patch('pathlib.Path.exists', return_value=False):
            repo = ConfigRepository("nonexistent.json")
            config = repo._load_from_file()
            assert config == ConfigRepository.DEFAULT_CONFIG

    def test_load_from_file_with_existing_file(self):
        """Test loading config from existing file"""
        test_config = {"pixel_size_mm": 0.05, "custom_setting": "test"}
        expected_config = {**ConfigRepository.DEFAULT_CONFIG, **test_config}

        with patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(test_config))):
            repo = ConfigRepository("test.json")
            config = repo._load_from_file()
            assert config == expected_config

    def test_load_from_file_invalid_json(self):
        """Test loading config with invalid JSON"""
        with patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data="invalid json")):
            repo = ConfigRepository("invalid.json")
            config = repo._load_from_file()
            assert config == ConfigRepository.DEFAULT_CONFIG

    def test_get_existing_key(self):
        """Test getting an existing configuration key"""
        repo = ConfigRepository()
        value = repo.get("pixel_size_mm")
        assert value == 0.1

    def test_get_nonexistent_key_with_default(self):
        """Test getting a nonexistent key with default value"""
        repo = ConfigRepository()
        value = repo.get("nonexistent", "default_value")
        assert value == "default_value"

    def test_get_nonexistent_key_without_default(self):
        """Test getting a nonexistent key without default value"""
        repo = ConfigRepository()
        value = repo.get("nonexistent")
        assert value is None

    def test_set_key(self):
        """Test setting a configuration key"""
        repo = ConfigRepository()
        repo.set("test_key", "test_value")
        assert repo._config["test_key"] == "test_value"

    def test_update_config(self):
        """Test updating configuration with dictionary"""
        repo = ConfigRepository()
        updates = {"key1": "value1", "key2": "value2"}
        repo.update(updates)
        assert repo._config["key1"] == "value1"
        assert repo._config["key2"] == "value2"

    def test_save_config(self):
        """Test saving configuration to file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            repo = ConfigRepository(str(config_path))

            repo.set("test_key", "test_value")
            repo.save()

            # Verify file was created and contains correct data
            assert config_path.exists()
            with open(config_path, 'r') as f:
                saved_config = json.load(f)
                assert saved_config["test_key"] == "test_value"

    def test_get_all(self):
        """Test getting all configuration"""
        repo = ConfigRepository()
        all_config = repo.get_all()
        assert isinstance(all_config, dict)
        assert "pixel_size_mm" in all_config

    def test_reset_to_defaults(self):
        """Test resetting configuration to defaults"""
        repo = ConfigRepository()
        repo.set("custom_key", "custom_value")
        repo.reset_to_defaults()

        assert repo._config == ConfigRepository.DEFAULT_CONFIG
        assert "custom_key" not in repo._config


class TestRecipeRepository:
    """Test cases for RecipeRepository"""

    def test_init_with_default_path(self):
        """Test initialization with default recipes path"""
        repo = RecipeRepository()
        assert repo.db_path == Path("recipes.json")

    def test_save_and_load_recipes(self):
        """Test saving and loading recipes"""
        with tempfile.TemporaryDirectory() as temp_dir:
            recipes_path = Path(temp_dir) / "test_recipes.json"
            repo = RecipeRepository(str(recipes_path))

            # Create test recipe
            recipe = Recipe(
                name="Test Recipe",
                ingredients={"flour": 500, "water": 350},
                mixing_time_min=10,
                proof_time_min=120,
                oven_temp_c=220,
                cooking_vessel="dutch oven",
                cook_time_min=45
            )

            # Save recipe
            saved_recipe = repo.save(recipe)

            # Verify ID was assigned
            assert saved_recipe.id is not None

            # Load recipes and verify
            loaded_recipes = repo.find_all()
            assert len(loaded_recipes) == 1
            assert loaded_recipes[0].name == "Test Recipe"
            assert loaded_recipes[0].id == saved_recipe.id

    def test_get_recipe_by_id(self):
        """Test getting recipe by ID"""
        with tempfile.TemporaryDirectory() as temp_dir:
            recipes_path = Path(temp_dir) / "test_recipes.json"
            repo = RecipeRepository(str(recipes_path))

            # Create and save test recipe
            recipe = Recipe(
                name="Test Recipe",
                ingredients={"flour": 500, "water": 350},
                mixing_time_min=10,
                proof_time_min=120,
                oven_temp_c=220,
                cooking_vessel="dutch oven",
                cook_time_min=45
            )
            saved_recipe = repo.save(recipe)

            # Retrieve by ID
            retrieved = repo.find_by_id(saved_recipe.id)
            assert retrieved is not None
            assert retrieved.name == "Test Recipe"
            assert retrieved.id == saved_recipe.id

    def test_get_recipe_by_id_not_found(self):
        """Test getting recipe by non-existent ID"""
        repo = RecipeRepository()
        retrieved = repo.find_by_id(999)
        assert retrieved is None

    def test_delete_recipe(self):
        """Test deleting a recipe"""
        with tempfile.TemporaryDirectory() as temp_dir:
            recipes_path = Path(temp_dir) / "test_recipes.json"
            repo = RecipeRepository(str(recipes_path))

            # Create and save test recipe
            recipe = Recipe(
                name="Test Recipe",
                ingredients={"flour": 500, "water": 350},
                mixing_time_min=10,
                proof_time_min=120,
                oven_temp_c=220,
                cooking_vessel="dutch oven",
                cook_time_min=45
            )
            saved_recipe = repo.save(recipe)

            # Verify recipe exists
            assert len(repo.find_all()) == 1

            # Delete recipe
            result = repo.delete(saved_recipe.id)
            assert result is True

            # Verify recipe is gone
            assert len(repo.find_all()) == 0

    def test_delete_recipe_not_found(self):
        """Test deleting a non-existent recipe"""
        with tempfile.TemporaryDirectory() as temp_dir:
            recipes_path = Path(temp_dir) / "test_recipes.json"
            repo = RecipeRepository(str(recipes_path))
            result = repo.delete(999)
            assert result is False


class TestResultsRepository:
    """Test cases for ResultsRepository"""

    def test_init_with_default_path(self):
        """Test initialization with default results path"""
        repo = ResultsRepository()
        assert repo.results_dir == Path("./results")

    def test_save_and_load_results(self):
        """Test saving and loading analysis results"""
        with tempfile.TemporaryDirectory() as temp_dir:
            results_dir = Path(temp_dir) / "test_results"
            repo = ResultsRepository(str(results_dir))

            # Create test result
            result = AnalysisResult(
                image_path="/path/to/image.jpg",
                image_filename="image.jpg",
                porosity_percent=65.5,
                hole_count_total=150,
                hole_diameter_mean_mm=2.5,
                hole_diameter_std_mm=0.8,
                hole_diameter_min_mm=1.0,
                hole_diameter_max_mm=5.0,
                holes_per_cm2=25.0,
                anisotropy_ratio=1.2,
                orientation_mean_deg=45.0,
                uniformity_score=0.85
            )

            # Save result
            repo.save(result)

            # Load results and verify
            loaded_results = repo.find_all()
            assert len(loaded_results) == 1
            assert loaded_results[0].porosity_percent == 65.5
            assert loaded_results[0].image_filename == "image.jpg"

    def test_get_results_by_image_path(self):
        """Test getting results by image path"""
        with tempfile.TemporaryDirectory() as temp_dir:
            results_dir = Path(temp_dir) / "test_results"
            repo = ResultsRepository(str(results_dir))

            # Create and save test result
            result = AnalysisResult(
                image_path="/path/to/test.jpg",
                image_filename="test.jpg",
                porosity_percent=70.0,
                hole_count_total=200,
                hole_diameter_mean_mm=3.0,
                hole_diameter_std_mm=1.0,
                hole_diameter_min_mm=1.5,
                hole_diameter_max_mm=6.0,
                holes_per_cm2=30.0,
                anisotropy_ratio=1.1,
                orientation_mean_deg=30.0,
                uniformity_score=0.92
            )
            repo.save(result)

            # Retrieve by image name
            retrieved = repo.find_by_image_name("test.jpg")
            assert retrieved is not None
            assert retrieved.porosity_percent == 70.0

    def test_get_results_by_image_path_not_found(self):
        """Test getting results by non-existent image path"""
        repo = ResultsRepository()
        retrieved = repo.find_by_image_name("nonexistent.jpg")
        assert retrieved is None

    def test_get_recent_results(self):
        """Test getting recent results"""
        with tempfile.TemporaryDirectory() as temp_dir:
            results_dir = Path(temp_dir) / "test_results"
            repo = ResultsRepository(str(results_dir))

            # Add multiple results
            for i in range(3):
                result = AnalysisResult(
                    image_path=f"/path/to/image{i}.jpg",
                    image_filename=f"image{i}.jpg",
                    porosity_percent=60.0 + i,
                    hole_count_total=100 + i * 10,
                    hole_diameter_mean_mm=2.0,
                    hole_diameter_std_mm=0.5,
                    hole_diameter_min_mm=1.0,
                    hole_diameter_max_mm=4.0,
                    holes_per_cm2=20.0,
                    anisotropy_ratio=1.0,
                    orientation_mean_deg=0.0,
                    uniformity_score=0.8
                )
                repo.save(result)

            # Get recent results (limit 2)
            recent = repo.get_latest(limit=2)
            assert len(recent) == 2