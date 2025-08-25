import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from main_app.models import PropertyInquiry, PropertyEstimate, AIAnalysisLog
from main_app.ai_service import ValoraEarthAIService
from main_app.ai_models import PropertyInquiryRequest, PropertyEstimateResponse, AIAnalysisResult


# ============================================================================
# MODEL TESTS
# ============================================================================

@pytest.mark.django_db
class TestPropertyInquiryModel:
    """Test cases for PropertyInquiry model"""
    
    def test_property_inquiry_creation(self):
        """Test creating a PropertyInquiry instance with valid data"""
        inquiry = PropertyInquiry.objects.create(
            address="123 Test Street",
            lot_size=10.5,
            lot_size_unit="acres",
            current_property="Vacant land with some trees",
            property_goals="Sustainable agriculture",
            investment_capacity="$100,000 - $200,000",
            preferences_concerns="Organic farming preferred",
            region="Test Region"
        )
        
        assert inquiry.address == "123 Test Street"
        assert inquiry.lot_size == 10.5
        assert inquiry.lot_size_unit == "acres"
        assert inquiry.current_property == "Vacant land with some trees"
        assert inquiry.property_goals == "Sustainable agriculture"
        assert inquiry.investment_capacity == "$100,000 - $200,000"
        assert inquiry.preferences_concerns == "Organic farming preferred"
        assert inquiry.region == "Test Region"
        assert inquiry.created_at is not None
    
    def test_property_inquiry_str_representation(self):
        """Test the string representation of PropertyInquiry"""
        inquiry = PropertyInquiry.objects.create(
            address="456 Test Ave",
            lot_size=15.0,
            lot_size_unit="hectares",
            current_property="Agricultural land",
            property_goals="Carbon sequestration",
            investment_capacity="$50,000 - $100,000",
            preferences_concerns="Low maintenance",
            region="Test Region"
        )
        
        expected_str = f"Property Inquiry - 456 Test Ave ({inquiry.lot_size} {inquiry.lot_size_unit})"
        assert str(inquiry) == expected_str
    
    def test_property_inquiry_default_lot_size_unit(self):
        """Test that lot_size_unit defaults to 'acres'"""
        inquiry = PropertyInquiry.objects.create(
            address="789 Test Blvd",
            lot_size=20.0,
            current_property="Mixed forest",
            property_goals="Biodiversity",
            investment_capacity="$200,000",
            preferences_concerns="Wildlife",
            region="Test Region"
        )
        
        assert inquiry.lot_size_unit == "acres"
    
    def test_property_inquiry_ordering(self):
        """Test that PropertyInquiry objects are ordered by created_at descending"""
        # Create inquiries with different timestamps
        inquiry1 = PropertyInquiry.objects.create(
            address="First",
            lot_size=10.0,
            current_property="Test",
            property_goals="Test",
            investment_capacity="$100,000",
            preferences_concerns="Test",
            region="Test"
        )
        
        inquiry2 = PropertyInquiry.objects.create(
            address="Second",
            lot_size=20.0,
            current_property="Test",
            property_goals="Test",
            investment_capacity="$200,000",
            preferences_concerns="Test",
            region="Test"
        )
        
        inquiries = list(PropertyInquiry.objects.all())
        assert inquiries[0] == inquiry2  # Most recent first
        assert inquiries[1] == inquiry1


