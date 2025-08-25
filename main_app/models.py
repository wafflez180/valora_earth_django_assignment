from django.db import models
from django.utils import timezone


class PropertyInquiry(models.Model):
    """Model to store property inquiry details"""
    address = models.CharField(max_length=500)
    lot_size = models.DecimalField(max_digits=10, decimal_places=2, help_text="Lot size value")
    lot_size_unit = models.CharField(max_length=10, choices=[('acres', 'Acres'), ('hectares', 'Hectares')], default='acres', help_text="Unit for lot size")
    current_property = models.TextField(help_text="Current property description")
    property_goals = models.TextField(help_text="Property goals and objectives")
    investment_capacity = models.TextField(help_text="Investment capacity and timeline")
    preferences_concerns = models.TextField(help_text="Preferences and concerns")
    region = models.CharField(max_length=100, help_text="Geographic region")
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Property Inquiry - {self.address} ({self.lot_size} {self.lot_size_unit})"
    
    class Meta:
        verbose_name_plural = "Property Inquiries"
        ordering = ['-created_at']


class PropertyEstimate(models.Model):
    """Model to store AI-generated property estimates"""
    inquiry = models.OneToOneField(PropertyInquiry, on_delete=models.CASCADE, related_name='estimate')
    project_name = models.CharField(max_length=200)
    project_description = models.TextField()
    confidence_score = models.FloatField(help_text="AI confidence score (0.0 to 1.0)")
    factors_considered = models.JSONField(help_text="Factors considered in the estimate")
    recommendations = models.JSONField(help_text="AI recommendations for the project")
    timeline = models.CharField(max_length=200, help_text="Recommended project timeline")
    risk_assessment = models.TextField(help_text="Risk assessment and mitigation strategies")
    
    # 10-year financial projections
    cash_flow_projection = models.JSONField(help_text="10-year net cash flow projection in USD", default=list)
    revenue_breakdown = models.JSONField(help_text="10-year revenue breakdown by category", default=dict)
    cost_breakdown = models.JSONField(help_text="10-year cost breakdown by category", default=dict)
    
    ai_response_raw = models.JSONField(help_text="Raw AI response data")
    processing_time = models.FloatField(help_text="Processing time in seconds")
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Estimate for {self.inquiry.address} - {self.project_name}"
    
    class Meta:
        verbose_name_plural = "Property Estimates"
        ordering = ['-created_at']


class AIAnalysisLog(models.Model):
    """Model to log AI analysis requests and responses for monitoring"""
    inquiry = models.ForeignKey(PropertyInquiry, on_delete=models.CASCADE, related_name='ai_logs')
    request_data = models.JSONField(help_text="Request data sent to AI")
    response_data = models.JSONField(help_text="Response data from AI")
    model_used = models.CharField(max_length=100, help_text="AI model used")
    tokens_used = models.IntegerField(help_text="Tokens consumed")
    processing_time = models.FloatField(help_text="Processing time in seconds")
    success = models.BooleanField(default=True, help_text="Whether the analysis was successful")
    error_message = models.TextField(blank=True, help_text="Error message if analysis failed")
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"AI Analysis Log - {self.inquiry.address} ({self.created_at})"
    
    class Meta:
        verbose_name_plural = "AI Analysis Logs"
        ordering = ['-created_at']
