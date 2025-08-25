from pydantic import BaseModel, Field
from typing import List, Optional


class PropertyInquiryRequest(BaseModel):
    """Pydantic model for property inquiry requests"""
    address: str = Field(..., description="Property address", min_length=1, max_length=500)
    lot_size: float = Field(..., description="Lot size value", gt=0)
    lot_size_unit: str = Field(..., description="Unit for lot size (acres or hectares)")
    current_property: str = Field(..., description="Current property description", min_length=1)
    property_goals: str = Field(..., description="Property goals and objectives", min_length=1)
    investment_capacity: str = Field(..., description="Investment capacity and timeline", min_length=1)
    preferences_concerns: str = Field(..., description="Preferences and concerns", min_length=1)
    region: str = Field(..., description="Geographic region", min_length=1)


class PropertyEstimateResponse(BaseModel):
    """Pydantic model for AI-generated property estimates"""
    project_name: str = Field(..., description="Generated project name")
    project_description: str = Field(..., description="Detailed project description")
    confidence_score: float = Field(..., description="AI confidence score", ge=0.0, le=1.0)
    factors_considered: List[str] = Field(..., description="Factors considered in the estimate")
    recommendations: List[str] = Field(..., description="AI recommendations for the project")
    timeline: str = Field(..., description="Recommended project timeline")
    risk_assessment: str = Field(..., description="Risk assessment and mitigation strategies")
    
    # 10-year financial projections
    cash_flow_projection: List[float] = Field(..., description="10-year net cash flow projection in USD")
    revenue_breakdown: dict = Field(..., description="10-year revenue breakdown by category")
    cost_breakdown: dict = Field(..., description="10-year cost breakdown by category")


class OpenAIRequest(BaseModel):
    """Pydantic model for OpenAI API requests"""
    model: str = Field(default="gpt-4.1-mini", description="OpenAI model to use")
    messages: List[dict] = Field(..., description="Chat messages for the API")
    temperature: float = Field(default=0.7, description="Creativity level", ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, description="Maximum tokens in response", gt=0)


class OpenAIResponse(BaseModel):
    """Pydantic model for OpenAI API responses"""
    content: str = Field(..., description="Generated content from OpenAI")
    model: str = Field(..., description="Model used for generation")
    usage: dict = Field(..., description="Token usage information")
    finish_reason: str = Field(..., description="Reason for completion")


class AIAnalysisResult(BaseModel):
    """Complete AI analysis result"""
    inquiry: PropertyInquiryRequest
    estimate: PropertyEstimateResponse
    openai_response: OpenAIResponse
    analysis_timestamp: str = Field(..., description="Timestamp of analysis")
    processing_time: float = Field(..., description="Processing time in seconds")
