import asyncio
import websockets
import os
import time
import json

async def send_image_stream(uri="ws://localhost:8000/ws/stream", image_dir="Data/", delay=0.5, output_file="websocket_test_results.json"):
    results = []
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to WebSocket: {uri}")

            response = await websocket.recv()
            print(f"Server says: {response}")
            session_id = None
            try:
                data = json.loads(response)
                if data.get("status") == "connected":
                    session_id = data.get("session_id")
                    print(f"Session ID: {session_id}")
            except json.JSONDecodeError:
                print("Could not decode server response as JSON.")

            if session_id:
                image_files = [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]
                print(f"Found {len(image_files)} images in '{image_dir}'")

                for image_file in image_files:
                    image_path = os.path.join(image_dir, image_file)
                    try:
                        with open(image_path, "rb") as f:
                            image_data = f.read()
                            await websocket.send(image_data)
                            print(f"Sent image: {image_file} ({len(image_data)} bytes)")

                            try:
                                prediction_response_str = await asyncio.wait_for(websocket.recv(), timeout=5)
                                print(f"Prediction Response for {image_file}: {prediction_response_str}")
                                try:
                                    prediction_response_json = json.loads(prediction_response_str)
                                    results.append({"image": image_file, "response": prediction_response_json})
                                except json.JSONDecodeError:
                                    results.append({"image": image_file, "response": prediction_response_str})
                            except asyncio.TimeoutError:
                                print(f"Timeout waiting for prediction response for {image_file}")
                                results.append({"image": image_file, "response": "Timeout"})
                            except websockets.exceptions.ConnectionClosedOK:
                                print("WebSocket connection closed by server.")
                                break
                            except websockets.exceptions.ConnectionClosedError as e:
                                print(f"WebSocket connection closed with error: {e}")
                                break

                            await asyncio.sleep(delay)

                    except FileNotFoundError:
                        print(f"Error: Image file not found: {image_path}")
                        results.append({"image": image_file, "error": "File Not Found"})
                    except Exception as e:
                        print(f"Error sending image {image_file}: {e}")
                        results.append({"image": image_file, "error": str(e)})
                        break

            else:
                print("Failed to establish a session with the server.")
                results.append({"error": "Failed to establish session"})

    except websockets.exceptions.ConnectionClosedError:
        print(f"Error: Could not connect to {uri}. Make sure the PlumVision API server is running.")
        results.append({"error": f"Connection refused at {uri}"})
    except Exception as e:
        print(f"An error occurred: {e}")
        results.append({"error": str(e)})
    finally:
        with open(output_file, "w") as f:
            json.dump(results, f, indent=4)
        print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    asyncio.run(send_image_stream())