"""
Batch Request Processor for Astro Engine
Phase 20: Batch Request Support

Allows multiple calculations in a single request.

Benefits:
- Reduced HTTP overhead (one request instead of many)
- Transactional processing (all or partial success)
- Better for mobile clients (fewer round trips)

Limitations:
- Maximum 10 requests per batch
- Total batch size under 1 MB
- Synchronous processing (not queued)
"""

import logging
from typing import List, Dict, Any
from flask import current_app

logger = logging.getLogger(__name__)


# =============================================================================
# PHASE 20, MODULE 20.1 & 20.2: BATCH PROCESSING
# =============================================================================

def process_batch_requests(requests: List[Dict[str, Any]], max_batch_size: int = 10) -> Dict[str, Any]:
    """
    Process multiple calculation requests in batch

    Phase 20, Module 20.1-20.2: Batch endpoint implementation

    Args:
        requests: List of request objects
        max_batch_size: Maximum requests per batch

    Returns:
        dict: Batch results with individual statuses

    Request Format:
        [
            {
                "type": "natal",
                "data": {birth_data}
            },
            {
                "type": "navamsa",
                "data": {birth_data}
            }
        ]

    Response Format:
        {
            "batch_id": "abc-123",
            "total_requests": 2,
            "successful": 2,
            "failed": 0,
            "results": [
                {"status": "success", "type": "natal", "data": {...}},
                {"status": "success", "type": "navamsa", "data": {...}}
            ]
        }
    """
    import uuid

    # Phase 20, Module 20.4: Batch size validation
    if len(requests) > max_batch_size:
        raise ValueError(f"Batch size exceeds limit. Maximum: {max_batch_size}, Requested: {len(requests)}")

    if len(requests) == 0:
        raise ValueError("Batch cannot be empty")

    batch_id = str(uuid.uuid4())
    results = []
    successful_count = 0
    failed_count = 0

    logger.info(f"Processing batch request: {batch_id} ({len(requests)} items)")

    # Phase 20, Module 20.2: Process each request
    for index, req in enumerate(requests):
        req_type = req.get('type', 'unknown')
        req_data = req.get('data', {})

        try:
            # Process based on type
            result_data = process_single_calculation(req_type, req_data)

            # Phase 20, Module 20.3: Partial success handling
            results.append({
                'index': index,
                'type': req_type,
                'status': 'success',
                'data': result_data
            })
            successful_count += 1

        except Exception as e:
            # Phase 20, Module 20.3: Handle individual failures
            logger.warning(f"Batch item {index} failed: {e}")

            results.append({
                'index': index,
                'type': req_type,
                'status': 'failed',
                'error': {
                    'message': str(e),
                    'type': e.__class__.__name__
                }
            })
            failed_count += 1

    # Return batch results
    return {
        'batch_id': batch_id,
        'total_requests': len(requests),
        'successful': successful_count,
        'failed': failed_count,
        'results': results,
        'processing_time': 'synchronous'  # Could add timing
    }


def process_single_calculation(calc_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a single calculation

    Args:
        calc_type: Type of calculation (natal, navamsa, etc.)
        data: Birth data

    Returns:
        dict: Calculation result

    Supported types:
        - natal
        - navamsa
        - transit
        - (can be extended)
    """
    # Import calculation functions
    from astro_engine.engine.natalCharts.natal import lahairi_natal
    from astro_engine.engine.divisionalCharts.NavamshaD9 import lahairi_navamsha_chart

    # Route to appropriate calculation
    if calc_type == 'natal':
        return lahairi_natal(data)
    elif calc_type == 'navamsa':
        return lahairi_navamsha_chart(data)
    elif calc_type == 'transit':
        from astro_engine.engine.natalCharts.transit import lahairi_tranist
        return lahairi_tranist(data)
    else:
        raise ValueError(f"Unsupported calculation type: {calc_type}")


# Critical Notes:
#
# 1. LIMIT batch size (10 requests max)
# 2. VALIDATE each request in batch
# 3. HANDLE partial failures gracefully
# 4. RETURN status for each item
# 5. LOG batch processing (with batch_id)
# 6. CONSIDER timeout (batch might take longer)
# 7. TEST with various batch sizes
# 8. MONITOR batch request patterns