@pytest.mark.django_db
class TestPropertyEstimateModel:
    """Test cases for PropertyEstimate model"""
    
    @pytest.fixture
    def inquiry(self):
        """Create a test PropertyInquiry"""
        return PropertyInquiry.objects.create(
            address="789 Test Blvd",
            lot_size=20.0,
            lot_size_unit="acres",
            current_property="Mixed forest and grassland",
            property_goals="Biodiversity restoration",
            investment_capacity="$200,000 - $500,000",
            preferences_concerns="Wildlife corridors",
            region="Test Region"
        )
    
    def test_property_estimate_creation(self, inquiry):
        """Test creating a PropertyEstimate instance with valid data"""
        estimate = PropertyEstimate.objects.create(
            inquiry=inquiry,
            project_name="Eco-Restoration Project",
            project_description="Comprehensive biodiversity restoration project",

            confidence_score=0.85,
            factors_considered=["Location", "Lot size", "Market trends"],
            recommendations=["Start with soil testing", "Implement agroforestry"],
            timeline="3-5 years",
            risk_assessment="Moderate risk with proper planning",
            ai_response_raw={"analysis": "Test analysis"},
            processing_time=2.5,
            cash_flow_projection=[15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000, 55000, 60000],
            revenue_breakdown={"Year 1": 20000, "Year 2": 25000},
            cost_breakdown={"Year 1": 5000, "Year 2": 5000}
        )
        
        assert estimate.project_name == "Eco-Restoration Project"

        assert estimate.confidence_score == 0.85
        assert estimate.timeline == "3-5 years"
        assert estimate.cash_flow_projection == [15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000, 55000, 60000]
        assert estimate.created_at is not None
    
    def test_property_estimate_str_representation(self, inquiry):
        """Test the string representation of PropertyEstimate"""
        estimate = PropertyEstimate.objects.create(
            inquiry=inquiry,
            project_name="Test Project",
            project_description="Test description",
            confidence_score=0.9,
            factors_considered=["Test factors"],
            recommendations=["Test recommendations"],
            timeline="2-3 years",
            risk_assessment="Low risk",
            ai_response_raw={"test": "data"},
            processing_time=1.5
        )
        
        expected_str = f"Estimate for 789 Test Blvd - Test Project"
        assert str(estimate) == expected_str
    
    def test_property_estimate_one_to_one_relationship(self, inquiry):
        """Test that PropertyEstimate has one-to-one relationship with PropertyInquiry"""
        estimate1 = PropertyEstimate.objects.create(
            inquiry=inquiry,
            project_name="First Project",
            project_description="First description",
            confidence_score=0.9,
            factors_considered=["Test factors"],
            recommendations=["Test recommendations"],
            timeline="2-3 years",
            risk_assessment="Low risk",
            ai_response_raw={"test": "data"},
            processing_time=1.5
        )
        
        # Try to create another estimate for the same inquiry
        with pytest.raises(IntegrityError):
            PropertyEstimate.objects.create(
                inquiry=inquiry,
                project_name="Second Project",
                project_description="Second description",
                confidence_score=0.8,
                factors_considered=["Test factors"],
                recommendations=["Test recommendations"],
                timeline="3-4 years",
                risk_assessment="Medium risk",
                ai_response_raw={"test": "data"},
                processing_time=2.0
            )


@pytest.mark.django_db
class TestAIAnalysisLogModel:
    """Test cases for AIAnalysisLog model"""
    
    @pytest.fixture
    def inquiry(self):
        """Create a test PropertyInquiry"""
        return PropertyInquiry.objects.create(
            address="321 Test Lane",
            lot_size=25.0,
            lot_size_unit="acres",
            current_property="Agricultural land",
            property_goals="Sustainable farming",
            investment_capacity="$75,000 - $150,000",
            preferences_concerns="Organic certification",
            region="Test Region"
        )
    
    def test_ai_analysis_log_creation(self, inquiry):
        """Test creating an AIAnalysisLog instance with valid data"""
        log = AIAnalysisLog.objects.create(
            inquiry=inquiry,
            request_data={"test": "request"},
            response_data={"test": "response"},
            model_used="gpt-4.1-mini",
            tokens_used=1500,
            processing_time=3.2,
            success=True
        )
        
        assert log.model_used == "gpt-4.1-mini"
        assert log.tokens_used == 1500
        assert log.processing_time == 3.2
        assert log.success is True
        assert log.created_at is not None
    
    def test_ai_analysis_log_str_representation(self, inquiry):
        """Test the string representation of AIAnalysisLog"""
        log = AIAnalysisLog.objects.create(
            inquiry=inquiry,
            request_data={"test": "request"},
            response_data={"test": "response"},
            model_used="gpt-3.5-turbo",
            tokens_used=800,
            processing_time=2.1,
            success=True
        )
        
        str_repr = str(log)
        assert "AI Analysis Log - 321 Test Lane" in str_repr
        assert log.model_used == "gpt-3.5-turbo"
    
    def test_ai_analysis_log_with_error(self, inquiry):
        """Test creating an AIAnalysisLog instance with error information"""
        log = AIAnalysisLog.objects.create(
            inquiry=inquiry,
            request_data={"test": "request"},
            response_data={},
            model_used="gpt-4.1-mini",
            tokens_used=0,
            processing_time=1.0,
            success=False,
            error_message="API rate limit exceeded"
        )
        
        assert log.success is False
        assert log.error_message == "API rate limit exceeded"
        assert log.tokens_used == 0


