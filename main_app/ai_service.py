import os
import json
import time
import asyncio
from typing import Dict, Any
from openai import AsyncOpenAI
from dotenv import load_dotenv
from .ai_models import (
    PropertyInquiryRequest, 
    PropertyEstimateResponse, 
    OpenAIRequest, 
    OpenAIResponse,
    AIAnalysisResult
)

# Load environment variables
load_dotenv()


class ValoraEarthAIService:
    """AI service for property estimation using OpenAI API"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        # Use GPT-4o-mini for better performance
        self.model = "gpt-4.1-mini"
        
    async def generate_property_estimate_async(self, inquiry: PropertyInquiryRequest) -> AIAnalysisResult:
        """
        Generate AI-powered property estimate using OpenAI API (async version)
        
        Args:
            inquiry: Validated property inquiry request
            
        Returns:
            Complete AI analysis result
        """
        start_time = time.time()
        
        print(f"DEBUG: Starting async property estimate generation for inquiry: {inquiry.address}")
        print(f"DEBUG: Using model: {self.model}")
        
        try:
            # Create the prompt for OpenAI
            prompt = self._create_analysis_prompt(inquiry)
            print(f"DEBUG: Created prompt with length: {len(prompt)}")
            
            # Make OpenAI API call asynchronously
            print(f"DEBUG: Making async OpenAI API call with model: {self.model}")
            openai_response = await self._call_openai_api_async(prompt)
            print(f"DEBUG: OpenAI API call successful")

            # Parse and validate the response
            print(f"DEBUG: Parsing OpenAI response...")
            estimate_data = self._parse_openai_response(openai_response.choices[0].message.content)
            print(f"DEBUG: Response parsing successful")

            # Create validated response models
            print(f"DEBUG: Creating PropertyEstimateResponse...")
            estimate = PropertyEstimateResponse(**estimate_data)
            print(f"DEBUG: Creating OpenAIResponse...")
            openai_response_model = OpenAIResponse(
                content=openai_response.choices[0].message.content,
                model=openai_response.model,
                usage=openai_response.usage.model_dump(mode='json'),  # Use JSON mode for safe serialization
                finish_reason=openai_response.choices[0].finish_reason
            )
            print(f"DEBUG: Creating AIAnalysisResult...")
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Create complete analysis result
            result = AIAnalysisResult(
                inquiry=inquiry,
                estimate=estimate,
                openai_response=openai_response_model,
                analysis_timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                processing_time=processing_time
            )
            
            print(f"DEBUG: Successfully generated estimate using model: {self.model}")
            return result
            
        except Exception as e:
            print(f"DEBUG: Failed to generate estimate: {str(e)}")
            raise Exception(f"Failed to generate estimate: {str(e)}")
    
    def generate_property_estimate(self, inquiry: PropertyInquiryRequest) -> AIAnalysisResult:
        """
        Generate AI-powered property estimate using OpenAI API (sync version for backward compatibility)
        
        Args:
            inquiry: Validated property inquiry request
            
        Returns:
            Complete AI analysis result
        """
        start_time = time.time()
        
        print(f"DEBUG: Starting property estimate generation for inquiry: {inquiry.address}")
        print(f"DEBUG: Using model: {self.model}")
        
        try:
            # Create the prompt for OpenAI
            prompt = self._create_analysis_prompt(inquiry)
            print(f"DEBUG: Created prompt with length: {len(prompt)}")
            
            # Make OpenAI API call
            print(f"DEBUG: Making OpenAI API call with model: {self.model}")
            openai_response = self._call_openai_api(prompt)
            print(f"DEBUG: OpenAI API call successful")

            # Parse and validate the response
            print(f"DEBUG: Parsing OpenAI response...")
            estimate_data = self._parse_openai_response(openai_response.choices[0].message.content)
            print(f"DEBUG: Response parsing successful")

            # Create validated response models
            print(f"DEBUG: Creating PropertyEstimateResponse...")
            estimate = PropertyEstimateResponse(**estimate_data)
            print(f"DEBUG: Creating OpenAIResponse...")
            openai_response_model = OpenAIResponse(
                content=openai_response.choices[0].message.content,
                model=openai_response.model,
                usage=openai_response.usage.model_dump(mode='json'),  # Use JSON mode for safe serialization
                finish_reason=openai_response.choices[0].finish_reason
            )
            print(f"DEBUG: Creating AIAnalysisResult...")
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Create complete analysis result
            result = AIAnalysisResult(
                inquiry=inquiry,
                estimate=estimate,
                openai_response=openai_response_model,
                analysis_timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
                processing_time=processing_time
            )
            
            print(f"DEBUG: Successfully generated estimate using model: {self.model}")
            return result
            
        except Exception as e:
            print(f"DEBUG: Failed to generate estimate: {str(e)}")
            raise Exception(f"Failed to generate estimate: {str(e)}")
    
    def _create_analysis_prompt(self, inquiry: PropertyInquiryRequest) -> str:
        """Create a comprehensive prompt for property analysis"""
        
        print(f"DEBUG: Creating prompt for inquiry object: {inquiry}")
        print(f"DEBUG: Inquiry object type: {type(inquiry)}")
        print(f"DEBUG: Inquiry object attributes: {dir(inquiry)}")
        
        # Validate that all required fields are present
        required_fields = ['address', 'lot_size', 'lot_size_unit', 'region', 'current_property', 'property_goals', 'investment_capacity', 'preferences_concerns']
        missing_fields = []
        
        for field in required_fields:
            if not hasattr(inquiry, field) or getattr(inquiry, field) is None:
                missing_fields.append(field)
            else:
                print(f"DEBUG: Field '{field}' = {getattr(inquiry, field)}")
        
        if missing_fields:
            print(f"DEBUG: Missing fields: {missing_fields}")
            raise Exception(f"Missing required inquiry fields: {', '.join(missing_fields)}")
        
        # Convert hectares to acres if needed for AI analysis
        lot_size_acres = inquiry.lot_size
        if inquiry.lot_size_unit == 'hectares':
            lot_size_acres = inquiry.lot_size * 2.47105  # Convert hectares to acres
        
        prompt = f"""Analyze this agricultural property and provide a JSON response ONLY with no other text:

