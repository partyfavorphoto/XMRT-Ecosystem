import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import hashlib
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTSService:
    """
    Text-to-Speech Service for AI Agent voices in X Spaces.
    Generates audio files for AI agent messages and manages voice profiles.
    """
    
    def __init__(self):
        self.audio_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'audio')
        self.ensure_audio_directory()
        
        # Voice profiles for different agent personalities
        self.voice_profiles = {
            'conservative': {
                'voice': 'male_voice',
                'description': 'Steady, authoritative voice for conservative financial agents'
            },
            'progressive': {
                'voice': 'female_voice',
                'description': 'Dynamic, forward-thinking voice for progressive agents'
            },
            'analytical': {
                'voice': 'male_voice',
                'description': 'Clear, precise voice for analytical agents'
            },
            'creative': {
                'voice': 'female_voice',
                'description': 'Expressive, engaging voice for creative agents'
            },
            'moderator': {
                'voice': 'male_voice',
                'description': 'Neutral, professional voice for moderator agents'
            },
            'default': {
                'voice': 'male_voice',
                'description': 'Standard voice for general purpose agents'
            }
        }
    
    def ensure_audio_directory(self):
        """Ensure the audio directory exists"""
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir, exist_ok=True)
            logger.info(f"Created audio directory: {self.audio_dir}")
    
    def get_voice_for_agent(self, agent_personality: str) -> str:
        """
        Get the appropriate voice type for an agent based on their personality.
        
        Args:
            agent_personality: The agent's personality type
            
        Returns:
            Voice type string for TTS generation
        """
        personality_lower = agent_personality.lower()
        
        for profile_key, profile_data in self.voice_profiles.items():
            if profile_key in personality_lower:
                return profile_data['voice']
        
        return self.voice_profiles['default']['voice']
    
    def generate_speech_for_message(self, message_content: str, agent_id: int, 
                                  agent_personality: str = "default") -> Dict[str, Any]:
        """
        Generate speech audio for an AI agent message.
        
        Args:
            message_content: The text content to convert to speech
            agent_id: ID of the agent
            agent_personality: Personality type of the agent
            
        Returns:
            Dictionary with audio file information or error details
        """
        try:
        except Exception as e:
            pass
            # Clean and prepare the text for TTS
            cleaned_text = self._prepare_text_for_tts(message_content)
            
            if len(cleaned_text.strip()) == 0:
                return {
                    'success': False,
                    'error': 'No valid text content for TTS generation'
                }
            
            # Check text length limit
            if len(cleaned_text) > 50000:
                return {
                    'success': False,
                    'error': 'Text content exceeds 50,00 character limit'
                }
            
            # Generate unique filename based on content hash
            content_hash = hashlib.md5(cleaned_text.encode()).hexdigest()[:8]
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"agent_{agent_id}_{timestamp}_{content_hash}.wav"
            file_path = os.path.join(self.audio_dir, filename)
            
            # Get appropriate voice for the agent
            voice_type = self.get_voice_for_agent(agent_personality)
            
            # Import the media generation function here to avoid circular imports
