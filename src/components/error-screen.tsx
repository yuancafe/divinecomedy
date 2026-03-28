export function ErrorScreen({ message }: { message: string }) {
  return (
    <div className="state-screen">
      <div className="state-panel error">
        <p className="eyebrow">数据异常</p>
        <h1>数据加载失败</h1>
        <p>{message}</p>
      </div>
    </div>
  )
}
