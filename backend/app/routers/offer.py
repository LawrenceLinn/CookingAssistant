from fastapi import APIRouter, HTTPException, WebSocket
from pydantic import BaseModel
from aiortc import (
    RTCSessionDescription,
    RTCPeerConnection,
    VideoStreamTrack,
    RTCIceCandidate,
)
from aiortc.contrib.media import MediaPlayer, MediaRelay
import asyncio


class Offer(BaseModel):
    sdp: str
    type: str


class Candidate(BaseModel):
    candidate: str
    sdpMid: str
    sdpMLineIndex: int


router = APIRouter()

pcs = set()  # Keep track of all PeerConnections

relay = MediaRelay()  # Relay to efficiently manage media streams


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    pc = RTCPeerConnection()
    pcs.add(pc)  # Add the new PeerConnection to the set

    @pc.on("track")
    async def on_track(track):
        if track.kind == "video":
            print("Video track added")
            # Process the track (e.g., relay it, record it, etc.)
            for other_pc in pcs:
                if other_pc is not pc:
                    other_pc.addTrack(track)

    @pc.on("icecandidate")
    async def on_icecandidate(candidate):
        print("New ICE candidate:", candidate)
        await websocket.send_json({"type": "candidate", "candidate": candidate.dict()})

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print(f"Connection state is {pc.connectionState}")
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    while True:
        print("Waiting for data")
        data = await websocket.receive_json()
        print(data)
        if data["type"] == "offer":
            offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
            await pc.setRemoteDescription(offer)
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            await websocket.send_json(
                {"type": "answer", "sdp": pc.localDescription.sdp}
            )
        elif data["type"] == "candidate":
            candidate = RTCIceCandidate(
                sdpMid=data["sdpMid"],
                sdpMLineIndex=data["sdpMLineIndex"],
                candidate=data["candidate"],
            )
            await pc.addIceCandidate(candidate)
        elif data["type"] == "disconnect":
            break

    await pc.close()
    pcs.discard(pc)


@router.on_event("shutdown")
async def shutdown():
    # Close all PeerConnections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()
