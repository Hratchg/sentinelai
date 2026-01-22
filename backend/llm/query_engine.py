"""
LLM-powered query engine for surveillance Q&A.

Uses Claude (Anthropic) to answer questions about surveillance data:
- "Who is on camera 1?"
- "When did I last see John?"
- "What is Sarah doing right now?"
"""

import os
import logging
from typing import List, Dict, Optional, Tuple
from anthropic import Anthropic
import json
from datetime import datetime

from backend.storage.crud import (
    get_all_persons,
    get_person_events,
    get_person_clips,
    get_recent_clips
)

logger = logging.getLogger(__name__)


class SurveillanceQueryEngine:
    """
    LLM-powered query engine for surveillance system.

    Features:
    - Natural language question answering
    - Context retrieval from database
    - Video clip attachment in responses

    Phase 1 Mode: Works as stub without API key
    Phase 2 Mode: Full LLM integration with Anthropic Claude
    """

    def __init__(self, api_key: Optional[str] = None, user_id: Optional[str] = None):
        """
        Initialize query engine.

        Args:
            api_key: Anthropic API key (or uses ANTHROPIC_API_KEY env var)
            user_id: User ID for multi-tenant context filtering
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.user_id = user_id

        if not self.api_key:
            logger.info("No Anthropic API key provided - running in Phase 1 stub mode")

        self.client = Anthropic(api_key=self.api_key) if self.api_key else None
        self.model = "claude-3-5-sonnet-20241022"

    async def answer_question(
        self,
        db_session,
        question: str,
        include_clips: bool = True
    ) -> Dict:
        """
        Answer user question about surveillance system.

        Args:
            db_session: Database session
            question: Natural language query
            include_clips: Whether to include video clips in response

        Returns:
            {
                'answer': str,
                'video_clips': List[Dict],
                'sources': List[Dict]
            }
        """
        if not self.client:
            # Phase 1 stub mode - return friendly response
            stub_response = (
                f"I received your question: '{question}'. "
                f"Voice command system is working! Full LLM integration with Claude API "
                f"will be implemented in Phase 2. For now, I'm running in demo mode. "
                f"You can test voice activation by saying 'Hey Sentinel' followed by your question!"
            )
            return {
                'answer': stub_response,
                'video_clips': [],
                'sources': []
            }

        try:
            # 1. Build context from database
            context, clips = await self._build_context(db_session, question)

            # 2. Build system prompt
            system_prompt = self._build_system_prompt()

            # 3. Build user prompt
            user_prompt = f"""
Context from surveillance system:
{context}

User question: {question}

Please answer the user's question based only on the provided context.
If you don't have enough information, say so clearly.
Be conversational and concise.
"""

            # 4. Query Claude
            message = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            answer = message.content[0].text

            # 5. Attach video clips if requested
            video_clips = []
            if include_clips and clips:
                video_clips = clips[:3]  # Limit to 3 clips

            return {
                'answer': answer,
                'video_clips': video_clips,
                'sources': []
            }

        except Exception as e:
            logger.error(f"LLM query failed: {e}")
            return {
                'answer': f"Sorry, I encountered an error processing your question: {str(e)}",
                'video_clips': [],
                'sources': []
            }

    async def _build_context(
        self,
        db_session,
        question: str
    ) -> Tuple[str, List[Dict]]:
        """
        Build context from database based on question.

        Args:
            db_session: Database session
            question: User question

        Returns:
            (context_string, video_clips)
        """
        context_parts = []
        relevant_clips = []

        # Extract potential person names from question
        person_names = self._extract_person_names(question)

        logger.info(f"Building context for question: '{question}', extracted names: {person_names}")

        # 1. Get current state (if asking "now", "currently", etc.)
        if any(word in question.lower() for word in ['now', 'currently', 'right now', 'camera']):
            # In real-time system, this would query current active tracks
            # For now, just note it
            context_parts.append("Current Status: Live monitoring active. Real-time tracking is operational.")

        # 2. Get person information
        if person_names:
            all_persons = await get_all_persons(db_session, include_archived=False)

            matched_persons = []
            for person in all_persons:
                # Match by name or display_name (case-insensitive, partial match)
                person_name = (person.display_name or person.name or "").lower()
                if person_name and any(name.lower() in person_name or person_name in name.lower() for name in person_names):
                    matched_persons.append(person)

            if matched_persons:
                for person in matched_persons:
                    # Calculate time since last seen
                    time_since_last = datetime.utcnow() - person.last_seen_at
                    if time_since_last.total_seconds() < 3600:  # Less than 1 hour
                        time_ago = f"{int(time_since_last.total_seconds() / 60)} minutes ago"
                    elif time_since_last.days == 0:
                        time_ago = f"{int(time_since_last.total_seconds() / 3600)} hours ago"
                    else:
                        time_ago = f"{time_since_last.days} days ago"

                    person_context = f"""
