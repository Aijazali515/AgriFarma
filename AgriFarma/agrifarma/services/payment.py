# -*- coding: utf-8 -*-
"""
Payment Service
Handles payment processing with support for multiple gateways
Currently implements mock/simulation mode for testing
"""
from __future__ import annotations
from typing import Dict, Optional
from decimal import Decimal
from datetime import datetime, UTC
from flask import current_app
import secrets


class PaymentResult:
    """Result of a payment transaction"""
    def __init__(self, success: bool, transaction_id: str = None, message: str = "", data: Dict = None):
        self.success = success
        self.transaction_id = transaction_id
        self.message = message
        self.data = data or {}
        self.timestamp = datetime.now(UTC)


class PaymentGateway:
    """Base payment gateway interface"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
    
    def process_payment(self, amount: Decimal, currency: str = "PKR", **kwargs) -> PaymentResult:
        """Process a payment transaction"""
        raise NotImplementedError
    
    def verify_payment(self, transaction_id: str) -> PaymentResult:
        """Verify a payment transaction"""
        raise NotImplementedError
    
    def refund_payment(self, transaction_id: str, amount: Decimal = None) -> PaymentResult:
        """Refund a payment transaction"""
        raise NotImplementedError


class MockPaymentGateway(PaymentGateway):
    """Mock payment gateway for testing and development"""
    
    def process_payment(self, amount: Decimal, currency: str = "PKR", **kwargs) -> PaymentResult:
        """
        Simulate payment processing
        Always succeeds in development mode
        """
        # Generate mock transaction ID
        transaction_id = f"MOCK_{secrets.token_hex(8).upper()}"
        
        # Log the payment
        current_app.logger.info(
            f"[MOCK PAYMENT] Amount: {amount} {currency}, Transaction ID: {transaction_id}"
        )
        
        # Simulate payment success
        return PaymentResult(
            success=True,
            transaction_id=transaction_id,
            message="Payment processed successfully (Mock)",
            data={
                'amount': float(amount),
                'currency': currency,
                'gateway': 'mock',
                'customer_email': kwargs.get('customer_email'),
                'order_id': kwargs.get('order_id')
            }
        )
    
    def verify_payment(self, transaction_id: str) -> PaymentResult:
        """Verify mock payment - always returns success for mock transactions"""
        if transaction_id.startswith('MOCK_'):
            return PaymentResult(
                success=True,
                transaction_id=transaction_id,
                message="Payment verified (Mock)",
                data={'status': 'completed'}
            )
        return PaymentResult(
            success=False,
            message="Invalid transaction ID"
        )
    
    def refund_payment(self, transaction_id: str, amount: Decimal = None) -> PaymentResult:
        """Simulate refund"""
        if transaction_id.startswith('MOCK_'):
            refund_id = f"REFUND_{secrets.token_hex(8).upper()}"
            return PaymentResult(
                success=True,
                transaction_id=refund_id,
                message="Refund processed successfully (Mock)",
                data={'original_transaction': transaction_id, 'amount': float(amount) if amount else None}
            )
        return PaymentResult(
            success=False,
            message="Cannot refund: Invalid transaction ID"
        )


class StripeGateway(PaymentGateway):
    """Stripe payment gateway (skeleton for future implementation)"""
    
    def process_payment(self, amount: Decimal, currency: str = "PKR", **kwargs) -> PaymentResult:
        """
        Process payment via Stripe
        Note: Requires Stripe API key configuration
        """
        # TODO: Implement Stripe integration
        # import stripe
        # stripe.api_key = self.config.get('api_key')
        # charge = stripe.Charge.create(...)
        
        return PaymentResult(
            success=False,
            message="Stripe integration not yet implemented"
        )


class JazzCashGateway(PaymentGateway):
    """JazzCash payment gateway for Pakistan (skeleton)"""
    
    def process_payment(self, amount: Decimal, currency: str = "PKR", **kwargs) -> PaymentResult:
        """
        Process payment via JazzCash
        Note: Requires JazzCash merchant credentials
        """
        # TODO: Implement JazzCash integration
        # Integration points:
        # 1. Generate transaction hash
        # 2. Send request to JazzCash API
        # 3. Handle callback/webhook
        
        return PaymentResult(
            success=False,
            message="JazzCash integration not yet implemented"
        )


def get_payment_gateway(gateway_type: str = None) -> PaymentGateway:
    """
    Factory function to get payment gateway instance
    
    Args:
        gateway_type: 'mock', 'stripe', 'jazzcash', etc.
    
    Returns:
        PaymentGateway instance
    """
    if gateway_type is None:
        # Get from config or default to mock
        gateway_type = current_app.config.get('PAYMENT_GATEWAY', 'mock')
    
    gateways = {
        'mock': MockPaymentGateway,
        'stripe': StripeGateway,
        'jazzcash': JazzCashGateway,
    }
    
    gateway_class = gateways.get(gateway_type.lower(), MockPaymentGateway)
    
    # Get gateway-specific config
    config = current_app.config.get(f'PAYMENT_{gateway_type.upper()}_CONFIG', {})
    
    return gateway_class(config)


def process_order_payment(order_id: int, amount: Decimal, customer_email: str, 
                         payment_method: str = 'card') -> PaymentResult:
    """
    Process payment for an order
    
    Args:
        order_id: Order ID
        amount: Payment amount
        customer_email: Customer email
        payment_method: Payment method (card, wallet, cod, etc.)
    
    Returns:
        PaymentResult object
    """
    # COD (Cash on Delivery) doesn't require payment processing
    if payment_method.lower() == 'cod':
        return PaymentResult(
            success=True,
            transaction_id=f"COD_{order_id}",
            message="Cash on Delivery - No payment processing required",
            data={
                'payment_method': 'cod',
                'order_id': order_id,
                'amount': float(amount)
            }
        )
    
    # Get appropriate payment gateway
    gateway = get_payment_gateway()
    
    # Process payment
    result = gateway.process_payment(
        amount=amount,
        currency='PKR',
        customer_email=customer_email,
        order_id=order_id,
        payment_method=payment_method
    )
    
    # Log result
    if result.success:
        current_app.logger.info(
            f"Payment successful for order {order_id}: {result.transaction_id}"
        )
    else:
        current_app.logger.error(
            f"Payment failed for order {order_id}: {result.message}"
        )
    
    return result
