"""Payment processing service for Bakhmach Business Hub.

Handles payment processing, invoicing, and subscription management.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from decimal import Decimal
import uuid

from pydantic import BaseModel, Field
import stripe
from sqlalchemy import Column, String, Numeric, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class PaymentStatus(str, Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class SubscriptionPlan(str, Enum):
    """Available subscription plans."""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class PaymentRequest(BaseModel):
    """Payment request model."""
    user_id: str
    amount: Decimal = Field(gt=0)
    currency: str = "USD"
    description: str
    plan: Optional[SubscriptionPlan] = None
    metadata: Optional[Dict[str, str]] = None


class PaymentResponse(BaseModel):
    """Payment response model."""
    payment_id: str
    status: PaymentStatus
    amount: Decimal
    currency: str
    created_at: datetime
    updated_at: datetime
    error: Optional[str] = None


class InvoiceRequest(BaseModel):
    """Invoice request model."""
    user_id: str
    payment_id: str
    items: List[Dict[str, Any]]
    due_date: datetime


class PaymentProcessor:
    """Handles payment processing with Stripe."""

    def __init__(self, api_key: str):
        """Initialize payment processor.

        Args:
            api_key: Stripe API key
        """
        stripe.api_key = api_key
        self.logger = logger

    def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Process a payment.

        Args:
            request: Payment request details

        Returns:
            Payment response with status

        Raises:
            PaymentException: If payment processing fails
        """
        try:
            payment_id = str(uuid.uuid4())
            self.logger.info(f"Processing payment {payment_id} for user {request.user_id}")

            # Create charge
            charge = stripe.Charge.create(
                amount=int(request.amount * 100),  # Convert to cents
                currency=request.currency.lower(),
                description=request.description,
                metadata={
                    "payment_id": payment_id,
                    "user_id": request.user_id,
                    "plan": request.plan.value if request.plan else None,
                    **(request.metadata or {})
                }
            )

            self.logger.info(f"Charge created: {charge.id}")

            return PaymentResponse(
                payment_id=payment_id,
                status=PaymentStatus.COMPLETED,
                amount=request.amount,
                currency=request.currency,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

        except stripe.error.CardError as e:
            self.logger.error(f"Card error: {e.message}")
            return PaymentResponse(
                payment_id=str(uuid.uuid4()),
                status=PaymentStatus.FAILED,
                amount=request.amount,
                currency=request.currency,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                error=e.message
            )
        except stripe.error.StripeError as e:
            self.logger.error(f"Stripe error: {str(e)}")
            raise PaymentException(f"Payment processing failed: {str(e)}") from e

    def create_subscription(self, user_id: str, plan: SubscriptionPlan) -> Dict[str, Any]:
        """Create a subscription for a user.

        Args:
            user_id: User ID
            plan: Subscription plan

        Returns:
            Subscription details
        """
        try:
            plan_prices = {
                SubscriptionPlan.STARTER: "price_starter",
                SubscriptionPlan.PROFESSIONAL: "price_professional",
                SubscriptionPlan.ENTERPRISE: "price_enterprise",
            }

            if plan not in plan_prices:
                raise ValueError(f"Invalid plan: {plan}")

            # Create customer if not exists
            customer = stripe.Customer.create(
                metadata={"user_id": user_id}
            )

            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[
                    {"price": plan_prices[plan]}
                ],
                payment_behavior="default_incomplete",
                expand=["latest_invoice.payment_intent"]
            )

            self.logger.info(f"Subscription created for user {user_id}: {subscription.id}")

            return {
                "subscription_id": subscription.id,
                "customer_id": customer.id,
                "plan": plan.value,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end
            }

        except stripe.error.StripeError as e:
            self.logger.error(f"Subscription creation failed: {str(e)}")
            raise PaymentException(f"Subscription creation failed: {str(e)}") from e

    def refund_payment(self, payment_id: str, reason: str = "requested_by_customer") -> PaymentResponse:
        """Refund a payment.

        Args:
            payment_id: Payment ID to refund
            reason: Refund reason

        Returns:
            Refund response
        """
        try:
            refund = stripe.Refund.create(
                charge=payment_id,
                reason=reason
            )

            self.logger.info(f"Refund processed: {refund.id}")

            return PaymentResponse(
                payment_id=payment_id,
                status=PaymentStatus.REFUNDED,
                amount=Decimal(refund.amount / 100),
                currency=refund.currency.upper(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

        except stripe.error.StripeError as e:
            self.logger.error(f"Refund failed: {str(e)}")
            raise PaymentException(f"Refund failed: {str(e)}") from e

    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a subscription.

        Args:
            subscription_id: Subscription ID to cancel

        Returns:
            Cancelled subscription details
        """
        try:
            subscription = stripe.Subscription.delete(subscription_id)

            self.logger.info(f"Subscription cancelled: {subscription_id}")

            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "canceled_at": subscription.canceled_at
            }

        except stripe.error.StripeError as e:
            self.logger.error(f"Subscription cancellation failed: {str(e)}")
            raise PaymentException(f"Cancellation failed: {str(e)}") from e

    def get_invoice(self, invoice_id: str) -> Dict[str, Any]:
        """Get invoice details.

        Args:
            invoice_id: Invoice ID

        Returns:
            Invoice details
        """
        try:
            invoice = stripe.Invoice.retrieve(invoice_id)

            return {
                "invoice_id": invoice.id,
                "amount": Decimal(invoice.amount_paid / 100),
                "currency": invoice.currency.upper(),
                "status": invoice.status,
                "paid": invoice.paid,
                "created": invoice.created,
                "due_date": invoice.due_date
            }

        except stripe.error.StripeError as e:
            self.logger.error(f"Invoice retrieval failed: {str(e)}")
            raise PaymentException(f"Invoice retrieval failed: {str(e)}") from e

    def handle_webhook(self, event: Dict[str, Any]) -> None:
        """Handle Stripe webhook events.

        Args:
            event: Webhook event from Stripe
        """
        event_type = event.get("type")

        if event_type == "charge.succeeded":
            charge = event["data"]["object"]
            self.logger.info(f"Payment succeeded: {charge['id']}")
            # Update database

        elif event_type == "charge.failed":
            charge = event["data"]["object"]
            self.logger.warning(f"Payment failed: {charge['id']}")
            # Update database

        elif event_type == "customer.subscription.updated":
            subscription = event["data"]["object"]
            self.logger.info(f"Subscription updated: {subscription['id']}")
            # Update database

        elif event_type == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            self.logger.info(f"Subscription deleted: {subscription['id']}")
            # Update database

        else:
            self.logger.debug(f"Unhandled event type: {event_type}")


class PaymentException(Exception):
    """Custom exception for payment errors."""
    pass
