import asyncio
import websockets
import httpx
import json

SERVER_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws/stream"

async def test_websocket_connect_disconnect_existing_server():
    session_id = None
    try:
        async with websockets.connect(WS_URL) as websocket:
            connected_message = await websocket.recv()
            connected_data = json.loads(connected_message)
            assert connected_data["status"] == "connected"
            session_id = connected_data["session_id"]
            print(f"Connected with session ID: {session_id}")
            await websocket.close()
            print("Disconnected from WebSocket.")

        await asyncio.sleep(0.5)

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SERVER_URL}/api/sessions")
            assert response.status_code == 200
            sessions = response.json()

            found_session = None
            for session in sessions:
                if session["session_id"] == session_id:
                    found_session = session
                    break

            assert found_session is not None
            assert found_session["is_active"] is False
            assert found_session["end_time"] is not None
            assert found_session["duration_seconds"] is not None
            print(f"Session details after disconnect: {found_session}")
            print("WebSocket connect and disconnect test passed!")

    except websockets.exceptions.ConnectionClosedError:
        print("Error: Could not connect to the WebSocket server. Ensure the server is running.")
    except httpx.ConnectError:
        print("Error: Could not connect to the HTTP server. Ensure the server is running.")
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_connect_disconnect_existing_server())