"""
WebSocket Server for Teams Meeting Coach
Broadcasts real-time meeting analysis to connected clients
"""
import asyncio
import json
import warnings

# Suppress websockets deprecation warnings
warnings.filterwarnings('ignore', message='.*websockets.server.*deprecated.*')

import websockets
from websockets.server import serve, WebSocketServerProtocol
import threading
import queue
from typing import Set, Dict, Any
from datetime import datetime


class MeetingCoachWebSocketServer:
    """WebSocket server that broadcasts meeting analysis in real-time"""
    
    def __init__(self, host: str = "localhost", port: int = 3001):
        """
        Initialize WebSocket server.
        
        Args:
            host: Server host address
            port: Server port number
        """
        self.host = host
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self.message_queue = queue.Queue()
        self.is_running = False
        self.server = None
        
    async def register_client(self, websocket: WebSocketServerProtocol):
        """Register a new client connection"""
        self.clients.add(websocket)
        print(f"✅ Client connected from {websocket.remote_address}. Total clients: {len(self.clients)}")
        
        # Send welcome message
        await self.send_to_client(websocket, {
            'type': 'connection',
            'status': 'connected',
            'message': 'Connected to Meeting Coach WebSocket Server',
            'timestamp': datetime.now().isoformat()
        })
    
    async def unregister_client(self, websocket: WebSocketServerProtocol):
        """Unregister a client connection"""
        self.clients.discard(websocket)
        print(f"❌ Client disconnected. Total clients: {len(self.clients)}")
    
    async def send_to_client(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Send data to a specific client"""
        try:
            message = json.dumps(data)
            await websocket.send(message)
        except websockets.exceptions.ConnectionClosed:
            await self.unregister_client(websocket)
        except Exception as e:
            print(f"Error sending to client: {e}")
    
    async def broadcast(self, data: Dict[str, Any]):
        """Broadcast data to all connected clients"""
        if not self.clients:
            return
        
        message = json.dumps(data)
        # Use asyncio.gather to send to all clients concurrently
        await asyncio.gather(
            *[self._safe_send(client, message) for client in self.clients],
            return_exceptions=True
        )
    
    async def _safe_send(self, websocket: WebSocketServerProtocol, message: str):
        """Safely send message to client with error handling"""
        try:
            await websocket.send(message)
        except websockets.exceptions.ConnectionClosed:
            await self.unregister_client(websocket)
        except Exception as e:
            print(f"Error broadcasting to client: {e}")
    
    async def handle_client(self, websocket: WebSocketServerProtocol):
        """Handle individual client connection"""
        await self.register_client(websocket)
        
        try:
            # Listen for messages from client
            async for message in websocket:
                await self.handle_client_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister_client(websocket)
    
    async def handle_client_message(self, websocket: WebSocketServerProtocol, message: str):
        """
        Handle incoming messages from clients.
        
        Clients can send commands like:
        - {"type": "start_session", "config": {...}}
        - {"type": "stop_session"}
        - {"type": "ping"}
        """
        try:
            data = json.loads(message)
            msg_type = data.get('type', 'unknown')
            
            if msg_type == 'ping':
                await self.send_to_client(websocket, {
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                })
            elif msg_type == 'start_session':
                # Handle session start (will be implemented with MeetingCoach integration)
                await self.send_to_client(websocket, {
                    'type': 'session_status',
                    'status': 'started',
                    'message': 'Session started'
                })
            elif msg_type == 'stop_session':
                # Handle session stop
                await self.send_to_client(websocket, {
                    'type': 'session_status',
                    'status': 'stopped',
                    'message': 'Session stopped'
                })
            else:
                await self.send_to_client(websocket, {
                    'type': 'error',
                    'message': f'Unknown message type: {msg_type}'
                })
                
        except json.JSONDecodeError:
            await self.send_to_client(websocket, {
                'type': 'error',
                'message': 'Invalid JSON'
            })
        except Exception as e:
            print(f"Error handling client message: {e}")
            await self.send_to_client(websocket, {
                'type': 'error',
                'message': str(e)
            })
    
    def broadcast_sync(self, data: Dict[str, Any]):
        """
        Synchronous method to broadcast data (for use from non-async code).
        This queues the message for the async broadcast worker.
        """
        self.message_queue.put(data)
    
    async def broadcast_worker(self):
        """Background worker that broadcasts queued messages"""
        while self.is_running:
            try:
                # Check queue with timeout
                try:
                    data = self.message_queue.get(timeout=0.1)
                    await self.broadcast(data)
                except queue.Empty:
                    pass
                
                await asyncio.sleep(0.01)  # Small delay to prevent tight loop
            except Exception as e:
                print(f"Error in broadcast worker: {e}")
    
    async def start_server(self):
        """Start the WebSocket server"""
        self.is_running = True
        
        # Start broadcast worker
        asyncio.create_task(self.broadcast_worker())
        
        # Start WebSocket server
        async with serve(self.handle_client, self.host, self.port):
            print(f"🚀 WebSocket server started on ws://{self.host}:{self.port}")
            print(f"📡 Waiting for client connections...")
            
            # Keep server running
            await asyncio.Future()  # Run forever
    
    def run(self):
        """Run the server (blocking)"""
        try:
            asyncio.run(self.start_server())
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
        finally:
            self.is_running = False


def main():
    """Test the WebSocket server standalone"""
    server = MeetingCoachWebSocketServer(host="localhost", port=3001)
    
    # Start server in background thread to allow testing
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()
    
    print("WebSocket server running. Press Ctrl+C to stop.")
    
    # Simulate broadcasting some test data
    import time
    try:
        time.sleep(2)
        for i in range(5):
            test_data = {
                'type': 'meeting_update',
                'emotional_state': 'calm',
                'social_cue': 'appropriate',
                'confidence': 0.9,
                'wpm': 150,
                'text': f'Test message {i+1}',
                'timestamp': datetime.now().isoformat()
            }
            server.broadcast_sync(test_data)
            print(f"📤 Broadcasted test message {i+1}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n🛑 Test stopped")
    
    # Keep main thread alive
    server_thread.join()


if __name__ == '__main__':
    main()
