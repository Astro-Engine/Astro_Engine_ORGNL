"""
Request Queue Manager for Astro Engine
Phase 12: Request Queuing System (PROPER IMPLEMENTATION)

Uses RQ (Redis Queue) for simple, effective job queuing.

Features:
- Redis-based job queue
- Priority queuing (high, normal, low)
- Queue depth monitoring
- Graceful degradation when queue full
- Job status tracking

Architecture:
- Default queue: Normal priority calculations
- High priority queue: Paid tier / critical requests
- Low priority queue: Background tasks
"""

import logging
from typing import Optional, Dict, Any
from redis import Redis
from rq import Queue, Worker
from rq.job import Job
from rq.registry import StartedJobRegistry, FinishedJobRegistry, FailedJobRegistry
import os

logger = logging.getLogger(__name__)


# =============================================================================
# PHASE 12, MODULE 12.1: REDIS QUEUE IMPLEMENTATION
# =============================================================================

class AstroQueueManager:
    """
    Manages job queues for Astro Engine calculations

    Phase 12, Module 12.1-12.5: Complete queue management
    """

    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize queue manager

        Args:
            redis_url: Redis connection URL (optional, reads from env)
        """
        self.redis_url = redis_url or os.getenv('REDIS_URL')
        self.redis_conn = None
        self.queues = {}
        self.is_enabled = False

        if self.redis_url:
            try:
                self.redis_conn = Redis.from_url(
                    self.redis_url,
                    socket_timeout=5,
                    socket_connect_timeout=5
                )
                self.redis_conn.ping()

                # Phase 12, Module 12.2: Priority queues
                self.queues = {
                    'high': Queue('high', connection=self.redis_conn),      # Priority: 9
                    'default': Queue('default', connection=self.redis_conn), # Priority: 5
                    'low': Queue('low', connection=self.redis_conn)         # Priority: 1
                }

                self.is_enabled = True
                logger.info("✅ Queue manager initialized with Redis")
                logger.info(f"   Queues: high, default, low")

            except Exception as e:
                logger.warning(f"⚠️  Queue manager disabled: {e}")
                self.is_enabled = False
        else:
            logger.info("ℹ️  Queue manager disabled (no REDIS_URL)")

    def enqueue_job(self, func, args=None, kwargs=None, priority='default',
                   timeout=300, result_ttl=3600, job_id=None):
        """
        Enqueue a job for async processing

        Phase 12, Module 12.1: Job submission

        Args:
            func: Function to execute
            args: Positional arguments
            kwargs: Keyword arguments
            priority: 'high', 'default', or 'low'
            timeout: Job timeout in seconds (default: 5 minutes)
            result_ttl: How long to keep result (default: 1 hour)
            job_id: Custom job ID (optional)

        Returns:
            Job: RQ Job object or None if disabled
        """
        if not self.is_enabled:
            logger.warning("Queue not enabled, executing synchronously")
            # Execute immediately if queue disabled
            return func(*args or [], **kwargs or {})

        # Get appropriate queue
        queue = self.queues.get(priority, self.queues['default'])

        # Enqueue job
        try:
            job = queue.enqueue(
                func,
                args=args or [],
                kwargs=kwargs or {},
                timeout=timeout,
                result_ttl=result_ttl,
                job_id=job_id
            )

            logger.info(f"Job enqueued: {job.id} (priority: {priority})")
            return job

        except Exception as e:
            logger.error(f"Failed to enqueue job: {e}")
            # Fallback: execute synchronously
            return func(*args or [], **kwargs or {})

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get status of a queued job

        Args:
            job_id: Job ID

        Returns:
            dict: Job status information
        """
        if not self.is_enabled:
            return {'error': 'Queue not enabled'}

        try:
            job = Job.fetch(job_id, connection=self.redis_conn)

            return {
                'job_id': job.id,
                'status': job.get_status(),
                'result': job.result if job.is_finished else None,
                'error': str(job.exc_info) if job.is_failed else None,
                'created_at': job.created_at.isoformat() if job.created_at else None,
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'ended_at': job.ended_at.isoformat() if job.ended_at else None
            }

        except Exception as e:
            return {'error': f'Job not found: {e}'}

    def get_queue_stats(self) -> Dict[str, Any]:
        """
        Get statistics for all queues

        Phase 12, Module 12.3: Queue depth monitoring

        Returns:
            dict: Queue statistics
        """
        if not self.is_enabled:
            return {
                'enabled': False,
                'message': 'Queue not enabled'
            }

        stats = {
            'enabled': True,
            'queues': {}
        }

        for name, queue in self.queues.items():
            try:
                stats['queues'][name] = {
                    'name': name,
                    'count': len(queue),  # Jobs waiting
                    'started': queue.started_job_registry.count,  # Jobs running
                    'finished': queue.finished_job_registry.count,  # Recently finished
                    'failed': queue.failed_job_registry.count  # Failed jobs
                }
            except Exception as e:
                logger.error(f"Error getting stats for queue {name}: {e}")
                stats['queues'][name] = {'error': str(e)}

        return stats

    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a queued job

        Args:
            job_id: Job ID to cancel

        Returns:
            bool: True if cancelled, False otherwise
        """
        if not self.is_enabled:
            return False

        try:
            job = Job.fetch(job_id, connection=self.redis_conn)
            job.cancel()
            logger.info(f"Job cancelled: {job_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to cancel job {job_id}: {e}")
            return False

    def clear_queue(self, queue_name: str = 'default') -> int:
        """
        Clear all jobs from a queue

        Args:
            queue_name: Queue to clear

        Returns:
            int: Number of jobs cleared
        """
        if not self.is_enabled:
            return 0

        queue = self.queues.get(queue_name)
        if not queue:
            return 0

        try:
            count = len(queue)
            queue.empty()
            logger.info(f"Cleared {count} jobs from {queue_name} queue")
            return count

        except Exception as e:
            logger.error(f"Failed to clear queue {queue_name}: {e}")
            return 0

    def is_queue_full(self, queue_name: str = 'default', max_size: int = 1000) -> bool:
        """
        Check if queue is approaching capacity

        Phase 12, Module 12.4: Graceful degradation

        Args:
            queue_name: Queue to check
            max_size: Maximum acceptable queue size

        Returns:
            bool: True if queue is full
        """
        if not self.is_enabled:
            return False

        queue = self.queues.get(queue_name)
        if not queue:
            return False

        try:
            current_size = len(queue)
            return current_size >= max_size

        except Exception as e:
            logger.error(f"Error checking queue size: {e}")
            return False


def create_queue_manager(app=None):
    """
    Factory function to create queue manager

    Args:
        app: Flask app (optional)

    Returns:
        AstroQueueManager: Configured queue manager
    """
    redis_url = os.getenv('REDIS_URL') if not app else app.config.get('REDIS_URL', os.getenv('REDIS_URL'))
    manager = AstroQueueManager(redis_url)

    if app:
        app.queue_manager = manager

    return manager


# Critical Notes:
#
# 1. REQUIRES Redis to be available
# 2. WORKERS must be started separately: rq worker high default low
# 3. MONITOR queue depth to prevent overflow
# 4. USE appropriate priority for each job type
# 5. SET reasonable timeouts (5 minutes default)
# 6. FALLBACK to synchronous if queue unavailable
# 7. LOG all queue operations
# 8. TEST with actual workload before production
