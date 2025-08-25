from django.contrib import admin
from .models import PropertyInquiry, PropertyEstimate, AIAnalysisLog


@admin.register(PropertyInquiry)
class PropertyInquiryAdmin(admin.ModelAdmin):
    list_display = ('address', 'lot_size', 'region', 'created_at')
    list_filter = ('region', 'created_at')
    search_fields = ('address', 'region', 'current_property', 'property_goals')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('address', 'lot_size', 'region')
        }),
        ('Property Details', {
            'fields': ('current_property', 'property_goals', 'investment_capacity', 'preferences_concerns')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )


@admin.register(PropertyEstimate)
class PropertyEstimateAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'inquiry_address', 'confidence_score', 'created_at')
    list_filter = ('confidence_score', 'created_at')
    search_fields = ('project_name', 'inquiry__address')
    readonly_fields = ('created_at', 'processing_time')
    fieldsets = (
        ('Project Information', {
            'fields': ('inquiry', 'project_name', 'project_description')
        }),
        ('10-Year Financial Projections', {
            'fields': ('cash_flow_projection', 'revenue_breakdown', 'cost_breakdown'),
            'classes': ('collapse',)
        }),
        ('AI Analysis', {
            'fields': ('confidence_score', 'factors_considered', 'recommendations', 'timeline', 'risk_assessment')
        }),
        ('Technical Details', {
            'fields': ('ai_response_raw', 'processing_time'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def inquiry_address(self, obj):
        return obj.inquiry.address if obj.inquiry else 'N/A'
    inquiry_address.short_description = 'Property Address'


@admin.register(AIAnalysisLog)
class AIAnalysisLogAdmin(admin.ModelAdmin):
    list_display = ('inquiry_address', 'model_used', 'tokens_used', 'processing_time', 'success', 'created_at')
    list_filter = ('success', 'model_used', 'created_at')
    search_fields = ('inquiry__address', 'model_used')
    readonly_fields = ('created_at', 'processing_time')
    fieldsets = (
        ('Analysis Details', {
            'fields': ('inquiry', 'model_used', 'tokens_used', 'processing_time', 'success')
        }),
        ('Request/Response Data', {
            'fields': ('request_data', 'response_data'),
            'classes': ('collapse',)
        }),
        ('Error Information', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def inquiry_address(self, obj):
        return obj.inquiry.address if obj.inquiry else 'N/A'
    inquiry_address.short_description = 'Property Address'