PROPERTY DETAILS:
- Address: {inquiry.address}
- Lot Size: {inquiry.lot_size} {inquiry.lot_size_unit} ({lot_size_acres:.2f} acres)
- Region: {inquiry.region}
- Current Property: {inquiry.current_property}
- Property Goals: {inquiry.property_goals}
- Investment Capacity: {inquiry.investment_capacity}
- Preferences/Concerns: {inquiry.preferences_concerns}

Return ONLY this JSON structure with realistic values based on the property details:
{{
    "project_name": "Creative and descriptive project name for this property",
    "project_description": "Detailed 100 word description of the regenerative agriculture project",
    "confidence_score": 0.85,
    "factors_considered": ["Location", "Lot size", "Market trends", "Soil quality", "Climate"],
    "recommendations": ["Start with soil testing", "Implement agroforestry", "Consider rotational grazing"],
    "timeline": "X-X years for full implementation",
    "risk_assessment": "Moderate risk with proper planning and execution",
    "cash_flow_projection": [year1, year2, year3, year4, year5, year6, year7, year8, year9, year10],
    "revenue_breakdown": {{
        "agricultural_sales": [year1, year2, year3, year4, year5, year6, year7, year8, year9, year10],
        "ecosystem_services": [year1, year2, year3, year4, year5, year6, year7, year8, year9, year10],
        "subsidies_incentives": [year1, year2, year3, year4, year5, year6, year7, year8, year9, year10]
    }},
    "cost_breakdown": {{
        "operational_costs": [year1, year2, year3, year4, year5, year6, year7, year8, year9, year10],
        "infrastructure": [year1, year2, year3, year4, year5, year6, year7, year8, year9, year10],
        "maintenance": [year1, year2, year3, year4, year5, year6, year7, year8, year9, year10]
    }}
}}

