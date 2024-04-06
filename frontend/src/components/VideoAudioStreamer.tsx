import React, { useEffect, useRef, useState } from 'react'

const VideoAudioStreamer = () => {
  const videoRef = useRef(null)
  const [pc, setPc] = useState(null)
  const [ws, setWs] = useState(null)

  useEffect(() => {
    // 创建WebSocket连接
    const websocket = new WebSocket(`wss://${import.meta.env.VITE_IP_ADDRESS}:443/ws`)

    websocket.onopen = () => {
      console.log('WebSocket Connected')
    }

    websocket.onmessage = (message) => {
      const data = JSON.parse(message.data)
      switch (data.type) {
        case 'offer':
          console.log('offer', data.offer)
          handleOffer(data.offer)
          break
        case 'answer':
          console.log('answer', data.answer)
          handleAnswer(data.answer)
          break
        case 'candidate':
          console.log('candidate', data.candidate)
          handleCandidate(data.candidate)
          break
        default:
          break
      }
    }

    setWs(websocket)

    return () => {
      if (websocket.readyState === WebSocket.OPEN) {
        websocket.close()
      }
    }
  }, [])

  const handleOffer = (offer) => {
    pc.setRemoteDescription(new RTCSessionDescription(offer))
    // 创建应答
    pc.createAnswer().then((answer) => {
      pc.setLocalDescription(answer)
      // 通过WebSocket发送应答
      ws.send(JSON.stringify({ type: 'answer', answer }))
    })
  }

  const handleAnswer = (answer) => {
    pc.setRemoteDescription(new RTCSessionDescription(answer))
  }

  const handleCandidate = (candidate) => {
    pc.addIceCandidate(new RTCIceCandidate(candidate))
  }

  const start = () => {
    const config = {
      iceServers: [{ urls: ['stun:stun1.l.google.com:19302'] }],
    }
    const newPc = new RTCPeerConnection(config)
    console.log('newPc', newPc.onicecandidate)
    newPc.onicecandidate = (event) => {
      console.log('onicecandidate', event)
      if (event.candidate) {
        ws.send(JSON.stringify({ type: 'candidate', candidate: event.candidate.toJSON() }))
      }
    }

    navigator.mediaDevices
      .getUserMedia({
        audio: true,
        video: { facingMode: 'environment' },
      })
      .then((stream) => {
        if (videoRef.current) videoRef.current.srcObject = stream
        stream.getTracks().forEach((track) => newPc.addTrack(track, stream))
      })
      .catch(console.error)

    setPc(newPc)
  }

  const stop = () => {
    if (pc) {
      pc.close()
      setPc(null)
      if (videoRef.current) videoRef.current.srcObject = null
    }
  }

  return (
    <div>
      <video ref={videoRef} autoPlay playsInline muted />
      <button onClick={start}>Start</button>
      <button onClick={stop}>Stop</button>
    </div>
  )
}

export default VideoAudioStreamer
