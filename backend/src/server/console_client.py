"""
Console WebSocket Client for Teams Meeting Coach
Connects to WebSocket server and displays real-time updates
"""

import asyncio
import json
from datetime import datetime

import websockets
from src import config
from src.ui.colors import (
    Colors,
    colorize_alert,
    colorize_emotional_state,
    colorize_social_cue,
)
from src.ui.dashboard import LiveDashboard
from src.ui.timeline import EmotionalTimeline


class ConsoleWebSocketClient:
    """WebSocket client that displays meeting updates in console"""

    def __init__(self, server_url: str = None):
        """
        Initialize WebSocket client.

        Args:
            server_url: WebSocket server URL (defaults to config values)
        """
        self.server_url = (
            server_url or f"ws://{config.WEBSOCKET_HOST}:{config.WEBSOCKET_PORT}"
        )
        self.websocket = None
        self.is_running = False
        self.dashboard = LiveDashboard()
        self.timeline = EmotionalTimeline(window_minutes=15, max_entries=200)

    async def connect(self, max_retries: int = 5, retry_delay: float = 1.0):
        """Connect to WebSocket server with retry logic"""
        import asyncio

        for attempt in range(max_retries):
            try:
                self.websocket = await websockets.connect(self.server_url)
                self.is_running = True
                print(f"✅ Connected to {self.server_url}")
                return True
            except Exception as e:
                if attempt < max_retries - 1:
                    print(
                        f"⏳ Waiting for server... (attempt {attempt + 1}/{max_retries})"
                    )
                    await asyncio.sleep(retry_delay)
                else:
                    print(f"❌ Failed to connect after {max_retries} attempts: {e}")
                    return False
        return False

    async def disconnect(self):
        """Disconnect from WebSocket server"""
        self.is_running = False
        if self.websocket:
            await self.websocket.close()
            print("🔌 Disconnected from server")

    async def send_message(self, message_type: str, data: dict = None):
        """Send a message to the server"""
        if not self.websocket:
            print("❌ Not connected to server")
            return

        message = {"type": message_type, "timestamp": datetime.now().isoformat()}

        if data:
            message.update(data)

        try:
            await self.websocket.send(json.dumps(message))
        except Exception as e:
            print(f"❌ Error sending message: {e}")

    async def send_ping(self):
        """Send ping to server"""
        await self.send_message("ping")

    async def start_session(self, config: dict = None):
        """Request server to start a session"""
        await self.send_message("start_session", {"config": config or {}})

    async def stop_session(self):
        """Request server to stop the session"""
        await self.send_message("stop_session")

    def handle_message(self, data: dict):
        """
        Handle incoming message from server.

        Message types:
        - connection: Initial connection confirmation
        - meeting_update: Real-time meeting data
        - transcription: New speech detected
        - emotion_update: Emotional state changed
        - alert: Important alert
        - session_status: Session started/stopped
        - pong: Response to ping
        - error: Error message
        """
        msg_type = data.get("type", "unknown")

        if msg_type == "connection":
            print(f"🔗 {data.get('message', 'Connected')}")
            self.dashboard.initialize_display(data.get("config"))
            self.dashboard.update_live_display(self.timeline)

        elif msg_type == "meeting_update":
            # Full meeting state update
            emotional_state = data.get("emotional_state", "unknown")
            social_cue = data.get("social_cue", "unknown")
            confidence = data.get("confidence", 0.0)
            wpm = data.get("wpm", 0)
            text = data.get("text", "")
            alert = data.get("alert", False)
            filler_counts = data.get("filler_counts", {})
            coaching = data.get("coaching", "")
            timestamp = data.get("timestamp")

            # Update dashboard state
            self.dashboard.update_current_status(
                emotional_state=emotional_state,
                social_cue=social_cue,
                confidence=confidence,
                text=text,
                coaching=coaching,
                alert=alert,
                wpm=wpm,
                filler_counts=filler_counts,
            )

            # Maintain timeline and refresh display
            self.timeline.add_entry(
                emotional_state=emotional_state,
                social_cue=social_cue,
                confidence=confidence,
                text=text,
                alert=alert,
                timestamp=timestamp,
            )
            self.dashboard.update_live_display(self.timeline)

        elif msg_type == "transcription":
            # New speech transcribed
            text = data.get("text", "")
            wpm = data.get("wpm", 0)
            print(f"\n🎙️ [{datetime.now().strftime('%H:%M:%S')}] {text} ({wpm} WPM)")

        elif msg_type == "emotion_update":
            # Emotional state changed
            state = data.get("emotional_state", "unknown")
            confidence = data.get("confidence", 0.0)
            colored_state = colorize_emotional_state(state)
            print(
                f"\n💭 Emotional state: {colored_state} (confidence: {confidence:.2f})"
            )

        elif msg_type == "alert":
            # Important alert
            message = data.get("message", "Alert!")
            colored_alert = colorize_alert(f"🚨 {message}", True)
            print(f"\n{colored_alert}")

        elif msg_type == "session_status":
            # Session started/stopped
            status = data.get("status", "unknown")
            message = data.get("message", "")
            print(f"\n📊 Session {status}: {message}")

            if status == "started":
                # Reset timeline for new session
                config_info = data.get("config")
                self.timeline = EmotionalTimeline(window_minutes=15, max_entries=200)
                self.dashboard.initialize_display(config_info)
                self.dashboard.update_live_display(self.timeline)

        elif msg_type == "recording_status":
            # Recording status update (microphone listening state)
            is_listening = data.get("is_listening", False)
            self.dashboard.set_listening_state(is_listening)
            self.dashboard.update_live_display(self.timeline)

        elif msg_type == "timeline_update":
            # Timeline summary update
            summary = data.get("summary", {})
            recent_entries = data.get("recent_entries", [])

            # Merge streamed timeline data into dashboard
            self.timeline.load_entries(recent_entries)
            self.dashboard.update_live_display(self.timeline)

        elif msg_type == "pong":
            # Response to ping
            timestamp = data.get("timestamp", "")
            print(f"🏓 Pong received at {timestamp}")

        elif msg_type == "error":
            # Error from server
            message = data.get("message", "Unknown error")
            print(f"\n❌ Error: {message}")

        else:
            print(f"\n❓ Unknown message type: {msg_type}")
            print(f"   Data: {data}")

    async def listen(self):
        """Listen for messages from server"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    self.handle_message(data)
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON received: {message}")
                except Exception as e:
                    print(f"❌ Error handling message: {e}")
        except websockets.exceptions.ConnectionClosed:
            print("\n🔌 Connection closed by server")
        except Exception as e:
            print(f"\n❌ Error in listen loop: {e}")
        finally:
            self.is_running = False

    async def run(self):
        """Run the client (connect and listen)"""
        if await self.connect():
            try:
                await self.listen()
            finally:
                await self.disconnect()
                self.dashboard.exit_alt_screen()


async def main():
    """Main entry point for console client"""
    print("🧠 Teams Meeting Coach - Console WebSocket Client")
    print("=" * 60)

    client = ConsoleWebSocketClient()

    try:
        await client.run()
    except KeyboardInterrupt:
        print("\n\n🛑 Client stopped by user")
        await client.disconnect()
        client.dashboard.exit_alt_screen()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
