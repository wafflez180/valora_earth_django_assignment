"""
Advanced async database utilities for Valora Earth Django application.
This module provides truly async database operations that can run concurrently.
"""

import asyncio
from typing import Any, List, Optional, Type, TypeVar, Dict
from django.db import models, transaction
from django.db.models import QuerySet
from asgiref.sync import sync_to_async
import logging

logger = logging.getLogger(__name__)

# Type variable for model classes
T = TypeVar('T', bound=models.Model)


class ConcurrentAsyncDBManager:
    """Manager class for concurrent async database operations"""
    
    @staticmethod
    async def concurrent_create(model_class: Type[T], objects_data: List[Dict]) -> List[T]:
        """Create multiple objects concurrently"""
        try:
            # Create all objects in parallel
            tasks = [
                sync_to_async(model_class.objects.create)(**data)
                for data in objects_data
            ]
            return await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error in concurrent create for {model_class.__name__}: {str(e)}")
            raise
    
    @staticmethod
    async def concurrent_get(model_class: Type[T], filters: List[Dict]) -> List[T]:
        """Get multiple objects concurrently using different filters"""
        try:
            # Get all objects in parallel
            tasks = [
                sync_to_async(model_class.objects.get)(**filter_data)
                for filter_data in filters
            ]
            return await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error in concurrent get for {model_class.__name__}: {str(e)}")
            raise
    
    @staticmethod
    async def concurrent_update(model_class: Type[T], updates: List[tuple]) -> List[bool]:
        """Update multiple objects concurrently (id, update_data pairs)"""
        try:
            # Update all objects in parallel
            async def update_single(obj_id: int, update_data: Dict) -> bool:
                try:
                    await sync_to_async(model_class.objects.filter(id=obj_id).update)(**update_data)
                    return True
                except Exception:
                    return False
            
            tasks = [
                update_single(obj_id, update_data)
                for obj_id, update_data in updates
            ]
            return await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error in concurrent update for {model_class.__name__}: {str(e)}")
            raise
    
    @staticmethod
    async def batch_operations(model_class: Type[T], operations: List[Dict]) -> List[Any]:
        """Execute multiple different database operations concurrently"""
        try:
            async def execute_operation(op_data: Dict) -> Any:
                op_type = op_data.get('type')
                if op_type == 'create':
                    return await sync_to_async(model_class.objects.create)(**op_data.get('data', {}))
                elif op_type == 'get':
                    return await sync_to_async(model_class.objects.get)(**op_data.get('filters', {}))
                elif op_type == 'update':
                    return await sync_to_async(model_class.objects.filter(**op_data.get('filters', {})).update)(**op_data.get('data', {}))
                elif op_type == 'delete':
                    return await sync_to_async(model_class.objects.filter(**op_data.get('filters', {})).delete)()
                else:
                    raise ValueError(f"Unknown operation type: {op_type}")
            
            # Execute all operations in parallel
            tasks = [execute_operation(op) for op in operations]
            return await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error in batch operations for {model_class.__name__}: {str(e)}")
            raise


class AsyncTransactionManager:
    """Manager class for async database transactions"""
    
    @staticmethod
    async def atomic_operations(operations: List[callable], *args, **kwargs):
        """Execute multiple operations within a single atomic transaction"""
        try:
            async def execute_in_transaction():
                # Use sync_to_async to wrap the transaction
                return await sync_to_async(transaction.atomic)(
                    lambda: [op(*args, **kwargs) for op in operations]
                )
            
            return await execute_in_transaction()
        except Exception as e:
            logger.error(f"Transaction error: {str(e)}")
            raise
    
    @staticmethod
    async def concurrent_transactions(transaction_groups: List[List[callable]], *args, **kwargs):
        """Execute multiple transaction groups concurrently"""
        try:
            async def execute_transaction_group(ops):
                return await AsyncTransactionManager.atomic_operations(ops, *args, **kwargs)
            
            # Execute all transaction groups in parallel
            tasks = [execute_transaction_group(ops) for ops in transaction_groups]
            return await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Concurrent transactions error: {str(e)}")
            raise


