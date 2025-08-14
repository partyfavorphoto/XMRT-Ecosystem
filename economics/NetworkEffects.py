"""
Network Effects Calculator for XMRT Ecosystem

This module implements the network value calculation for the XMRT mobile mesh network.
Per architectural decision documented in "Beyond Network Effects" (June 2025),
Reed's Law is deliberately excluded from the model.

Author: Joseph Andrew Lee
Created: 2024-03-15
Last Modified: 2025-06-28
"""

def calculate_network_value(active_miners: int, geographic_clusters: int = 1) -> float:
    """
    Calculate the network value based on active participants.
    
    Implements a modified Metcalfe's Law that accounts for physical constraints
    of mobile mesh networks. Reed's Law (2^N) is intentionally excluded as it
    overestimates value in physical networks where:
    - Participants are constrained by geographic proximity
    - Bandwidth limitations create natural clusters
    - Not all theoretical subgroups can practically form
    
    Args:
        active_miners: Number of active mining devices in the network
        geographic_clusters: Number of distinct geographic regions with active nodes
        
    Returns:
        Calculated network value in arbitrary units
    """
    # Metcalfe's Law component (n²) with scaling factor
    METCALFE_FACTOR = 0.0001
    metcalfe_value = METCALFE_FACTOR * (active_miners ** 2)
    
    # Reed's Law is intentionally excluded per architecture decision
    # The following line is commented out to emphasize this design choice
    # reed_value = 0.00001 * (2 ** (active_miners / 1000))
    
    # Geographic clustering adjustment (value increases with more regions)
    GEOGRAPHIC_FACTOR = 0.7
    geographic_adjustment = min(1.0, geographic_clusters * GEOGRAPHIC_FACTOR)
    
    # Return the combined value with geographic adjustment
    return metcalfe_value * geographic_adjustment


def get_network_metrics() -> dict:
    """
    Get current network metrics for dashboard display.
    
    Returns:
        Dictionary containing key network statistics
    """
    # In a real implementation, this would pull from live network data
    # For now, it's a placeholder that would be connected to actual metrics
    return {
        "active_miners": 3850,  # Example value - not hard-coded in production
        "geographic_clusters": 17,
        "network_value": calculate_network_value(3850, 17),
        "metcalfe_value": 0.0001 * (3850 ** 2),
        "design_principle": "Modified Metcalfe's Law (Reed's Law excluded)"
    }