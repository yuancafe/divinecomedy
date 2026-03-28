import { Link, NavLink, Outlet } from 'react-router-dom'

import { cn } from '../lib/utils'

const navItems = [
  ['/', '首页'],
  ['/dante', '但丁'],
  ['/about', '神曲导读'],
  ['/map', '神曲阅读'],
  ['/inferno', '地狱'],
  ['/purgatorio', '炼狱'],
  ['/paradiso', '天堂'],
  ['/graph', '知识图谱'],
  ['/epic-status', '史诗谱系'],
] as const

export function SiteShell() {
  return (
    <div className="site-shell">
      <header className="site-header">
        <div className="site-header-top">
          <Link className="site-brand" to="/">
            <img alt="但丁《神曲》数字阅读标志" className="site-brand-mark-image" src="/media/logo.png" />
            <span className="site-brand-copy">
              <strong>但丁《神曲》数字阅读</strong>
              <small>《神曲》地图、整歌对读与知识图谱 | Digital Dante Museum</small>
            </span>
          </Link>
          <nav aria-label="主导航" className="site-nav">
            {navItems.map(([href, label]) => (
              <NavLink
                key={href}
                className={({ isActive }) => cn('site-nav-link', isActive && 'site-nav-link-active')}
                to={href}
              >
                {label}
              </NavLink>
            ))}
          </nav>
        </div>
        <div className="site-header-ribbon">
          <p>中文数字阅读馆 · 神曲阅读 · 整歌对读 · 译注编号 · 知识图谱</p>
        </div>
      </header>
      <main className="page-frame">
        <Outlet />
      </main>
      <footer className="site-footer">
        <nav className="site-footer-nav" aria-label="页脚导航">
          {navItems.map(([href, label]) => (
            <NavLink key={href} to={href}>
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="site-footer-copy">
          <span>© 2026 </span>
          <a href="https://www.yuan.cafe" rel="noreferrer" target="_blank">
            Leo Yuan Tsao
          </a>
          <span> · </span>
          <a href="https://yuandian.club" rel="noreferrer" target="_blank">
            SEED Reading Club
          </a>
        </div>

        <div className="site-footer-socials" aria-label="社交媒体链接">
          <a
            aria-label="GitHub"
            className="social-link"
            href="https://github.com/yuancafe"
            rel="noreferrer"
            target="_blank"
            title="GitHub"
          >
            <svg aria-hidden="true" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.58 2 12.24c0 4.53 2.87 8.37 6.84 9.73.5.1.66-.22.66-.49 0-.24-.01-1.04-.01-1.88-2.78.62-3.37-1.22-3.37-1.22-.45-1.19-1.11-1.5-1.11-1.5-.91-.64.07-.63.07-.63 1 .08 1.53 1.06 1.53 1.06.9 1.58 2.35 1.13 2.92.86.09-.67.35-1.13.63-1.39-2.22-.26-4.56-1.15-4.56-5.11 0-1.13.39-2.05 1.03-2.77-.1-.26-.45-1.31.1-2.74 0 0 .84-.27 2.75 1.06A9.3 9.3 0 0 1 12 6.84c.85 0 1.71.12 2.52.37 1.91-1.33 2.75-1.06 2.75-1.06.55 1.43.2 2.48.1 2.74.64.72 1.03 1.64 1.03 2.77 0 3.97-2.35 4.84-4.59 5.1.36.32.68.94.68 1.9 0 1.38-.01 2.49-.01 2.83 0 .27.18.59.67.49A10.27 10.27 0 0 0 22 12.24C22 6.58 17.52 2 12 2Z" />
            </svg>
          </a>

          <a
            aria-label="LinkedIn"
            className="social-link"
            href="https://www.linkedin.com/in/yuan-cao/"
            rel="noreferrer"
            target="_blank"
            title="LinkedIn"
          >
            <svg aria-hidden="true" viewBox="0 0 24 24">
              <path d="M6.94 8.5H3.56V20h3.38V8.5ZM5.25 3C4.17 3 3.3 3.9 3.3 5s.87 2 1.95 2 1.95-.9 1.95-2S6.33 3 5.25 3Zm14.45 9.87c0-3.28-1.72-4.81-4.02-4.81-1.85 0-2.67 1.03-3.13 1.75V8.5H9.18V20h3.37v-6.4c0-.34.02-.69.13-.93.27-.69.88-1.4 1.91-1.4 1.35 0 1.89 1.06 1.89 2.62V20h3.37l-.01-7.13Z" />
            </svg>
          </a>

          <a
            aria-label="Instagram"
            className="social-link"
            href="https://www.instagram.com/leo.yuan.cao/"
            rel="noreferrer"
            target="_blank"
            title="Instagram"
          >
            <svg aria-hidden="true" viewBox="0 0 24 24">
              <path d="M7.5 2h9A5.5 5.5 0 0 1 22 7.5v9a5.5 5.5 0 0 1-5.5 5.5h-9A5.5 5.5 0 0 1 2 16.5v-9A5.5 5.5 0 0 1 7.5 2Zm0 1.8A3.7 3.7 0 0 0 3.8 7.5v9a3.7 3.7 0 0 0 3.7 3.7h9a3.7 3.7 0 0 0 3.7-3.7v-9a3.7 3.7 0 0 0-3.7-3.7h-9Zm9.95 1.35a1.15 1.15 0 1 1 0 2.3 1.15 1.15 0 0 1 0-2.3ZM12 7a5 5 0 1 1 0 10 5 5 0 0 1 0-10Zm0 1.8A3.2 3.2 0 1 0 12 15.2 3.2 3.2 0 0 0 12 8.8Z" />
            </svg>
          </a>

          <div aria-label="微信" className="social-link social-link-wechat" title="微信">
            <svg aria-hidden="true" viewBox="0 0 24 24">
              <path d="M9.44 4C5.33 4 2 6.76 2 10.17c0 1.93 1.07 3.65 2.74 4.79L4 18l3.15-1.58c.73.19 1.49.3 2.29.3 4.11 0 7.44-2.76 7.44-6.17S13.55 4 9.44 4Zm-2.6 5.39a.8.8 0 1 1 0 1.6.8.8 0 0 1 0-1.6Zm5.2 0a.8.8 0 1 1 0 1.6.8.8 0 0 1 0-1.6Zm7.03 2.53c-2.72 0-4.93 1.84-4.93 4.1 0 2.26 2.21 4.1 4.93 4.1.53 0 1.04-.07 1.52-.2L23 21l-.69-2.08C23.37 18.2 24 17.17 24 16.02c0-2.26-2.21-4.1-4.93-4.1Zm-1.72 3.42a.63.63 0 1 1 0 1.26.63.63 0 0 1 0-1.26Zm3.44 0a.63.63 0 1 1 0 1.26.63.63 0 0 1 0-1.26Z" />
            </svg>
            <div className="wechat-popover">
              <img alt="Leo Yuan Tsao 微信二维码" src="/social/wechat-qrcode.jpg" />
              <span>微信扫码关注</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