class AsyncQueryOptimizer:
    """Optimizer for async database queries"""
    
    @staticmethod
    async def prefetch_related_async(queryset: QuerySet, *related_fields) -> List[T]:
        """Async version of prefetch_related for better performance"""
        try:
            # Use sync_to_async to wrap the prefetch operation
            return await sync_to_async(lambda: list(queryset.prefetch_related(*related_fields)))()
        except Exception as e:
            logger.error(f"Error in prefetch_related_async: {str(e)}")
            raise
    
    @staticmethod
    async def select_related_async(queryset: QuerySet, *related_fields) -> List[T]:
        """Async version of select_related for better performance"""
        try:
            # Use sync_to_async to wrap the select operation
            return await sync_to_async(lambda: list(queryset.select_related(*related_fields)))()
        except Exception as e:
            logger.error(f"Error in select_related_async: {str(e)}")
            raise
    
    @staticmethod
    async def bulk_operations_async(model_class: Type[T], operations: List[Dict]) -> List[Any]:
        """Execute bulk operations asynchronously"""
        try:
            # Group operations by type for efficiency
            creates = [op['data'] for op in operations if op['type'] == 'create']
            updates = [op for op in operations if op['type'] == 'update']
            deletes = [op['filters'] for op in operations if op['type'] == 'delete']
            
            results = []
            
            # Execute bulk operations
            if creates:
                created = await sync_to_async(model_class.objects.bulk_create)(
                    [model_class(**data) for data in creates]
                )
                results.extend(created)
            
            if updates:
                for update_op in updates:
                    updated = await sync_to_async(model_class.objects.filter(**update_op['filters']).update)(**update_op['data'])
                    results.append(updated)
            
            if deletes:
                for delete_filter in deletes:
                    deleted = await sync_to_async(model_class.objects.filter(**delete_filter).delete)()
                    results.append(deleted)
            
            return results
        except Exception as e:
            logger.error(f"Error in bulk_operations_async: {str(e)}")
            raise


# Convenience functions for concurrent operations
async def concurrent_create(model_class: Type[T], objects_data: List[Dict]) -> List[T]:
    """Create multiple objects concurrently"""
    return await ConcurrentAsyncDBManager.concurrent_create(model_class, objects_data)


async def concurrent_get(model_class: Type[T], filters: List[Dict]) -> List[T]:
    """Get multiple objects concurrently"""
    return await ConcurrentAsyncDBManager.concurrent_get(model_class, filters)


async def concurrent_update(model_class: Type[T], updates: List[tuple]) -> List[bool]:
    """Update multiple objects concurrently"""
    return await ConcurrentAsyncDBManager.concurrent_update(model_class, updates)


async def batch_operations(model_class: Type[T], operations: List[Dict]) -> List[Any]:
    """Execute multiple different database operations concurrently"""
    return await ConcurrentAsyncDBManager.batch_operations(model_class, operations)


async def atomic_operations(operations: List[callable], *args, **kwargs):
    """Execute multiple operations within a single atomic transaction"""
    return await AsyncTransactionManager.atomic_operations(operations, *args, **kwargs)


async def concurrent_transactions(transaction_groups: List[List[callable]], *args, **kwargs):
    """Execute multiple transaction groups concurrently"""
    return await AsyncTransactionManager.concurrent_transactions(transaction_groups, *args, **kwargs)


async def prefetch_related_async(queryset: QuerySet, *related_fields) -> List[T]:
    """Async version of prefetch_related"""
    return await AsyncQueryOptimizer.prefetch_related_async(queryset, *related_fields)


async def select_related_async(queryset: QuerySet, *related_fields) -> List[T]:
    """Async version of select_related"""
    return await AsyncQueryOptimizer.select_related_async(queryset, *related_fields)


async def bulk_operations_async(model_class: Type[T], operations: List[Dict]) -> List[Any]:
    """Execute bulk operations asynchronously"""
    return await AsyncQueryOptimizer.bulk_operations_async(model_class, operations)
