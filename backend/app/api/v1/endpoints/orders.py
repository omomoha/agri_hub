from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.auth import get_current_user, require_role
from app.core.database import get_session
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus
from app.models.contract import Contract
from app.models.escrow import Escrow, EscrowStatus
from app.schemas.order import OrderResponse
from datetime import datetime
import uuid

router = APIRouter()

@router.post("/{contract_id}/create", response_model=OrderResponse)
async def create_order(
    contract_id: int,
    delivery_address: str,
    delivery_instructions: str = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Get the contract
    contract = session.exec(select(Contract).where(Contract.id == contract_id)).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    # Check if user is the buyer
    if contract.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only buyers can create orders"
        )
    
    # Check if escrow is funded
    escrow = session.exec(select(Escrow).where(Escrow.contract_id == contract_id)).first()
    if not escrow or escrow.status != EscrowStatus.FUNDED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Escrow must be funded before creating order"
        )
    
    # Check if order already exists
    existing_order = session.exec(
        select(Order).where(Order.contract_id == contract_id)
    ).first()
    
    if existing_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order already exists for this contract"
        )
    
    # Generate order number
    order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    
    # Create order
    order = Order(
        order_number=order_number,
        quantity_kg=contract.quantity_kg,
        delivery_address=delivery_address,
        delivery_instructions=delivery_instructions,
        contract_id=contract.id,
        farmer_id=contract.farmer_id,
        buyer_id=contract.buyer_id
    )
    
    session.add(order)
    session.commit()
    session.refresh(order)
    
    return OrderResponse.from_orm(order)

@router.get("/", response_model=list[OrderResponse])
async def get_orders(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Users can see orders they're involved in
    orders = session.exec(
        select(Order).where(
            (Order.farmer_id == current_user.id) | 
            (Order.buyer_id == current_user.id) |
            (Order.logistics_id == current_user.id)
        )
    ).all()
    
    return [OrderResponse.from_orm(order) for order in orders]

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    order = session.exec(select(Order).where(Order.id == order_id)).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check if user is involved in this order
    if (order.farmer_id != current_user.id and 
        order.buyer_id != current_user.id and 
        order.logistics_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return OrderResponse.from_orm(order)

@router.post("/{order_id}/confirm", response_model=OrderResponse)
async def confirm_order(
    order_id: int,
    current_user: User = Depends(require_role("farmer")),
    session: Session = Depends(get_session)
):
    order = session.exec(select(Order).where(Order.id == order_id)).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check if user is the farmer
    if order.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only farmers can confirm orders"
        )
    
    # Check if order is in pending status
    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order is not in pending status"
        )
    
    # Confirm the order
    order.status = OrderStatus.CONFIRMED
    order.confirmed_at = datetime.utcnow()
    
    session.commit()
    session.refresh(order)
    
    return OrderResponse.from_orm(order)

@router.post("/{order_id}/deliver", response_model=OrderResponse)
async def deliver_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    order = session.exec(select(Order).where(Order.id == order_id)).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check if user is the farmer or logistics provider
    if (order.farmer_id != current_user.id and 
        order.logistics_id != current_user.id and
        current_user.role != UserRole.LOGISTICS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if order is confirmed
    if order.status != OrderStatus.CONFIRMED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must be confirmed before delivery"
        )
    
    # Mark as delivered
    order.status = OrderStatus.DELIVERED
    order.delivered_at = datetime.utcnow()
    
    # Release escrow (in real implementation, this would trigger payment release)
    escrow = session.exec(
        select(Escrow).where(Escrow.contract_id == order.contract_id)
    ).first()
    
    if escrow:
        escrow.status = EscrowStatus.RELEASED
        escrow.released_at = datetime.utcnow()
    
    session.commit()
    session.refresh(order)
    
    return OrderResponse.from_orm(order)
