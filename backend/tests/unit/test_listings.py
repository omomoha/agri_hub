import pytest
from app.models.listing import Listing, ListingStatus
from app.models.user import User, UserRole
from app.models.farm import Farm
from app.schemas.listing import ListingCreate, ListingResponse, ListingUpdate
from sqlmodel import Session, select
from datetime import datetime, timedelta

class TestListingModel:
    """Test Listing model functionality."""
    
    def test_listing_creation(self, session, test_user, test_farm):
        """Test creating a new listing."""
        listing_data = {
            "title": "Fresh Tomatoes",
            "description": "Organic red tomatoes from our farm",
            "produce_type": "vegetables",
            "quantity_kg": 100.0,
            "unit_price_ngn": 500.0,
            "total_price_ngn": 50000.0,
            "harvest_date": datetime.now().date(),
            "expiry_date": (datetime.now() + timedelta(days=30)).date(),
            "status": ListingStatus.ACTIVE,
            "is_organic": True,
            "quality_grade": "A",
            "farmer_id": test_user.id,
            "farm_id": test_farm.id
        }
        
        listing = Listing(**listing_data)
        session.add(listing)
        session.commit()
        session.refresh(listing)
        
        assert listing.id is not None
        assert listing.title == "Fresh Tomatoes"
        assert listing.description == "Organic red tomatoes from our farm"
        assert listing.produce_type == "vegetables"
        assert listing.quantity_kg == 100.0
        assert listing.unit_price_ngn == 500.0
        assert listing.total_price_ngn == 50000.0
        assert listing.is_organic is True
        assert listing.quality_grade == "A"
        assert listing.status == ListingStatus.ACTIVE
        assert listing.farmer_id == test_user.id
        assert listing.farm_id == test_farm.id
        assert listing.created_at is not None
        assert listing.updated_at is not None
    
    def test_listing_price_calculation(self, session, test_user, test_farm):
        """Test automatic price calculation."""
        listing = Listing(
            title="Test Produce",
            description="Testing price calculation",
            produce_type="fruits",
            quantity_kg=50.0,
            unit_price_ngn=300.0,
            harvest_date=datetime.now().date(),
            expiry_date=(datetime.now() + timedelta(days=30)).date(),
            status=ListingStatus.ACTIVE,
            farmer_id=test_user.id,
            farm_id=test_farm.id
        )
        
        # Calculate expected total price
        expected_total = listing.quantity_kg * listing.unit_price_ngn
        assert expected_total == 15000.0
        
        # Set the calculated total
        listing.total_price_ngn = expected_total
        
        session.add(listing)
        session.commit()
        session.refresh(listing)
        
        assert listing.total_price_ngn == 15000.0
    
    def test_listing_status_transitions(self, session, test_user, test_farm):
        """Test listing status transitions."""
        listing = Listing(
            title="Status Test",
            description="Testing status transitions",
            produce_type="vegetables",
            quantity_kg=25.0,
            unit_price_ngn=400.0,
            total_price_ngn=10000.0,
            harvest_date=datetime.now().date(),
            expiry_date=(datetime.now() + timedelta(days=30)).date(),
            status=ListingStatus.ACTIVE,
            farmer_id=test_user.id,
            farm_id=test_farm.id
        )
        session.add(listing)
        session.commit()
        session.refresh(listing)
        
        # Initially active
        assert listing.status == ListingStatus.ACTIVE
        
        # Change to sold
        listing.status = ListingStatus.SOLD
        session.commit()
        session.refresh(listing)
        assert listing.status == ListingStatus.SOLD
        
        # Change to expired
        listing.status = ListingStatus.EXPIRED
        session.commit()
        session.refresh(listing)
        assert listing.status == ListingStatus.EXPIRED
        
        # Change back to active
        listing.status = ListingStatus.ACTIVE
        session.commit()
        session.refresh(listing)
        assert listing.status == ListingStatus.ACTIVE
    
    def test_listing_dates_validation(self, session, test_user, test_farm):
        """Test listing date validation."""
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        next_month = today + timedelta(days=30)
        
        # Valid dates
        listing = Listing(
            title="Date Test",
            description="Testing date validation",
            produce_type="vegetables",
            quantity_kg=25.0,
            unit_price_ngn=400.0,
            total_price_ngn=10000.0,
            harvest_date=today,
            expiry_date=next_month,
            status=ListingStatus.ACTIVE,
            farmer_id=test_user.id,
            farm_id=test_farm.id
        )
        session.add(listing)
        session.commit()
        session.refresh(listing)
        
        assert listing.harvest_date == today
        assert listing.expiry_date == next_month
        
        # Test that expiry date is after harvest date
        assert listing.expiry_date > listing.harvest_date
    
    def test_listing_produce_types(self, session, test_user, test_farm):
        """Test different produce type configurations."""
        produce_types = ["vegetables", "fruits", "grains", "tubers", "legumes"]
        
        for produce_type in produce_types:
            listing = Listing(
                title=f"Test {produce_type.title()}",
                description=f"Testing {produce_type}",
                produce_type=produce_type,
                quantity_kg=25.0,
                unit_price_ngn=400.0,
                total_price_ngn=10000.0,
                harvest_date=datetime.now().date(),
                expiry_date=(datetime.now() + timedelta(days=30)).date(),
                status=ListingStatus.ACTIVE,
                farmer_id=test_user.id,
                farm_id=test_farm.id
            )
            session.add(listing)
        
        session.commit()
        
        # Verify all produce types were saved
        for produce_type in produce_types:
            listing = session.exec(select(Listing).where(Listing.produce_type == produce_type)).first()
            assert listing is not None
            assert listing.produce_type == produce_type
    
    def test_listing_quality_grades(self, session, test_user, test_farm):
        """Test different quality grade configurations."""
        quality_grades = ["A", "B", "C", "Premium", "Standard"]
        
        for grade in quality_grades:
            listing = Listing(
                title=f"Grade {grade} Produce",
                description=f"Testing grade {grade}",
                produce_type="vegetables",
                quantity_kg=25.0,
                unit_price_ngn=400.0,
                total_price_ngn=10000.0,
                harvest_date=datetime.now().date(),
                expiry_date=(datetime.now() + timedelta(days=30)).date(),
                status=ListingStatus.ACTIVE,
                quality_grade=grade,
                farmer_id=test_user.id,
                farm_id=test_farm.id
            )
            session.add(listing)
        
        session.commit()
        
        # Verify all quality grades were saved
        for grade in quality_grades:
            listing = session.exec(select(Listing).where(Listing.quality_grade == grade)).first()
            assert listing is not None
            assert listing.quality_grade == grade

