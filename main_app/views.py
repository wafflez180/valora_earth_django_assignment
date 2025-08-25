from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from asgiref.sync import sync_to_async
from .models import PropertyInquiry, PropertyEstimate, AIAnalysisLog
from .ai_service import ValoraEarthAIService
from .ai_models import PropertyInquiryRequest
from .utils.db_utils import async_create, async_get, async_update_or_create
import json
import logging
import asyncio

# Set up logging
logger = logging.getLogger(__name__)


def index(request):
    """Display the property estimate form (landing page)"""
    if request.method == 'GET':
        return render(request, 'main_app/index.html')
    
    elif request.method == 'POST':
        # Handle form submission
        try:
            # Extract form data
            lot_size = request.POST.get('lot_size', '').strip()
            region = request.POST.get('region', '').strip()
            lot_size_unit = request.POST.get('lot_size_unit', 'acres').strip()
            
            # Debug logging
            print(f"DEBUG: Form submitted - lot_size: '{lot_size}', region: '{region}', unit: '{lot_size_unit}'")
            print(f"DEBUG: All POST data: {request.POST}")
            
            # Basic validation
            if not lot_size or not region:
                messages.error(request, 'Lot size and region are required fields.')
                return render(request, 'main_app/index.html', {
                    'form_data': request.POST
                })
            
            try:
                lot_size_float = float(lot_size)
                if lot_size_float <= 0:
                    raise ValueError("Lot size must be greater than 0")
            except ValueError:
                messages.error(request, 'Please enter a valid lot size greater than 0.')
                return render(request, 'main_app/index.html', {
                    'form_data': request.POST
                })
            
            # Store data in session for estimate
            request.session['initial_data'] = {
                'lot_size': lot_size_float,
                'lot_size_unit': lot_size_unit,
                'region': region
            }
            
            print(f"DEBUG: Stored in session: {request.session['initial_data']}")
            print(f"DEBUG: Redirecting to estimate...")
            
            # Redirect to estimate questionnaire
            return redirect('main_app:estimate_questionnaire')
            
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'main_app/index.html', {
                'form_data': request.POST
            })


def estimate_questionnaire(request):
    """Display the multi-step estimate questionnaire flow"""
    # Get initial data from session
    initial_data = request.session.get('initial_data', {})
    
    print(f"DEBUG: Estimate questionnaire view - initial_data: {initial_data}")
    
    if not initial_data:
        print("DEBUG: No initial data found, redirecting to form")
        return redirect('main_app:index')
    
    # Get current step from URL parameter or default to 1
    step = int(request.GET.get('step', 1))
    
    # Ensure step is within valid range
    if step < 1 or step > 4:
        step = 1
    
    # Get existing answers from session
    questionnaire_answers = request.session.get('questionnaire_answers', {})
    
    if request.method == 'POST':
        try:
            # Get the answer for current step
            answer = request.POST.get('answer', '').strip()
            
            if not answer:
                messages.error(request, 'Please provide an answer before continuing.')
                return render(request, 'main_app/estimate_questionnaire.html', {
                    'step': step,
                    'initial_data': initial_data,
                    'questionnaire_answers': questionnaire_answers
                })
            
            # Map step to field name
            field_mapping = {
                1: 'current_property',
                2: 'property_goals', 
                3: 'investment_capacity',
                4: 'preferences_concerns'
            }
            
            # Store answer in session
            questionnaire_answers[field_mapping[step]] = answer
            request.session['questionnaire_answers'] = questionnaire_answers
            
            # If this is the last step, process the complete estimate
            if step == 4:
                try:
                    # Combine all data
                    inquiry_data = {
                        **initial_data,
                        'address': f"Property in {initial_data.get('region', 'Unknown Region')}",
                        **questionnaire_answers
                    }
                    
                    # Create PropertyInquiry object in database using sync operation
                    inquiry = PropertyInquiry.objects.create(
                        address=inquiry_data['address'],
                        lot_size=inquiry_data['lot_size'],
                        lot_size_unit=inquiry_data['lot_size_unit'],
                        current_property=inquiry_data['current_property'],
                        property_goals=inquiry_data['property_goals'],
                        investment_capacity=inquiry_data['investment_capacity'],
                        preferences_concerns=inquiry_data['preferences_concerns'],
                        region=inquiry_data['region']
                    )
                    
                    # Store inquiry ID in session for loading screen
                    request.session['current_inquiry_id'] = inquiry.id
                    request.session['questionnaire_data'] = inquiry_data
                    
                    print(f"DEBUG: Created PropertyInquiry with ID: {inquiry.id}")
                    print(f"DEBUG: Inquiry data: {inquiry_data}")
                    
                    # Redirect to loading screen
                    return redirect('main_app:loading_screen')
                    
                except Exception as e:
                    print(f"DEBUG: Error creating PropertyInquiry: {str(e)}")
                    messages.error(request, f'Error processing estimate: {str(e)}')
                    return render(request, 'main_app/estimate_questionnaire.html', {
                        'step': step,
                        'initial_data': initial_data,
                        'questionnaire_answers': questionnaire_answers
                    })
            else:
                # Go to next step
                return redirect(f"{request.path}?step={step + 1}")
                
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'main_app/estimate_questionnaire.html', {
                'step': step,
                'initial_data': initial_data,
                'questionnaire_answers': questionnaire_answers
            })
    
    return render(request, 'main_app/estimate_questionnaire.html', {
        'step': step,
        'initial_data': initial_data,
        'questionnaire_answers': questionnaire_answers
    })