# ============================================================================
# VIEW TESTS
# ============================================================================

@pytest.mark.django_db
class TestPropertyEstimateViews:
    """Test cases for property estimate views"""
    
    @pytest.fixture
    def client(self):
        """Create a test client"""
        return Client()
    
    @pytest.fixture
    def user(self):
        """Create a test user"""
        return User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_index_view_get(self, client):
        """Test GET request to index view (landing page)"""
        response = client.get(reverse('main_app:index'))
        assert response.status_code == 200
        assert 'main_app/index.html' in [t.name for t in response.templates]
    
    def test_index_view_post_valid_data(self, client):
        """Test POST request to index view with valid data"""
        data = {
            'lot_size': '15.5',
            'region': 'Test Region',
            'lot_size_unit': 'acres'
        }
        
        response = client.post(reverse('main_app:index'), data)
        
        # Should redirect to estimate questionnaire
        assert response.status_code == 302
        assert response.url == reverse('main_app:estimate_questionnaire')
        
        # Check that session data was stored
        session = client.session
        assert 'initial_data' in session
        assert session['initial_data']['lot_size'] == 15.5
        assert session['initial_data']['region'] == 'Test Region'
        assert session['initial_data']['lot_size_unit'] == 'acres'
    
    def test_index_view_post_invalid_lot_size(self, client):
        """Test POST request to index view with invalid lot size"""
        data = {
            'lot_size': 'invalid',
            'region': 'Test Region'
        }
        
        response = client.post(reverse('main_app:index'), data)
        
        # Should return to form with error
        assert response.status_code == 200
        assert 'main_app/index.html' in [t.name for t in response.templates]
    
    def test_index_view_post_missing_required_fields(self, client):
        """Test POST request to index view with missing required fields"""
        data = {
            'lot_size': '',
            'region': ''
        }
        
        response = client.post(reverse('main_app:index'), data)
        
        # Should return to form with error
        assert response.status_code == 200
        assert 'main_app/index.html' in [t.name for t in response.templates]
    
    def test_estimate_questionnaire_get_with_session_data(self, client):
        """Test GET request to estimate questionnaire with valid session data"""
        # Set up session data
        session = client.session
        session['initial_data'] = {'lot_size': 10.0, 'region': 'Test Region', 'lot_size_unit': 'acres'}
        session.save()
        
        response = client.get(reverse('main_app:estimate_questionnaire'))
        assert response.status_code == 200
        assert 'main_app/estimate_questionnaire.html' in [t.name for t in response.templates]
    
    def test_estimate_questionnaire_get_without_session_data(self, client):
        """Test GET request to estimate questionnaire without session data"""
        response = client.get(reverse('main_app:estimate_questionnaire'))
        
        # Should redirect to index
        assert response.status_code == 302
        assert response.url == reverse('main_app:index')
    
    def test_estimate_questionnaire_post_step_1(self, client):
        """Test POST request to estimate questionnaire step 1"""
        # Set up session data
        session = client.session
        session['initial_data'] = {'lot_size': 12.0, 'region': 'Test Region', 'lot_size_unit': 'acres'}
        session.save()
        
        data = {'answer': 'Vacant agricultural land'}
        response = client.post(f"{reverse('main_app:estimate_questionnaire')}?step=1", data)
        
        # Should redirect to step 2
        assert response.status_code == 302
        assert 'step=2' in response.url
        
        # Check that answer was stored
        session = client.session
        assert 'questionnaire_answers' in session
        assert session['questionnaire_answers']['current_property'] == 'Vacant agricultural land'
    
    def test_estimate_questionnaire_post_final_step(self, client):
        """Test POST request to estimate questionnaire final step"""
        # Set up session data
        session = client.session
        session['initial_data'] = {'lot_size': 12.0, 'region': 'Test Region', 'lot_size_unit': 'acres'}
        session['questionnaire_answers'] = {
            'current_property': 'Vacant agricultural land',
            'property_goals': 'Sustainable farming',
            'investment_capacity': '$100,000 - $200,000'
        }
        session.save()
        
        data = {'answer': 'Organic certification'}
        response = client.post(f"{reverse('main_app:estimate_questionnaire')}?step=4", data)
        
        # Should redirect to loading screen
        assert response.status_code == 302
        assert response.url == reverse('main_app:loading_screen')
        
        # Check that complete estimate data was stored
        session = client.session
        assert 'questionnaire_data' in session
        assert session['questionnaire_data']['preferences_concerns'] == 'Organic certification'
    
    def test_loading_screen_get(self, client):
        """Test GET request to loading screen"""
        # Set up session data with inquiry ID
        session = client.session
        session['current_inquiry_id'] = 1
        session.save()
        
        response = client.get(reverse('main_app:loading_screen'))
        assert response.status_code == 200
        assert 'main_app/loading_screen.html' in [t.name for t in response.templates]
    
    def test_loading_screen_get_without_session_data(self, client):
        """Test GET request to loading screen without session data (should redirect)"""
        response = client.get(reverse('main_app:loading_screen'))
        
        # Should redirect to index when no inquiry ID
        assert response.status_code == 302
        assert response.url == reverse('main_app:index')


