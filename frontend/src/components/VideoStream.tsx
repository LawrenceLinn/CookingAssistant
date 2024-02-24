import React, { useEffect, useRef } from 'react'

const VideoStream: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    // 分别为视频和音频数据建立 WebSocket 连接
    const videoWs = new WebSocket('wss://192.168.2.92/ws/video')
    const audioWs = new WebSocket('wss://192.168.2.92/ws/audio')

    navigator.mediaDevices
      .getUserMedia({
        audio: true,
        video: true,
      })
      .then((stream) => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream
        }

        // 分离视频流中的音频和视频轨道
        const videoTracks = stream.getVideoTracks()
        const audioTracks = stream.getAudioTracks()

        // 创建用于视频的 MediaRecorder
        const videoRecorder = new MediaRecorder(new MediaStream(videoTracks), {
          mimeType: 'video/webm; codecs=vp8',
        })
        videoRecorder.ondataavailable = (event) => {
          if (event.data.size > 0 && videoWs.readyState === WebSocket.OPEN) {
            videoWs.send(event.data)
          }
        }

        // 创建用于音频的 MediaRecorder
        const audioRecorder = new MediaRecorder(new MediaStream(audioTracks), {
          mimeType: 'audio/webm; codecs=opus',
        })
        audioRecorder.ondataavailable = (event) => {
          if (event.data.size > 0 && audioWs.readyState === WebSocket.OPEN) {
            audioWs.send(event.data)
          }
        }

        // 启动录制
        videoRecorder.start(1000) // 调整这个值以满足你的需求
        audioRecorder.start(1000)
      })
      .catch((error) => {
        console.log('Error accessing media devices:', error)
      })

    // 组件卸载时关闭 WebSocket 连接
    return () => {
      videoWs.close()
      audioWs.close()
      console.log('WebSocket connections closed.')
    }
  }, [])

  return <video ref={videoRef} autoPlay playsInline muted />
}

export default VideoStream