def loading_screen(request):
    """Display the loading screen while calculating estimates"""
    # Get the current inquiry ID from session
    inquiry_id = request.session.get('current_inquiry_id')
    
    if not inquiry_id:
        messages.error(request, 'No estimate data found. Please start over.')
        return redirect('main_app:index')
    
    context = {
        'inquiry_id': inquiry_id
    }
    
    return render(request, 'main_app/loading_screen.html', context)


async def estimate_results(request, inquiry_id):
    """Display property estimate results"""
    try:
        # Use async database operation
        inquiry = await async_get(PropertyInquiry, id=inquiry_id)
        
        # Check if estimate exists
        try:
            estimate = await sync_to_async(lambda: inquiry.estimate)()
            has_estimate = True
        except PropertyEstimate.DoesNotExist:
            estimate = None
            has_estimate = False
        
        context = {
            'inquiry': inquiry,
            'estimate': estimate,
            'has_estimate': has_estimate,
        }
        
        return render(request, 'main_app/estimate_results.html', context)
        
    except PropertyInquiry.DoesNotExist:
        # Use sync_to_async for messages and redirect in async view
        await sync_to_async(messages.error)(request, 'Property inquiry not found.')
        return await sync_to_async(redirect)('main_app:index')


@csrf_exempt
@require_http_methods(["POST"])
async def generate_ai_estimate(request, inquiry_id):
    """API endpoint to generate AI estimate using OpenAI API"""
    try:
        # Use async database operation
        inquiry = await async_get(PropertyInquiry, id=inquiry_id)
        
        # Initialize AI service
        ai_service = ValoraEarthAIService()
        
        # Create inquiry request object
        inquiry_request = PropertyInquiryRequest(
            address=inquiry.address,
            lot_size=float(inquiry.lot_size),
            lot_size_unit=inquiry.lot_size_unit,
            current_property=inquiry.current_property,
            property_goals=inquiry.property_goals,
            investment_capacity=inquiry.investment_capacity,
            preferences_concerns=inquiry.preferences_concerns,
            region=inquiry.region
        )
        
        # Generate AI estimate using async method
        ai_result = await ai_service.generate_property_estimate_async(inquiry_request)
        
        # Create or update the estimate and log the analysis concurrently
        from .utils.async_db_utils import concurrent_create, batch_operations
        
        # Execute both operations concurrently
        try:
            estimate_result, ai_log = await asyncio.gather(
                async_update_or_create(PropertyEstimate,
                    inquiry=inquiry,
                    defaults={
                        'project_name': ai_result.estimate.project_name,
                        'project_description': ai_result.estimate.project_description,
                        'confidence_score': ai_result.estimate.confidence_score,
                        'factors_considered': ai_result.estimate.factors_considered,
                        'recommendations': ai_result.estimate.recommendations,
                        'timeline': ai_result.estimate.timeline,
                        'risk_assessment': ai_result.estimate.risk_assessment,
                        'cash_flow_projection': ai_result.estimate.cash_flow_projection,
                        'revenue_breakdown': ai_result.estimate.revenue_breakdown,
                        'cost_breakdown': ai_result.estimate.cost_breakdown,
                        'ai_response_raw': ai_result.openai_response.model_dump(mode='json'),
                        'processing_time': ai_result.processing_time,
                    }
                ),
                async_create(AIAnalysisLog,
                    inquiry=inquiry,
                    request_data=inquiry_request.model_dump(mode='json'),
                    response_data=ai_result.openai_response.model_dump(mode='json'),
                    model_used=ai_result.openai_response.model,
                    tokens_used=ai_result.openai_response.usage.get('total_tokens', 0),
                    processing_time=ai_result.processing_time,
                    success=True
                )
            )
        except Exception as e:
            print(f"DEBUG: Error in concurrent database operations: {str(e)}")
            raise Exception(f"Database operation failed: {str(e)}")
        
        # Unpack the estimate result (update_or_create returns (object, created))
        estimate, created = estimate_result
        
        # Validate the estimate object
        if not estimate or not hasattr(estimate, 'id'):
            raise Exception("Invalid estimate object returned from database")
        
        print(f"DEBUG: Estimate {'created' if created else 'updated'} with ID: {estimate.id}")
        print(f"DEBUG: AI log created with ID: {ai_log.id}")
        
        # Clear session data after successful estimate generation
        from asgiref.sync import sync_to_async
        
        # Use sync_to_async for session operations
        await sync_to_async(request.session.pop)('questionnaire_data', None)
        await sync_to_async(request.session.pop)('initial_data', None)
        await sync_to_async(request.session.pop)('questionnaire_answers', None)
        await sync_to_async(request.session.pop)('current_inquiry_id', None)
        
        return JsonResponse({
            'success': True,
            'estimate': {
                'id': estimate.id,
                'project_name': estimate.project_name,
                'project_description': estimate.project_description,
                'confidence_score': estimate.confidence_score,
                'factors_considered': estimate.factors_considered,
                'recommendations': estimate.recommendations,
                'timeline': estimate.timeline,
                'risk_assessment': estimate.risk_assessment,
                'cash_flow_projection': estimate.cash_flow_projection,
                'revenue_breakdown': estimate.revenue_breakdown,
                'cost_breakdown': estimate.cost_breakdown,
            }
        })
        
    except PropertyInquiry.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Property inquiry not found'
        }, status=404)
    except Exception as e:
        logger.error(f"AI estimate generation failed: {str(e)}")
        
        # Log the error using async database operation
        if 'inquiry' in locals():
            await async_create(AIAnalysisLog,
                inquiry=inquiry,
                request_data={},
                response_data={},
                model_used='unknown',
                tokens_used=0,
                processing_time=0,
                success=False,
                error_message=str(e)
            )
        
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
async def debug_session(request):
    """Debug endpoint to check session data"""
    from asgiref.sync import sync_to_async
    
    # Use sync_to_async for session operations
    session_data = await sync_to_async(dict)(request.session)
    initial_data = await sync_to_async(request.session.get)('initial_data', {})
    estimate_answers = await sync_to_async(request.session.get)('questionnaire_answers', {})
    estimate_data = await sync_to_async(request.session.get)('questionnaire_data', {})
    
    return JsonResponse({
        'session_data': session_data,
        'initial_data': initial_data,
        'estimate_answers': estimate_answers,
        'estimate_data': estimate_data
    })
