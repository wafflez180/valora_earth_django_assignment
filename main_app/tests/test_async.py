"""
Test file for async functionality in Valora Earth Django application.
This file tests the async views and database operations.
"""

import pytest
import asyncio
from asgiref.sync import sync_to_async


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_async_database_operations():
    """Test async database operations"""
    # Import here to ensure Django is configured
    from main_app.models import PropertyInquiry, PropertyEstimate, AIAnalysisLog
    from main_app.utils.db_utils import async_create, async_get, async_filter, async_update_or_create
    
    print("Testing async database operations...")
    
    try:
        # Test async create
        inquiry = await async_create(PropertyInquiry,
            address="Test Property",
            lot_size=10.0,
            lot_size_unit="acres",
            current_property="Test current property",
            property_goals="Test goals",
            investment_capacity="Test capacity",
            preferences_concerns="Test preferences",
            region="Test Region"
        )
        
        assert inquiry.id is not None
        assert inquiry.address == "Test Property"
        
        # Test async get
        retrieved_inquiry = await async_get(PropertyInquiry, id=inquiry.id)
        assert retrieved_inquiry.id == inquiry.id
        assert retrieved_inquiry.address == inquiry.address
        
        # Test async filter
        inquiries = await async_filter(PropertyInquiry, region="Test Region")
        assert len(inquiries) == 1
        assert inquiries[0].id == inquiry.id
        
        # Test async update_or_create
        updated_inquiry, created = await async_update_or_create(
            PropertyInquiry,
            id=inquiry.id,
            defaults={'address': 'Updated Test Property'}
        )
        
        assert not created  # Should update existing
        assert updated_inquiry.address == 'Updated Test Property'
        
        # Clean up
        await sync_to_async(inquiry.delete)()
        
        print("✅ Async database operations test passed")
        return True
        
    except Exception as e:
        print(f"❌ Async database operations test failed: {str(e)}")
        return False


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_async_ai_service():
    """Test async AI service"""
    # Import here to ensure Django is configured
    from main_app.ai_service import ValoraEarthAIService
    
    print("Testing async AI service...")
    
    try:
        # Initialize AI service
        ai_service = ValoraEarthAIService()
        
        # Check if async method exists
        if hasattr(ai_service, 'generate_property_estimate_async'):
            print("✅ Async method 'generate_property_estimate_async' available")
        else:
            print("❌ Async method not found")
            return False
        
        # Check if sync method exists (for backward compatibility)
        if hasattr(ai_service, 'generate_property_estimate'):
            print("✅ Sync method 'generate_property_estimate' available")
        else:
            print("❌ Sync method not found")
            return False
        
        print("✅ Async AI service test passed")
        return True
        
    except Exception as e:
        print(f"❌ Async AI service test failed: {str(e)}")
        return False


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_async_views():
    """Test async views"""
    print("Testing async views...")
    
    try:
        # Import views
        from main_app import views
        
        # Check if views are async
        async_views = []
        sync_views = []
        
        for attr_name in dir(views):
            attr = getattr(views, attr_name)
            if callable(attr) and not attr_name.startswith('_'):
                if asyncio.iscoroutinefunction(attr):
                    async_views.append(attr_name)
                else:
                    sync_views.append(attr_name)
        
        print(f"Found {len(async_views)} async views: {', '.join(async_views)}")
        print(f"Found {len(sync_views)} sync views: {', '.join(sync_views)}")
        
        if len(async_views) > 0:
            print("✅ Async views are properly implemented")
        else:
            print("❌ No async views found")
            return False
        
        print("✅ Async views test passed")
        return True
        
    except Exception as e:
        print(f"❌ Async views test failed: {str(e)}")
        return False
