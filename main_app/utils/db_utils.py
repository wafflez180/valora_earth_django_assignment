"""
Database utilities for async operations in Valora Earth Django application.
This module provides async-compatible database operations and utilities.
"""

from typing import Any, List, Optional, Type, TypeVar
from django.db import models, transaction
from django.db.models import QuerySet
from asgiref.sync import sync_to_async
import logging

logger = logging.getLogger(__name__)

# Type variable for model classes
T = TypeVar('T', bound=models.Model)


class AsyncDBManager:
    """Manager class for async database operations"""
    
    @staticmethod
    async def create(model_class: Type[T], **kwargs) -> T:
        """Async create operation for any model"""
        try:
            return await sync_to_async(model_class.objects.create)(**kwargs)
        except Exception as e:
            logger.error(f"Error creating {model_class.__name__}: {str(e)}")
            raise
    
    @staticmethod
    async def get(model_class: Type[T], **kwargs) -> T:
        """Async get operation for any model"""
        try:
            return await sync_to_async(model_class.objects.get)(**kwargs)
        except model_class.DoesNotExist:
            raise
        except Exception as e:
            logger.error(f"Error getting {model_class.__name__}: {str(e)}")
            raise
    
    @staticmethod
    async def filter(model_class: Type[T], **kwargs) -> List[T]:
        """Async filter operation for any model"""
        try:
            queryset = await sync_to_async(lambda: model_class.objects.filter(**kwargs))()
            return await sync_to_async(list)(queryset)
        except Exception as e:
            logger.error(f"Error filtering {model_class.__name__}: {str(e)}")
            raise
    
    @staticmethod
    async def update_or_create(model_class: Type[T], defaults: dict = None, **kwargs) -> tuple[T, bool]:
        """Async update_or_create operation for any model"""
        try:
            return await sync_to_async(model_class.objects.update_or_create)(
                defaults=defaults or {}, **kwargs
            )
        except Exception as e:
            logger.error(f"Error in update_or_create for {model_class.__name__}: {str(e)}")
            raise
    
    @staticmethod
    async def bulk_create(model_class: Type[T], objects: List[T], **kwargs) -> List[T]:
        """Async bulk_create operation for any model"""
        try:
            return await sync_to_async(model_class.objects.bulk_create)(objects, **kwargs)
        except Exception as e:
            logger.error(f"Error in bulk_create for {model_class.__name__}: {str(e)}")
            raise
    
    @staticmethod
    async def delete(model_class: Type[T], **kwargs) -> int:
        """Async delete operation for any model"""
        try:
            return await sync_to_async(model_class.objects.filter(**kwargs).delete)()
        except Exception as e:
            logger.error(f"Error deleting {model_class.__name__}: {str(e)}")
            raise
    
    @staticmethod
    async def exists(model_class: Type[T], **kwargs) -> bool:
        """Async exists operation for any model"""
        try:
            return await sync_to_async(model_class.objects.filter(**kwargs).exists)()
        except Exception as e:
            logger.error(f"Error checking existence for {model_class.__name__}: {str(e)}")
            raise
    
    @staticmethod
    async def count(model_class: Type[T], **kwargs) -> int:
        """Async count operation for any model"""
        try:
            return await sync_to_async(model_class.objects.filter(**kwargs).count)()
        except Exception as e:
            logger.error(f"Error counting {model_class.__name__}: {str(e)}")
            raise


class AsyncTransactionManager:
    """Manager class for async database transactions"""
    
    @staticmethod
    async def atomic(func, *args, **kwargs):
        """Execute a function within an async database transaction"""
        try:
            return await sync_to_async(transaction.atomic)(func, *args, **kwargs)
        except Exception as e:
            logger.error(f"Transaction error: {str(e)}")
            raise
    
    @staticmethod
    async def on_commit(func, *args, **kwargs):
        """Execute a function after the current transaction commits"""
        try:
            return await sync_to_async(transaction.on_commit)(func, *args, **kwargs)
        except Exception as e:
            logger.error(f"On commit error: {str(e)}")
            raise


# Convenience functions for common operations
async def async_create(model_class: Type[T], **kwargs) -> T:
    """Convenience function for async create"""
    return await AsyncDBManager.create(model_class, **kwargs)


async def async_get(model_class: Type[T], **kwargs) -> T:
    """Convenience function for async get"""
    return await AsyncDBManager.get(model_class, **kwargs)


async def async_filter(model_class: Type[T], **kwargs) -> List[T]:
    """Convenience function for async filter"""
    return await AsyncDBManager.filter(model_class, **kwargs)


async def async_update_or_create(model_class: Type[T], defaults: dict = None, **kwargs) -> tuple[T, bool]:
    """Convenience function for async update_or_create"""
    return await AsyncDBManager.update_or_create(model_class, defaults, **kwargs)


async def async_bulk_create(model_class: Type[T], objects: List[T], **kwargs) -> List[T]:
    """Convenience function for async bulk_create"""
    return await AsyncDBManager.bulk_create(model_class, objects, **kwargs)


async def async_delete(model_class: Type[T], **kwargs) -> int:
    """Convenience function for async delete"""
    return await AsyncDBManager.delete(model_class, **kwargs)


async def async_exists(model_class: Type[T], **kwargs) -> bool:
    """Convenience function for async exists"""
    return await AsyncDBManager.exists(model_class, **kwargs)


async def async_count(model_class: Type[T], **kwargs) -> int:
    """Convenience function for async count"""
    return await AsyncDBManager.count(model_class, **kwargs)
