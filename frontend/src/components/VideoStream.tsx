import React, { useEffect, useRef } from 'react'

const VideoStream: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    // 分别为视频和音频数据建立 WebSocket 连接
    const videoWs = new WebSocket(`wss://${import.meta.env.VITE_IP_ADDRESS}:443/ws/video`)
    const audioWs = new WebSocket(`wss://${import.meta.env.VITE_IP_ADDRESS}:443/ws/audio`)

    // 监听连接开启事件
    videoWs.onopen = function (event) {
      console.log('Video WebSocket is open now.')
    }

    // 监听接收消息事件
    videoWs.onmessage = function (event) {
      console.log('Video WebSocket message received:', event.data)
    }
    audioWs.onmessage = function (event) {
      console.log('Audio WebSocket message received:', event.data)
    }

    // 监听错误事件
    videoWs.onerror = function (event) {
      console.error('Video WebSocket encountered error: ', event)
    }
    audioWs.onerror = function (event) {
      console.error('Audio WebSocket encountered error: ', event)
    }

    // 监听连接关闭事件
    videoWs.onclose = function (event) {
      console.log('Video WebSocket is closed now.')
    }
    audioWs.onclose = function (event) {
      console.log('Audio WebSocket is closed now.')
    }

    const peer = new RTCPeerConnection();


    // 当WebRTC准备好将ICE候选发送到对方时
    peer.onicecandidate = event => {
      if (event.candidate) {
          videoWs.current.send(JSON.stringify({ candidate: event.candidate }));
      }
    };  

    console.log('peer', peer);

    navigator.mediaDevices
      .getUserMedia({
        audio: true,
        video: { facingMode: 'environment' },
      })
      .then((stream) => {
        // 分离视频流中的音频和视频轨道
        const videoTracks = stream.getVideoTracks()
        const audioTracks = stream.getAudioTracks()
        // 将音频和视频轨道添加到 RTCPeerConnection
        videoTracks.forEach(track => peer.addTrack(track, stream));
        audioTracks.forEach(track => peer.addTrack(track, stream));

        // // 创建用于视频的 MediaRecorder
        // const videoRecorder = new MediaRecorder(new MediaStream(videoTracks), {
        //   mimeType: 'video/mp4; codecs="avc1.42E01E"',
        // })
        // videoRecorder.ondataavailable = (event) => {
        //   if (event.data.size > 0 && videoWs.readyState === WebSocket.OPEN) {
        //     videoWs.send(event.data)
        //   }
        // }

        // // 创建用于音频的 MediaRecorder
        // const audioRecorder = new MediaRecorder(new MediaStream(audioTracks), {
        //   mimeType: 'audio/webm; codecs=opus',
        // })

        // audioRecorder.ondataavailable = (event) => {
        //   if (event.data.size > 0 && audioWs.readyState === WebSocket.OPEN) {
        //     audioWs.send(event.data)
        //   }
        // }

        // // 启动录制
        // videoRecorder.start(1000) // 调整这个值以满足你的需求
        // audioRecorder.start(1000)

        // if (videoRef.current) {
        //   videoRef.current.srcObject = stream
        // }
      })
      .catch((error) => {
        console.log('Error accessing media devices:', error)
      })

      peer.createOffer()
      .then(offer => peer.setLocalDescription(offer))
      .then(() => {
          videoWs.current.send(JSON.stringify({ offer: peer.localDescription }));
      });

    // 组件卸载时关闭 WebSocket 连接
    return () => {
      if (videoWs.readyState === WebSocket.OPEN && audioWs.readyState === WebSocket.OPEN) {
        videoWs.close()
        audioWs.close()
      }
      console.log('WebSocket connections closed.')
    }
  }, [])

  // return the video from backend

  return <video ref={videoRef} autoPlay playsInline muted />
}

export default VideoStream
