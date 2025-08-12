import pytest
import asyncio
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_session
from app.core.auth import create_access_token
from app.models.user import User, UserRole
from app.models.farm import Farm
from app.models.listing import Listing, ListingStatus
from app.models.offer import Offer, OfferStatus
from app.models.contract import Contract, ContractStatus
from app.models.escrow import Escrow, EscrowStatus
from app.models.order import Order, OrderStatus
from app.models.kyc import KYC, KYCStatus
from datetime import datetime, timedelta

# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def engine():
    """Create a test database engine."""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def session(engine):
    """Create a test database session."""
    with Session(engine) as session:
        yield session

@pytest.fixture(scope="function")
def client(session):
    """Create a test client with overridden dependencies."""
    def override_get_session():
        yield session
    
    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user(session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.i8rG",  # password123
        full_name="Test User",
        phone="+1234567890",
        role=UserRole.FARMER,
        is_active=True,
        is_verified=True,
        kyc_status="approved"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_admin(session):
    """Create a test admin user."""
    admin = User(
        email="admin@example.com",
        username="admin",
        hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.i8rG",  # password123
        full_name="Admin User",
        phone="+1234567890",
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True,
        kyc_status="approved"
    )
    session.add(admin)
    session.commit()
    session.refresh(admin)
    return admin

@pytest.fixture(scope="function")
def test_buyer(session):
    """Create a test buyer user."""
    buyer = User(
        email="buyer@example.com",
        username="buyer",
        hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.i8rG",  # password123
        full_name="Buyer User",
        phone="+1234567890",
        role=UserRole.BUYER,
        is_active=True,
        is_verified=True,
        kyc_status="approved"
    )
    session.add(buyer)
    session.commit()
    session.refresh(buyer)
    return buyer

@pytest.fixture(scope="function")
def test_farm(session, test_user):
    """Create a test farm."""
    farm = Farm(
        name="Test Farm",
        description="A test farm for testing",
        location="Test Location",
        size_hectares=10.0,
        soil_type="Loamy",
        irrigation_type="Drip",
        is_active=True,
        farmer_id=test_user.id
    )
    session.add(farm)
    session.commit()
    session.refresh(farm)
    return farm

@pytest.fixture(scope="function")
def test_listing(session, test_user, test_farm):
    """Create a test listing."""
    listing = Listing(
        title="Test Produce",
        description="Fresh test produce",
        produce_type="vegetables",
        quantity_kg=100.0,
        unit_price_ngn=500.0,
        total_price_ngn=50000.0,
        harvest_date=datetime.now().date(),
        expiry_date=(datetime.now() + timedelta(days=30)).date(),
        status=ListingStatus.ACTIVE,
        is_organic=True,
        quality_grade="A",
        farmer_id=test_user.id,
        farm_id=test_farm.id
    )
    session.add(listing)
    session.commit()
    session.refresh(listing)
    return listing

@pytest.fixture(scope="function")
def test_offer(session, test_buyer, test_listing):
    """Create a test offer."""
    offer = Offer(
        quantity_kg=50.0,
        unit_price_ngn=450.0,
        total_price_ngn=22500.0,
        delivery_date=(datetime.now() + timedelta(days=7)).date(),
        delivery_location="Test Delivery Location",
        notes="Test offer",
        status=OfferStatus.PENDING,
        expiration_date=(datetime.now() + timedelta(days=3)).date(),
        buyer_id=test_buyer.id,
        listing_id=test_listing.id
    )
    session.add(offer)
    session.commit()
    session.refresh(offer)
    return offer

@pytest.fixture(scope="function")
def test_contract(session, test_user, test_buyer, test_listing, test_offer):
    """Create a test contract."""
    contract = Contract(
        contract_number="CON-001",
        quantity_kg=50.0,
        unit_amount_ngn=450.0,
        total_amount_ngn=22500.0,
        delivery_date=(datetime.now() + timedelta(days=7)).date(),
        delivery_location="Test Delivery Location",
        terms="Test contract terms",
        status=ContractStatus.ACTIVE,
        farmer_id=test_user.id,
        buyer_id=test_buyer.id,
        listing_id=test_listing.id,
        offer_id=test_offer.id
    )
    session.add(contract)
    session.commit()
    session.refresh(contract)
    return contract

@pytest.fixture(scope="function")
def test_escrow(session, test_contract, test_buyer, test_user):
    """Create a test escrow."""
    escrow = Escrow(
        escrow_number="ESC-001",
        amount=22500.0,
        status=EscrowStatus.FUNDED,
        funded_date=datetime.now(),
        contract_id=test_contract.id,
        buyer_id=test_buyer.id,
        seller_id=test_user.id
    )
    session.add(escrow)
    session.commit()
    session.refresh(escrow)
    return escrow

@pytest.fixture(scope="function")
def test_order(session, test_contract, test_user, test_buyer):
    """Create a test order."""
    order = Order(
        order_number="ORD-001",
        quantity_kg=50.0,
        delivery_address="Test Delivery Address",
        delivery_instructions="Handle with care",
        status=OrderStatus.CONFIRMED,
        confirmed_date=datetime.now(),
        contract_id=test_contract.id,
        farmer_id=test_user.id,
        buyer_id=test_buyer.id
    )
    session.add(order)
    session.commit()
    session.refresh(order)
    return order

@pytest.fixture(scope="function")
def test_kyc(session, test_user):
    """Create a test KYC record."""
    kyc = KYC(
        user_id=test_user.id,
        document_type="national_id",
        document_number="ID123456",
        document_file_path="/test/path/document.pdf",
        selfie_file_path="/test/path/selfie.jpg",
        business_registration="/test/path/business.pdf",
        business_address="Test Business Address",
        status=KYCStatus.PENDING
    )
    session.add(kyc)
    session.commit()
    session.refresh(kyc)
    return kyc

@pytest.fixture(scope="function")
def auth_headers(test_user):
    """Create authentication headers for a test user."""
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function")
def admin_headers(test_admin):
    """Create authentication headers for a test admin."""
    token = create_access_token(data={"sub": str(test_admin.id)})
    return {"Authorization": f"Bearer {token}"}