Person: {person.display_name or person.name or 'Unknown'}
First seen: {person.first_seen_at.strftime('%B %d, %Y at %I:%M %p')}
Last seen: {person.last_seen_at.strftime('%B %d, %Y at %I:%M %p')} ({time_ago})
Total appearances: {person.total_appearances}
"""
                    context_parts.append(person_context)

                    # Get recent events for this person
                    events = await get_person_events(db_session, person.id, limit=10)

                    if events:
                        recent_actions = [f"  - {e.action or e.event_type} at {e.created_at.strftime('%I:%M %p')}" for e in events[:5]]
                        context_parts.append(f"Recent activities:\n" + "\n".join(recent_actions))

                    # Get video clips
                    clips = await get_person_clips(db_session, person.id, limit=3)

                    for clip in clips:
                        relevant_clips.append({
                            'clip_url': f'/api/v1/clips/{clip.id}',
                            'person_id': person.display_name or person.name or person.id,
                            'timestamp': clip.created_at.isoformat(),
                            'event_type': clip.event_type
                        })
            else:
                context_parts.append(f"Note: No persons found matching the names: {', '.join(person_names)}")

        # 3. Get time-based information (if asking "when", "last time", etc.)
        if any(word in question.lower() for word in ['when', 'last', 'recent', 'yesterday', 'today']):
            # Get recent events across all persons
            all_persons = await get_all_persons(db_session, include_archived=False)

            if all_persons:
                recent_activity = []
                for person in all_persons[:5]:  # Top 5 most recent
                    recent_activity.append(
                        f"- {person.display_name}: last seen {person.last_seen_at.strftime('%Y-%m-%d %H:%M:%S')}"
                    )

                if recent_activity:
                    context_parts.append("Recent activity:\n" + "\n".join(recent_activity))

        # 4. If no specific context found, provide general stats
        if not context_parts:
            all_persons = await get_all_persons(db_session, include_archived=False)

            if all_persons:
                context_parts.append(f"System Status: {len(all_persons)} known person(s) in database")

                # Show top 3 most recently seen
                for idx, person in enumerate(all_persons[:3], 1):
                    time_since_last = datetime.utcnow() - person.last_seen_at
                    if time_since_last.total_seconds() < 3600:
                        time_ago = f"{int(time_since_last.total_seconds() / 60)} minutes ago"
                    elif time_since_last.days == 0:
                        time_ago = f"{int(time_since_last.total_seconds() / 3600)} hours ago"
                    else:
                        time_ago = f"{time_since_last.days} days ago"

                    context_parts.append(f"{idx}. {person.display_name or person.name or 'Unknown'} - last seen {time_ago}")
            else:
                context_parts.append("System Status: No persons detected yet. Monitoring is active.")

        context = "\n\n".join(context_parts)

        logger.info(f"Built context with {len(context_parts)} parts, {len(relevant_clips)} clips")

        return context, relevant_clips

    def _extract_person_names(self, text: str) -> List[str]:
        """
        Extract potential person names from question.

        Simple heuristic - looks for capitalized words.

        Args:
            text: Question text

        Returns:
            List of potential names
        """
        words = text.split()
        names = []

        for word in words:
            # Remove punctuation
            word = word.strip('?,.')

            # Check if capitalized (likely a name)
            if word and word[0].isupper() and len(word) > 2:
                # Skip common question words
                if word not in ['Who', 'What', 'When', 'Where', 'Why', 'How', 'Show', 'Tell']:
                    names.append(word)

        return names

    def _build_system_prompt(self) -> str:
        """Build system prompt for Claude."""
        return """You are an AI surveillance assistant. You help users understand what's happening in their surveillance system.

You have access to:
- Live camera feeds
- Person recognition (faces + names)
- Action/gesture detection
- Historical event logs
- Video clips of important events

Answer questions conversationally and concisely. If you don't have information, say so clearly.
Use present tense for current events, past tense for historical data.
When you mention a person or event, be specific about timestamps.

Example questions you can answer:
- "Who is that person?" → Check recent detections
- "When did I last see John?" → Check person's last_seen_at
- "What is Sarah doing?" → Check recent events for Sarah
- "Show me when Michael visited this week" → Retrieve clips for Michael

Keep responses brief and helpful."""
