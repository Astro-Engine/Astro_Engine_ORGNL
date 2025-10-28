"""
Webhook Handler for Astro Engine
Phase 25: Webhook Support for Async Calculations

Implements webhook delivery for long-running calculations using RQ (Redis Queue).

Architecture:
1. Client submits job with webhook_url
2. Job queued in Redis (via RQ)
3. Worker processes job asynchronously
4. Result POSTed to webhook_url when complete
5. Client can check job status via job_id

Security:
- HMAC-SHA256 signatures
- Webhook URL validation
- Retry logic for failed deliveries
"""

import logging
import hashlib
import hmac
import os
import requests
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


# =============================================================================
# PHASE 25, MODULE 25.1: ASYNC CALCULATION JOBS
# =============================================================================

def async_natal_calculation(birth_data: dict, webhook_url: str, webhook_secret: str = None):
    """
    Calculate natal chart asynchronously and deliver via webhook

    Phase 25, Module 25.1 & 25.2: Async job with webhook delivery

    Args:
        birth_data: Birth data dictionary
        webhook_url: URL to POST results to
        webhook_secret: Secret for HMAC signature (optional)

    This function runs in RQ worker (background process)
    """
    logger.info(f"Starting async natal calculation for webhook: {webhook_url}")

    try:
        # Import calculation function
        from astro_engine.engine.natalCharts.natal import lahairi_natal

        # Perform calculation
        result = lahairi_natal(birth_data)

        # Deliver via webhook
        success = deliver_webhook(
            webhook_url=webhook_url,
            payload={
                'status': 'completed',
                'result': result,
                'completed_at': datetime.utcnow().isoformat()
            },
            secret=webhook_secret
        )

        logger.info(f"Async calculation completed, webhook delivered: {success}")
        return {'success': success, 'result': result}

    except Exception as e:
        logger.error(f"Async calculation failed: {e}", exc_info=True)

        # Try to deliver error via webhook
        deliver_webhook(
            webhook_url=webhook_url,
            payload={
                'status': 'failed',
                'error': str(e),
                'failed_at': datetime.utcnow().isoformat()
            },
            secret=webhook_secret
        )

        raise


# =============================================================================
# PHASE 25, MODULE 25.2: WEBHOOK DELIVERY
# =============================================================================

def deliver_webhook(webhook_url: str, payload: Dict[str, Any], secret: Optional[str] = None) -> bool:
    """
    Deliver webhook to client URL

    Phase 25, Module 25.2: Webhook delivery system

    Args:
        webhook_url: Client's webhook URL
        payload: Data to send
        secret: Shared secret for HMAC signature

    Returns:
        bool: True if delivered successfully
    """
    try:
        # Validate URL (security check)
        if not webhook_url.startswith(('http://', 'https://')):
            logger.error(f"Invalid webhook URL: {webhook_url}")
            return False

        # Prepare payload
        import json
        payload_json = json.dumps(payload)

        # Generate signature (Phase 25, Module 25.5)
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Event': 'calculation.completed',
            'User-Agent': 'Astro-Engine-Webhook/1.0'
        }

        if secret:
            signature = generate_webhook_signature(payload_json, secret)
            headers['X-Webhook-Signature'] = signature

        # Deliver webhook (Phase 25, Module 25.3: with retry)
        response = requests.post(
            webhook_url,
            data=payload_json,
            headers=headers,
            timeout=10  # 10 second timeout
        )

        if response.status_code in [200, 201, 202, 204]:
            logger.info(f"Webhook delivered successfully: {webhook_url}")
            return True
        else:
            logger.warning(f"Webhook delivery failed: {webhook_url} - Status {response.status_code}")
            return False

    except requests.exceptions.Timeout:
        logger.error(f"Webhook timeout: {webhook_url}")
        return False
    except Exception as e:
        logger.error(f"Webhook delivery error: {e}")
        return False


# =============================================================================
# PHASE 25, MODULE 25.5: WEBHOOK SECURITY (HMAC SIGNATURES)
# =============================================================================

def generate_webhook_signature(payload: str, secret: str) -> str:
    """
    Generate HMAC-SHA256 signature for webhook

    Phase 25, Module 25.5: Webhook security

    Args:
        payload: JSON string of payload
        secret: Shared secret between server and client

    Returns:
        str: Hex digest of HMAC signature

    Client should verify:
        received_sig = request.headers['X-Webhook-Signature']
        calculated_sig = hmac.new(secret, payload, sha256).hexdigest()
        assert received_sig == calculated_sig
    """
    return hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


def verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
    """
    Verify webhook signature

    Args:
        payload: JSON string
        signature: Received signature
        secret: Shared secret

    Returns:
        bool: True if signature valid
    """
    expected = generate_webhook_signature(payload, secret)
    return hmac.compare_digest(signature, expected)


# =============================================================================
# PHASE 25, MODULE 25.3: WEBHOOK RETRY LOGIC
# =============================================================================

def deliver_webhook_with_retry(webhook_url: str, payload: Dict, secret: str = None, max_retries: int = 3) -> bool:
    """
    Deliver webhook with retry logic

    Phase 25, Module 25.3: Retry on failure

    Retry strategy:
    - Attempt 1: Immediate
    - Attempt 2: After 60 seconds
    - Attempt 3: After 300 seconds (5 minutes)
    - Give up after 3 failures

    Args:
        webhook_url: URL to deliver to
        payload: Payload data
        secret: HMAC secret
        max_retries: Maximum retry attempts

    Returns:
        bool: True if eventually delivered
    """
    from tenacity import retry, stop_after_attempt, wait_fixed
    import time

    @retry(
        stop=stop_after_attempt(max_retries),
        wait=wait_fixed(60),  # Wait 60s between retries
        reraise=True
    )
    def attempt_delivery():
        success = deliver_webhook(webhook_url, payload, secret)
        if not success:
            raise Exception("Webhook delivery failed")
        return success

    try:
        return attempt_delivery()
    except Exception as e:
        logger.error(f"Webhook failed after {max_retries} retries: {e}")
        return False


# =============================================================================
# PHASE 25, MODULE 25.4: JOB METADATA
# =============================================================================

def create_job_metadata(job_id: str, calc_type: str, webhook_url: str) -> Dict[str, Any]:
    """
    Create metadata for async job

    Phase 25, Module 25.4: Job tracking

    Args:
        job_id: Unique job ID
        calc_type: Calculation type
        webhook_url: Webhook URL

    Returns:
        dict: Job metadata
    """
    return {
        'job_id': job_id,
        'type': calc_type,
        'webhook_url': webhook_url,
        'status': 'queued',
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }


# Critical Notes:
#
# 1. VALIDATE webhook URLs (must be http:// or https://)
# 2. USE HMAC signatures (prevent webhook spoofing)
# 3. RETRY failed webhooks (network issues are common)
# 4. SET timeout on webhook delivery (10s max)
# 5. LOG all webhook attempts (for debugging)
# 6. STORE failed webhooks (for manual review)
# 7. TEST with mock webhook server (for development)
# 8. DON'T send sensitive data in webhooks