IMPORTANT FINANCIAL PROJECTION REQUIREMENTS:
- Provide 10 years of realistic financial projections
- All values should be in USD
- Consider regional market conditions for {inquiry.region}
- Factor in regenerative agriculture benefits like ecosystem services and carbon credits

Focus on regenerative agriculture, sustainability, and economic viability. Use realistic financial estimates for {inquiry.region}."""
        
        print(f"DEBUG: Created prompt with length: {len(prompt)}")
        return prompt
    
    async def _call_openai_api_async(self, prompt: str):
        """Make the actual OpenAI API call asynchronously"""
        
        if not os.getenv('OPENAI_API_KEY'):
            raise Exception("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.")
        
        try:
            print(f"DEBUG: Making async API call with model: {self.model}")
            print(f"DEBUG: API call parameters: temperature=0.7, max_tokens=2000, timeout=30")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert regenerative agriculture property analyst. Provide detailed, accurate analysis in the requested JSON format. IMPORTANT: Your response must be valid JSON only, no other text."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
                timeout=30  # 30 second timeout
            )
            
            # Validate that we got a response with content
            print(f"DEBUG: Full API response object: {response}")
            print(f"DEBUG: Response choices count: {len(response.choices) if response.choices else 'None'}")
            
            if not response or not response.choices:
                raise Exception("OpenAI API returned no choices")
            
            print(f"DEBUG: First choice: {response.choices[0]}")
            print(f"DEBUG: First choice message: {response.choices[0].message}")
            
            if not response.choices[0].message or not response.choices[0].message.content:
                print(f"DEBUG: Message content is empty or None: '{response.choices[0].message.content if response.choices[0].message else 'No message'}'")
                raise Exception("OpenAI API returned empty content")
            
            return response
            
        except Exception as e:
            print(f"DEBUG: OpenAI API call failed: {str(e)}")
            raise Exception(f"OpenAI API call failed: {str(e)}")
    
    def _call_openai_api(self, prompt: str):
        """Make the actual OpenAI API call (sync version for backward compatibility)"""
        
        if not os.getenv('OPENAI_API_KEY'):
            raise Exception("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.")
        
        try:
            print(f"DEBUG: Making API call with model: {self.model}")
            print(f"DEBUG: API call parameters: temperature=0.7, max_tokens=2000, timeout=30")
            
            # Create a sync client for backward compatibility
            from openai import OpenAI
            sync_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            response = sync_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert regenerative agriculture property analyst. Provide detailed, accurate analysis in the requested JSON format. IMPORTANT: Your response must be valid JSON only, no other text."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
                timeout=30  # 30 second timeout
            )
            
            # Validate that we got a response with content
            print(f"DEBUG: Full API response object: {response}")
            print(f"DEBUG: Response choices count: {len(response.choices) if response.choices else 'None'}")
            
            if not response or not response.choices:
                raise Exception("OpenAI API call failed")
            
            print(f"DEBUG: First choice: {response.choices[0]}")
            print(f"DEBUG: First choice message: {response.choices[0].message}")
            
            if not response.choices[0].message or not response.choices[0].message.content:
                print(f"DEBUG: Message content is empty or None: '{response.choices[0].message.content if response.choices[0].message else 'No message'}'")
                raise Exception("OpenAI API call failed")
            
            return response
            
        except Exception as e:
            print(f"DEBUG: OpenAI API call failed: {str(e)}")
            raise Exception(f"OpenAI API call failed: {str(e)}")
    
    def _parse_openai_response(self, content: str) -> Dict[str, Any]:
        """Parse and validate the OpenAI response"""
        
        try:
            # Check if content is empty or None
            if not content or not content.strip():
                raise Exception("OpenAI response is empty or contains no content")
            
            print(f"DEBUG: Parsing OpenAI response. Content length: {len(content)}")
            print(f"DEBUG: Content preview: {content[:300]}...")
            
            # Extract JSON from the response
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                if json_end == -1:
                    json_end = len(content)
                json_content = content[json_start:json_end].strip()
                print(f"DEBUG: Extracted JSON from code block: {json_content}...")
            elif content.strip().startswith('{') and content.strip().endswith('}'):
                # Response is already JSON
                json_content = content.strip()
                print(f"DEBUG: Response appears to be direct JSON: {json_content}...")
            else:
                # Try to find JSON in the response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_content = json_match.group(0)
                    print(f"DEBUG: Found JSON using regex: {json_content}...")
                else:
                    print(f"DEBUG: No JSON pattern found in content. Full content: {content}")
                    raise Exception("No valid JSON found in OpenAI response")
            
            # Parse JSON
            data = json.loads(json_content)
            print(f"DEBUG: Successfully parsed JSON with {len(data)} fields")
            
            # Validate required fields
            required_fields = [
                "project_name", "project_description", "confidence_score",
                "factors_considered", "recommendations", "timeline", "risk_assessment",
                "cash_flow_projection", "revenue_breakdown", "cost_breakdown"
            ]
            
            # Validate financial projection structure
            if "cash_flow_projection" in data:
                if not isinstance(data["cash_flow_projection"], list) or len(data["cash_flow_projection"]) != 10:
                    raise ValueError("cash_flow_projection must be a list of exactly 10 values")
            
            if "revenue_breakdown" in data:
                revenue_keys = ["agricultural_sales", "ecosystem_services", "subsidies_incentives"]
                for key in revenue_keys:
                    if key not in data["revenue_breakdown"]:
                        raise ValueError(f"Missing {key} in revenue_breakdown")
                    if not isinstance(data["revenue_breakdown"][key], list) or len(data["revenue_breakdown"][key]) != 10:
                        raise ValueError(f"{key} must be a list of exactly 10 values")
            
            if "cost_breakdown" in data:
                cost_keys = ["operational_costs", "infrastructure", "maintenance"]
                for key in cost_keys:
                    if key not in data["cost_breakdown"]:
                        raise ValueError(f"Missing {key} in cost_breakdown")
                    if not isinstance(data["cost_breakdown"][key], list) or len(data["cost_breakdown"][key]) != 10:
                        raise ValueError(f"{key} must be a list of exactly 10 values")
            
            missing_fields = []
            for field in required_fields:
                if field not in data:
                    missing_fields.append(field)
            
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
            
            print(f"DEBUG: All required fields present. Data keys: {list(data.keys())}")
            return data
            
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON decode error: {str(e)}")
            print(f"DEBUG: Content that failed to parse: {content}")
            raise Exception(f"Failed to parse OpenAI response as JSON: {str(e)}")
        except Exception as e:
            print(f"DEBUG: Parse error: {str(e)}")
            print(f"DEBUG: Content that caused error: {content}")
            raise Exception(f"Failed to parse OpenAI response: {str(e)}")
    
    def validate_inquiry(self, data: Dict[str, Any]) -> PropertyInquiryRequest:
        """Validate inquiry data using Pydantic"""
        
        try:
            return PropertyInquiryRequest(**data)
        except Exception as e:
            raise Exception(f"Invalid inquiry data: {str(e)}")
    
    def get_analysis_summary(self, result: AIAnalysisResult) -> Dict[str, Any]:
        """Get a summary of the AI analysis for display"""
        
        return {
            "project_name": result.estimate.project_name,
            "project_description": result.estimate.project_description,
            "confidence_score": result.estimate.confidence_score,
            "key_recommendations": result.estimate.recommendations[:3],
            "timeline": result.estimate.timeline,
            "processing_time": result.processing_time,
            "financial_projections": {
                "cash_flow_projection": result.estimate.cash_flow_projection,
                "revenue_breakdown": result.estimate.revenue_breakdown,
                "cost_breakdown": result.estimate.cost_breakdown
            }
        }
