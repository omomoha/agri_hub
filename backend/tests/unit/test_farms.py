import pytest
from app.models.farm import Farm
from app.models.user import User, UserRole
from app.schemas.farm import FarmCreate, FarmResponse, FarmUpdate
from sqlmodel import Session, select
from datetime import datetime

class TestFarmModel:
    """Test Farm model functionality."""
    
    def test_farm_creation(self, session, test_user):
        """Test creating a new farm."""
        farm_data = {
            "name": "Test Farm",
            "description": "A test farm for testing purposes",
            "location": "Test Location, Nigeria",
            "size_hectares": 25.5,
            "soil_type": "Loamy",
            "irrigation_type": "Drip Irrigation",
            "is_active": True,
            "farmer_id": test_user.id
        }
        
        farm = Farm(**farm_data)
        session.add(farm)
        session.commit()
        session.refresh(farm)
        
        assert farm.id is not None
        assert farm.name == "Test Farm"
        assert farm.description == "A test farm for testing purposes"
        assert farm.location == "Test Location, Nigeria"
        assert farm.size_hectares == 25.5
        assert farm.soil_type == "Loamy"
        assert farm.irrigation_type == "Drip Irrigation"
        assert farm.is_active is True
        assert farm.farmer_id == test_user.id
        assert farm.created_at is not None
        assert farm.updated_at is not None
    
    def test_farm_relationships(self, session, test_user):
        """Test farm relationships with users."""
        farm = Farm(
            name="Relationship Farm",
            description="Testing relationships",
            location="Test Location",
            size_hectares=10.0,
            farmer_id=test_user.id
        )
        session.add(farm)
        session.commit()
        session.refresh(farm)
        
        # Test that farm is associated with the correct farmer
        assert farm.farmer_id == test_user.id
        
        # Test that we can access the farmer through the relationship
        # (This would require setting up the relationship in the model)
    
    def test_farm_size_validation(self, session, test_user):
        """Test farm size validation."""
        # Valid sizes
        valid_sizes = [0.1, 1.0, 100.0, 1000.0]
        
        for size in valid_sizes:
            farm = Farm(
                name=f"Farm {size}",
                description="Testing size validation",
                location="Test Location",
                size_hectares=size,
                farmer_id=test_user.id
            )
            session.add(farm)
        
        session.commit()
        
        # Verify all farms were created
        farms = session.exec(select(Farm)).all()
        assert len(farms) >= len(valid_sizes)
    
    def test_farm_soil_types(self, session, test_user):
        """Test different soil type configurations."""
        soil_types = ["Loamy", "Sandy", "Clay", "Silt", "Peaty", "Chalky"]
        
        for soil_type in soil_types:
            farm = Farm(
                name=f"Farm {soil_type}",
                description=f"Testing {soil_type} soil",
                location="Test Location",
                size_hectares=10.0,
                soil_type=soil_type,
                farmer_id=test_user.id
            )
            session.add(farm)
        
        session.commit()
        
        # Verify all soil types were saved
        for soil_type in soil_types:
            farm = session.exec(select(Farm).where(Farm.soil_type == soil_type)).first()
            assert farm is not None
            assert farm.soil_type == soil_type
    
    def test_farm_irrigation_types(self, session, test_user):
        """Test different irrigation type configurations."""
        irrigation_types = ["Drip", "Sprinkler", "Flood", "Center Pivot", "None"]
        
        for irrigation_type in irrigation_types:
            farm = Farm(
                name=f"Farm {irrigation_type}",
                description=f"Testing {irrigation_type} irrigation",
                location="Test Location",
                size_hectares=10.0,
                irrigation_type=irrigation_type,
                farmer_id=test_user.id
            )
            session.add(farm)
        
        session.commit()
        
        # Verify all irrigation types were saved
        for irrigation_type in irrigation_types:
            farm = session.exec(select(Farm).where(Farm.irrigation_type == irrigation_type)).first()
            assert farm is not None
            assert farm.irrigation_type == irrigation_type

