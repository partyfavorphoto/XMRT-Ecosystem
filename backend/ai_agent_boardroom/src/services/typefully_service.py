import requests
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TypefullyService:
    """
    Typefully API Service for easier Twitter posting.
    Handles posting tweets, threads, and scheduling for the main Eliza account.
    """
    
    def __init__(self):
        self.api_key = "1p80KNGogHZnWXYo"
        self.base_url = "https://api.typefully.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def post_tweet(self, content: str, schedule_time: Optional[str] = None) -> Dict[str, Any]:
        """
        Post a single tweet using Typefully API.
        
        Args:
            content: Tweet content
            schedule_time: Optional ISO format datetime string for scheduling
            
        Returns:
            Dictionary with posting result
        """
        try:
            url = f"{self.base_url}/drafts"
            
            data = {
                "content": content,
                "publish": True if not schedule_time else False
            }
            
            if schedule_time:
                data["schedule_date"] = schedule_time
            
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code in [200, 201]:
                result = response.json()
                logger.info(f"Successfully posted tweet via Typefully: {result.get('id')}")
                return {
                    "success": True,
                    "draft_id": result.get("id"),
                    "content": content,
                    "scheduled": bool(schedule_time),
                    "schedule_time": schedule_time,
                    "posted_at": datetime.utcnow().isoformat()
                }
            else:
                logger.error(f"Failed to post tweet via Typefully: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"Error posting tweet via Typefully: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def post_thread(self, tweets: List[str], schedule_time: Optional[str] = None) -> Dict[str, Any]:
        """
        Post a Twitter thread using Typefully API.
        
        Args:
            tweets: List of tweet contents for the thread
            schedule_time: Optional ISO format datetime string for scheduling
            
        Returns:
            Dictionary with posting result
        """
        try:
            url = f"{self.base_url}/drafts"
            
            # Join tweets with thread separators
            thread_content = "\n\n---\n\n".join(tweets)
            
            data = {
                "content": thread_content,
                "publish": True if not schedule_time else False
            }
            
            if schedule_time:
                data["schedule_date"] = schedule_time
            
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code in [200, 201]:
                result = response.json()
                logger.info(f"Successfully posted thread via Typefully: {result.get('id')}")
                return {
                    "success": True,
                    "draft_id": result.get("id"),
                    "thread_length": len(tweets),
                    "content": thread_content,
                    "scheduled": bool(schedule_time),
                    "schedule_time": schedule_time,
                    "posted_at": datetime.utcnow().isoformat()
                }
            else:
                logger.error(f"Failed to post thread via Typefully: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"Error posting thread via Typefully: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def post_boardroom_announcement(self, session_title: str, session_description: str, 
                                  space_url: str = None) -> Dict[str, Any]:
        """
        Post an announcement about a boardroom session.
        
        Args:
            session_title: Title of the boardroom session
            session_description: Description of the session
            space_url: Optional X Spaces URL
            
        Returns:
            Dictionary with posting result
        """
        try:
            announcement = f"""🚀 DAO Boardroom Session LIVE NOW!

📋 {session_title}

{session_description}

🤖 AI Agents are gathering for transparent governance discussions

#DAO #Governance #AI #Transparency #Blockchain"""

            if space_url:
                announcement += f"\n\n🎙️ Join us live: {space_url}"
            
            return self.post_tweet(announcement)
            
        except Exception as e:
            logger.error(f"Error posting boardroom announcement: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def post_vote_results(self, agenda_item: str, results: Dict[str, int]) -> Dict[str, Any]:
        """
        Post vote results from a boardroom session.
        
        Args:
            agenda_item: The agenda item that was voted on
            results: Dictionary with vote counts
            
        Returns:
            Dictionary with posting result
        """
        try:
            yes_votes = results.get('yes', 0)
            no_votes = results.get('no', 0)
            abstain_votes = results.get('abstain', 0)
            total_votes = yes_votes + no_votes + abstain_votes
            
            if yes_votes > no_votes:
                outcome = "✅ APPROVED"
            elif no_votes > yes_votes:
                outcome = "❌ REJECTED"
            else:
                outcome = "🤝 TIED"
            
            vote_tweet = f"""📊 DAO VOTE RESULTS

📋 {agenda_item}

🗳️ Results:
• Yes: {yes_votes}
• No: {no_votes}
• Abstain: {abstain_votes}
• Total: {total_votes}

{outcome}

#DAO #Governance #Voting #Transparency"""
            
            return self.post_tweet(vote_tweet)
            
        except Exception as e:
            logger.error(f"Error posting vote results: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def post_agent_message(self, agent_name: str, message: str, session_title: str = None) -> Dict[str, Any]:
        """
        Post a message from an AI agent.
        
        Args:
            agent_name: Name of the AI agent
            message: The agent's message
            session_title: Optional session title for context
            
        Returns:
            Dictionary with posting result
        """
        try:
            agent_tweet = f"🤖 {agent_name}: {message}"
            
            if session_title:
                agent_tweet += f"\n\n📋 Session: {session_title}"
            
            agent_tweet += "\n\n#DAO #AI #Governance"
            
            # Truncate if too long
            if len(agent_tweet) > 280:
                agent_tweet = agent_tweet[:277] + "..."
            
            return self.post_tweet(agent_tweet)
            
        except Exception as e:
            logger.error(f"Error posting agent message: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def post_session_summary(self, session_title: str, duration_minutes: int, 
                           agenda_items_count: int, votes_cast: int) -> Dict[str, Any]:
        """
        Post a summary of a completed boardroom session.
        
        Args:
            session_title: Title of the session
            duration_minutes: Duration in minutes
            agenda_items_count: Number of agenda items discussed
            votes_cast: Number of votes cast
            
        Returns:
            Dictionary with posting result
        """
        try:
            summary_tweets = [
                f"""📋 DAO BOARDROOM SESSION COMPLETE

🎯 {session_title}

⏱️ Duration: {duration_minutes} minutes
📝 Agenda Items: {agenda_items_count}
🗳️ Votes Cast: {votes_cast}

#DAO #Governance #Summary""",
                
                f"""🤖 Our AI agents demonstrated transparent, autonomous decision-making in today's session.

All discussions were conducted publicly on X Spaces for regulatory compliance and community oversight.

#Transparency #AI #Blockchain #Governance""",
                
                f"""🚀 The future of DAO governance is here!

Autonomous AI agents making decisions transparently, with full public oversight and regulatory compliance.

Join us for the next session! 

#Innovation #DAO #Future"""
            ]
            
            return self.post_thread(summary_tweets)
            
        except Exception as e:
            logger.error(f"Error posting session summary: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def schedule_session_reminder(self, session_title: str, start_time: str, 
                                schedule_time: str) -> Dict[str, Any]:
        """
        Schedule a reminder tweet for an upcoming session.
        
        Args:
            session_title: Title of the session
            start_time: When the session starts (human readable)
            schedule_time: When to post the reminder (ISO format)
            
        Returns:
            Dictionary with scheduling result
        """
        try:
            reminder_tweet = f"""⏰ REMINDER: DAO Boardroom Session

📋 {session_title}

🕐 Starting: {start_time}

🤖 AI agents will gather for transparent governance discussions

Set your notifications! 🔔

#DAO #Governance #Reminder"""
            
            return self.post_tweet(reminder_tweet, schedule_time)
            
        except Exception as e:
            logger.error(f"Error scheduling session reminder: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_drafts(self) -> Dict[str, Any]:
        """
        Get list of drafts from Typefully.
        
        Returns:
            Dictionary with drafts information
        """
        try:
            url = f"{self.base_url}/drafts"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "drafts": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"Error getting drafts: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_draft(self, draft_id: str) -> Dict[str, Any]:
        """
        Delete a draft from Typefully.
        
        Args:
            draft_id: ID of the draft to delete
            
        Returns:
            Dictionary with deletion result
        """
        try:
            url = f"{self.base_url}/drafts/{draft_id}"
            response = requests.delete(url, headers=self.headers)
            
            if response.status_code in [200, 204]:
                return {
                    "success": True,
                    "draft_id": draft_id,
                    "deleted_at": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"Error deleting draft: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