class TestListingSchemas:
    """Test listing Pydantic schemas."""
    
    def test_listing_create_schema(self):
        """Test ListingCreate schema validation."""
        listing_data = {
            "title": "Schema Test",
            "description": "Testing schema validation",
            "produce_type": "fruits",
            "quantity_kg": 75.0,
            "unit_price_ngn": 600.0,
            "harvest_date": datetime.now().date(),
            "expiry_date": (datetime.now() + timedelta(days=30)).date(),
            "is_organic": True,
            "quality_grade": "Premium",
            "farm_id": 1
        }
        
        listing_create = ListingCreate(**listing_data)
        
        assert listing_create.title == "Schema Test"
        assert listing_create.description == "Testing schema validation"
        assert listing_create.produce_type == "fruits"
        assert listing_create.quantity_kg == 75.0
        assert listing_create.unit_price_ngn == 600.0
        assert listing_create.is_organic is True
        assert listing_create.quality_grade == "Premium"
        assert listing_create.farm_id == 1
    
    def test_listing_update_schema(self):
        """Test ListingUpdate schema validation."""
        update_data = {
            "title": "Updated Title",
            "description": "Updated description",
            "quantity_kg": 80.0,
            "unit_price_ngn": 650.0
        }
        
        listing_update = ListingUpdate(**update_data)
        
        assert listing_update.title == "Updated Title"
        assert listing_update.description == "Updated description"
        assert listing_update.quantity_kg == 80.0
        assert listing_update.unit_price_ngn == 650.0
        assert listing_update.produce_type is None  # Not provided
    
    def test_listing_response_schema(self):
        """Test ListingResponse schema validation."""
        response_data = {
            "id": 1,
            "title": "Response Test",
            "description": "Testing response schema",
            "produce_type": "vegetables",
            "quantity_kg": 50.0,
            "unit_price_ngn": 400.0,
            "total_price_ngn": 20000.0,
            "harvest_date": datetime.now().date(),
            "expiry_date": (datetime.now() + timedelta(days=30)).date(),
            "status": "active",
            "is_organic": False,
            "quality_grade": "A",
            "farmer_id": 1,
            "farm_id": 1,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        listing_response = ListingResponse(**response_data)
        
        assert listing_response.id == 1
        assert listing_response.title == "Response Test"
        assert listing_response.description == "Testing response schema"
        assert listing_response.produce_type == "vegetables"
        assert listing_response.quantity_kg == 50.0
        assert listing_response.unit_price_ngn == 400.0
        assert listing_response.total_price_ngn == 20000.0
        assert listing_response.status == "active"
        assert listing_response.is_organic is False
        assert listing_response.quality_grade == "A"

class TestListingValidation:
    """Test listing data validation."""
    
    def test_listing_title_validation(self):
        """Test listing title validation."""
        # Valid titles
        valid_titles = ["Fresh Tomatoes", "Organic Apples", "Premium Rice", "Farm Fresh Eggs"]
        
        for title in valid_titles:
            data = {
                "title": title,
                "description": "Test description",
                "produce_type": "vegetables",
                "quantity_kg": 25.0,
                "unit_price_ngn": 400.0,
                "harvest_date": datetime.now().date(),
                "expiry_date": (datetime.now() + timedelta(days=30)).date(),
                "farm_id": 1
            }
            listing_create = ListingCreate(**data)
            assert listing_create.title == title
        
        # Invalid titles (empty)
        with pytest.raises(ValueError):
            ListingCreate(
                title="",  # Empty title
                description="Test description",
                produce_type="vegetables",
                quantity_kg=25.0,
                unit_price_ngn=400.0,
                harvest_date=datetime.now().date(),
                expiry_date=(datetime.now() + timedelta(days=30)).date(),
                farm_id=1
            )
    
    def test_listing_quantity_validation(self):
        """Test listing quantity validation."""
        # Valid quantities
        valid_quantities = [0.1, 1.0, 50.0, 100.0, 1000.0]
        
        for quantity in valid_quantities:
            data = {
                "title": "Test Produce",
                "description": "Test description",
                "produce_type": "vegetables",
                "quantity_kg": quantity,
                "unit_price_ngn": 400.0,
                "harvest_date": datetime.now().date(),
                "expiry_date": (datetime.now() + timedelta(days=30)).date(),
                "farm_id": 1
            }
            listing_create = ListingCreate(**data)
            assert listing_create.quantity_kg == quantity
        
        # Invalid quantities
        with pytest.raises(ValueError):
            ListingCreate(
                title="Test Produce",
                description="Test description",
                produce_type="vegetables",
                quantity_kg=0.0,  # Zero quantity
                unit_price_ngn=400.0,
                harvest_date=datetime.now().date(),
                expiry_date=(datetime.now() + timedelta(days=30)).date(),
                farm_id=1
            )
        
        with pytest.raises(ValueError):
            ListingCreate(
                title="Test Produce",
                description="Test description",
                produce_type="vegetables",
                quantity_kg=-1.0,  # Negative quantity
                unit_price_ngn=400.0,
                harvest_date=datetime.now().date(),
                expiry_date=(datetime.now() + timedelta(days=30)).date(),
                farm_id=1
            )
    
    def test_listing_price_validation(self):
        """Test listing price validation."""
        # Valid prices
        valid_prices = [1.0, 100.0, 1000.0, 10000.0]
        
        for price in valid_prices:
            data = {
                "title": "Test Produce",
                "description": "Test description",
                "produce_type": "vegetables",
                "quantity_kg": 25.0,
                "unit_price_ngn": price,
                "harvest_date": datetime.now().date(),
                "expiry_date": (datetime.now() + timedelta(days=30)).date(),
                "farm_id": 1
            }
            listing_create = ListingCreate(**data)
            assert listing_create.unit_price_ngn == price
        
        # Invalid prices
        with pytest.raises(ValueError):
            ListingCreate(
                title="Test Produce",
                description="Test description",
                produce_type="vegetables",
                quantity_kg=25.0,
                unit_price_ngn=0.0,  # Zero price
                harvest_date=datetime.now().date(),
                expiry_date=(datetime.now() + timedelta(days=30)).date(),
                farm_id=1
            )
        
        with pytest.raises(ValueError):
            ListingCreate(
                title="Test Produce",
                description="Test description",
                produce_type="vegetables",
                quantity_kg=25.0,
                unit_price_ngn=-1.0,  # Negative price
                harvest_date=datetime.now().date(),
                expiry_date=(datetime.now() + timedelta(days=30)).date(),
                farm_id=1
            )

class TestListingBusinessLogic:
    """Test listing business logic and constraints."""
    
    def test_listing_organic_premium_pricing(self, session, test_user, test_farm):
        """Test that organic listings can have premium pricing."""
        # Organic listing with premium pricing
        organic_listing = Listing(
            title="Organic Tomatoes",
            description="Premium organic tomatoes",
            produce_type="vegetables",
            quantity_kg=25.0,
            unit_price_ngn=800.0,  # Higher price for organic
            total_price_ngn=20000.0,
            harvest_date=datetime.now().date(),
            expiry_date=(datetime.now() + timedelta(days=30)).date(),
            status=ListingStatus.ACTIVE,
            is_organic=True,
            quality_grade="Premium",
            farmer_id=test_user.id,
            farm_id=test_farm.id
        )
        session.add(organic_listing)
        
        # Regular listing with standard pricing
        regular_listing = Listing(
            title="Regular Tomatoes",
            description="Standard tomatoes",
            produce_type="vegetables",
            quantity_kg=25.0,
            unit_price_ngn=400.0,  # Standard price
            total_price_ngn=10000.0,
            harvest_date=datetime.now().date(),
            expiry_date=(datetime.now() + timedelta(days=30)).date(),
            status=ListingStatus.ACTIVE,
            is_organic=False,
            quality_grade="A",
            farmer_id=test_user.id,
            farm_id=test_farm.id
        )
        session.add(regular_listing)
        
        session.commit()
        
        # Verify organic listing has higher price
        assert organic_listing.unit_price_ngn > regular_listing.unit_price_ngn
        assert organic_listing.is_organic is True
        assert regular_listing.is_organic is False
    
    def test_listing_expiry_handling(self, session, test_user, test_farm):
        """Test listing expiry handling."""
        # Create listing that expires tomorrow
        tomorrow = datetime.now().date() + timedelta(days=1)
        expiring_listing = Listing(
            title="Expiring Soon",
            description="Will expire tomorrow",
            produce_type="vegetables",
            quantity_kg=25.0,
            unit_price_ngn": 400.0,
            "total_price_ngn": 10000.0,
            "harvest_date": datetime.now().date(),
            "expiry_date": tomorrow,
            "status": ListingStatus.ACTIVE,
            "farmer_id": test_user.id,
            "farm_id": test_farm.id
        )
        session.add(expiring_listing)
        session.commit()
        session.refresh(expiring_listing)
        
        # Check if listing expires tomorrow
        assert expiring_listing.expiry_date == tomorrow
        
        # Simulate expiry by changing status
        expiring_listing.status = ListingStatus.EXPIRED
        session.commit()
        session.refresh(expiring_listing)
        
        assert expiring_listing.status == ListingStatus.EXPIRED
    
    def test_listing_quantity_availability(self, session, test_user, test_farm):
        """Test listing quantity availability tracking."""
        listing = Listing(
            title="Quantity Test",
            description="Testing quantity tracking",
            produce_type="vegetables",
            quantity_kg": 100.0,
            "unit_price_ngn": 400.0,
            "total_price_ngn": 40000.0,
            "harvest_date": datetime.now().date(),
            "expiry_date": (datetime.now() + timedelta(days=30)).date(),
            "status": ListingStatus.ACTIVE,
            "farmer_id": test_user.id,
            "farm_id": test_farm.id
        )
        session.add(listing)
        session.commit()
        session.refresh(listing)
        
        # Initially full quantity available
        assert listing.quantity_kg == 100.0
        
        # Simulate partial sale
        sold_quantity = 30.0
        remaining_quantity = listing.quantity_kg - sold_quantity
        
        listing.quantity_kg = remaining_quantity
        listing.total_price_ngn = remaining_quantity * listing.unit_price_ngn
        session.commit()
        session.refresh(listing)
        
        assert listing.quantity_kg == 70.0
        assert listing.total_price_ngn == 28000.0
        
        # Simulate complete sale
        listing.quantity_kg = 0.0
        listing.total_price_ngn = 0.0
        listing.status = ListingStatus.SOLD
        session.commit()
        session.refresh(listing)
        
        assert listing.quantity_kg == 0.0
        assert listing.status == ListingStatus.SOLD