from src.utils.media_utils import generate_speech_audio
            
            # Generate the speech audio
            audio_result = generate_speech_audio(cleaned_text, file_path, voice_type)
            
            if audio_result['success']:
                return {
                    'success': True,
                    'audio_file_path': file_path,
                    'filename': filename,
                    'voice_type': voice_type,
                    'duration_estimate': self._estimate_duration(cleaned_text),
                    'generated_at': datetime.utcnow().isoformat(),
                    'agent_id': agent_id,
                    'content_hash': content_hash
                }
            else:
                return {
                    'success': False,
                    'error': f"TTS generation failed: {audio_result.get('error', 'Unknown error')}"
                }
                
        except Exception as e:
            logger.error(f"Error generating speech for agent {agent_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _prepare_text_for_tts(self, text: str) -> str:
        """
        Prepare text for optimal TTS generation.
        
        Args:
            text: Raw text content
            
        Returns:
            Cleaned and formatted text
        """
        # Remove excessive whitespace
        cleaned = ' '.join(text.split())
        
        # Ensure proper sentence endings
        if cleaned and not cleaned.endswith(('.', '!', '?')):
            cleaned += '.'
        
        # Replace common abbreviations for better pronunciation
        replacements = {
            'DAO': 'D A O',
            'AI': 'A I',
            'API': 'A P I',
            'NFT': 'N F T',
            'DeFi': 'Dee Fi',
            'CEO': 'C E O',
            'CTO': 'C T O',
            'CFO': 'C F O',
            'USD': 'U S D',
            'ETH': 'E T H',
            'BTC': 'B T C'
        }
        
        for abbrev, pronunciation in replacements.items():
            cleaned = cleaned.replace(abbrev, pronunciation)
        
        return cleaned
    
    def _estimate_duration(self, text: str) -> float:
        """
        Estimate the duration of the generated audio in seconds.
        
        Args:
            text: Text content
            
        Returns:
            Estimated duration in seconds
        """
        # Rough estimate: average speaking rate is about 150-160 words per minute
        words = len(text.split())
        estimated_minutes = words / 155  # Use 155 WPM as average
        return estimated_minutes * 60  # Convert to seconds
    
    def generate_session_intro(self, session_title: str, moderator_name: str, 
                             participant_names: list) -> Dict[str, Any]:
        """
        Generate an introduction audio for a boardroom session.
        
        Args:
            session_title: Title of the session
            moderator_name: Name of the moderator
            participant_names: List of participant names
            
        Returns:
            Dictionary with audio file information
        """
        try:
            participants_text = ", ".join(participant_names[:-1])
            if len(participant_names) > 1:
                participants_text += f", and {participant_names[-1]}"
            else:
                participants_text = participant_names[0] if participant_names else "no participants"
            
            intro_text = f"""
            Welcome to the D A O Boardroom session: {session_title}.
            
            I am {moderator_name}, your moderator for today's discussion.
            
            Joining us today are our A I agents: {participants_text}.
            
            This session is being conducted transparently on X Spaces for public oversight and regulatory compliance.
            
            Let's begin our discussion.
            """
            
            return self.generate_speech_for_message(
                intro_text.strip(),
                agent_id=0,  # Use 0 for system/moderator messages
                agent_personality="moderator"
            )
            
        except Exception as e:
            logger.error(f"Error generating session intro: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_vote_announcement(self, agenda_item_title: str, 
                                 vote_results: Dict[str, int]) -> Dict[str, Any]:
        """
        Generate an audio announcement for vote results.
        
        Args:
            agenda_item_title: Title of the agenda item that was voted on
            vote_results: Dictionary with vote counts (yes, no, abstain)
            
        Returns:
            Dictionary with audio file information
        """
        try:
            yes_votes = vote_results.get('yes', 0)
            no_votes = vote_results.get('no', 0)
            abstain_votes = vote_results.get('abstain', 0)
            total_votes = yes_votes + no_votes + abstain_votes
            
            if yes_votes > no_votes:
                result = "approved"
            elif no_votes > yes_votes:
                result = "rejected"
            else:
                result = "tied"
            
            announcement_text = f"""
            The voting on agenda item "{agenda_item_title}" has concluded.
            
            Results: {yes_votes} votes in favor, {no_votes} votes against, and {abstain_votes} abstentions.
            
            With {total_votes} total votes cast, the proposal is {result}.
            
            Thank you to all agents for their participation in this democratic process.
            """
            
            return self.generate_speech_for_message(
                announcement_text.strip(),
                agent_id=0,  # Use 0 for system announcements
                agent_personality="moderator"
            )
            
        except Exception as e:
            logger.error(f"Error generating vote announcement: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_available_voices(self) -> Dict[str, Any]:
        """
        Get information about available voice profiles.
        
        Returns:
            Dictionary with voice profile information
        """
        return {
            'voice_profiles': self.voice_profiles,
            'total_profiles': len(self.voice_profiles),
            'available_voices': ['male_voice', 'female_voice']
        }
    
    def cleanup_old_audio_files(self, days_old: int = 7) -> Dict[str, Any]:
        """
        Clean up audio files older than specified days.
        
        Args:
            days_old: Number of days after which to delete files
            
        Returns:
            Dictionary with cleanup results
        """
        try:
            import time
            
            current_time = time.time()
            cutoff_time = current_time - (days_old * 24 * 60 * 60)
            
            deleted_files = []
            total_size_freed = 0
            
            for filename in os.listdir(self.audio_dir):
                if filename.endswith('.wav'):
                    file_path = os.path.join(self.audio_dir, filename)
                    file_mtime = os.path.getmtime(file_path)
                    
                    if file_mtime < cutoff_time:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        deleted_files.append(filename)
                        total_size_freed += file_size
            
            return {
                'success': True,
                'deleted_files': len(deleted_files),
                'files_deleted': deleted_files,
                'size_freed_bytes': total_size_freed,
                'size_freed_mb': round(total_size_freed / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up audio files: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