# ============================================================================
# AI SERVICE TESTS
# ============================================================================

class TestValoraEarthAIService:
    """Test cases for ValoraEarthAIService"""
    
    @pytest.fixture
    def ai_service(self):
        """Create an AI service instance"""
        return ValoraEarthAIService()
    
    @pytest.fixture
    def mock_inquiry(self):
        """Create a mock PropertyInquiryRequest"""
        return PropertyInquiryRequest(
            address="123 Test Street",
            lot_size=10.5,
            lot_size_unit="acres",
            current_property="Vacant land",
            property_goals="Sustainable agriculture",
            investment_capacity="$100,000 - $200,000",
            preferences_concerns="Organic farming",
            region="Test Region"
        )
    
    @pytest.fixture
    def mock_openai_response(self):
        """Create a mock OpenAI response"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "project_name": "Test Project",
            "project_description": "Test description",
            "confidence_score": 0.85,
            "factors_considered": ["Location", "Size"],
            "recommendations": ["Start small"],
            "timeline": "2-3 years",
            "risk_assessment": "Low risk"
        })
        mock_response.model = "gpt-4.1-mini"
        mock_response.usage = Mock()
        mock_response.usage.model_dump.return_value = {"total_tokens": 1500}
        mock_response.choices[0].finish_reason = "stop"
        return mock_response
    
    def test_ai_service_initialization(self, ai_service):
        """Test AI service initialization"""
        assert ai_service.model == "gpt-4.1-mini"
    
    @patch('main_app.ai_service.time.time')
    @patch.object(ValoraEarthAIService, '_call_openai_api')
    @patch.object(ValoraEarthAIService, '_parse_openai_response')
    def test_generate_property_estimate_success(
        self, 
        mock_parse_response, 
        mock_call_api, 
        mock_time,
        ai_service, 
        mock_inquiry, 
        mock_openai_response
    ):
        """Test successful property estimate generation"""
        # Mock time.time to return predictable values
        mock_time.side_effect = [1000.0, 1002.5]  # start_time, end_time
        
        # Mock the API call and response parsing
        mock_call_api.return_value = mock_openai_response
        mock_parse_response.return_value = {
            "project_name": "Test Project",
            "project_description": "Test description",
            "confidence_score": 0.85,
            "factors_considered": ["Location", "Size"],
            "recommendations": ["Start small"],
            "timeline": "2-3 years",
            "risk_assessment": "Low risk",
            "cash_flow_projection": [10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000, 50000, 55000],
            "revenue_breakdown": {"Year 1": 20000, "Year 2": 25000},
            "cost_breakdown": {"Year 1": 10000, "Year 2": 10000}
        }
        
        # Call the method
        result = ai_service.generate_property_estimate(mock_inquiry)
        
        # Verify the result
        assert isinstance(result, AIAnalysisResult)
        assert result.inquiry == mock_inquiry
        assert result.processing_time == 2.5
        assert result.analysis_timestamp is not None
        
        # Verify the estimate data
        assert result.estimate.project_name == "Test Project"
        assert result.estimate.confidence_score == 0.85
        
        # Verify the OpenAI response
        assert result.openai_response.model == "gpt-4.1-mini"
        assert result.openai_response.finish_reason == "stop"
    
    @patch.object(ValoraEarthAIService, '_call_openai_api')
    def test_generate_property_estimate_api_failure(self, mock_call_api, ai_service, mock_inquiry):
        """Test property estimate generation when API call fails"""
        # Mock API call to raise an exception
        mock_call_api.side_effect = Exception("API rate limit exceeded")
        
        # Call the method and expect an exception
        with pytest.raises(Exception) as exc_info:
            ai_service.generate_property_estimate(mock_inquiry)
        
        assert "Failed to generate estimate" in str(exc_info.value)
        assert "API rate limit exceeded" in str(exc_info.value)
    
    def test_create_analysis_prompt(self, ai_service, mock_inquiry):
        """Test prompt creation for analysis"""
        prompt = ai_service._create_analysis_prompt(mock_inquiry)
        
        # Verify prompt contains all required information
        assert mock_inquiry.address in prompt
        assert str(mock_inquiry.lot_size) in prompt
        assert mock_inquiry.lot_size_unit in prompt
        assert mock_inquiry.region in prompt
        assert mock_inquiry.current_property in prompt
        assert mock_inquiry.property_goals in prompt
        assert mock_inquiry.investment_capacity in prompt
        assert mock_inquiry.preferences_concerns in prompt
    
    @patch('openai.OpenAI')
    def test_call_openai_api(self, mock_openai_class, ai_service, mock_inquiry):
        """Test OpenAI API call"""
        # Mock the OpenAI client and chat completion
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.model = "gpt-4.1-mini"
        mock_response.usage = Mock()
        mock_response.usage.model_dump.return_value = {"total_tokens": 1000}
        mock_response.choices[0].finish_reason = "stop"
        
        mock_client.chat.completions.create.return_value = mock_response
        
        # Create a new service instance to use the mocked client
        service = ValoraEarthAIService()
        service.client = mock_client
        
        # Call the method
        result = service._call_openai_api("Test prompt")
        
        # Verify the API was called correctly
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]['model'] == "gpt-4.1-mini"
        
        # Check that we have 2 messages: system and user
        messages = call_args[1]['messages']
        assert len(messages) == 2
        assert messages[0]['role'] == 'system'
        assert messages[1]['role'] == 'user'
        assert messages[1]['content'] == "Test prompt"
        
        # Verify the response
        assert result == mock_response


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.django_db
class TestPropertyEstimateIntegration:
    """Integration tests for the complete property estimate flow"""
    
    @pytest.fixture
    def client(self):
        """Create a test client"""
        return Client()
    
    def test_complete_property_estimate_flow(self, client):
        """Test the complete flow from form submission to estimate creation"""
        # Step 1: Submit initial form
        initial_data = {
            'lot_size': '25.0',
            'region': 'California',
            'lot_size_unit': 'acres'
        }
        
        response = client.post(reverse('main_app:index'), initial_data)
        assert response.status_code == 302
        assert response.url == reverse('main_app:estimate_questionnaire')
        
        # Step 2: Complete questionnaire step 1
        session = client.session
        session['initial_data'] = initial_data
        session.save()
        
        step1_data = {'answer': 'Vacant agricultural land'}
        response = client.post(f"{reverse('main_app:estimate_questionnaire')}?step=1", step1_data)
        assert response.status_code == 302
        
        # Step 3: Complete questionnaire step 2
        step2_data = {'answer': 'Sustainable farming and carbon sequestration'}
        response = client.post(f"{reverse('main_app:estimate_questionnaire')}?step=2", step2_data)
        assert response.status_code == 302
        
        # Step 4: Complete questionnaire step 3
        step3_data = {'answer': '$200,000 - $500,000'}
        response = client.post(f"{reverse('main_app:estimate_questionnaire')}?step=3", step3_data)
        assert response.status_code == 302
        
        # Step 5: Complete questionnaire step 4
        step4_data = {'answer': 'Organic certification and wildlife preservation'}
        response = client.post(f"{reverse('main_app:estimate_questionnaire')}?step=4", step4_data)
        assert response.status_code == 302
        assert response.url == reverse('main_app:loading_screen')
        
        # Verify all data was stored in session
        session = client.session
        assert 'questionnaire_data' in session
        assert session['questionnaire_data']['current_property'] == 'Vacant agricultural land'
        assert session['questionnaire_data']['property_goals'] == 'Sustainable farming and carbon sequestration'
        assert session['questionnaire_data']['investment_capacity'] == '$200,000 - $500,000'
        assert session['questionnaire_data']['preferences_concerns'] == 'Organic certification and wildlife preservation'


# ============================================================================
# TEST RUNNERS
# ============================================================================

if __name__ == '__main__':
    # This allows running tests directly with python
    import django
    django.setup()
    
    # Run tests
    pytest.main([__file__, '-v'])
