"""
Weather tool for PocketFlow agents.
"""

import requests
from typing import Dict, Any
from .base import Tool, ToolResult
from ..utils.logging import get_logger


class WeatherTool(Tool):
    """
    Tool for getting weather information.
    """
    
    def __init__(self):
        super().__init__(
            name="weather",
            description="Get current weather information for a location"
        )
    
    @property
    def parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            "location": {
                "type": str,
                "required": True,
                "description": "City name or location (e.g., 'San Francisco')"
            },
            "units": {
                "type": str,
                "required": False,
                "description": "Temperature units: 'celsius' or 'fahrenheit' (default: 'celsius')"
            }
        }
    
    def execute(self, **kwargs) -> ToolResult:
        """
        Get weather information for a location.
        
        Args:
            location: The location to get weather for
            units: Temperature units
            
        Returns:
            ToolResult with weather data
        """
        location = kwargs.get("location")
        units = kwargs.get("units", "celsius")
        
        try:
            # For now, return mock weather data
            # In production, you'd integrate with a real weather API
            weather_data = self._get_mock_weather(location, units)
            
            return ToolResult(
                success=True,
                data=weather_data,
                metadata={
                    "location": location,
                    "units": units,
                    "source": "weather"
                }
            )
            
        except Exception as e:
            self.logger.error(f"Weather lookup failed: {str(e)}")
            return ToolResult(
                success=False,
                error=f"Weather lookup failed: {str(e)}"
            )
    
    def _get_mock_weather(self, location: str, units: str) -> Dict[str, Any]:
        """
        Get mock weather data for demonstration.
        In production, replace with real weather API.
        """
        import random
        
        # Mock weather data
        temp_c = random.randint(10, 30)
        temp_f = int(temp_c * 9/5 + 32)
        
        conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy", "Clear"]
        condition = random.choice(conditions)
        
        return {
            "location": location,
            "temperature": {
                "celsius": temp_c,
                "fahrenheit": temp_f
            },
            "condition": condition,
            "humidity": random.randint(30, 80),
            "wind_speed": random.randint(0, 20),
            "units": units
        } 