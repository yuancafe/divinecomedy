export function LoadingScreen({ message }: { message: string }) {
  return (
    <div className="state-screen">
      <div className="state-panel">
        <p className="eyebrow">数据装配中</p>
        <h1>{message}</h1>
        <p>正在装配六版本文本、世界地图、知识图谱与路线数据。</p>
      </div>
    </div>
  )
}