class TestFarmSchemas:
    """Test farm Pydantic schemas."""
    
    def test_farm_create_schema(self):
        """Test FarmCreate schema validation."""
        farm_data = {
            "name": "Schema Farm",
            "description": "Testing schema validation",
            "location": "Schema Location",
            "size_hectares": 15.0,
            "soil_type": "Loamy",
            "irrigation_type": "Drip"
        }
        
        farm_create = FarmCreate(**farm_data)
        
        assert farm_create.name == "Schema Farm"
        assert farm_create.description == "Testing schema validation"
        assert farm_create.location == "Schema Location"
        assert farm_create.size_hectares == 15.0
        assert farm_create.soil_type == "Loamy"
        assert farm_create.irrigation_type == "Drip"
    
    def test_farm_update_schema(self):
        """Test FarmUpdate schema validation."""
        update_data = {
            "name": "Updated Farm Name",
            "description": "Updated description",
            "size_hectares": 20.0
        }
        
        farm_update = FarmUpdate(**update_data)
        
        assert farm_update.name == "Updated Farm Name"
        assert farm_update.description == "Updated description"
        assert farm_update.size_hectares == 20.0
        assert farm_update.location is None  # Not provided
    
    def test_farm_response_schema(self):
        """Test FarmResponse schema validation."""
        response_data = {
            "id": 1,
            "name": "Response Farm",
            "description": "Testing response schema",
            "location": "Response Location",
            "size_hectares": 12.5,
            "soil_type": "Sandy",
            "irrigation_type": "Sprinkler",
            "is_active": True,
            "farmer_id": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        farm_response = FarmResponse(**response_data)
        
        assert farm_response.id == 1
        assert farm_response.name == "Response Farm"
        assert farm_response.description == "Testing response schema"
        assert farm_response.location == "Response Location"
        assert farm_response.size_hectares == 12.5
        assert farm_response.soil_type == "Sandy"
        assert farm_response.irrigation_type == "Sprinkler"
        assert farm_response.is_active is True
        assert farm_response.farmer_id == 1

class TestFarmValidation:
    """Test farm data validation."""
    
    def test_farm_name_validation(self):
        """Test farm name validation."""
        # Valid names
        valid_names = ["Farm 1", "My Farm", "Organic Farm", "Farm-123", "Farm_Test"]
        
        for name in valid_names:
            data = {
                "name": name,
                "description": "Test description",
                "location": "Test location",
                "size_hectares": 10.0
            }
            farm_create = FarmCreate(**data)
            assert farm_create.name == name
        
        # Invalid names (empty or too long)
        with pytest.raises(ValueError):
            FarmCreate(
                name="",  # Empty name
                description="Test description",
                location="Test location",
                size_hectares=10.0
            )
    
    def test_farm_size_validation(self):
        """Test farm size validation."""
        # Valid sizes
        valid_sizes = [0.1, 1.0, 50.0, 100.0, 1000.0]
        
        for size in valid_sizes:
            data = {
                "name": "Test Farm",
                "description": "Test description",
                "location": "Test location",
                "size_hectares": size
            }
            farm_create = FarmCreate(**data)
            assert farm_create.size_hectares == size
        
        # Invalid sizes
        with pytest.raises(ValueError):
            FarmCreate(
                name="Test Farm",
                description="Test description",
                location="Test location",
                size_hectares=0.0  # Zero size
            )
        
        with pytest.raises(ValueError):
            FarmCreate(
                name="Test Farm",
                description="Test description",
                location="Test location",
                size_hectares=-1.0  # Negative size
            )
    
    def test_farm_location_validation(self):
        """Test farm location validation."""
        # Valid locations
        valid_locations = [
            "Lagos, Nigeria",
            "Abuja, FCT",
            "Kano, Nigeria",
            "Port Harcourt, Rivers State"
        ]
        
        for location in valid_locations:
            data = {
                "name": "Test Farm",
                "description": "Test description",
                "location": location,
                "size_hectares": 10.0
            }
            farm_create = FarmCreate(**data)
            assert farm_create.location == location

class TestFarmBusinessLogic:
    """Test farm business logic and constraints."""
    
    def test_farm_activation_deactivation(self, session, test_user):
        """Test farm activation and deactivation."""
        farm = Farm(
            name="Activation Farm",
            description="Testing activation",
            location="Test Location",
            size_hectares=10.0,
            is_active=True,
            farmer_id=test_user.id
        )
        session.add(farm)
        session.commit()
        session.refresh(farm)
        
        # Initially active
        assert farm.is_active is True
        
        # Deactivate farm
        farm.is_active = False
        session.commit()
        session.refresh(farm)
        
        assert farm.is_active is False
        
        # Reactivate farm
        farm.is_active = True
        session.commit()
        session.refresh(farm)
        
        assert farm.is_active is True
    
    def test_farm_size_calculations(self, session, test_user):
        """Test farm size calculations and conversions."""
        # Test different size units and calculations
        farm = Farm(
            name="Calculation Farm",
            description="Testing calculations",
            location="Test Location",
            size_hectares=10.0,
            farmer_id=test_user.id
        )
        session.add(farm)
        session.commit()
        session.refresh(farm)
        
        # 10 hectares = 100,000 square meters
        size_sqm = farm.size_hectares * 10000
        assert size_sqm == 100000.0
        
        # 10 hectares = 24.71 acres (approximate)
        size_acres = farm.size_hectares * 2.471
        assert abs(size_acres - 24.71) < 0.01
    
    def test_farm_soil_irrigation_combinations(self, session, test_user):
        """Test different soil and irrigation combinations."""
        combinations = [
            ("Loamy", "Drip"),
            ("Sandy", "Sprinkler"),
            ("Clay", "Flood"),
            ("Silt", "Center Pivot"),
            ("Peaty", "None")
        ]
        
        for soil_type, irrigation_type in combinations:
            farm = Farm(
                name=f"Farm {soil_type}-{irrigation_type}",
                description=f"Testing {soil_type} soil with {irrigation_type} irrigation",
                location="Test Location",
                size_hectares=10.0,
                soil_type=soil_type,
                irrigation_type=irrigation_type,
                farmer_id=test_user.id
            )
            session.add(farm)
        
        session.commit()
        
        # Verify all combinations were saved
        for soil_type, irrigation_type in combinations:
            farm = session.exec(
                select(Farm).where(
                    Farm.soil_type == soil_type,
                    Farm.irrigation_type == irrigation_type
                )
            ).first()
            assert farm is not None
            assert farm.soil_type == soil_type
            assert farm.irrigation_type == irrigation_type
    
    def test_farm_timestamps(self, session, test_user):
        """Test that farm timestamps are set correctly."""
        before_creation = datetime.now()
        
        farm = Farm(
            name="Timestamp Farm",
            description="Testing timestamps",
            location="Test Location",
            size_hectares=10.0,
            farmer_id=test_user.id
        )
        session.add(farm)
        session.commit()
        session.refresh(farm)
        
        after_creation = datetime.now()
        
        assert farm.created_at >= before_creation
        assert farm.created_at <= after_creation
        assert farm.updated_at >= before_creation
        assert farm.updated_at <= after_creation
        assert farm.created_at == farm.updated_at  # Initially they should be the same
        
        # Update farm and check updated_at changes
        farm.description = "Updated description"
        session.commit()
        session.refresh(farm)
        
        assert farm.updated_at > farm.created_at
