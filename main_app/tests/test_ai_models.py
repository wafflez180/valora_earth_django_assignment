import pytest
import json
from pydantic import ValidationError
from main_app.ai_models import (
    PropertyInquiryRequest, 
    PropertyEstimateResponse, 
    OpenAIRequest, 
    OpenAIResponse,
    AIAnalysisResult
)


class TestPropertyInquiryRequest:
    """Test cases for PropertyInquiryRequest model"""
    
    def test_valid_property_inquiry_request(self):
        """Test creating a valid PropertyInquiryRequest"""
        data = {
            "address": "123 Test Street",
            "lot_size": 10.5,
            "lot_size_unit": "acres",
            "current_property": "Vacant land with some trees",
            "property_goals": "Sustainable agriculture",
            "investment_capacity": "$100,000 - $200,000",
            "preferences_concerns": "Organic farming preferred",
            "region": "Test Region"
        }
        
        inquiry = PropertyInquiryRequest(**data)
        
        assert inquiry.address == "123 Test Street"
        assert inquiry.lot_size == 10.5
        assert inquiry.lot_size_unit == "acres"
        assert inquiry.current_property == "Vacant land with some trees"
        assert inquiry.property_goals == "Sustainable agriculture"
        assert inquiry.investment_capacity == "$100,000 - $200,000"
        assert inquiry.preferences_concerns == "Organic farming preferred"
        assert inquiry.region == "Test Region"
    
    def test_property_inquiry_request_default_lot_size_unit(self):
        """Test that lot_size_unit is required and must be provided"""
        data = {
            "address": "456 Test Ave",
            "lot_size": 15.0,
            "current_property": "Agricultural land",
            "property_goals": "Carbon sequestration",
            "investment_capacity": "$50,000 - $100,000",
            "preferences_concerns": "Low maintenance",
            "region": "Test Region"
        }
        
        # lot_size_unit is required, so this should fail
        with pytest.raises(ValidationError) as exc_info:
            PropertyInquiryRequest(**data)
        
        assert "lot_size_unit" in str(exc_info.value)
    
    def test_property_inquiry_request_invalid_lot_size(self):
        """Test that invalid lot_size raises validation error"""
        data = {
            "address": "789 Test Blvd",
            "lot_size": -5.0,  # Invalid negative value
            "current_property": "Mixed forest",
            "property_goals": "Biodiversity",
            "investment_capacity": "$200,000",
            "preferences_concerns": "Wildlife",
            "region": "Test Region"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PropertyInquiryRequest(**data)
        
        assert "lot_size" in str(exc_info.value)
    
    def test_property_inquiry_request_missing_required_fields(self):
        """Test that missing required fields raises validation error"""
        data = {
            "address": "Test Street",
            "lot_size": 10.0,
            # Missing other required fields
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PropertyInquiryRequest(**data)
        
        # Should have multiple validation errors
        assert len(exc_info.value.errors()) > 1
    
    def test_property_inquiry_request_invalid_lot_size_unit(self):
        """Test that lot_size_unit accepts any string value (no validation)"""
        data = {
            "address": "Test Street",
            "lot_size": 10.0,
            "lot_size_unit": "invalid_unit",  # Any string is accepted
            "current_property": "Test",
            "property_goals": "Test",
            "investment_capacity": "$100,000",
            "preferences_concerns": "Test",
            "region": "Test"
        }
        
        # This should work since lot_size_unit only requires a string
        inquiry = PropertyInquiryRequest(**data)
        assert inquiry.lot_size_unit == "invalid_unit"


class TestPropertyEstimateResponse:
    """Test cases for PropertyEstimateResponse model"""
    
    def test_valid_property_estimate_response(self):
        """Test creating a valid PropertyEstimateResponse"""
        data = {
            "project_name": "Eco-Restoration Project",
            "project_description": "Comprehensive biodiversity restoration project",
            "confidence_score": 0.85,
            "factors_considered": ["Location", "Lot size", "Market trends"],
            "recommendations": ["Start with soil testing", "Implement agroforestry"],
            "timeline": "3-5 years",
            "risk_assessment": "Moderate risk with proper planning",
            "cash_flow_projection": [15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000, 55000, 60000],
            "revenue_breakdown": {"Year 1": 20000, "Year 2": 25000},
            "cost_breakdown": {"Year 1": 5000, "Year 2": 5000}
        }
        
        estimate = PropertyEstimateResponse(**data)
        
        assert estimate.project_name == "Eco-Restoration Project"
        assert estimate.project_description == "Comprehensive biodiversity restoration project"
        assert estimate.confidence_score == 0.85
        assert estimate.factors_considered == ["Location", "Lot size", "Market trends"]
        assert estimate.recommendations == ["Start with soil testing", "Implement agroforestry"]
        assert estimate.timeline == "3-5 years"
        assert estimate.risk_assessment == "Moderate risk with proper planning"
        assert estimate.cash_flow_projection == [15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000, 55000, 60000]
    
    def test_property_estimate_response_confidence_score_range(self):
        """Test that confidence_score must be between 0 and 1"""
        data = {
            "project_name": "Test Project",
            "project_description": "Test description",
            "confidence_score": 1.5,  # Invalid: > 1.0
            "factors_considered": ["Test factors"],
            "recommendations": ["Test recommendations"],
            "timeline": "2-3 years",
            "risk_assessment": "Low risk",
            "cash_flow_projection": [10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000, 55000],
            "revenue_breakdown": {"Year 1": 15000, "Year 2": 20000},
            "cost_breakdown": {"Year 1": 5000, "Year 2": 5000}
        }
        
        with pytest.raises(ValidationError) as exc_info:
            PropertyEstimateResponse(**data)
        
        assert "confidence_score" in str(exc_info.value)
    
    def test_property_estimate_response_negative_cash_flow(self):
        """Test that negative cash flow values are allowed (for loss scenarios)"""
        data = {
            "project_name": "Test Project",
            "project_description": "Test description",
            "confidence_score": 0.7,
            "factors_considered": ["Test factors"],
            "recommendations": ["Test recommendations"],
            "timeline": "2-3 years",
            "risk_assessment": "High risk",
            "cash_flow_projection": [-5000, -3000, 0, 2000, 5000, 8000, 12000, 15000, 18000, 22000],
            "revenue_breakdown": {"Year 1": 10000, "Year 2": 12000},
            "cost_breakdown": {"Year 1": 15000, "Year 2": 15000}
        }
        
        estimate = PropertyEstimateResponse(**data)
        # Note: Removed assertion for estimated_net_cash_flow as field no longer exists
    
    def test_property_estimate_response_empty_arrays(self):
        """Test that empty arrays are allowed for factors and recommendations"""
        data = {
            "project_name": "Test Project",
            "project_description": "Test description",
            "confidence_score": 0.8,
            "factors_considered": [],  # Empty array
            "recommendations": [],     # Empty array
            "timeline": "2-3 years",
            "risk_assessment": "Low risk",
            "cash_flow_projection": [10000, 12000, 14000, 16000, 18000, 20000, 22000, 24000, 26000, 28000],
            "revenue_breakdown": {"Year 1": 20000, "Year 2": 22000},
            "cost_breakdown": {"Year 1": 10000, "Year 2": 10000}
        }
        
        estimate = PropertyEstimateResponse(**data)
        assert estimate.factors_considered == []
        assert estimate.recommendations == []


class TestOpenAIRequest:
    """Test cases for OpenAIRequest model"""
    
    def test_valid_openai_request(self):
        """Test creating a valid OpenAIRequest"""
        data = {
            "model": "gpt-4.1-mini",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, how are you?"}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        request = OpenAIRequest(**data)
        
        assert request.model == "gpt-4.1-mini"
        assert len(request.messages) == 2
        assert request.messages[0]["role"] == "system"
        assert request.messages[1]["content"] == "Hello, how are you?"
        assert request.max_tokens == 1000
        assert request.temperature == 0.7
    
    def test_openai_request_default_values(self):
        """Test that default values are applied correctly"""
        data = {
            "model": "gpt-4.1-mini",
            "messages": [
                {"role": "user", "content": "Test message"}
            ]
        }
        
        request = OpenAIRequest(**data)
        
        assert request.max_tokens == 2000  # Default value
        assert request.temperature == 0.7  # Default value (from the model)
        # Note: top_p, frequency_penalty, presence_penalty are not in the model
    
    def test_openai_request_invalid_model(self):
        """Test that model accepts any string value (no validation)"""
        data = {
            "model": "invalid-model",
            "messages": [
                {"role": "user", "content": "Test message"}
            ]
        }
        
        # This should work since model only requires a string
        request = OpenAIRequest(**data)
        assert request.model == "invalid-model"
    
    def test_openai_request_empty_messages(self):
        """Test that empty messages array is allowed (no validation)"""
        data = {
            "model": "gpt-4.1-mini",
            "messages": []  # Empty messages
        }
        
        # This should work since messages only requires a list
        request = OpenAIRequest(**data)
        assert request.messages == []


class TestOpenAIResponse:
    """Test cases for OpenAIResponse model"""
    
    def test_valid_openai_response(self):
        """Test creating a valid OpenAIResponse"""
        data = {
            "content": "This is a test response from the AI model.",
            "model": "gpt-4.1-mini",
            "usage": {"total_tokens": 1500, "prompt_tokens": 500, "completion_tokens": 1000},
            "finish_reason": "stop"
        }
        
        response = OpenAIResponse(**data)
        
        assert response.content == "This is a test response from the AI model."
        assert response.model == "gpt-4.1-mini"
        assert response.usage == {"total_tokens": 1500, "prompt_tokens": 500, "completion_tokens": 1000}
        assert response.finish_reason == "stop"
    
    def test_openai_response_serialization(self):
        """Test that OpenAIResponse can be serialized to JSON"""
        data = {
            "content": "Test content",
            "model": "gpt-4.1-mini",
            "usage": {"total_tokens": 1000},
            "finish_reason": "stop"
        }
        
        response = OpenAIResponse(**data)
        
        # Test JSON serialization
        json_str = response.model_dump_json()
        parsed_data = json.loads(json_str)
        
        assert parsed_data["content"] == "Test content"
        assert parsed_data["model"] == "gpt-4.1-mini"
        assert parsed_data["usage"] == {"total_tokens": 1000}
        assert parsed_data["finish_reason"] == "stop"


class TestAIAnalysisResult:
    """Test cases for AIAnalysisResult model"""
    
    def test_valid_ai_analysis_result(self):
        """Test creating a valid AIAnalysisResult"""
        # Create required components
        inquiry = PropertyInquiryRequest(
            address="123 Test Street",
            lot_size=10.5,
            lot_size_unit="acres",
            current_property="Vacant land",
            property_goals="Sustainable agriculture",
            investment_capacity="$100,000 - $200,000",
            preferences_concerns="Organic farming",
            region="Test Region"
        )
        
        estimate = PropertyEstimateResponse(
            project_name="Test Project",
            project_description="Test description",
            confidence_score=0.85,
            factors_considered=["Location", "Size"],
            recommendations=["Start small"],
            timeline="2-3 years",
            risk_assessment="Low risk",
            cash_flow_projection=[10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000, 55000],
            revenue_breakdown={"Year 1": 20000, "Year 2": 25000},
            cost_breakdown={"Year 1": 10000, "Year 2": 10000}
        )
        
        openai_response = OpenAIResponse(
            content="Test AI response",
            model="gpt-4.1-mini",
            usage={"total_tokens": 1500},
            finish_reason="stop"
        )
        
        data = {
            "inquiry": inquiry,
            "estimate": estimate,
            "openai_response": openai_response,
            "analysis_timestamp": "2024-01-15 10:30:00",
            "processing_time": 2.5
        }
        
        result = AIAnalysisResult(**data)
        
        assert result.inquiry == inquiry
        assert result.estimate == estimate
        assert result.openai_response == openai_response
        assert result.analysis_timestamp == "2024-01-15 10:30:00"
        assert result.processing_time == 2.5
    
    def test_ai_analysis_result_processing_time_validation(self):
        """Test that processing_time accepts negative values (no validation)"""
        inquiry = PropertyInquiryRequest(
            address="Test",
            lot_size=10.0,
            lot_size_unit="acres",
            current_property="Test",
            property_goals="Test",
            investment_capacity="$100,000",
            preferences_concerns="Test",
            region="Test"
        )
        
        estimate = PropertyEstimateResponse(
            project_name="Test",
            project_description="Test",
            confidence_score=0.8,
            factors_considered=["Test"],
            recommendations=["Test"],
            timeline="2-3 years",
            risk_assessment="Low risk",
            cash_flow_projection=[10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000, 55000],
            revenue_breakdown={"Year 1": 20000, "Year 2": 25000},
            cost_breakdown={"Year 1": 10000, "Year 2": 10000}
        )
        
        openai_response = OpenAIResponse(
            content="Test",
            model="gpt-4.1-mini",
            usage={"total_tokens": 1000},
            finish_reason="stop"
        )
        
        data = {
            "inquiry": inquiry,
            "estimate": estimate,
            "openai_response": openai_response,
            "analysis_timestamp": "2024-01-15 10:30:00",
            "processing_time": -1.0  # Negative value is allowed
        }
        
        # This should work since processing_time has no validation
        result = AIAnalysisResult(**data)
        assert result.processing_time == -1.0
    
    def test_ai_analysis_result_serialization(self):
        """Test that AIAnalysisResult can be serialized to JSON"""
        inquiry = PropertyInquiryRequest(
            address="Test",
            lot_size=10.0,
            lot_size_unit="acres",
            current_property="Test",
            property_goals="Test",
            investment_capacity="$100,000",
            preferences_concerns="Test",
            region="Test"
        )
        
        estimate = PropertyEstimateResponse(
            project_name="Test",
            project_description="Test",
            confidence_score=0.8,
            factors_considered=["Test"],
            recommendations=["Test"],
            timeline="2-3 years",
            risk_assessment="Low risk",
            cash_flow_projection=[10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000, 55000],
            revenue_breakdown={"Year 1": 20000, "Year 2": 25000},
            cost_breakdown={"Year 1": 10000, "Year 2": 10000}
        )
        
        openai_response = OpenAIResponse(
            content="Test",
            model="gpt-4.1-mini",
            usage={"total_tokens": 1000},
            finish_reason="stop"
        )
        
        data = {
            "inquiry": inquiry,
            "estimate": estimate,
            "openai_response": openai_response,
            "analysis_timestamp": "2024-01-15 10:30:00",
            "processing_time": 2.5
        }
        
        result = AIAnalysisResult(**data)
        
        # Test JSON serialization
        json_str = result.model_dump_json()
        parsed_data = json.loads(json_str)
        
        assert parsed_data["analysis_timestamp"] == "2024-01-15 10:30:00"
        assert parsed_data["processing_time"] == 2.5
        assert "inquiry" in parsed_data
        assert "estimate" in parsed_data
        assert "openai_response" in parsed_data


# ============================================================================
# TEST RUNNERS
# ============================================================================

if __name__ == '__main__':
    # This allows running tests directly with python
    import django
    django.setup()
    
    # Run tests
    pytest.main([__file__, '-v'])
